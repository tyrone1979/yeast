# Industrial Yeast Fed-Batch Fermentation Nutrient-Addition Dataset

This release provides cleaned, analysis-ready CSV files digitized from industrial baker’s-yeast (*Saccharomyces*) fed-batch fermentation **PDF batch logs**. The PDF sheets were completed by experienced plant operators and technicians based on on-site measurements and observations during production. Original PDF sheets are **not** redistributed with this package. The dataset supports research on nutrient (primarily sugar) feed-rate prediction, process monitoring, and machine-learning models for fed-batch fermentation control.

## Contents

| File | Description |
|------|-------------|
| `batch_metadata.csv` | One row per fermentation batch (61 batches): lot number, strain, seed information, yield, completeness flag |
| `fermentation_timeseries.csv` | Hourly process records stacked across batches (1,127 rows) |
| `evaluation_profiles.csv` | Reference alcohol and growth-modulus profiles used for batch evaluation |
| `summary_stats.json` | Machine-readable descriptive statistics used in the accompanying data paper |
| `README.md` | This file |

Paper figures are **not** part of this dataset release; they are kept with the manuscript under `paper/figures/`.

## Batch completeness

- **full_process** (10 batches, `B01`–`B10`): hourly airflow, volume, pH, alcohol, cell concentration, biomass, growth modulus, and sugar feed rate are largely available.
- **alcohol_sugar_biomass** (51 batches, `B11`–`B61`): primarily alcohol, biomass (`biomass_y30_kg`), and sugar feed rate (`sugar_feed_rate_kg_rs_h`) are recorded.

All released batches use strain ID `167`.

## Known data notes

- **B05:** `volume_m3` values are ~10× larger than peer full-process batches (flagged in metadata).
- **B04 / B09:** end-of-batch `airflow_m3_h` values > 40,000 m³/h (flagged).
- **B10 / B11:** share lot number 2616 and the same yield header; B11 is a sparse incomplete sheet.
- **Sugar feed missingness:** mostly at `time_h = 0` (feed not yet started), not random gaps.
- **Sparse biomass extremes:** some early-phase `biomass_y30_kg` values exceed 60,000 kg (flagged when present); treat cautiously.
- Rows that contain only helper fields (no process variables) were dropped during packaging.

## Column dictionary (`fermentation_timeseries.csv`)

| Column | Unit / type | Description |
|--------|-------------|-------------|
| `batch_id` | string | Batch identifier (`B01`…`B61`) |
| `lot_no` | integer | Production lot number |
| `time_h` | h | Fermentation hour |
| `airflow_m3_h` | m³/h | Aeration rate |
| `volume_m3` | m³ | Broth / fermenter working volume |
| `ph` | – | Culture pH |
| `alcohol_vv_pct` | v/v % | Ethanol concentration |
| `cell_concentration_gpl` | g/L | Cell concentration |
| `biomass_y30_kg` | kg | Yeast solids biomass expressed as Y30 |
| `growth_modulus` | – | Growth modulus (GM) |
| `sugar_feed_rate_kg_rs_h` | kg RS/h | Reducing-sugar (wort) feed rate — primary nutrient-addition target |
| `total_fermentable_sugar_kg` | kg | Cumulative / total fermentable sugar (TFS) |
| `remark` | – | Operator remark / score field from source sheet |
| `delta_alcohol` | v/v % | Alcohol deviation helper field from source |
| `delta_growth_modulus` | – | GM deviation helper field from source |
| `auto_growth_modulus` | – | Auto-computed GM helper field from source |

Empty cells denote values not recorded on the source batch sheet (not imputed).

## Recommended prediction task

Predict `sugar_feed_rate_kg_rs_h` at hour *t* (or *t+1*) from recent process states (`alcohol_vv_pct`, `biomass_y30_kg`, `ph`, `airflow_m3_h`, `growth_modulus`, etc.).

A ready-to-run example with BiLSTM / 1D-CNN leave-one-batch-out evaluation (plus alcohol-profile tracking via `evaluation_profiles.csv`) is in [`usage/`](../usage/).

## Provenance

1. Experienced operators/technicians measured fermentation variables and recorded them on industrial PDF batch sheets (source archive retained by data owners; not part of this public deposit).
2. Records were digitized into structured tables and packaged as CSV files in this folder.
3. Conversion helper: `scripts/convert_excel_to_dataset.py` (assembles already-digitized tabular extracts into the public CSV layout).
4. Values are released as recorded after tabular restructuring; no smoothing or imputation was applied.

## License / citation

This package is deposited on figshare: https://doi.org/10.6084/m9.figshare.33201579

```text
Ren C., Zhao L., Kang L., Guo Q. An industrial yeast fed-batch fermentation
dataset for nutrient feed-rate prediction. figshare (2026).
https://doi.org/10.6084/m9.figshare.33201579
```
