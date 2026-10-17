# R06 evidence status

Updated 17 October 2026 by a Claude Code cloud session (phase-1 checkpoint).

**Scientific decision: REDESIGN.** Uganda target is **HOLD_DATA**. The East African seasonal target is
**CONDITIONAL** (not cleared for full-study protocol).

## What was executed

* Environment: Linux container, 4 vCPU (work limited to ≤2 threads; no parallel jobs), 15 GiB RAM, Python 3.13.16, pandas 3.0.5, numpy 2.5.3; no scikit-learn installed (not needed: no model fitted).
* Network: HTTPS via an egress proxy. `api.github.com` unauthenticated → 403. `datadryad.org` metadata → 200. Dryad file download → 401. `github.com` git clone → OK.
* Acquisition: HarvestStat Africa v1.2 from GitHub commit `c80b451`. Bytes and SHA256 are in `results/tables/acquisition_manifest.json`.
* Audit: `python -m cropshortfall.audit`, then `python -m cropshortfall.labels`, writing tables to `results/tables/`.
* Tests: `pytest -q` → 11 passed.

## Key findings

1. Uganda has a single agricultural year in HarvestStat (harvests 2008 second and 2009 first season, 80 districts). 0 eligible series. No shortfall label is possible.
2. Kenya (Long/Short rains maize, 1991–2024) and Somalia (Gu/Deyr maize/sorghum, 1995–2026) pass the prespecified length and recency rule.
3. Effective validation sample: about 10–11 seasons (Kenya) and about 20–21 seasons (Somalia) per crop-season, because shortfalls co-occur spatially.
4. Ethiopia Meher has a shortfall prevalence near 1%, which suggests smoothed estimates. Not a usable target without source checks.
5. The publication date of individual official estimates is unknown. Lead-time legitimacy of previous-season baselines is unverified.

## Attempt log (honest count)

* `datadryad.org` file downloads: the first acquisition run made 3 attempts for each of 3 files (9 requests, all 401) before a per-host cap existed. The rerun with the cap made 3 requests (all 401) and stopped. This exceeded the "3 attempts per host" instruction on the first run. The code now enforces the cap (`acquire._take_attempt`) and never retries a 401/403.
* `github.com`: 1 clone. `api.github.com`: 2 requests (403).

## Not done (by design)

No climate rasters, no CHIRPS/WaPOR download, no ML. The gate requires a valid target and a prespecified lead-time design first. No dashboard: there are no model results to present, and the feasibility tables are in `results/tables/`.

See `docs/AGRICULTURE_DATA_FEASIBILITY.md` for detail and `docs/DECISION_LOG.md` for next steps.
