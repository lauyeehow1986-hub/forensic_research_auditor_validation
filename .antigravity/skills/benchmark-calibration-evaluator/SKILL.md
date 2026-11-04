---
name: benchmark-calibration-evaluator
description: Case-control benchmark calibration, historical concordance verification, confusion matrix computation, and false-positive post-mortem auditing.
---

# Benchmark Calibration & Concordance Evaluator

## Purpose
Validate the `forensic_research_auditor` pipeline against established ground-truth datasets and previously published forensic meta-research findings to demonstrate diagnostic robustness, reproducibility, and a <1.0% false-positive rate on clean clinical controls.

## Ground-Truth Benchmark Suites
1. **Carlisle RCT Baseline Corpus (Carlisle 2012, 2017):**
   - Verify concordance with Carlisle's published Stouffer/Fisher combined baseline p-values on known fabricated trials (e.g., Yoshitaka Fujii, Joachim Boldt, Yoshihiro Sato) vs. non-retracted control RCTs.
2. **Brown & Heathers (2016) GRIM Validation Set:**
   - Reproduce exact integer impossibility flags on benchmark cases (e.g., $N=28, M=5.19$; $N=27, M=3.86$) while verifying zero false flags on valid rounded means across `half_up`, `half_to_even`, and `truncate` conventions.
3. **Allard (2018) Analytic-GRIMMER & Heathers/Brown (2019) DEBIT Corpus:**
   - Reproduce exact standard deviation impossibility flags (e.g., $N=18, M=3.44, SD=2.47$ for GRIMMER; $N=20, M=0.36, SD=0.11$ for DEBIT).
4. **Crossref / Retraction Watch Case-Control Cohort:**
   - 1:1 matched case-control evaluation of papers retracted for `+Falsification/Fabrication of Data` against non-retracted OpenAlex controls from identical journals and publication years.

## Required Diagnostic Metrics
- Confusion Matrix: True Positives (TP), False Positives (FP), True Negatives (TN), False Negatives (FN)
- Sensitivity (Recall), Specificity, Precision (PPV), Negative Predictive Value (NPV), False Discovery Rate (FDR), F1-Score, Matthew's Correlation Coefficient (MCC), and Concordance Rate (%) against published reference values.
