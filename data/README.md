# Data access and publication boundary

Raw inputs live under `data/raw/` (gitignored) and are recreated by `python -m cropshortfall.acquire`.
Provenance (URL, git commit, bytes, SHA256, access time, license) is in
`results/tables/acquisition_manifest.json`.

| Source | License | Observed period (East Africa) | In Git? |
|---|---|---|---|
| HarvestStat Africa v1.2 (FEWS NET official statistics, harmonised) | CC0-1.0 (Dryad) / MIT (GitHub repo) | Kenya 1966–2024, Somalia 1995–2026, Ethiopia 1993–2022, Uganda 2008–2009 only | No — aggregate audit tables only |

Only aggregate counts derived from open data are committed. No respondent microdata is used. There
are no synthetic samples: test fixtures are built inline in `tests/` and are clearly synthetic.
