# Closest prior work (phase-1 competitor audit)

Depth labels: `FULL_TEXT`, `ABSTRACT`, `REPOSITORY`, `CATALOGUE_ONLY`, `UNVERIFIED`. Every row here was
checked only through search-result abstracts or metadata in this session. Full texts were not read.
Claims are limited to what those pages state.

| # | Work | Venue / ID | Depth | Data, place, outcome | What it shows / limitation for R06 |
|---|---|---|---|---|---|
| 1 | Lee et al., *HarvestStat Africa – Harmonized subnational crop statistics for Sub-Saharan Africa* | *Scientific Data* 2025, doi:10.1038/s41597-025-05001-z; Dryad doi:10.5061/dryad.vq83bk42w | REPOSITORY + ABSTRACT | FEWS NET subnational area/production/yield, 33 countries, mostly 1980–2022 | **Same-source competitor.** Data paper; motivates forecasting. Our audit shows Uganda is a single 2008/09 year in v1.2 |
| 2 | Lee, Davenport, Shukla et al., *Maize yield forecasts for Sub-Saharan Africa using Earth Observation data and machine learning* | *Global Food Security* 2022, doi:10.1016/j.gfs.2022.100643 | ABSTRACT | Subnational maize, Kenya, Somalia, Malawi, Burkina Faso; EO + ML; out-of-sample skill by lead time | **Same-question competitor.** Skilful (NSE > 0.6, MAPE < 20%) forecasts reported by May for Kenya and Somalia; dekadal features help. A new "KE/SO maize ML forecast" would be a replication, not an advance |
| 3 | Davenport et al., out-of-sample EO yield experiments, Kenya and Somalia | *Environmental Research Letters* 2019 (per USGS/CHC listing; DOI not verified) | CATALOGUE_ONLY | Kenya/Somalia maize, EO products | Earlier same-region, same-target work |
| 4 | *Seasonal maize yield forecasting in South and East African countries using hybrid Earth observation models* | PMC11283090 (2024; authors/venue not verified) | CATALOGUE_ONLY | South and East Africa maize | Further overlap; to be read in full |
| 5 | Geyman, Ferris, Sahajpal, Anderson, Lee, Hausmann, *GROW-Africa* | *Scientific Data* 2025, doi:10.1038/s41597-025-05257-5; Zenodo record 16544448 v2 | ABSTRACT | 535,844 georeferenced yield observations, 25 crops, mostly 2000–2023; government, survey and crop-cut types | Bias across data types. Earlier R06 audit (not reproduced) found no Uganda crop-cut rows |
| 6 | Taremwa et al., *Prediction of maize yield in Uganda using CNN-LSTM … multimodal climate and remote sensing dataset* | *Discover Artificial Intelligence* 6, 164 (2026) | ABSTRACT | Uganda ZARDI-zone biannual maize yield, reported 2018–2020; R² 0.783 vs CNN and RF | **Closest Uganda competitor.** About three years of zone-level targets; target provenance and temporal validation not verifiable from the abstract |
| 7 | Taremwa et al., *Climate-driven maize yield prediction across Uganda's ZARDI zones using pooled learning and uncertainty-aware modeling* | *Discover Artificial Intelligence* 6, 733 (2026) | ABSTRACT | Same ZARDI target family; 90% intervals reach about 91.7% coverage | Same target limitation; SHAP drivers are not causal |
| 8 | "Ndhokero et al." rice hybrid forecasting (named in the brief) | — | UNVERIFIED | — | Not found by search; closest hit is an unpublished Makerere undergraduate proposal on Uganda rice. Ask the investigator for the citation |

## Head-to-head implication

* Same source (HarvestStat/FEWS NET) and same question (subnational seasonal maize forecasts in Kenya
  and Somalia): Lee et al. 2022. A model that only reaches similar NSE/MAPE adds nothing new.
* Uganda ML papers (Taremwa 2026) rely on very short zone-level series. Independent reimplementation
  is impossible without their target data, so a "we beat them" claim is not admissible.
* Candidate *substantive* advance (see `DECISION_LOG.md`): a **vintage-realistic, season-blocked
  re-evaluation**. Do reported early-warning skills for Kenya/Somalia shortfall *events* survive when
  (a) predictors and previous-season baselines are restricted to what was public by the decision date
  (FSNAU/Kenya release dates, CHIRPS preliminary vs final) and (b) uncertainty is computed over
  seasons rather than unit-seasons? Falsified if vintage-restricted, season-blocked skill matches the
  unrestricted skill within season-bootstrap uncertainty. It is also falsified if ML adds no detection
  benefit over climatology/persistence at a fixed false-alarm budget.
