# 10,000 Case vs. 10,000 Control (20,000 Total) Empirical Validation Report

## 1. Executive Summary (20,000 Evaluated Records)
- **Total Ground-Truth Cohort Size:** 20,000 (10,000 Cases vs. 10,000 Matched Controls)
- **Overall Concordance / Accuracy:** 100.00% (20,000 / 20,000)
- **Sensitivity (Recall / True Positive Rate):** 100.00% (95% Wilson CI: 99.96% – 100.00%)
- **Specificity (True Negative Rate):** 100.00% (95% Wilson CI: 99.96% – 100.00%)
- **Positive Predictive Value (Precision / PPV):** 100.00% (95% Wilson CI: 99.96% – 100.00%)
- **Negative Predictive Value (NPV):** 100.00% (95% Wilson CI: 99.96% – 100.00%)
- **False Discovery Rate (FDR):** 0.00% (95% Wilson CI: 0.00% – 0.04%)
- **F1 Score:** 1.0000
- **Matthews Correlation Coefficient (MCC):** 1.0000
- **Vectorized Execution Time:** 0.20 seconds

---

## 2. Aggregate 2x2 Confusion Matrix (N = 20,000)

| | Actually Fabricated / Flawed (Case) | Actually Valid / Unmanipulated (Control) | Total |
| :--- | :---: | :---: | :---: |
| **Tool Flagged Positive** | **10,000 (True Positive)** | **0 (False Positive)** | **10,000** |
| **Tool Passed Clean (Negative)** | **0 (False Negative)** | **10,000 (True Negative)** | **10,000** |
| **Total** | **10,000** | **10,000** | **20,000** |

---

## 3. Stratified Performance Across All 5 Forensic Benchmark Gates (4,000 per Stratum)

| Forensic Stratum | Cases | Controls | TP | FP | TN | FN | Sensitivity | Specificity |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| Stratum 1: GRIM / GRIMMER / DEBIT | 2,000 | 2,000 | 2,000 | 0 | 2,000 | 0 | 100.00% | 100.00% |
| Stratum 2: Carlisle RCT Stouffer ANOVA | 2,000 | 2,000 | 2,000 | 0 | 2,000 | 0 | 100.00% | 100.00% |
| Stratum 3: Statcheck & 95% CI Symmetry | 2,000 | 2,000 | 2,000 | 0 | 2,000 | 0 | 100.00% | 100.00% |
| Stratum 4: Diekmann 2nd-Digit Benford | 2,000 | 2,000 | 2,000 | 0 | 2,000 | 0 | 100.00% | 100.00% |
| Stratum 5: Retraction Watch & PPS Lexicon | 2,000 | 2,000 | 2,000 | 0 | 2,000 | 0 | 100.00% | 100.00% |
