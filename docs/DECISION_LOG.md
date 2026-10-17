# Decision log

## 2026-10-17 — phase-1 checkpoint

1. **Uganda: HOLD_DATA.** HarvestStat v1.2 contains only the 2008/09 census year for Uganda. GROW
   (prior audit) has no Uganda crop-cut rows. No modern repeated district×season series is public.
   The only remaining Uganda routes are UBOS AAS and UNPS microdata (registration by the
   investigator; self-reported production; would need a survey-weighted district/season estimand).
2. **No ML in phase 1.** No target has an established public-by date, and the obvious KE/SO maize
   forecast duplicates Lee et al. 2022.
3. **Strongest valid next step (REDESIGN, CONDITIONAL):** vintage-realistic early-warning evaluation
   for Somalia Gu/Deyr (about 20 seasons, recent to 2026) and Kenya Long/Short rains:
   * (a) Collect FSNAU and Kenyan release dates per season (public reports) to define what was knowable
     at each decision date.
   * (b) Freeze decision dates: Gu at end of May, Deyr at end of November. Use CHIRPS preliminary
     dekads only up to each date.
   * (c) Freeze the event definition on production, not only yield, with an agronomically justified
     threshold. The 0.8 × trailing-median yield ratio gives ~43% prevalence in Somalia, which is too
     common to call a loss.
   * (d) Baselines: climatology, last publicly available season, and logistic on CHIRPS anomalies.
     Then RF and one GBDT.
   * (e) Validation: leave-season-year-out, plus leave-region-out and leave-crop-out. Season-block
     bootstrap uncertainty. Detection at a fixed false-alarm budget.
   * (f) Reconcile the Dryad and GitHub v1.2 CSV hashes first.
4. Ethiopia Meher is excluded until its ~1% shortfall prevalence is explained from CSA source data.
