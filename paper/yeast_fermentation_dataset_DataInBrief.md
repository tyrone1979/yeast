# ARTICLE INFORMATION

**Article title:**

An Industrial Yeast Fed-Batch Fermentation Dataset for Nutrient Feed-Rate Prediction

**Authors:**

[Author 1]$^{1}$, [Author 2]$^{1,*}$

**Affiliations:**

$^{1}$ [Institution, City, Country]

**Corresponding author’s email address:**

[corresponding@author.edu]

**Keywords**

Yeast fermentation; Fed-batch culture; Nutrient addition; Sugar feed rate; Industrial process data; Time-series dataset; Deep learning

**Abstract**

This data article presents an industrial baker’s-yeast fed-batch fermentation dataset curated for nutrient-addition (primarily reducing-sugar feed-rate) prediction. The release comprises 61 production batches following a Differential Brew protocol, yielding 1,128 hourly records of process variables including alcohol concentration, biomass (Y30), sugar feed rate, and—for a 10-batch full-process subset—airflow, volume, pH, cell concentration, and growth modulus. Accompanying files provide protocol hourly setpoints, evaluation profiles for alcohol and growth modulus, and recipe/materials parameters. All files are UTF-8 CSV with documented headers. The dataset supports development and benchmarking of machine-learning and deep-learning models for fed-batch nutrient dosing, process monitoring, and transfer learning across fermentation batches. Data are intended for deposition in a public repository under an open license.

# SPECIFICATIONS TABLE

