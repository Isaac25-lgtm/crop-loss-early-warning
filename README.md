# Crop-production shortfall early-warning feasibility (R06)

Investigator: Isaac Omoding · Research programme R06 · Stage: **target discovery (phase 1 complete)**

Early warning of seasonal crop-production shortfalls is only as credible as the shortfall label it is
trained on. That label must be observed, season-resolved, sub-national, and public by the time a
forecaster would have used it. This repository tests whether such a target exists for Uganda or East
Africa *before* any model is built.

**Status: REDESIGN.** Uganda: **HOLD_DATA**. East Africa (Kenya, Somalia): **CONDITIONAL**. No model has
been trained, and no dashboard has been built or deployed.

## Research questions

1. Is there a lawful, observed district×crop×season production/yield series for Uganda with modern repeated seasons? *(Phase 1: no.)*
2. If not, which East African series support a training-only shortfall label with enough independent seasons? *(Kenya Long/Short rains maize; Somalia Gu/Deyr maize and sorghum.)*
3. Does reported early-warning skill survive vintage-realistic, season-blocked evaluation? *(Not yet tested.)*

## What phase 1 found (real data, this repo's code)

* HarvestStat Africa v1.2 (FEWS NET official statistics; GitHub commit `c80b451`): 217,370 rows, of which 66,446 are East African.
* **Uganda: 1,804 rows, only harvest years 2008–2009 (one agricultural year, 80 districts). 0 eligible series.**
* Prespecified eligibility (≥15 valid years, ≥5 since 2012, latest ≥2018): Kenya 245 series / 47 counties; Somalia 227 / 40 districts; Ethiopia 515 / 68 (but see below); Tanzania, Rwanda, Burundi, South Sudan 0.
* Shortfall label (yield < 0.8 × trailing 10-season median, earlier seasons only):
  * Somalia ≈ 43% prevalence over about 20–21 seasons.
  * Kenya 32–48% over about 10–11 seasons.
  * Ethiopia ≈ 1%, which suggests smoothed estimates.
  * Events cluster by season, so the **effective sample is seasons, not district-seasons**.
* Publication (public-by) dates of individual official estimates are not in the source. Lead-time legitimacy is unverified.
* The obvious "Kenya/Somalia maize ML forecast" is already published on the same source (Lee et al. 2022, *Global Food Security*).

Details: [`docs/AGRICULTURE_DATA_FEASIBILITY.md`](docs/AGRICULTURE_DATA_FEASIBILITY.md) · [`docs/PRIOR_ART.md`](docs/PRIOR_ART.md) · [`docs/STATUS.md`](docs/STATUS.md) · [`docs/DATA_ACCESS.md`](docs/DATA_ACCESS.md) · [`docs/DECISION_LOG.md`](docs/DECISION_LOG.md)

## Not claimed

No forecast skill, no economic impact, no Uganda yield trend, and no aquaculture productivity
inference. A newer upload date does not mean newer observations.

## Reproduce

```bash
pip install -e '.[test]'
python -m cropshortfall.acquire && python -m cropshortfall.audit && python -m cropshortfall.labels
pytest -q
```

Raw data stays outside Git (`data/raw/`, gitignored). See [`docs/REPRODUCIBILITY.md`](docs/REPRODUCIBILITY.md).

## Next step

A vintage-realistic, season-blocked shortfall-event evaluation for Somalia Gu/Deyr and Kenya rains
seasons. This first requires per-season release dates and a production-based event definition. See the
decision log.

## Data citation

Lee, D. et al. (2025). HarvestStat Africa – Harmonized subnational crop statistics for Sub-Saharan Africa. *Scientific Data*. doi:10.1038/s41597-025-05001-z. Data: doi:10.5061/dryad.vq83bk42w.

*AI assistance:* code and documentation in this checkpoint were drafted by an AI coding assistant (Claude Code) under investigator direction. They must be reviewed before any publication use.
