---
name: forensic-table-extractor
description: Rules and SOPs for parsing JATS XML and PDF clinical/scientific tables, normalizing summary statistics, and typing variables before running mathematical consistency tests.
---

# Forensic Table Extractor & Semantic Variable Typer

## Purpose
Prevent false-positive mathematical flags by enforcing strict variable typing and structural validation prior to invoking the deterministic FastMCP math server.

## Step 1: Structural Normalization
1. **Header & Arm Resolution:** Extract exact sample sizes ($N_{\text{arm}}$) from column headers and verify whether sub-rows report local denominators ($n/N$).
2. **Statistic Format Disambiguation:** Distinguish between:
   - `MEAN_SD`: Mean $\pm$ SD or Mean (SD)
   - `MEAN_SE`: Mean $\pm$ SE (Convert $SD = SE \times \sqrt{N}$ before variance checks)
   - `MEDIAN_IQR`: Median (Q1–Q3) or Median [IQR] (Suppress GRIM, GRIMMER, and parametric ANOVA)
   - `COUNT_PCT`: $n$ (\%) categorical counts

## Step 2: Semantic Variable Classification (Pre-Math Gate)
Assign each extracted row to exactly one semantic class:
- `DISCRETE_INTEGER_COUNT`: Whole-number count or single-item ordinal score (Eligible for GRIM, GRIMMER, SPRITE).
- `LIKERT_COMPOSITE`: Multi-item scale with known integer item count $k$ (Eligible for GRIM/GRIMMER with effective granularity $N \times k$ when $N \times k < 10^{D+1}$).
- `BINARY_SUMMARY`: Dichotomous 0/1 outcome reported as Mean and SD (Eligible for DEBIT).
- `CONTINUOUS_BIOMARKER`: Physiological or laboratory continuous variables (e.g., age with decimal components, LVEF %, serum creatinine, BMI, blood pressure, troponin). **NEVER run GRIM or GRIMMER on `CONTINUOUS_BIOMARKER`.** Eligible for Carlisle baseline ANOVA p-value pooling.
- `WEIGHTED_OR_SURVIVAL`: Propensity-score matched, inverse-probability weighted (IPW), or Kaplan-Meier survival estimates. **Suppress integer numerator and raw granularity checks.**
