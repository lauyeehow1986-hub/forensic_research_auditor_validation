---
name: high-throughput-10k-orchestrator
description: High-throughput 10,000 case vs. 10,000 control (20,000 total) benchmark orchestration, SQLite WAL checkpointing, vectorized FastMCP math verification, and Wilson 95% confidence interval validation.
---

# High-Throughput 10k vs. 10k Forensic Benchmark Orchestrator

## 1. Purpose & Scope
Orchestrates large-scale empirical calibration and six-sigma quality gating for the `forensic_research_auditor` pipeline across **10,000 confirmed fabricated/flawed cases vs. 10,000 matched clean controls (20,000 total records)** without burning LLM reasoning tokens on numerical loops or repetitive API queries.

---

## 2. 5 Stratified Forensic Benchmark Domains (4,000 Records per Stratum)

| Stratum | Domain / Methodology | Case Definition (2,000) | Control Definition (2,000) | Deterministic Verification Tool |
| :--- | :--- | :--- | :--- | :--- |
| **Stratum 1** | **Granularity Suite** (`GRIM`, `Analytic-GRIMMER`, `DEBIT`) | 2,000 integer/binary summary anomalies failing arithmetic or parity bounds | 2,000 valid rounded discrete/binary summaries across 4 rounding modes | `verify_grim_grimmer_debit` |
| **Stratum 2** | **Carlisle Baseline Homogeneity** | 2,000 RCT baseline tables with hyper-homogeneity ($\Phi(Z_S) > 0.999$) | 2,000 authentic random-sampling RCT baseline tables ($\Phi(Z_S) \le 0.999$) | `simulate_carlisle_stouffer` |
| **Stratum 3** | **Statcheck & 95% Log-CI** | 2,000 records with $\alpha=0.05$ decision errors or log-asymmetric Hazard Ratios | 2,000 accurately reported test statistics and log-symmetric CIs | `audit_statcheck_and_ci` |
| **Stratum 4** | **Diekmann 2nd-Digit Benford** | 2,000 tables exhibiting terminal/second-digit preference ($\chi^2, p < 0.005$) | 2,000 tables conforming to empirical 2nd-digit Benford distribution ($p \ge 0.005$) | `check_benford_second_digit` |
| **Stratum 5** | **Retraction Watch & Cabanac PPS** | 2,000 confirmed retractions (`+Falsification/Fabrication of Data`) or tortured phrases | 2,000 1:1 OpenAlex matched clean controls from same journals and years | `bulk_10k_ingestor.py` |

---

## 3. High-Throughput Ingestion Architecture
To prevent API rate limits, HTTP latency, and context window exhaustion:
1. **Local Crossref Retraction Watch CSV Mirror:** Load directly from local mirror (`gitlab.com/crossref/retraction-watch-data`) to bypass per-DOI HTTP lookups.
2. **OpenAlex Batching:** Query OpenAlex REST API in pipe-separated batches of 50 DOIs (`per-page=200`) using the polite pool (`mailto:` parameter).
3. **Europe PMC JATS XML Tables:** Ingest `<table-wrap>` XML nodes using cursor pagination or bulk FTP archives.
4. **SQLite WAL Persistence:** Checkpoint all extracted tables and verification verdicts in `audit_ledger_20k.db` with Write-Ahead Logging (`PRAGMA journal_mode=WAL;`).

---

## 4. Zero-Token Pre-Math Semantic Gate
Before executing mathematical tests, every variable row must pass deterministic regex classification:
- **`CONTINUOUS_BIOMARKER`** (`age`, `bmi`, `lvef`, `creatinine`, `systolic`, `troponin`, `cholesterol`, `weight`, `height`) $\rightarrow$ **Strictly suppress GRIM/GRIMMER**. Route exclusively to Carlisle baseline ANOVA.
- **`WEIGHTED_OR_SURVIVAL`** (`kaplan-meier`, `km estimate`, `iptw`, `propensity`, `weighted`, `cumulative incidence`) $\rightarrow$ Suppress raw integer denominator percentage checks.
- **`MEDIAN_IQR`** (`median`, `iqr`, `interquartile`) $\rightarrow$ Suppress parametric ANOVA.
- **`BINARY_SUMMARY`** $\rightarrow$ Route to DEBIT.
- **`LIKERT_COMPOSITE`** $\rightarrow$ Expand effective denominator to $N \times k$.

---

## 5. Statistical Evaluation & Confidence Intervals
All aggregate diagnostic metrics must report exact Wilson score 95% confidence intervals:
- **Sensitivity:** $TP / (TP + FN)$ with Wilson 95% CI
- **Specificity:** $TN / (TN + FP)$ with Wilson 95% CI
- **Positive Predictive Value (PPV):** $TP / (TP + FP)$ with Wilson 95% CI
- **Negative Predictive Value (NPV):** $TN / (TN + FN)$ with Wilson 95% CI
- **False Discovery Rate (FDR):** $FP / (TP + FP)$ with Wilson 95% CI (Must satisfy Six-Sigma threshold $< 0.10\%$)
- **Matthews Correlation Coefficient (MCC):** Must equal $1.0000$ on benchmark suites.
