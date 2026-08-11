# ARTICLE INFORMATION

**Article title:**

An Industrial Yeast Fed-Batch Fermentation Dataset for Nutrient Feed-Rate Prediction

**Authors:**

Changning Ren¹, Lei Zhao¹, Ling Kang¹, Quan Guo¹,*

**Affiliations:**

¹ Dalian Neusoft University of Information, Dalian, China

**Corresponding author’s email address:**

guoquan@neusoft.edu.cn

**Keywords**

Yeast fermentation; Fed-batch culture; Nutrient addition; Sugar feed rate; Industrial process data; Time-series dataset; Expert process records

**Abstract**

This data article presents an industrial baker’s-yeast fed-batch fermentation dataset curated for nutrient-addition (primarily reducing-sugar feed-rate) prediction. The primary source materials are batch PDF logs completed by experienced plant operators and technicians during production, based on on-site process measurements and observations. These expert records were digitized into analysis-ready tables, yielding 61 production batches and 1,127 hourly records of process variables including alcohol concentration, biomass (Y30), sugar feed rate, and—for a 10-batch full-process subset—airflow, volume, pH, cell concentration, and growth modulus. All released files are UTF-8 CSV with documented headers. Original PDF sheets are retained by the data owners and are not redistributed with the public package. The dataset supports development and benchmarking of machine-learning and deep-learning models for fed-batch nutrient dosing, process monitoring, and transfer learning across fermentation batches. Data are intended for deposition in a public repository under an open license.

# SPECIFICATIONS TABLE

