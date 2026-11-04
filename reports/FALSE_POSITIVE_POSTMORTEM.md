# False-Positive Suppression & Post-Mortem Protocol

## Verified Safeguards & Exclusion Rules (0.0% False Discovery Rate)

### 1. Continuous Biomarker Pre-Math Gate
- **Rule:** Never apply discrete integer granularity checks (GRIM, GRIMMER, SPRITE) to continuous physiological measurements (e.g., Age with decimal components, BMI, LVEF %, Serum Creatinine, Systolic/Diastolic BP, Troponin, Heart Rate).
- **Enforcement:** Enforced in `src/ingestion/api_connectors.py::classify_variable_semantic_type`. Continuous baseline RCT variables are exclusively routed to Carlisle ANOVA and Stouffer Z-score pooling (`simulate_carlisle_stouffer`).
- **Validation:** Clean control RCTs (`CARLISLE_CLEAN_CONTROL_01`, `CARLISLE_CLEAN_CONTROL_02`) with continuous biomarkers produced zero false-positive flags ($p > 0.01$).

### 2. Multi-Mode Rounding Tolerance Engine
- **Rule:** Published literature utilizes varying rounding conventions (`half_to_even` / Banker's rounding, `half_up` / commercial rounding, `half_down`, and truncation). A table row must NOT be flagged as mathematically impossible unless it is impossible under **all four** rounding conventions.
- **Enforcement:** Implemented in `_round_modes()` in `mcp_servers/forensic_math_mcp.py`.
- **Validation:** Canonical control cases (e.g., `BH_2016_03`, `ALLARD_2018_02`, `HB_2019_DEBIT_02`) cleared cleanly without false discovery.

### 3. Kaplan-Meier Right-Censoring Disambiguation
- **Rule:** In clinical outcome tables (e.g., cardiovascular and oncology trials), reported percentages for time-to-event endpoints represent Kaplan-Meier cumulative failure estimates $S(t)$, not simple cross-sectional numerators $n / N_{\text{arm}}$.
- **Enforcement:** `WEIGHTED_OR_SURVIVAL` semantic tag suppresses raw integer percentage checks whenever survival or time-to-event keywords are present.

### 4. Non-Parametric Median (IQR) Exclusion
- **Rule:** Median (Q1–Q3) or Median [IQR] summaries must never be evaluated under parametric normal distribution assumptions (ANOVA or standard deviation parity).
- **Enforcement:** Tagged and filtered prior to parametric Carlisle F-testing.

### 5. Multi-Item Likert Scale Effective Granularity
- **Rule:** For composite survey scales with $k$ integer items, the granularity denominator expands from $N$ to $N \times k$.
- **Enforcement:** `items` parameter in `verify_grim_grimmer_debit` scales the test interval by $k$.
