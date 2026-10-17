# Reproducibility

```bash
pip install -e '.[test]'                 # pandas, numpy, pytest
python -m cropshortfall.acquire          # Dryad attempt (expected 401) + GitHub sparse clone into data/raw/ (gitignored)
python -m cropshortfall.audit            # -> results/tables/{audit_checks.json, ea_*.csv, uganda_harveststat_coverage.csv}
python -m cropshortfall.labels           # -> results/tables/shortfall_label_feasibility.csv
pytest -q                                # 11 fixture/aggregate tests
```

Runtime: audit about 1.4 s, labels a few seconds, single-threaded. The raw CSV (about 25 MB) is
never committed. Verify it against the SHA256 in the manifest. CI runs only `pytest`, with no
downloads.
