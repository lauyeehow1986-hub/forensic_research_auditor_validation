#!/usr/bin/env python3
"""
Unit tests for deterministic forensic mathematics and blind ledger integrity.
"""

import json
import os
import sys
import pytest
import numpy as np

# Ensure project root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from mcp_servers.forensic_math_mcp import (
    verify_grim_grimmer_debit,
    simulate_carlisle_stouffer,
    audit_statcheck_and_ci,
    check_benford_second_digit,
)
from src.ingestion.api_connectors import classify_retraction_tier


class TestForensicMathGates:
    """Tests deterministic modular arithmetic gates."""

    def test_grim_impossible_mean(self):
        """Mean 36.45 with N=32 cannot be produced from discrete integer sums."""
        res = verify_grim_grimmer_debit(mean=36.45, sd=5.0, n=32, decimals_mean=2, decimals_sd=2)
        assert res["grim_pass"] is False
        assert res["verdict"] == "GRIM_IMPOSSIBLE"

    def test_grim_valid_mean(self):
        """Mean 3.50 with N=20 corresponds to an exact integer sum of 70."""
        res = verify_grim_grimmer_debit(mean=3.50, sd=1.20, n=20, decimals_mean=2, decimals_sd=2)
        assert res["grim_pass"] is True
        assert 70 in res["valid_integer_sums"]

    def test_debit_binary_summary(self):
        """DEBIT consistency test for binary proportions."""
        # For N=100, proportion p = 40/100 = 0.40
        # SD = sqrt((100/99) * 0.4 * 0.6) = sqrt(0.242424) = 0.4923659
        res = verify_grim_grimmer_debit(mean=0.40, sd=0.49, n=100, is_binary=True)
        assert res["grim_pass"] is True
        assert res["debit_pass"] is True
        assert res["verdict"] == "CONSISTENT"

    def test_debit_impossible_binary_summary(self):
        """Impossible binary SD that violates the binomial variance formula."""
        res = verify_grim_grimmer_debit(mean=0.40, sd=1.25, n=100, is_binary=True)
        assert res["debit_pass"] is False
        assert res["verdict"] == "IMPOSSIBLE_BINARY_SUMMARY"

    def test_carlisle_variance_compression(self):
        """Carlisle ANOVA across hyper-homogeneous arms (unnatural identical means)."""
        baseline_rows = [
            {"variable": f"Biomarker_{i}", "means": [50.01, 50.02], "sds": [10.0, 10.0], "ns": [100, 100]}
            for i in range(15)
        ]
        res = simulate_carlisle_stouffer(baseline_rows)
        assert res["carlisle_combined_p"] > 0.999
        assert res["verdict"] == "VARIANCE_COMPRESSION_HYPER_HOMOGENEITY"

    def test_carlisle_random_sampling(self):
        """Normal variance across independent arms passes Carlisle test."""
        baseline_rows = [
            {"variable": "Age", "means": [52.4, 54.1], "sds": [8.2, 8.5], "ns": [60, 60]},
            {"variable": "BMI", "means": [26.1, 25.8], "sds": [3.4, 3.2], "ns": [60, 60]},
            {"variable": "BP", "means": [128.0, 131.0], "sds": [12.0, 11.5], "ns": [60, 60]},
        ]
        res = simulate_carlisle_stouffer(baseline_rows)
        assert res["carlisle_combined_p"] < 0.999
        assert res["verdict"] == "CONSISTENT_RANDOM_SAMPLING"

    def test_statcheck_decision_error(self):
        """Statcheck recalculates p from t-statistic and flags decision errors."""
        # t=2.10, df=30 -> true two-tailed p = 0.0442 (significant), reported as 0.06 (non-significant)
        res = audit_statcheck_and_ci(
            test_type="t",
            df1=30,
            reported_stat=2.10,
            reported_p=0.06
        )
        assert res["decision_error_alpha_05"] is True
        assert res["verdict"] == "DECISION_ERROR_FLAG"

    def test_confidence_interval_log_symmetry(self):
        """Verifies log-scale confidence interval midpoint symmetry for ratios."""
        # Clean: HR = 1.5, 95% CI: 1.125 to 2.0 (log(1.125)+log(2))/2 = log(1.5)
        res_clean = audit_statcheck_and_ci(
            test_type="z",
            df1=1,
            reported_stat=2.0,
            reported_p=0.045,
            estimate=1.5,
            lower_ci=1.125,
            upper_ci=2.0,
            is_log_scale=True
        )
        assert res_clean["ci_audit"]["verdict"] == "SYMMETRIC"

        # Flagged: Severely asymmetric CI
        res_flagged = audit_statcheck_and_ci(
            test_type="z",
            df1=1,
            reported_stat=2.0,
            reported_p=0.045,
            estimate=1.5,
            lower_ci=0.8,
            upper_ci=4.5,
            is_log_scale=True
        )
        assert res_flagged["ci_audit"]["verdict"] == "ASYMMETRIC_CI_FLAG"

    def test_benford_second_digit_anomaly(self):
        """Fabricated numbers clustering on terminal digits 0 and 5 trigger anomaly alert."""
        clustered_vals = [100.0 + (0 if i % 2 == 0 else 5) * 10.0 + 1.23 for i in range(100)]
        res = check_benford_second_digit(clustered_vals)
        assert res["verdict"] == "DIGIT_PREFERENCE_ANOMALY"
        assert res["p_value"] < 0.01


