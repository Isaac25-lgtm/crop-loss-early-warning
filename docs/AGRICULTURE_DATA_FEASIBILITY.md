# R06 agriculture data feasibility (phase 1, 17 October 2026)

All numbers below were produced in this cloud session by the code in
`src/cropshortfall/` against the file identified in
`results/tables/acquisition_manifest.json`. Nothing is simulated or imputed.

## 1. Source actually acquired

| Item | Value |
|---|---|
| Dataset | HarvestStat Africa v1.2 (Lee et al., *Scientific Data* 2025, doi:10.1038/s41597-025-05001-z) |
| Underlying observations | FEWS NET Data Warehouse compilations of official national/subnational crop statistics, harmonised across boundary changes |
| Route that worked | Public GitHub repo `HarvestStat/HarvestStat-Africa`, commit `c80b451df014e6a15aed75e70cd9c2ddd3631f82` (2026-09-30), sparse clone of `public/` |
| Route that failed | Dryad API file download (`datadryad.org/api/v2/files/<id>/download`) → **HTTP 401 Unauthorized** for all files; metadata endpoint public (v12, published 2026-07-17, 94,023,588 bytes, CC0-1.0) |
| Main file | `hvstat_africa_data_v1.2.csv`, 25,299,000 bytes, SHA256 `a95e71bb…f225` (Dryad's v1.2 CSV is listed at 25,312,039 bytes / `f659e121…bef9`; the two are **not byte-identical** and were not reconciled because the Dryad file could not be downloaded) |
| CHANGELOG | SHA256 matches Dryad digest exactly (`ad21f228…ad74`) |
| License | Dryad: CC0-1.0; GitHub repo: MIT; CGIAR listing reports CC-BY-4.0. Treat as open, cite the paper; resolve wording before redistribution |
| Rows | 217,370 (all countries in this v1.2 file); 66,446 in nine East African countries |
| Units | area ha, production t, yield t/ha; `yield == production/area` for all 57,025 valid East African rows (0 inconsistencies) |
| Duplicates | 0 duplicate series×season×year keys in East Africa |
| Missing | East Africa: area 7,513, production 1,322, yield 8,898 rows missing (excluded, not filled) |

*Valid row* = production > 0, area > 0 and `qc_flag == 0` (flags: 1 outlier, 2 low variance).

## 2. Uganda: no observed seasonal time series in HarvestStat

* 1,804 Uganda rows, **all** on boundary set `UG2007A2` (80 districts).
* Only harvest years **2008 (Second season) and 2009 (First season)**, i.e. a single agricultural year, consistent with the Uganda Census of Agriculture 2008/09.
* 0 Uganda series meet the eligibility rule; a shortfall relative to a district's own history cannot be defined.
* Combined with the earlier GROW audit (mostly historical survey/plot rows, zero Uganda crop-cut rows, reported but not reproduced here), **no lawful public Uganda district×crop×season production series with modern repeated observations was found.**

Decision for Uganda: **HOLD_DATA**.

## 3. East Africa: prespecified eligibility

Rule fixed in `audit.Eligibility` before inspecting East African detail: ≥15 valid harvest years per
series (unit×crop×season×system), ≥5 of them in 2012 or later, latest ≥2018.

| Country | Rows | Harvest years | Eligible series | Eligible units | Rows with harvest ≥2023 |
|---|---|---|---|---|---|
| Uganda | 1,804 | 2008–2009 | 0 | 0 | 0 |
| Kenya | 15,795 | 1966–2024 | 245 | 47 | 711 |
| Somalia | 7,441 | 1995–2026 | 227 | 40 | 1,304 |
| Ethiopia | 19,662 | 1993–2022 | 515 | 68 | 0 |
| Sudan | 3,733 | 1975–2024 | 83 | 18 | 65 |
| Tanzania | 6,397 | 1989–2015 | 0 | 0 | 0 |
| Rwanda | 3,612 | 2008–2017 | 0 | 0 | 0 |
| Burundi | 7,683 | 1996–2016 | 0 | 0 | 0 |
| South Sudan | 319 | 1975–2022 | 0 | 0 | 0 |

Full detail: `results/tables/ea_country_summary.csv`, `results/tables/ea_crop_season_coverage.csv`.

Season-resolved candidates (not merely annual totals): Kenya maize Long rains (42 counties eligible,
harvest mode August) and Short rains (21 counties, harvest mode March), 1991–2024; Somalia maize and
sorghum Gu (harvest mode August) and Deyr (harvest mode March), 1995–2026, 26–35 districts each;
Ethiopia Meher (single main season, to 2021).

## 4. Shortfall label characterisation (no model fitted)

Primary label, fixed in `labels.py` before computing prevalence: yield in season *t* < 0.80 × median of
the previous ≤10 valid seasons of the same unit/crop/season, requiring 10 prior seasons. Thresholds use
only earlier seasons (tested in `test_labels_use_only_past_seasons`).

| Candidate | Labelled unit-seasons | Shortfalls | Prevalence | Labelled years | Years with ≥30% of units in shortfall | Labelled years ≥2018 |
|---|---|---|---|---|---|---|
| KE maize Long | 434 | 138 | 0.32 | 11 | 6 | 7 |
| KE maize Short | 164 | 79 | 0.48 | 10 | 5 | 7 |
| SO maize Gu | 616 | 265 | 0.43 | 21 | 17 | 8 |
| SO maize Deyr | 515 | 226 | 0.44 | 21 | 16 | 9 |
| SO sorghum Gu | 483 | 218 | 0.45 | 21 | 15 | 8 |
| SO sorghum Deyr | 416 | 168 | 0.40 | 20 | 12 | 8 |
| ET maize Meher | 666 | 9 | 0.01 | 17 | 0 | 4 |
| ET sorghum Meher | 547 | 8 | 0.01 | 15 | 0 | 4 |

Interpretation:

* **Effective sample size is seasons, not unit-seasons.** Shortfalls co-occur across units in the same
  season, so Kenya offers about 10–11 labelled seasons per rainy season and Somalia about 20–21.
  Any validation must block on season-year (leave-season-out) and report uncertainty over seasons.
* **Ethiopia Meher prevalence (~1%) is implausibly low** for a rainfed system with documented droughts.
  This suggests smoothed or modelled official estimates, which would make it an invalid shortfall
  target until checked against CSA source reports.
* **Somalia prevalence (~43%) means a 0.8 ratio describes volatility, not rare loss.** FSNAU
  post-harvest estimates are assessment-based, and conflict and access affect area. A
  production-based or more extreme threshold must be justified agronomically before any model.
* **Kenya** gaps (only 10–11 labelled seasons despite 1991–2024 coverage) need to be traced to
  missing years in the source.

## 5. Public-by timing (Gate 4/7)

HarvestStat provides no per-record publication date. `harvest_year`/`harvest_month` give the
*observation* timing; the release vintage of each official estimate is unknown. Consequences:

* A previous-season baseline is only legitimate if that season's estimate was public by the forecast
  date. FSNAU Gu assessments are typically released around August–September and Deyr around
  February. Kenya county figures are released later and irregularly. **This is unverified here.**
* HarvestStat v1.2 values are *harmonised/calibrated* across boundary changes, i.e. later revisions,
  not the vintage a forecaster would have seen. That is acceptable for the target, but it disqualifies
  using HarvestStat values of earlier seasons as as-of predictors without vintage evidence.

## 6. Status by gate

| Dimension | Status |
|---|---|
| Data access | Uganda HOLD_DATA; East Africa ACCESSED (GitHub mirror); Dryad API blocked (401) |
| Target validity | Uganda none. KE/SO seasonal yields are CONDITIONAL (official estimates, not crop cuts; ET suspect) |
| Lead-time design | Not established: needs dekadal CHIRPS with release-lag rules and verified previous-season release dates |
| Novelty | Weak if framed as "forecast KE/SO maize": the same FEWS NET source is already used for operational and ML yield forecasting by the HarvestStat/CHC authors (see PRIOR_ART.md) |
| AI incremental value | Untested (no model fitted, by design) |
| Readiness | REDESIGN |
