# Empirical Benchmark & Historical Concordance Validation Report

## 1. Executive Summary
- **Total Ground-Truth Benchmark Cases Evaluated:** 20
- **Concordance with Published Reference Verdicts:** 100.0% (20/20)
- **Sensitivity (True Positive Rate / Recall):** 100.0% (11/11)
- **Specificity (True Negative Rate):** 100.0% (9/9)
- **Positive Predictive Value (Precision / PPV):** 100.0% (11/11)
- **Negative Predictive Value (NPV):** 100.0% (9/9)
- **False Discovery Rate (FDR):** 0.0% (0/11)
- **F1 Score:** 1.0000
- **Matthews Correlation Coefficient (MCC):** 1.0000

---

## 2. 2x2 Diagnostic Confusion Matrix

| | Actually Fabricated / Flawed (Case) | Actually Valid / Unmanipulated (Control) | Total |
| :--- | :---: | :---: | :---: |
| **Tool Flagged Positive** | **11 (True Positive)** | **0 (False Positive)** | **11** |
| **Tool Passed Clean (Negative)** | **0 (False Negative)** | **9 (True Negative)** | **9** |
| **Total** | **11** | **9** | **20** |

---

## 3. Case-by-Case Concordance Against Published Literature

| Case ID | Corpus | Gate | Cohort | Published Verdict | Tool Verdict | Concordant |
| :--- | :--- | :--- | :--- | :--- | :--- | :---: |
| `BH_2016_01` | Brown_Heathers_2016 | `GRIM` | **CASE** | `GRIM_IMPOSSIBLE` | `GRIM_IMPOSSIBLE` | **YES** |
| `BH_2016_02` | Brown_Heathers_2016 | `GRIM` | **CASE** | `GRIM_IMPOSSIBLE` | `GRIM_IMPOSSIBLE` | **YES** |
| `BH_2016_03` | Brown_Heathers_2016 | `GRIM` | **CONTROL** | `CONSISTENT` | `CONSISTENT` | **YES** |
| `ALLARD_2018_01` | Allard_2018_GRIMMER | `GRIMMER` | **CASE** | `GRIMMER_SD_IMPOSSIBLE` | `GRIMMER_SD_IMPOSSIBLE` | **YES** |
| `ALLARD_2018_02` | Allard_2018_GRIMMER | `GRIMMER` | **CONTROL** | `CONSISTENT` | `CONSISTENT` | **YES** |
| `HB_2019_DEBIT_01` | Heathers_Brown_2019_DEBIT | `DEBIT` | **CASE** | `IMPOSSIBLE_BINARY_SUMMARY` | `IMPOSSIBLE_BINARY_SUMMARY` | **YES** |
| `HB_2019_DEBIT_02` | Heathers_Brown_2019_DEBIT | `DEBIT` | **CONTROL** | `CONSISTENT` | `CONSISTENT` | **YES** |
| `CARLISLE_FUJII_CASE_01` | Carlisle_2012_2017_Anaesthesia | `CARLISLE_STOUFFER_ANOVA` | **CASE** | `VARIANCE_COMPRESSION_HYPER_HOMOGENEITY` | `VARIANCE_COMPRESSION_HYPER_HOMOGENEITY` | **YES** |
| `CARLISLE_BOLDT_CASE_02` | Carlisle_2012_2017_Anaesthesia | `CARLISLE_STOUFFER_ANOVA` | **CASE** | `VARIANCE_COMPRESSION_HYPER_HOMOGENEITY` | `VARIANCE_COMPRESSION_HYPER_HOMOGENEITY` | **YES** |
| `CARLISLE_SATO_CASE_03` | Carlisle_2012_2017_Anaesthesia | `CARLISLE_STOUFFER_ANOVA` | **CASE** | `VARIANCE_COMPRESSION_HYPER_HOMOGENEITY` | `VARIANCE_COMPRESSION_HYPER_HOMOGENEITY` | **YES** |
| `CARLISLE_CLEAN_CONTROL_01` | Carlisle_2017_Control_RCT | `CARLISLE_STOUFFER_ANOVA` | **CONTROL** | `CONSISTENT_RANDOM_SAMPLING` | `CONSISTENT_RANDOM_SAMPLING` | **YES** |
| `CARLISLE_CLEAN_CONTROL_02` | Carlisle_2017_Control_RCT | `CARLISLE_STOUFFER_ANOVA` | **CONTROL** | `CONSISTENT_RANDOM_SAMPLING` | `CONSISTENT_RANDOM_SAMPLING` | **YES** |
| `CABANAC_PPS_CASE_01` | Cabanac_Problematic_Paper_Screener | `TORTURED_PHRASES` | **CASE** | `TORTURED_PHRASES_DETECTED` | `TORTURED_PHRASES_DETECTED` | **YES** |
| `CABANAC_PPS_CONTROL_01` | Cabanac_Problematic_Paper_Screener_Control | `TORTURED_PHRASES` | **CONTROL** | `CLEAN_LEXICON` | `CLEAN_LEXICON` | **YES** |
| `DIEKMANN_BENFORD_CASE_01` | Diekmann_2007_Benford_Forensics | `BENFORD_SECOND_DIGIT` | **CASE** | `DIGIT_PREFERENCE_ANOMALY` | `DIGIT_PREFERENCE_ANOMALY` | **YES** |
| `DIEKMANN_BENFORD_CONTROL_01` | Diekmann_2007_Benford_Forensics | `BENFORD_SECOND_DIGIT` | **CONTROL** | `BENFORD_CONSISTENT` | `BENFORD_CONSISTENT` | **YES** |
| `STATCHECK_DECISION_CASE_01` | Nuijten_2016_Statcheck | `STATCHECK` | **CASE** | `DECISION_ERROR_FLAG` | `DECISION_ERROR_FLAG` | **YES** |
| `STATCHECK_CONTROL_01` | Nuijten_2016_Statcheck | `STATCHECK` | **CONTROL** | `CONSISTENT` | `CONSISTENT` | **YES** |
| `RW_FABRICATION_CASE_01` | Retraction_Watch_Crossref | `RETRACTION_REGISTRY_AUDIT` | **CASE** | `RETRACTED_FABRICATION_DETECTED` | `RETRACTED_FABRICATION_DETECTED` | **YES** |
| `RW_CLEAN_CONTROL_01` | Retraction_Watch_Crossref_Control | `RETRACTION_REGISTRY_AUDIT` | **CONTROL** | `CONSISTENT_CONTROL_VERIFIED` | `CONSISTENT_CONTROL_VERIFIED` | **YES** |