| Item | Details |
|------|---------|
| Subject | Biological sciences / Bioprocess engineering |
| Specific subject area | Industrial yeast fed-batch fermentation; nutrient feed-rate time series |
| Type of data | Table: CSV process records, batch metadata, protocol setpoints, evaluation profiles |
| Data collection | Hourly fermentation records were extracted from industrial batch sheets associated with a Differential Brew protocol (Nov. 2014). Variables include aeration, volume, pH, alcohol, cell/biomass measures, growth modulus, and reducing-sugar feed rate. Protocol setpoints and evaluation profiles were digitized from the same workbook. |
| Data source location | Industrial yeast fermentation facility records compiled in the source workbook `data.xlsx` (institution to be specified by data owners before submission) |
| Data accessibility | Repository name: [figshare/Zenodo — to be completed] Data identification number: [DOI — to be completed] Direct URL to data: [https://doi.org/… — to be completed] |
| Related research article | Related patent application: *A deep learning-based method for predicting nutrient addition in yeast fed-batch fermentation* (P250382). Related research article: none / [to be completed] |

# VALUE OF THE DATA

This dataset is particularly valuable for researchers developing and benchmarking **fed-batch nutrient dosing predictors**, process soft-sensors, and deep temporal models for industrial fermentation. The following points summarize the specific contributions of this release.

**Relevance to industrial bioprocess control:** Sugar feed rate is a critical operator-adjusted actuator in yeast manufacture. Public access to paired process states and recorded feed rates enables data-driven controllers and advisory systems that aim to reduce alcohol overflow, stabilize growth modulus, and improve biomass yield.

**Scarcity of open industrial fermentation batches:** Public multi-batch industrial yeast fermentation datasets with explicit nutrient feed-rate labels remain uncommon. Most open bioprocess resources are laboratory-scale, simulated, or lack feed-actuator targets. This release provides 61 industrial batches under a documented Differential Brew protocol.

**Dual completeness tiers for flexible reuse:** Ten batches (`B01`–`B10`) include rich process covariates (airflow, volume, pH, cell concentration, growth modulus), while 51 additional batches supply alcohol–biomass–sugar trajectories for large-sample feed-rate modelling and transfer-learning studies.

**Protocol and evaluation references included:** Hourly setpoints (temperature, air, pH, sugar/N/P feeds) and alcohol/growth-modulus evaluation profiles allow users to compare actual operation against planned trajectories and to construct supervised targets or constraint-aware losses.

**Accessible CSV format:** Files use UTF-8 CSV with stable English headers, compatible with Python, MATLAB, and R without proprietary Excel parsing.

# BACKGROUND

Baker’s yeast production commonly employs aerobic fed-batch fermentation on molasses wort, in which sugar (reducing sugar, RS), nitrogen, and phosphorus feeds are adjusted over a ~16 h cycle to maximize biomass while limiting ethanol formation [1,2]. In plant practice, sugar addition is often guided by alcohol and growth-modulus trends and still requires frequent human intervention, creating variability across lots [3].

Deep learning has been increasingly applied to fermentation soft sensing and predictive control, including convolutional and recurrent architectures for multiparameter time series [4,5]. Domain-adaptation and continual-learning strategies have also been proposed to transfer models across strains or operating regimes [6]. Progress is hindered by limited release of industrial batch data that jointly expose process states and nutrient feed actuators.

The present dataset was curated from industrial Differential Brew records (protocol dated 18 November 2014) covering strain ID 167. It is designed to support nutrient feed-rate prediction methods consistent with dual temporal–spatial modelling pipelines that fuse sequential process features with protocol-informed spatial/process topology [7]. The release preserves recorded values after tabular restructuring and does not apply smoothing or imputation.

# DATA DESCRIPTION

The dataset package consists of five primary CSV files plus documentation and overview figures, summarized in Table 1.

**Table 1. File inventory for the dataset.**

| File name | Format | Description |
|-----------|--------|-------------|
| `batch_metadata.csv` | CSV | One row per batch (n = 61): lot number, strain, recipe, seed information, yield, completeness flag |
| `fermentation_timeseries.csv` | CSV | Stacked hourly records (n = 1,128) across all batches |
| `protocol_hourly_setpoints.csv` | CSV | Planned hourly setpoints for temperature, air, pH, biomass trajectory, and sugar/N/P feeds |
| `evaluation_profiles.csv` | CSV | Reference alcohol and growth-modulus profiles (0–17 h) |
| `recipe_parameters.csv` | CSV | Protocol-level materials, fermenter geometry, and process assumptions |
| `README.md` | Markdown | Column definitions, completeness notes, recommended prediction task |
| `figures/` | SVG | Overview plots corresponding to Figs. 1–4 |

**Table 2. Column definitions for `fermentation_timeseries.csv`.**

| Column name | Data type | Description | Example |
|-------------|-----------|-------------|---------|
| `batch_id` | String | Batch identifier | B01 |
| `lot_no` | Integer | Production lot number | 2592 |
| `time_h` | Integer/Float | Fermentation hour | 4 |
| `airflow_m3_h` | Float | Aeration rate (m³/h) | 14065 |
| `volume_m3` | Float | Working volume (m³) | 96.0 |
| `ph` | Float | Culture pH | 4.38 |
| `alcohol_vv_pct` | Float | Ethanol (v/v %) | 0.130 |
| `cell_concentration_gpl` | Float | Cell concentration (g/L) | 128 |
| `biomass_y30_kg` | Float | Biomass as Y30 (kg) | 12288 |
| `growth_modulus` | Float | Growth modulus (GM) | 1.36 |
| `sugar_feed_rate_kg_rs_h` | Float | Reducing-sugar feed rate (kg RS/h); primary nutrient-addition label | 939 |
| `total_fermentable_sugar_kg` | Float | Total fermentable sugar / TFS (kg) | 2905 |
| `remark` | String/Float | Operator remark field from source | 2 |
| `delta_alcohol` | Float | Alcohol deviation helper field | −0.05 |
| `delta_growth_modulus` | Float | GM deviation helper field | 0.033 |
| `auto_growth_modulus` | Float | Auto GM helper field | 1.363 |

**Table 3. Batch completeness summary.**

| Completeness class | Batches | n | Typical available variables |
|--------------------|---------|---|-----------------------------|
| `full_process` | B01–B10 | 10 | Airflow, volume, pH, alcohol, cell concentration, biomass, GM, sugar feed, TFS |
| `alcohol_sugar_biomass` | B11–B61 | 51 | Alcohol, biomass, sugar feed (other covariates mostly missing) |

All batches share `strain_id = 167` and `recipe = Diff`. Lot numbers range from 2212 to 2682. Records per batch range from 17 to 21 hourly points.

# EXPERIMENTAL DESIGN, MATERIALS AND METHODS

## Fermentation protocol and equipment context

Batches follow the ZHENAO Trial Differential Brew Protocol (modified 18 November 2014). The protocol targets protein 57–58% and P₂O₅ 2.8–3.0%, with an assumed yield of 1.55 kg Y30 per kg RS. Wort is specified as beet molasses based (100% beet / 0% cane) at 0.35 kg RS/kg wort and density 1.24 kg/L. Nominal fermenter geometry in the protocol sheet is diameter 4 m, height 12 m, and nominal working volume ≈151.3 m³. Planned fermentation time is 16 h plus 40 min maturation. Major nutrient charges include 15,000 kg RS, 800 kg ammonia (100%), 420 kg H₃PO₄ (100%), and micronutrient / vitamin additions (MgSO₄, ZnSO₄, CuSO₄, B1/B5/B6, biotin) as listed in `recipe_parameters.csv`.

## Measured variables and nutrient-addition target

Industrial sheets record hourly values of aeration, volume, pH, alcohol, cell concentration, biomass (Y30), growth modulus (GM), reducing-sugar feed rate (RS kg/h), and total fermentable sugar. Protocol notes emphasize that sugar addition is the key human-adjusted input and is intended to be assisted by algorithmic recommendations—motivating the prediction use case. Nitrogen and phosphorus feeds are proportionally linked to sugar in the protocol setpoints.

**Fig. 1.** Sugar feed trajectories for full-process batches compared with protocol setpoints (`figures/fig1_sugar_feed_trajectories.svg`).

**Fig. 2.** Representative alcohol and biomass dynamics for batch B01 against the alcohol evaluation profile (`figures/fig2_alcohol_biomass_b01.svg`).

## Data acquisition and curation workflow

1. Source workbook sheets `01`–`61` were parsed for batch headers (lot, strain, seed, yield) and hourly tables.
2. Sheet `DIFF` was converted into structured recipe parameters and hourly setpoint rows.
3. Sheet `评价标准` provided alcohol and GM evaluation profiles.
4. English, machine-readable headers replaced mixed Chinese/English Excel labels.
5. No imputation, smoothing, or unit renormalization was applied. Empty cells remain empty.
6. Batch `B05` retains volume values that are approximately an order of magnitude larger than peer batches; this is flagged in `batch_metadata.csv` notes and treated as a raw recording anomaly.

**Table 4. Data flow from source workbook to released CSVs.**

| Stage | Component | Function | Output |
|-------|-----------|----------|--------|
| 1 | Industrial Excel sheets | Store batch headers and hourly logs | `data.xlsx` |
| 2 | Conversion script | Normalize identifiers, stack timeseries, extract protocol tables | CSV files |
| 3 | Metadata tagging | Completeness flags and anomaly notes | `batch_metadata.csv` |
| 4 | Summary statistics | Compute descriptive stats for documentation | `summary_stats.json` |

## Descriptive statistics

**Table 5. Descriptive statistics for full-process batches (B01–B10).**

| Variable | n | Mean | SD | Min | Max |
|----------|---|------|----|-----|-----|
| Airflow (m³/h) | 179 | 16459.2 | 5748.3 | 4961 | 49992 |
| Volume (m³) | 179 | 219.9 | 319.5 | 87.7 | 1470 |
| pH | 179 | 5.77 | 1.07 | 3.91 | 7.75 |
| Alcohol (v/v %) | 179 | 0.103 | 0.071 | 0.002 | 0.393 |
| Cell concentration (g/L) | 179 | 206.3 | 80.1 | 57 | 300 |
| Biomass Y30 (kg) | 179 | 25346.4 | 13016.4 | 5056 | 44253 |
| Growth modulus | 169 | 1.135 | 0.097 | 1.00 | 1.56 |
| Sugar feed (kg RS/h) | 169 | 1342.7 | 518.8 | 127 | 2194 |

**Table 6. Descriptive statistics for key variables across all 61 batches.**

| Variable | n | Mean | SD | Min | Max |
|----------|---|------|----|-----|-----|
| Alcohol (v/v %) | 1127 | 0.104 | 0.061 | 0.001 | 0.393 |
| Biomass Y30 (kg) | 1127 | 25562.1 | 13250.1 | 1417 | 71101 |
| Sugar feed (kg RS/h) | 1066 | 1300.5 | 478.2 | 127 | 2194 |

Note: Volume maxima are dominated by batch B05; users analysing volume should either exclude B05 or apply batch-wise robust scaling.

**Fig. 3.** Mean pH and airflow versus fermentation hour for full-process batches (`figures/fig3_mean_ph_airflow.svg`).

**Fig. 4.** Histogram of recorded sugar feed rates across all batches (`figures/fig4_sugar_feed_hist.svg`).

## Data quality validation

Prior to release, the following checks were performed:

- **Completeness check:** Counted non-missing values per variable and tagged batches as `full_process` or `alcohol_sugar_biomass`.
- **Range screening:** Verified alcohol ≥ 0, pH roughly 3–8, growth modulus near 1–1.6, and sugar feed rates within protocol-compatible magnitudes.
- **Batch integrity:** Confirmed `time_h` is unique within each `batch_id` and monotonically non-decreasing.
- **Protocol alignment:** Confirmed setpoint hours 0–16 exist in `protocol_hourly_setpoints.csv`.

**Table 7. Data quality validation outcomes.**

| Check | Outcome |
|-------|---------|
| Batches parsed | 61/61 |
| Timeseries rows | 1,128 |
| Full-process batches | 10 |
| Missing sugar feed rate | 62/1,128 (5.5%) |
| Missing alcohol | 1/1,128 (0.1%) |
| Flagged volume anomaly | B05 |
| Imputation applied | None |

## Example workflow for data loading

```python
import pandas as pd
ts = pd.read_csv("fermentation_timeseries.csv")
meta = pd.read_csv("batch_metadata.csv")
full = meta.loc[meta["data_completeness"]=="full_process", "batch_id"]
df = ts[ts["batch_id"].isin(full)].copy()
# Example supervised target: next-hour sugar feed
df = df.sort_values(["batch_id", "time_h"])
df["sugar_feed_next"] = df.groupby("batch_id")["sugar_feed_rate_kg_rs_h"].shift(-1)
```

# Example Data Reuse and Quality Assessment

**Feed-rate prediction baseline.** Using full-process batches, a simple lag model that predicts current sugar feed rate from the previous hour’s alcohol, biomass, pH, and airflow can be trained with ordinary least squares or gradient boosting. Users should evaluate with leave-one-batch-out validation to reflect industrial lot shift.

**Profile tracking.** Differences between measured alcohol and `evaluation_profiles.csv` provide a batch-quality indicator; batches with persistently elevated alcohol relative to the profile are candidates for feed-rate oversupply studies.

**Protocol residual analysis.** Subtracting `protocol_hourly_setpoints.csv` sugar feed from measured `sugar_feed_rate_kg_rs_h` yields operator adjustment residuals—useful labels for imitation learning or human-in-the-loop control research.

# LIMITATIONS

- **Single strain and recipe:** All batches are strain 167 under the Diff protocol; cross-strain generalization cannot be assessed from this release alone.
- **Uneven covariate coverage:** Only 10 batches include rich process covariates; 51 batches are sparse.
- **Hourly resolution:** Records are hourly rather than high-frequency (≥1 Hz) IoT streams described in related method patents.
- **Temperature field not released:** Protocol temperature setpoints exist, but distributed temperature-field measurements are not present in the batch sheets.
- **Possible recording anomaly:** Volume values in B05 appear inflated relative to peers and should be handled cautiously.
- **Confidential plant metadata:** Exact plant identity, calendar dates, and operator identities are not included.
- **Repository DOI pending:** Public DOI/URL placeholders must be completed upon deposition.

# ETHICS STATEMENT

The authors have read and follow the ethical requirements for publication in *Data in Brief*. The current work does not involve human subjects, animal experiments, or data collected from social media platforms. Industrial process values are released without personally identifiable information.

# CRediT AUTHOR STATEMENT

[Author 1]: Conceptualization, Data curation, Investigation, Methodology, Writing – original draft. [Author 2]: Supervision, Writing – review & editing.

# ACKNOWLEDGEMENTS

[Acknowledgements and funding statement to be completed by the authors.]

# DATA AVAILABILITY

The datasets will be deposited on [figshare/Zenodo] (DOI: [to be completed]). Repository contents include: (i) CSV files listed in Table 1; (ii) `README.md` with column definitions; (iii) conversion and figure scripts under `scripts/`; and (iv) overview figures. Source conversion script: `scripts/convert_excel_to_dataset.py`.

# DECLARATION OF COMPETING INTERESTS

The authors declare that they have no known competing financial interests or personal relationships that could have appeared to influence the work reported in this paper.

# REFERENCES

[1] G.M. Walker, P.M. Walker, Yeast fermentation: physiology and biotechnology, in: Comprehensive Biotechnology, Elsevier, 2011.

[2] B. Sonnleitner, O. Käppeli, Growth of *Saccharomyces cerevisiae* is controlled by its limited respiratory capacity: formulation and verification of a hypothesis, Biotechnol. Bioeng. 28 (1986) 927–937. https://doi.org/10.1002/bit.260280620.

[3] M. Rizzi, M. Baltes, U. Theobald, M. Reuss, In vivo analysis of metabolic dynamics in *Saccharomyces cerevisiae*: II. Mathematical model, Biotechnol. Bioeng. 55 (1997) 592–608.

[4] P. Kadlec, B. Gabrys, S. Strandt, Data-driven soft sensors in the process industry, Comput. Chem. Eng. 33 (2009) 795–814. https://doi.org/10.1016/j.compchemeng.2008.12.012.

[5] Z. Ge, Review on data-driven modeling and monitoring for plant-wide industrial processes, Chemometrics and Intelligent Laboratory Systems 171 (2017) 16–25. https://doi.org/10.1016/j.chemolab.2017.09.021.

[6] S.J. Pan, Q. Yang, A survey on transfer learning, IEEE Trans. Knowl. Data Eng. 22 (2010) 1345–1359. https://doi.org/10.1109/TKDE.2009.35.

[7] Patent application P250382, A deep learning-based method for predicting nutrient addition in yeast fed-batch fermentation.
