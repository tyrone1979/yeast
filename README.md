# Yeast Fed-Batch Fermentation Nutrient-Addition Dataset

Industrial baker’s-yeast fed-batch fermentation records for **nutrient (sugar) feed-rate prediction**, with a *Data in Brief* manuscript draft and a simple deep-learning usage example.

Repository: https://gitee.com/sacourse/yeast.git

## Overview

| Item | Description |
|------|-------------|
| Source | Expert-completed industrial PDF batch logs (digitized; PDFs not redistributed) |
| Digitized release | 61 batches, 1,127 hourly records (CSV) |
| Prediction target | `sugar_feed_rate_kg_rs_h` (kg reducing sugar / h) |
| Usage demo | BiLSTM / 1D-CNN leave-one-batch-out (`usage/`) |

Primary scientific provenance is **on-plant measurement and recording by experienced operators/technicians** on PDF batch sheets. The released CSVs are digitized tables for computational reuse (no imputation or smoothing).

## Repository layout

```text
.
├── usage/                           # Baseline prediction example
│   ├── predict_sugar_feed.py
│   ├── README.md
│   └── results/
├── scripts/                         # Figure generation
│   ├── make_figures_png.py
│   └── make_figures_svg.py
├── requirements.txt
└── README.md                        # This file
```

## Quick start

```bash
# clone
git clone https://gitee.com/sacourse/yeast.git
cd yeast

# install (for usage example / figure scripts)
pip install -r requirements.txt

# run sugar feed-rate prediction demo (BiLSTM, leave-one-batch-out)
python usage/predict_sugar_feed.py --model bilstm

# optional: 1D-CNN
python usage/predict_sugar_feed.py --model cnn

# alcohol vs evaluation profile (uses evaluation_profiles.csv)
python usage/predict_sugar_feed.py --profile-only
```

Typical BiLSTM result (excluding anomalous-volume batch `B05`): pooled **MAE ≈ 102.5 kg RS/h**, **MAPE ≈ 11.6%**, **R² ≈ 0.872**. See `usage/results/lobo_metrics.json`.

## Dataset (short)

- **61** production batches (strain ID `167`)
- **10** `full_process` batches with rich covariates (airflow, volume, pH, alcohol, cell concentration, biomass, growth modulus, sugar feed, …)
- **51** sparse batches mainly with alcohol / biomass / sugar feed
- Original PDF logs are the provenance source but are **not** included in the public package

### Recommended ML task

Predict current- or next-hour `sugar_feed_rate_kg_rs_h` from a short window of process variables within each `batch_id`. Prefer leave-one-batch-out validation. The usage demo trains on the **full_process subset** (default excludes `B05`); sparse batches and evaluation profiles support profile-tracking analyses.

## Scripts

| Script | Role |
|--------|------|
| `scripts/make_figures_png.py` | Publication PNG figures |
| `scripts/make_figures_svg.py` | Optional SVG figures |

```bash
python scripts/make_figures_png.py
```

## Authors

Changning Ren, Lei Zhao, Ling Kang, Quan Guo\*  

\*Corresponding author: guoquan@neusoft.edu.cn  
Dalian Neusoft University of Information, Dalian, China

## Citation

```text
Ren C., Zhao L., Kang L., Guo Q. An industrial yeast fed-batch fermentation
dataset for nutrient feed-rate prediction. figshare (2026).
https://doi.org/10.6084/m9.figshare.33201579
```

Code companion: https://gitee.com/sacourse/yeast

## License

Follow the license stated on the figshare deposit (https://doi.org/10.6084/m9.figshare.33201579).
