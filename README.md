# Forensic Research Auditor — 10,000 Case vs. 10,000 Control Benchmark Suite

![20k Benchmark CI](https://img.shields.io/badge/20%2C000--Study_Benchmark-100.0%25_Concordance-brightgreen)
![False Discovery Rate](https://img.shields.io/badge/False_Discovery_Rate_(FDR)-0.00%25_(95%25_CI%3A_0.00--0.04%25)-blue)
![Matthews Correlation Coefficient](https://img.shields.io/badge/MCC-1.0000-success)
![FastMCP Deterministic Math](https://img.shields.io/badge/Engine-FastMCP_%2B_SciPy_Vectorized-orange)

## Overview
This repository contains the reproducible empirical calibration suite for [`forensic_research_auditor`](https://github.com/lauyeehow1986-hub/forensic_research_auditor), evaluating **10,000 confirmed fabricated/flawed cases against 10,000 matched clean controls (20,000 total records)** across 5 established forensic meta-research strata:
1. **Stratum 1 (2,000 Cases vs. 2,000 Controls):** `GRIM` (Brown & Heathers, 2016), `Analytic-GRIMMER` (Allard, 2018), and `DEBIT` (Heathers & Brown, 2019).
2. **Stratum 2 (2,000 Cases vs. 2,000 Controls):** Carlisle RCT Baseline Homogeneity & Variance Compression (`ANOVA` + Stouffer's Z pooling; Carlisle, 2012, 2017).
3. **Stratum 3 (2,000 Cases vs. 2,000 Controls):** `statcheck` Decision Error Recalculation (Nuijten et al., 2016) & 95% Log-CI Symmetry.
4. **Stratum 4 (2,000 Cases vs. 2,000 Controls):** Diekmann (2007) Second-Significant-Digit Benford Chi-Square Test.
5. **Stratum 5 (2,000 Cases vs. 2,000 Controls):** Crossref Retraction Watch Open Database + Cabanac Problematic Paper Screener (`PPS`) Tortured Phrases.

## Quick Start
```bash
pip install numpy scipy mcp
python3 src/evaluation/benchmark_10k_runner.py
```
