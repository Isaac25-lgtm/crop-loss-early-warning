"""Fixture-based tests for target eligibility, label leakage and provenance.

Fixtures are small hand-built frames, clearly synthetic; they are never used
as observed data.
"""

import json
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from cropshortfall import acquire, audit, labels

ROOT = Path(__file__).resolve().parents[1]


def _rows(cc="KE", fnid="KE001", years=range(2000, 2020), season="Long", yld=None, qc=0):
    years = list(years)
    yld = yld if yld is not None else [2.0] * len(years)
    return pd.DataFrame({
        "fnid": fnid, "country": cc, "country_code": cc, "admin_1": "A", "admin_2": "B",
        "product": "Maize", "season_name": season, "planting_year": [y for y in years],
        "planting_month": 3, "harvest_year": years, "harvest_month": 8,
        "crop_production_system": "none", "qc_flag": qc, "area": 100.0,
        "production": [100.0 * v for v in yld], "yield": yld,
    })


def test_schema_drift_is_rejected(tmp_path):
    p = tmp_path / "x.csv"
    _rows().drop(columns=["season_name"]).to_csv(p, index=False)
    with pytest.raises(ValueError, match="season_name"):
        audit.load(p)


def test_valid_rows_exclude_qc_flags_and_nonpositive():
    df = pd.concat([_rows(years=[2000]), _rows(years=[2001], qc=1),
                    _rows(years=[2002], yld=[0.0])])
    assert audit.valid_rows(df).tolist() == [True, False, False]


def test_yield_consistency_detects_unit_error():
    df = _rows(years=[2000, 2001])
    df.loc[1, "yield"] = 2000.0  # kg/ha mistaken for mt/ha
    assert audit.yield_consistency(df).tolist() == [True, False]


def test_eligibility_requires_length_recency_and_latest():
    long_recent = _rows(fnid="A", years=range(2000, 2020))
    short = _rows(fnid="B", years=range(2010, 2020))
    stale = _rows(fnid="C", years=range(1990, 2010))
    s = audit.series_table(pd.concat([long_recent, short, stale])).set_index("fnid")
    assert s.loc["A", "eligible"] and not s.loc["B", "eligible"] and not s.loc["C", "eligible"]
    assert s.loc["A", "n_testable_years"] == 10


def test_single_year_cross_section_is_never_eligible():
    # the Uganda pattern: many districts, one agricultural year
    df = pd.concat([_rows(cc="UG", fnid=f"UG{i}", years=[2009], season="First") for i in range(80)])
    assert audit.series_table(df)["eligible"].sum() == 0


def test_labels_use_only_past_seasons():
    years = np.arange(2000, 2025)
    vals = np.linspace(2.0, 3.0, len(years))
    base = labels.trailing_labels(years, vals.copy())
    perturbed = vals.copy()
    perturbed[-1] = 0.01  # change only the final season
    after = labels.trailing_labels(years, perturbed)
    pd.testing.assert_series_equal(base["reference"], after["reference"])
    assert after["shortfall"].iloc[-1] == 1.0
    pd.testing.assert_series_equal(base["shortfall"].iloc[:-1], after["shortfall"].iloc[:-1])


def test_labels_unlabelled_without_enough_history():
    out = labels.trailing_labels(np.arange(2000, 2012), np.ones(12))
    assert out["shortfall"].isna().sum() == labels.MIN_HISTORY
    assert out["shortfall"].iloc[-1] == 0.0


def test_label_threshold_is_strictly_below_ratio_of_median():
    years = np.arange(2000, 2012)
    vals = np.r_[np.ones(10), 0.80, 0.79]
    out = labels.trailing_labels(years, vals)
    assert out["shortfall"].iloc[10] == 0.0 and out["shortfall"].iloc[11] == 1.0


def test_duplicate_years_rejected():
    with pytest.raises(ValueError):
        labels.trailing_labels(np.array([2000, 2000]), np.array([1.0, 2.0]))


def test_sha256_and_host_budget(tmp_path):
    p = tmp_path / "f.bin"
    p.write_bytes(b"abc")
    assert acquire.sha256_file(p) == "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad"
    acquire._HOST_ATTEMPTS.clear()
    url = "https://example.invalid/x"
    assert [acquire._take_attempt(url) for _ in range(4)] == [True, True, True, False]


def test_committed_audit_outputs_are_consistent():
    checks = json.loads((ROOT / "results/tables/audit_checks.json").read_text())
    assert checks["uganda_harvest_years"] == [2008, 2009]
    assert checks["uganda_eligible_series"] == 0
    summary = pd.read_csv(ROOT / "results/tables/ea_country_summary.csv").set_index("country_code")
    assert summary.loc["UG", "eligible_series"] == 0
    assert summary.loc["KE", "eligible_series"] > 0
    manifest = json.loads((ROOT / "results/tables/acquisition_manifest.json").read_text())
    git = [m for m in manifest if m.get("name") == "hvstat_africa_data_v1.2.csv" and m.get("git_commit")]
    assert git and git[0]["pinned_commit_matches"] and len(git[0]["sha256"]) == 64
    assert all(m["status"] != "downloaded" or m.get("sha256_matches_source") for m in manifest
               if "expected_sha256" in m)
