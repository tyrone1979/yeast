# Usage: sugar feed-rate prediction

This example shows that the released dataset can train a simple sequence model to predict nutrient addition (`sugar_feed_rate_kg_rs_h`), and that `evaluation_profiles.csv` can be used for alcohol-profile tracking.

## Scope (which files are used)

| Dataset file | Role in this demo |
|--------------|-------------------|
| `batch_metadata.csv` | Select `full_process` batches |
| `fermentation_timeseries.csv` | Features + sugar-feed labels |
| `evaluation_profiles.csv` | Alcohol trajectory reference (MAE vs measured) |
| `summary_stats.json` | Not used (paper statistics only) |

The demo trains on the **full_process subset** (all 10 batches, `B01`–`B10`). The 49 sparse batches are not used for model training; they remain available for larger-sample or transfer studies.

## Task

- **Input:** sliding window of recent process variables  
  `airflow_m3_h`, `volume_m3`, `ph`, `alcohol_vv_pct`, `cell_concentration_gpl`, `biomass_y30_kg`, `growth_modulus`
- **Output:** current-hour sugar feed rate (`kg RS/h`)
- **Data:** full-process batches `B01`–`B10` (all 10 batches; the B05 volume anomaly was corrected in the release)
- **Validation:** leave-one-batch-out

## Models

| `--model` | Description |
|-----------|-------------|
| `bilstm` (default) | Bidirectional LSTM + small MLP head |
| `cnn` | 1D-CNN over the time window |

## Run

```bash
# from repository root
pip install -r requirements.txt

# first run auto-downloads the required CSVs from the figshare deposit into ./dataset/
python usage/predict_sugar_feed.py --model bilstm
python usage/predict_sugar_feed.py --model cnn

# alcohol vs evaluation profile only (no training)
python usage/predict_sugar_feed.py --profile-only

# include all full-process batches (including B05)
python usage/predict_sugar_feed.py --exclude-batches ""

# use a local directory of pre-downloaded figshare files instead
python usage/predict_sugar_feed.py --data-dir /path/to/csvs
```

Metrics are printed per held-out batch and saved to `usage/results/lobo_metrics.json` (BiLSTM; use `--model cnn --out usage/results/lobo_metrics_cnn.json` for the 1D-CNN variant). Profile MAE is saved to `usage/results/alcohol_profile_mae.json`.

## Example result (BiLSTM, all 10 full-process batches)

Leave-one-batch-out on 10 full-process batches (`seed=42`, `window=5`):

| Metric | Pooled | Fold-mean |
|--------|--------|-----------|
| MAE (kg RS/h) | 99.1 | 99.1 |
| RMSE | 130.1 | 125.2 |
| MAPE (%) | 10.5 | 10.4 |
| R² | 0.901 | 0.903 |

The 1D-CNN variant gives pooled MAE ≈ 102.7 kg RS/h, MAPE ≈ 11.1%, R² ≈ 0.893 (see `usage/results/lobo_metrics_cnn.json`).

This supports reuse of the dataset for nutrient feed-rate prediction. Re-run to regenerate `usage/results/lobo_metrics.json`.

## Notes

- Window length defaults to 5 hours (hourly industrial logs are short; ~17–18 points/batch).
- Features are min–max scaled to `[-1, 1]` using training folds only.
- The end-of-batch aeration readings of B04/B09 and the B05 volume values were corrected in the release (documented in `batch_metadata.csv`); no batches are excluded by default.
