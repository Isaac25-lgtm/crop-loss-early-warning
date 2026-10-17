# Data access: fetched vs catalogued

| Source | Status | Evidence |
|---|---|---|
| HarvestStat Africa v1.2, GitHub `HarvestStat/HarvestStat-Africa@c80b451` | **FETCHED** | `results/tables/acquisition_manifest.json` (bytes, SHA256, commit time) |
| HarvestStat Africa, Dryad v12 file API | **BLOCKED (HTTP 401)** | Metadata public (CC0-1.0, 2026-07-17). Downloads appear to need a Dryad API token or browser session. Access path: the investigator downloads from https://doi.org/10.5061/dryad.vq83bk42w in a browser, or supplies a free Dryad API token, so the Dryad v1.2 CSV hash can be reconciled with the GitHub copy |
| FEWS NET raw `fdw_raw_data_v1.2.zip` (54.7 MB, Dryad) | BLOCKED with Dryad | Needed to inspect source-level reporting (estimate vs survey) |
| GROW-Africa (Zenodo 16544448) | CATALOGUE_ONLY this session | Earlier audit reported, not reproduced |
| UBOS Annual Agricultural Survey / UCA 2008/09; UNPS (LSMS-ISA) | CATALOGUE_ONLY | Microdata via UBOS NADA / World Bank Microdata Library require registration and terms acceptance by the investigator. UNPS crop production is self-reported, not crop-cut |
| FSNAU Somalia Gu/Deyr post-harvest assessment reports | CATALOGUE_ONLY | Needed for release dates (public-by) per season |
| CHIRPS v2/v3 dekadal, FAO WaPOR | NOT FETCHED (by design) | Only after the target and lead-time design are frozen |
| FEWS NET Data Warehouse | NOT ATTEMPTED | Requires account login |
