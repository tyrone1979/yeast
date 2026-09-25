# Yeast Fed-Batch Fermentation Nutrient-Addition Dataset

Industrial baker’s-yeast fed-batch fermentation records for **nutrient (sugar) feed-rate prediction**, with a simple deep-learning usage example.

## Overview

| Item | Description |
|------|-------------|
| Dataset | [figshare](https://doi.org/10.6084/m9.figshare.33201579) — 59 batches, 1,090 hourly CSV records |
| Prediction target | `sugar_feed_rate_kg_rs_h` (kg reducing sugar / h) |
| This repo | Usage demo (BiLSTM / 1D-CNN leave-one-batch-out) |

Primary scientific provenance is **on-plant measurement and recording by experienced operators/technicians** on PDF batch sheets. The released CSVs on figshare are digitized tables for computational reuse (no imputation or smoothing).

## Repository layout

```text
.
├── usage/                           # Baseline prediction example
│   ├── predict_sugar_feed.py
│   ├── README.md
│   └── results/
├── requirements.txt
└── README.md                        # This file
```

## Quick start

```bash
git clone https://github.com/tyrone1979/yeast.git
cd yeast

pip install -r requirements.txt

# downloads CSVs from figshare into ./dataset/ on first run
python usage/predict_sugar_feed.py --model bilstm

# optional: 1D-CNN
python usage/predict_sugar_feed.py --model cnn

# alcohol vs evaluation profile (no training)
python usage/predict_sugar_feed.py --profile-only
```

Typical BiLSTM result (all 10 full-process batches): pooled **MAE ≈ 99.1 kg RS/h**, **MAPE ≈ 10.5%**, **R² ≈ 0.901**. The 1D-CNN variant gives MAE ≈ 102.7, MAPE ≈ 11.1%, R² ≈ 0.893. See `usage/results/lobo_metrics.json` and `usage/results/lobo_metrics_cnn.json`.

## Dataset

Download the CSV package from figshare (DOI **10.6084/m9.figshare.33201579**):

https://doi.org/10.6084/m9.figshare.33201579

Contents include `batch_metadata.csv`, `fermentation_timeseries.csv`, `evaluation_profiles.csv`, `summary_stats.json`, and `README.md` (column dictionary).

- **59** production batches (strain ID `167`)
- **10** `full_process` batches with rich covariates
- **49** sparse batches mainly with alcohol / biomass / sugar feed

The usage script auto-downloads required CSVs into `dataset/` if that folder is empty. To use a custom path:

```bash
python usage/predict_sugar_feed.py --data-dir /path/to/figshare_files
```

### Recommended ML task

Predict current- or next-hour `sugar_feed_rate_kg_rs_h` from a short window of process variables within each `batch_id`. Prefer leave-one-batch-out validation.

## Authors

Changning Ren, Lei Zhao, Yao Wu, Ling Kang, Quan Guo\*  

\*Corresponding author: guoquan@neusoft.edu.cn  
Dalian Neusoft University of Information, Dalian, China

## Citation

```text
Ren C., Zhao L., Wu Y., Kang L., Guo Q. An industrial yeast fed-batch fermentation
dataset for nutrient feed-rate prediction. figshare (2026).
https://doi.org/10.6084/m9.figshare.33201579
```

Code companion: https://github.com/tyrone1979/yeast

## License

Follow the license stated on the figshare deposit (https://doi.org/10.6084/m9.figshare.33201579).