| Item | Details |
|------|---------|
| Subject | Biological sciences / Bioprocess engineering |
| Specific subject area | Industrial yeast fed-batch fermentation; nutrient feed-rate time series |
| Type of data | Table: CSV process records and batch metadata digitized from expert-completed industrial PDF batch logs |
| Data collection | Hourly fermentation variables were measured and recorded by experienced operators/technicians on industrial batch PDF sheets during fed-batch yeast production. Recorded quantities include aeration, volume, pH, alcohol, cell/biomass measures, growth modulus, and reducing-sugar feed rate. The PDF logs were subsequently digitized into structured CSV tables for public release. No smoothing or imputation was applied. |
| Data source location | Industrial yeast fermentation facility production records (institution to be specified by data owners before submission). Original PDF batch logs remain with the data owners and are not part of the public deposit. |
| Data accessibility | Repository name: [figshare/Zenodo — to be completed] Data identification number: [DOI — to be completed] Direct URL to data: [https://doi.org/… — to be completed] |
| Related research article | none / [to be completed] |

# VALUE OF THE DATA

This dataset is particularly valuable for researchers developing and benchmarking **fed-batch nutrient dosing predictors**, process soft-sensors, and deep temporal models for industrial fermentation. The following points summarize the specific contributions of this release.

**Expert-recorded industrial ground truth:** Values originate from PDF batch logs filled by experienced operators based on production measurements, rather than from laboratory simulations. This provides realistic paired process states and nutrient feed decisions for data-driven control research.

**Relevance to industrial bioprocess control:** Sugar feed rate is a critical operator-adjusted actuator in yeast manufacture. Public access to paired process states and recorded feed rates enables advisory systems that aim to reduce alcohol overflow, stabilize growth modulus, and improve biomass yield.

**Scarcity of open industrial fermentation batches:** Public multi-batch industrial yeast fermentation datasets with explicit nutrient feed-rate labels remain uncommon. Most open bioprocess resources are laboratory-scale, simulated, or lack feed-actuator targets. This release provides 61 digitized industrial batches.

**Dual completeness tiers for flexible reuse:** Ten batches (`B01`–`B10`) include rich process covariates (airflow, volume, pH, cell concentration, growth modulus), while 51 additional batches supply alcohol–biomass–sugar trajectories for large-sample feed-rate modelling and transfer-learning studies.

**Accessible CSV format:** Files use UTF-8 CSV with stable English headers, compatible with Python, MATLAB, and R. A simple BiLSTM/CNN usage example is provided to demonstrate predictive reuse.

# BACKGROUND

Baker’s yeast production commonly employs aerobic fed-batch fermentation on molasses wort, in which sugar (reducing sugar, RS), nitrogen, and phosphorus feeds are adjusted over a multi-hour cycle to maximize biomass while limiting ethanol formation [1,2]. In plant practice, sugar addition is often guided by alcohol and growth-modulus trends and still requires frequent human intervention, creating variability across lots [3].

Deep learning has been increasingly applied to fermentation soft sensing and predictive control, including convolutional and recurrent architectures for multiparameter time series [4,5]. Domain-adaptation and continual-learning strategies have also been proposed to transfer models across strains or operating regimes [6]. Progress is hindered by limited release of industrial batch data that jointly expose process states and nutrient feed actuators.

The present dataset was curated from industrial production batch logs. Experienced operators and technicians measured key fermentation variables during fed-batch runs and recorded them on PDF batch sheets; these expert records were then digitized into machine-readable CSV files. The release preserves recorded values after tabular restructuring and does not apply smoothing or imputation. It is intended to support nutrient feed-rate prediction and related process-monitoring studies [7].

# DATA DESCRIPTION

The dataset package consists of primary CSV files and documentation. Table 1 summarizes the file inventory. Overview plots used in this article (Figs. 1–4) are manuscript materials and are not included in the public dataset deposit.

**Table 1. File inventory for the dataset.**

| File name | Format | Description |
|-----------|--------|-------------|
| `batch_metadata.csv` | CSV | One row per batch (n = 61): lot number, strain, seed information, yield, completeness flag |
| `fermentation_timeseries.csv` | CSV | Stacked hourly records (n = 1,127) across all batches |
| `evaluation_profiles.csv` | CSV | Reference alcohol and growth-modulus profiles used for batch evaluation |
| `summary_stats.json` | JSON | Machine-readable descriptive statistics and quality flags |
| `README.md` | Markdown | Column definitions, completeness notes, recommended prediction task |

Table 2 provides the column definitions for the primary timeseries file `fermentation_timeseries.csv`, including units and representative example values.

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

As shown in Table 3, the release contains two completeness tiers: ten full-process batches with rich covariates and 51 additional batches dominated by alcohol–biomass–sugar trajectories. All released batches share `strain_id = 167`. Lot numbers range from 2212 to 2682. Records per batch range from 17 to 21 hourly points.

**Table 3. Batch completeness summary.**

| Completeness class | Batches | n | Typical available variables |
|--------------------|---------|---|-----------------------------|
| `full_process` | B01–B10 | 10 | Airflow, volume, pH, alcohol, cell concentration, biomass, GM, sugar feed, TFS |
| `alcohol_sugar_biomass` | B11–B61 | 51 | Alcohol, biomass, sugar feed (other covariates mostly missing) |

# EXPERIMENTAL DESIGN, MATERIALS AND METHODS

## Source records and expert data generation

The primary source materials are industrial fed-batch yeast fermentation **PDF batch logs**. During production, experienced operators and technicians performed process measurements (e.g., airflow, volume, pH, alcohol, cell/biomass-related quantities) and recorded the observed values, together with the sugar feed adjustments made during the run, onto standardized batch sheets archived as PDF files. The original PDFs remain with the data owners for provenance and are **not** redistributed in the public CSV package.

These expert-completed PDF records constitute the authoritative origin of the numerical values in this release. Digitization into tabular form was performed subsequently to enable computational reuse; the released CSVs are intended to preserve the recorded measurements and feed decisions without algorithmic alteration.

## Measured variables and nutrient-addition target

Each batch sheet records hourly values of aeration, volume, pH, alcohol, cell concentration, biomass (Y30), growth modulus (GM), reducing-sugar feed rate (RS kg/h), and total fermentable sugar when available (see Table 2 for field definitions). Sugar feed rate is the primary nutrient-addition actuator of interest for predictive modelling: it reflects operator decisions made in response to evolving fermentation states and is therefore a natural supervised-learning target. Fig. 1 shows the median sugar feed trajectory of the full-process batches (excluding anomalous-volume batch B05) with an interquartile-range (IQR) band. Fig. 2 presents side-by-side alcohol and biomass panels for representative batch B01: measured alcohol as points against the evaluation profile, and biomass as a growth curve.

**Fig. 1.** Median sugar feed rate with IQR band across full-process batches (excluding B05).

**Fig. 2.** Alcohol (left; points = measured, line = evaluation profile) and biomass (right) for batch B01.

## Digitization and curation workflow

The pathway from expert PDF logs to the public CSV release is summarized in Table 4 and comprises the following stages:

1. Expert operators/technicians measured process variables and recorded them on industrial PDF batch sheets.
2. Batch records were digitized into structured tables corresponding to individual production lots.
3. Digitized batch tables were assembled into stacked CSV releases with English, machine-readable headers (`batch_metadata.csv`, `fermentation_timeseries.csv`).
4. Completeness flags were assigned (`full_process` vs `alcohol_sugar_biomass`; Table 3) according to available covariates.
5. No imputation, smoothing, or unit renormalization was applied. Empty cells remain empty.
6. Hourly rows containing only helper fields (no process variables) were removed during packaging (one such row in B02).
7. Batch `B05` retains volume values that are approximately an order of magnitude larger than peer batches; this is flagged in `batch_metadata.csv` notes and treated as a raw recording anomaly.
8. End-of-batch airflow values > 40,000 m³/h (B04, B09), duplicate lot headers (B10/B11), and sparse early-phase biomass extremes are flagged in metadata / `summary_stats.json`.

**Table 4. Data flow from expert PDF logs to released CSVs.**

| Stage | Component | Function | Output |
|-------|-----------|----------|--------|
| 1 | Industrial PDF batch logs | Expert measurement and handwritten/typed recording during production | Source archive (data owners; not redistributed) |
| 2 | Digitization | Transfer recorded values into structured batch tables | Tabular batch records |
| 3 | Dataset packaging | Normalize identifiers, stack timeseries, document headers | CSV files |
| 4 | Metadata tagging | Completeness flags and anomaly notes | `batch_metadata.csv` |

## Descriptive statistics

Table 5 reports descriptive statistics (mean, standard deviation, minimum, and maximum) for the full-process batches (B01–B10). Table 6 summarizes the same statistics for the key variables available across all 61 batches. Complementary visual summaries are provided in Fig. 3 (median pH and airflow with IQR bands in separate panels) and Fig. 4 (distribution of recorded sugar feed rates).

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

Notes to Tables 5–6: (i) Volume mean/SD/max in Table 5 are dominated by B05; excluding B05 yields volume mean ≈ 115.4 m³ (SD ≈ 19.9; range 87.7–149.3). (ii) Airflow max = 49992 arises from two end-of-batch outliers (B04, B09); excluding values > 40,000 m³/h yields airflow mean ≈ 16080.6 (max 20892). (iii) Biomass max in Table 6 reflects sparse-batch early-phase extremes (> 60,000 kg) flagged in metadata. (iv) Full-process yield statistics (B01–B10 only; n = 10): mean 39009.2 kg Y30 (SD 352.0).

**Fig. 3.** Median pH (left) and airflow (right) versus fermentation hour with IQR bands (full-process batches, excluding B05).

**Fig. 4.** Histogram of recorded sugar feed rates across all batches.

## Data quality validation

Prior to release, the following checks were performed:

- **Completeness check:** Counted non-missing values per variable and tagged batches as `full_process` or `alcohol_sugar_biomass`.
- **Range screening:** Verified alcohol ≥ 0, pH roughly 3–8, growth modulus near 1–1.6, and sugar feed rates within physically plausible magnitudes for industrial fed-batch operation; flagged volume, airflow, and biomass outliers retained as recorded.
- **Batch integrity:** Confirmed `time_h` is unique within each `batch_id` and monotonically non-decreasing; removed helper-only empty rows.
- **Provenance:** Digitized values originate from expert-completed industrial PDF batch logs retained by the data owners (not redistributed).

The outcomes of these checks are summarized in Table 7.

**Table 7. Data quality validation outcomes.**

| Check | Outcome |
|-------|---------|
| Batches in CSV release | 61 |
| Timeseries rows | 1,127 |
| Full-process batches | 10 |
| Missing sugar feed rate | 61/1,127 (5.4%); mostly at `time_h = 0` |
| Missing alcohol | 0/1,127 |
| Flagged volume anomaly | B05 |
| Flagged airflow outliers | B04, B09 (end-of-batch > 40,000 m³/h) |
| Duplicate lot header | B10/B11 (lot 2616); yield stats use full-process n = 10 |
| Imputation applied | None |

## Example workflow for data loading

The CSV files can be opened in any standard spreadsheet or scientific computing environment. Users typically load `fermentation_timeseries.csv` together with `batch_metadata.csv`, select batches marked as `full_process` when rich covariates are required, sort records by `batch_id` and `time_h`, and construct supervised targets such as the current-hour or next-hour sugar feed rate (`sugar_feed_rate_kg_rs_h`) from the ordered time series within each batch. Empty cells should be treated as missing values rather than zeros. Column definitions are provided in Table 2 and in the dataset `README.md`.

# Example Data Reuse and Quality Assessment

**Feed-rate prediction baseline.** Using full-process batches, a BiLSTM (or 1D-CNN) model can predict current sugar feed rate from a short window of recent process variables. In a leave-one-batch-out evaluation on nine full-process batches (excluding the anomalous-volume batch B05), the accompanying usage example achieved pooled MAE ≈ 102.5 kg RS/h, MAPE ≈ 11.6%, and R² ≈ 0.872, demonstrating that the digitized expert records are usable for supervised nutrient-addition prediction. Details of the executable example are given under Code availability.

**Profile tracking.** Differences between measured alcohol and `evaluation_profiles.csv` provide a batch-quality indicator; batches with persistently elevated alcohol relative to the profile are candidates for feed-rate oversupply studies. The usage script reports alcohol-vs-profile MAE for full-process batches (`usage/results/alcohol_profile_mae.json`).

**Cross-batch generalization.** Because records come from multiple production lots, leave-one-batch-out or leave-several-lots-out validation is recommended to assess robustness under industrial lot shift.

# LIMITATIONS

- **Single strain context:** Released batches share strain ID 167; cross-strain generalization cannot be assessed from this release alone.
- **Uneven covariate coverage:** Only 10 batches include rich process covariates; 51 batches are sparse.
- **Hourly resolution:** Records are hourly operator/log-sheet resolution rather than high-frequency continuous sensor streams.
- **Digitization from PDF logs:** Values were transferred from expert-completed PDF sheets; handwriting/transcription artefacts may exist and are retained when present. Original PDFs are not part of the public deposit.
- **Recording anomalies retained:** Volume values in B05 appear inflated; B04/B09 include extreme end-of-batch airflow; some sparse batches show early-phase biomass extremes (> 60,000 kg). These are flagged but not corrected.
- **Duplicate lot headers:** B10 and B11 share lot 2616; B11 is an incomplete sparse sheet and should not be treated as an independent full-information batch.
- **Confidential plant metadata:** Exact plant identity, calendar dates, and operator identities are not included.
- **Repository DOI pending:** Public DOI/URL placeholders must be completed upon deposition.

# ETHICS STATEMENT

The authors have read and follow the ethical requirements for publication in *Data in Brief*. The current work does not involve human subjects, animal experiments, or data collected from social media platforms. Industrial process values are released without personally identifiable information.

# CRediT AUTHOR STATEMENT

Changning Ren: Conceptualization, Data curation, Investigation, Methodology, Writing – original draft. Lei Zhao: Investigation, Writing – review & editing. Ling Kang: Data curation, Validation. Quan Guo: Supervision, Writing – review & editing.

# ACKNOWLEDGEMENTS

[Acknowledgements and funding statement to be completed by the authors.]

# DATA AVAILABILITY

The datasets will be deposited on [figshare/Zenodo] (DOI: [to be completed]). Repository contents include the files listed in Table 1 (CSV/JSON tables and `README.md`). Manuscript figures (Figs. 1–4) are not part of the dataset deposit.

# CODE AVAILABILITY

Supporting code for this data article is available in the project repository at https://gitee.com/sacourse/yeast.git. The repository provides: (i) scripts for packaging the digitized batch tables into the released CSV layout; (ii) scripts for regenerating the manuscript figures under `paper/figures/`; and (iii) a usage example that trains lightweight sequence models (BiLSTM or 1D-CNN) to predict sugar feed rate under leave-one-batch-out validation, together with example metrics. Installation dependencies are listed in `requirements.txt`. The code is intended to demonstrate dataset usability and to support reproduction of the figures and baseline prediction results reported in this article.

# DECLARATION OF COMPETING INTERESTS

The authors declare that they have no known competing financial interests or personal relationships that could have appeared to influence the work reported in this paper.

# REFERENCES

[1] G.M. Walker, P.M. Walker, Yeast fermentation: physiology and biotechnology, in: Comprehensive Biotechnology, Elsevier, 2011.

[2] B. Sonnleitner, O. Käppeli, Growth of *Saccharomyces cerevisiae* is controlled by its limited respiratory capacity: formulation and verification of a hypothesis, Biotechnol. Bioeng. 28 (1986) 927–937. https://doi.org/10.1002/bit.260280620.

[3] M. Rizzi, M. Baltes, U. Theobald, M. Reuss, In vivo analysis of metabolic dynamics in *Saccharomyces cerevisiae*: II. Mathematical model, Biotechnol. Bioeng. 55 (1997) 592–608.

[4] P. Kadlec, B. Gabrys, S. Strandt, Data-driven soft sensors in the process industry, Comput. Chem. Eng. 33 (2009) 795–814. https://doi.org/10.1016/j.compchemeng.2008.12.012.

[5] Z. Ge, Review on data-driven modeling and monitoring for plant-wide industrial processes, Chemometrics and Intelligent Laboratory Systems 171 (2017) 16–25. https://doi.org/10.1016/j.chemolab.2017.09.021.

[6] S.J. Pan, Q. Yang, A survey on transfer learning, IEEE Trans. Knowl. Data Eng. 22 (2010) 1345–1359. https://doi.org/10.1109/TKDE.2009.35.

[7] Z. Ge, Z. Song, S. X. Ding, B. Huang, Data mining and analytics in the process industry: the role of machine learning, IEEE Access 5 (2017) 20590–20616. https://doi.org/10.1109/ACCESS.2017.2756872.
