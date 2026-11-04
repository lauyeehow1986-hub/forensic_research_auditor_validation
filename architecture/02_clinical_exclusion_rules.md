# 02: Clinical Cardiology & Trial Exclusion Rules (Zero-False-Positive Suppression at 20,000 Scale)

1. **Continuous Physiological Measurements:** Never apply GRIM, GRIMMER, or SPRITE to continuous measurements (e.g., age, BMI, LVEF %, serum creatinine, eGFR, syntax score, lesion length in mm).
2. **Propensity-Matched & Weighted Cohorts:** Suppress integer denominator percentage checks and GRIM tests when the study uses IPTW or propensity score matching.
3. **Time-to-Event Kaplan-Meier Percentages:** In cardiovascular trials, event rates reported as `n (%)` in outcome tables frequently represent Kaplan-Meier failure estimates at time $t$ rather than raw $n / N_{\text{arm}}$ proportions.
4. **Median (IQR) vs. Mean (SD):** Filter out non-parametric Median (Q1-Q3) rows prior to running parametric ANOVA or variance parity checks.
