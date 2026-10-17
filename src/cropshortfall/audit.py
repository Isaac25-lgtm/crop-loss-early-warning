"""Target-eligibility audit of HarvestStat Africa for a seasonal shortfall label.

Eligibility rules are fixed here *before* any model is fitted and were written
before inspecting East African series detail (only the Uganda coverage and
per-country row counts had been seen). They decide whether an observed,
season-resolved production/yield series is long and recent enough to define a
shortfall threshold from training years only and still leave independent
out-of-sample seasons.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass
from pathlib import Path

import pandas as pd

EAST_AFRICA = ["UG", "KE", "TZ", "RW", "BI", "ET", "SO", "SS", "SD"]
SERIES_KEY = ["country_code", "fnid", "product", "season_name", "crop_production_system"]
REQUIRED_COLUMNS = SERIES_KEY + ["country", "admin_1", "admin_2", "planting_year",
                                 "planting_month", "harvest_year", "harvest_month",
                                 "qc_flag", "area", "production", "yield"]


@dataclass(frozen=True)
class Eligibility:
    min_years: int = 15          # distinct valid harvest years per series
    min_recent_years: int = 5    # valid years with harvest_year >= recent_from
    recent_from: int = 2012
    latest_at_least: int = 2018  # most recent valid harvest year
    min_train_years: int = 10    # years needed before a test year to set a threshold


def load(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path)
    missing = set(REQUIRED_COLUMNS) - set(df.columns)
    if missing:
        raise ValueError(f"schema drift: missing columns {sorted(missing)}")
    return df


def valid_rows(df: pd.DataFrame) -> pd.Series:
    """Observed, internally consistent, non-flagged rows (no imputation)."""
    return ((df["production"] > 0) & (df["area"] > 0) & (df["qc_flag"] == 0)
            & df["harvest_year"].notna())


def yield_consistency(df: pd.DataFrame, rtol: float = 1e-3) -> pd.Series:
    """True where yield == production/area within tolerance (units mt/ha)."""
    implied = df["production"] / df["area"]
    return ((df["yield"] - implied).abs() <= rtol * implied.abs().clip(lower=1e-9))


def duplicate_keys(df: pd.DataFrame) -> int:
    return int(df.duplicated(SERIES_KEY + ["harvest_year", "harvest_month",
                                           "planting_year", "planting_month"]).sum())


def series_table(df: pd.DataFrame, rule: Eligibility = Eligibility()) -> pd.DataFrame:
    v = df[valid_rows(df)]
    g = v.groupby(SERIES_KEY, dropna=False)["harvest_year"]
    s = pd.DataFrame({
        "n_years": g.nunique(),
        "first_year": g.min(),
        "last_year": g.max(),
        "n_recent_years": v[v["harvest_year"] >= rule.recent_from]
        .groupby(SERIES_KEY, dropna=False)["harvest_year"].nunique(),
    }).fillna({"n_recent_years": 0}).reset_index()
    s["n_recent_years"] = s["n_recent_years"].astype(int)
    # test years available after at least min_train_years earlier valid years
    years = g.apply(lambda x: sorted(set(x)))
    s["n_testable_years"] = years.apply(
        lambda ys: max(0, len(ys) - rule.min_train_years)).values
    s["eligible"] = ((s["n_years"] >= rule.min_years)
                     & (s["n_recent_years"] >= rule.min_recent_years)
                     & (s["last_year"] >= rule.latest_at_least))
    return s


def coverage_table(df: pd.DataFrame, series: pd.DataFrame) -> pd.DataFrame:
    keys = ["country_code", "product", "season_name"]
    v = df[valid_rows(df)]
    rows = v.groupby(keys).agg(valid_rows=("fnid", "size"), units=("fnid", "nunique"),
                               first_year=("harvest_year", "min"),
                               last_year=("harvest_year", "max"),
                               n_years=("harvest_year", "nunique"),
                               harvest_month_mode=("harvest_month",
                                                   lambda m: int(m.mode().iloc[0])))
    el = series.groupby(keys).agg(series=("eligible", "size"),
                                  eligible_series=("eligible", "sum"),
                                  eligible_units=("fnid", lambda f: f[series.loc[f.index, "eligible"]].nunique()))
    out = rows.join(el, how="left").fillna(0).reset_index()
    for c in ["series", "eligible_series", "eligible_units"]:
        out[c] = out[c].astype(int)
    return out.sort_values(["country_code", "eligible_series", "valid_rows"],
                           ascending=[True, False, False])


def country_summary(df: pd.DataFrame, series: pd.DataFrame) -> pd.DataFrame:
    v = valid_rows(df)
    out = df.groupby("country_code").agg(rows=("fnid", "size"),
                                         first_year=("harvest_year", "min"),
                                         last_year=("harvest_year", "max"),
                                         n_years=("harvest_year", "nunique"),
                                         units=("fnid", "nunique"),
                                         products=("product", "nunique"),
                                         seasons=("season_name", "nunique"))
    out["valid_rows"] = df[v].groupby("country_code").size()
    out["rows_harvest_2020_plus"] = df[df["harvest_year"] >= 2020].groupby("country_code").size()
    out["rows_harvest_2023_plus"] = df[df["harvest_year"] >= 2023].groupby("country_code").size()
    out["qc_flagged_rows"] = df[df["qc_flag"] != 0].groupby("country_code").size()
    out["eligible_series"] = series.groupby("country_code")["eligible"].sum()
    out["eligible_units"] = series[series["eligible"]].groupby("country_code")["fnid"].nunique()
    return out.fillna(0).astype({c: int for c in out.columns}).reset_index()


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--csv", type=Path, default=Path("data/raw/harveststat/hvstat_africa_data_v1.2.csv"))
    ap.add_argument("--out", type=Path, default=Path("results/tables"))
    args = ap.parse_args()
    rule = Eligibility()
    df = load(args.csv)
    args.out.mkdir(parents=True, exist_ok=True)
    ea = df[df["country_code"].isin(EAST_AFRICA)].copy()
    series = series_table(ea, rule)
    country_summary(ea, series).to_csv(args.out / "ea_country_summary.csv", index=False)
    coverage_table(ea, series).to_csv(args.out / "ea_crop_season_coverage.csv", index=False)
    ug = df[df["country_code"] == "UG"]
    ug_cov = ug.groupby(["product", "season_name", "planting_year", "planting_month",
                         "harvest_year", "harvest_month"]).agg(
        rows=("fnid", "size"), districts=("fnid", "nunique")).reset_index()
    ug_cov.to_csv(args.out / "uganda_harveststat_coverage.csv", index=False)
    checks = {
        "source_rows_all_countries": int(len(df)),
        "east_africa_rows": int(len(ea)),
        "east_africa_valid_rows": int(valid_rows(ea).sum()),
        "east_africa_duplicate_keys": duplicate_keys(ea),
        "east_africa_yield_inconsistent_rows": int((~yield_consistency(ea[valid_rows(ea)])).sum()),
        "east_africa_missing_by_column": {c: int(n) for c, n in ea.isna().sum().items() if n},
        "uganda_rows": int(len(ug)),
        "uganda_harvest_years": sorted(int(y) for y in ug["harvest_year"].unique()),
        "uganda_fnid_prefixes": sorted(ug["fnid"].str[:8].unique().tolist()),
        "uganda_eligible_series": int(series.query("country_code == 'UG'")["eligible"].sum()),
        "max_harvest_year_all_countries": int(df["harvest_year"].max()),
        "eligibility_rule": asdict(rule),
    }
    (args.out / "audit_checks.json").write_text(json.dumps(checks, indent=2) + "\n")
    print(json.dumps(checks, indent=2))


if __name__ == "__main__":
    main()
