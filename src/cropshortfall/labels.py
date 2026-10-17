"""Prespecified, training-only shortfall labels on observed seasonal yields.

Primary label (fixed before computing any prevalence):
    shortfall_t = yield_t < RATIO * median(yield of the previous valid years,
                  up to WINDOW years, at least MIN_HISTORY of them)
The threshold for season t uses only seasons harvested before t, so a test
season never contributes to its own threshold. No values are imputed; seasons
without enough history are left unlabelled rather than filled.

This module only characterises the target (event counts, clustering by
country-season-year). It fits no predictive model.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd

from .audit import EAST_AFRICA, load, valid_rows

RATIO = 0.80
WINDOW = 10
MIN_HISTORY = 10
CANDIDATES = [("KE", "Maize", "Long"), ("KE", "Maize", "Short"),
              ("SO", "Maize", "Gu"), ("SO", "Maize", "Deyr"),
              ("SO", "Sorghum", "Gu"), ("SO", "Sorghum", "Deyr"),
              ("ET", "Maize", "Meher"), ("ET", "Sorghum", "Meher")]


def trailing_labels(years: np.ndarray, values: np.ndarray, ratio: float = RATIO,
                    window: int = WINDOW, min_history: int = MIN_HISTORY) -> pd.DataFrame:
    order = np.argsort(years)
    years, values = years[order], values[order]
    if len(np.unique(years)) != len(years):
        raise ValueError("duplicate harvest years within one series")
    ref = np.full(len(values), np.nan)
    for i in range(len(values)):
        hist = values[max(0, i - window):i]
        if len(hist) >= min_history:
            ref[i] = np.median(hist)
    label = np.where(np.isnan(ref), np.nan, (values < ratio * ref).astype(float))
    return pd.DataFrame({"harvest_year": years, "value": values,
                         "reference": ref, "shortfall": label})


def label_candidates(df: pd.DataFrame) -> pd.DataFrame:
    v = df[valid_rows(df)]
    out = []
    for cc, prod, season in CANDIDATES:
        sub = v[(v.country_code == cc) & (v["product"] == prod) & (v.season_name == season)]
        for keys, s in sub.groupby(["fnid", "crop_production_system"]):
            lab = trailing_labels(s["harvest_year"].to_numpy(), s["yield"].to_numpy())
            lab.insert(0, "fnid", keys[0])
            lab.insert(0, "season_name", season)
            lab.insert(0, "product", prod)
            lab.insert(0, "country_code", cc)
            lab["crop_production_system"] = keys[1]
            out.append(lab)
    return pd.concat(out, ignore_index=True)


def summarise(labels: pd.DataFrame) -> pd.DataFrame:
    lab = labels.dropna(subset=["shortfall"])
    keys = ["country_code", "product", "season_name"]
    by_year = lab.groupby(keys + ["harvest_year"])["shortfall"].agg(["size", "mean"])
    s = lab.groupby(keys).agg(labelled_unit_seasons=("shortfall", "size"),
                              shortfall_events=("shortfall", "sum"),
                              units=("fnid", "nunique"),
                              first_labelled_year=("harvest_year", "min"),
                              last_labelled_year=("harvest_year", "max"))
    s["prevalence"] = s["shortfall_events"] / s["labelled_unit_seasons"]
    s["labelled_years"] = by_year.groupby(keys).size()
    # years in which >= 30% of labelled units are in shortfall: the effective
    # independent "event seasons" once spatial co-occurrence is acknowledged
    s["widespread_shortfall_years"] = (by_year["mean"] >= 0.30).groupby(keys).sum()
    s["labelled_years_2018_plus"] = by_year.reset_index().query("harvest_year >= 2018").groupby(keys).size()
    return s.fillna(0).reset_index()


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--csv", type=Path, default=Path("data/raw/harveststat/hvstat_africa_data_v1.2.csv"))
    ap.add_argument("--out", type=Path, default=Path("results/tables"))
    args = ap.parse_args()
    df = load(args.csv)
    df = df[df.country_code.isin(EAST_AFRICA)]
    summary = summarise(label_candidates(df))
    summary.to_csv(args.out / "shortfall_label_feasibility.csv", index=False)
    print(summary.to_string(index=False))


if __name__ == "__main__":
    main()
