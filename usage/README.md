# Usage: sugar feed-rate prediction

This example trains a simple sequence model on the figshare dataset to predict nutrient addition (`sugar_feed_rate_kg_rs_h`).

**Dataset:** https://doi.org/10.6084/m9.figshare.33201579

On first run, `predict_sugar_feed.py` downloads the required CSV files into `dataset/` (or `--data-dir`).

## Scope (which files are used)

| Dataset file | Role in this demo |
|--------------|-------------------|
| `batch_metadata.csv` | Select `full_process` batches |
| `fermentation_timeseries.csv` | Features + sugar-feed labels |
| `evaluation_profiles.csv` | Alcohol trajectory reference (MAE vs measured) |
| `summary_stats.json` | Not used (paper statistics only) |

The demo trains on the **full_process subset** (default excludes `B05`).

## Task

- **Input:** sliding window of recent process variables  
  `airflow_m3_h`, `volume_m3`, `ph`, `alcohol_vv_pct`, `cell_concentration_gpl`, `biomass_y30_kg`, `growth_modulus`
- **Output:** current-hour sugar feed rate (`kg RS/h`)
- **Validation:** leave-one-batch-out

## Run

```bash
pip install -r requirements.txt

python usage/predict_sugar_feed.py --model bilstm
python usage/predict_sugar_feed.py --model cnn
python usage/predict_sugar_feed.py --profile-only

# use pre-downloaded figshare files
python usage/predict_sugar_feed.py --data-dir /path/to/csvs --no-download
```

Metrics: `usage/results/lobo_metrics.json`  
Profile MAE: `usage/results/alcohol_profile_mae.json`

## Example result (BiLSTM, exclude B05)

Leave-one-batch-out on 9 full-process batches (`seed=42`, `window=5`):

| Metric | Pooled | Fold-mean |
|--------|--------|-----------|
| MAE (kg RS/h) | 102.5 | 102.6 |
| RMSE | 145.4 | 140.2 |
| MAPE (%) | 11.6 | 11.6 |
| R² | 0.872 | 0.873 |

## Notes

- Window length defaults to 5 hours.
- Features are min–max scaled to `[-1, 1]` using training folds only.
- Batch `B05` volume values are unusually large; excluded by default.
