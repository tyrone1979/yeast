# Industrial Yeast Fed-Batch Fermentation Nutrient-Addition Dataset

This release provides cleaned, analysis-ready CSV files derived from industrial baker’s-yeast (*Saccharomyces*) fed-batch fermentation records originally stored in a multi-sheet Excel workbook. The dataset is intended to support research on nutrient (primarily sugar) feed-rate prediction, process monitoring, and machine-learning / deep-learning models for fed-batch fermentation control.

## Contents

| File | Description |
|------|-------------|
| `batch_metadata.csv` | One row per fermentation batch (61 batches): lot number, strain, recipe, seed information, yield, completeness flag |
| `fermentation_timeseries.csv` | Hourly process records stacked across batches (1,128 rows) |
| `protocol_hourly_setpoints.csv` | Planned hourly setpoints from the Differential Brew protocol (temperature, air, pH, sugar/N/P feeds) |
| `evaluation_profiles.csv` | Reference alcohol and growth-modulus profiles used for batch evaluation |
| `recipe_parameters.csv` | Protocol-level recipe, materials, and fermenter parameters |
| `summary_stats.json` | Machine-readable descriptive statistics used in the accompanying data paper |
| `figures/` | Overview plots (SVG) |

## Batch completeness

- **full_process** (10 batches, `B01`–`B10`): hourly airflow, volume, pH, alcohol, cell concentration, biomass, growth modulus, and sugar feed rate are largely available.
- **alcohol_sugar_biomass** (51 batches, `B11`–`B61`): primarily alcohol, biomass (`biomass_y30_kg`), and sugar feed rate (`sugar_feed_rate_kg_rs_h`) are recorded.

All batches use strain ID `167` and recipe code `Diff` (Differential Brew protocol, Nov. 2014).

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

Empty cells denote values not recorded in the source workbook (not imputed).

## Recommended prediction task

Predict `sugar_feed_rate_kg_rs_h` at hour *t* (or *t+1*) from recent process states (`alcohol_vv_pct`, `biomass_y30_kg`, `ph`, `airflow_m3_h`, `growth_modulus`, etc.), optionally conditioned on `protocol_hourly_setpoints.csv`.

A ready-to-run example with BiLSTM / 1D-CNN leave-one-batch-out evaluation is in [`usage/`](../usage/).

## Provenance

- Source workbook: `data/data.xlsx` (sheets: `DIFF`, `评价标准`, `01`…`61`).
- Conversion script: `scripts/convert_excel_to_dataset.py`.
- Values are released as recorded after tabular restructuring; no smoothing or imputation was applied.

## License / citation

Deposit the `dataset/` folder in a public repository (e.g., figshare / Zenodo) and replace the placeholder DOI in the accompanying Data in Brief manuscript before submission.