class TestRetractionTaxonomy:
    """Tests 3-Tier Retraction Stratification."""

    def test_tier_1_data_fabrication(self):
        res = classify_retraction_tier("falsification of data and image manipulation in figures")
        assert res is not None
        assert res["primary_tier"] == "TIER_1_MATH_DATA"
        assert res["is_math_data_fraud"] is True

    def test_tier_2_papermill(self):
        res = classify_retraction_tier("compromised peer review by paper mill and machine translation")
        assert res is not None
        assert res["primary_tier"] == "TIER_2_PAPERMILL"
        assert res["is_papermill"] is True

    def test_tier_3_editorial_governance(self):
        res = classify_retraction_tier("retracted due to authorship dispute and lack of institutional authorization")
        assert res is not None
        assert res["primary_tier"] == "TIER_3_EDITORIAL_GOVERNANCE"
        assert res["is_editorial_governance"] is True

    def test_clean_control(self):
        assert classify_retraction_tier("") is None
        assert classify_retraction_tier(None) is None


class TestBlind100FullTextLedgerIntegrity:
    """Verifies empirical integrity of the live blind 100-study full-text ledger."""

    def test_ledger_exists_and_complete(self):
        ledger_path = os.path.join("data", "extracted_tables", "real_100_fulltext_blind_ledger.jsonl")
        assert os.path.exists(ledger_path), f"Ledger file not found: {ledger_path}"

        records = []
        with open(ledger_path, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    records.append(json.loads(line))

        assert len(records) == 100, f"Expected 100 blind studies, got {len(records)}"

        cases = [r for r in records if r.get("cohort") == "CASE"]
        controls = [r for r in records if r.get("cohort") == "CONTROL"]
        assert len(cases) == 50, f"Expected 50 cases, got {len(cases)}"
        assert len(controls) == 50, f"Expected 50 controls, got {len(controls)}"

        # Verify Tier 1 Data Fraud sensitivity is >= 70%
        tier1_cases = [r for r in cases if r.get("retraction_tier") == "TIER_1_MATH_DATA"]
        assert len(tier1_cases) == 9
        detected_tier1 = [r for r in tier1_cases if r.get("blind_verdict") == "FLAGGED_FORENSIC_ANOMALY"]
        sensitivity = len(detected_tier1) / len(tier1_cases)
        assert sensitivity >= 0.70, f"Expected Tier 1 sensitivity >= 70%, got {sensitivity:.2%}"

        # Verify Control Specificity is >= 90%
        clean_controls = [r for r in controls if r.get("blind_verdict") == "CLEAN"]
        specificity = len(clean_controls) / len(controls)
        assert specificity >= 0.90, f"Expected Control Specificity >= 90%, got {specificity:.2%}"

        # Verify Tier 3 Editorial retractions have clean table numbers (authentic math)
        tier3_cases = [r for r in cases if r.get("retraction_tier") == "TIER_3_EDITORIAL_GOVERNANCE"]
        assert len(tier3_cases) == 41
        clean_math_tier3 = [r for r in tier3_cases if not r.get("math_gate_triggered", False)]
        tier3_math_pass_rate = len(clean_math_tier3) / len(tier3_cases)
        assert tier3_math_pass_rate >= 0.95, f"Expected Tier 3 math consistency >= 95%, got {tier3_math_pass_rate:.2%}"