---

## 4. Methodological Alignment Across the 5 Benchmark Domains
1. **Carlisle RCT Corpus (2012, 2017):** Verified 100% concordance across Yoshitaka Fujii, Joachim Boldt, and Yoshihiro Sato baseline hyper-homogeneity ($p < 10^{-6}$) vs. authentic random sampling in clean RCT controls ($p > 0.05$).
2. **Brown & Heathers GRIM (2016):** Successfully reproduces mathematical impossibility flags on discrete integer means ($N=28, M=5.19$ and $N=27, M=3.86$) across multiple rounding modes while clearing clean integer sums.
3. **Allard Analytic-GRIMMER (2018) & Heathers/Brown DEBIT (2019):** Accurately detects parity violations ($N=18, M=3.44, SD=2.47$) and impossible binary standard deviations ($N=20, M=0.36, SD=0.11$) without false alarms on verified distributions.
4. **Crossref Retraction Watch & ClinicalTrials.gov Ingestion:** Confirms data fabrication retractions matching 1:1 against clean peer-reviewed control trials with verified registry enrollment and primary endpoints.
5. **Cabanac Problematic Paper Screener (PPS) & Diekmann Benford Tests:** Correctly screens tortured phrases and isolates artificial terminal/second-digit clustering ($\chi^2, p < 0.0001$) from natural empirical distributions.
