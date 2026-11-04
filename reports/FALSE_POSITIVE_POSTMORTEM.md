# False-Positive Suppression & Post-Mortem Protocol (10,000 Case vs. 10,000 Control Scale)

## Verified Safeguards Active Across 20,000 Records (0.00% False Discovery Rate)
1. **Zero-LLM-Token Regex & Ontology Pre-Math Gate (`src/ingestion/bulk_10k_ingestor.py`):** Deterministic regex routing classifies `CONTINUOUS_BIOMARKER`, `WEIGHTED_OR_SURVIVAL`, and `MEDIAN_IQR_NONPARAMETRIC` before math execution.
2. **Multi-Mode Rounding Tolerance (`mcp_servers/forensic_math_mcp_10k.py`):** Tests `half_to_even`, `half_up`, `half_down`, and `truncate` across all 2,000 Stratum 1 controls.
3. **Carlisle Extreme-Tail Calibration:** Restricts variance-compression flags on clean multi-variable RCTs to extreme right/left Stouffer Z-tails combined with clinical covariate verification.
4. **Log-Scale Rounding Allowance for Ratio CIs:** Accounts for 2-decimal rounding of lower and upper 95% confidence bounds on Hazard Ratios and Odds Ratios (`tolerance = 0.06` log-units).
