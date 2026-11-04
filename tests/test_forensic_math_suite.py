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
    audit_regression_triangulation,
    verify_ai_confusion_matrix_triangulation,
    audit_cross_table_marginal_conservation,
    audit_physiological_variance_bounds,
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


class TestBlind2000FullTextLedgerIntegrity:
    """Verifies empirical integrity of the large-scale 2,000-study full-text blind benchmark."""

    def test_2000_ledger_exists_and_complete(self):
        ledger_path = os.path.join("data", "extracted_tables", "real_2000_fulltext_blind_ledger.jsonl")
        assert os.path.exists(ledger_path), f"2000-study ledger not found: {ledger_path}"

        records = []
        with open(ledger_path, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    records.append(json.loads(line))

        assert len(records) == 2000, f"Expected 2000 blind studies, got {len(records)}"

        cases = [r for r in records if r.get("cohort") == "CASE"]
        controls = [r for r in records if r.get("cohort") == "CONTROL"]
        assert len(cases) == 1000, f"Expected 1000 cases, got {len(cases)}"
        assert len(controls) == 1000, f"Expected 1000 controls, got {len(controls)}"

        # Verify Gate 3 Math & Data Fraud sensitivity is >= 20% (actual 25.00%, 22/88)
        gate3_cases = [r for r in cases if r.get("retraction_tier") == "GATE_3_MATH_DATA"]
        assert len(gate3_cases) == 88
        detected_gate3 = [r for r in gate3_cases if r.get("blind_verdict") == "FLAGGED_FORENSIC_ANOMALY"]
        sensitivity = len(detected_gate3) / len(gate3_cases)
        assert sensitivity >= 0.20, f"Expected Gate 3 sensitivity >= 20%, got {sensitivity:.2%}"

        # Verify Control Specificity is >= 80% (actual 80.10%)
        clean_controls = [r for r in controls if r.get("blind_verdict") == "CLEAN"]
        specificity = len(clean_controls) / len(controls)
        assert specificity >= 0.80, f"Expected Control Specificity >= 80%, got {specificity:.2%}"

        # Verify Gate 4 Governance specificity is >= 75% (actual 78.19%, 595/761)
        gate4_cases = [r for r in cases if r.get("retraction_tier") == "GATE_4_GOVERNANCE"]
        assert len(gate4_cases) == 761
        clean_gate4 = [r for r in gate4_cases if r.get("blind_verdict") == "CLEAN"]
        gate4_spec = len(clean_gate4) / len(gate4_cases)
        assert gate4_spec >= 0.75, f"Expected Gate 4 governance specificity >= 75%, got {gate4_spec:.2%}"

        # Verify Gate 3.5 Image fraud specificity is >= 75% (actual 79.17%, 76/96)
        gate35_cases = [r for r in cases if r.get("retraction_tier") == "GATE_35_IMAGES"]
        assert len(gate35_cases) == 96
        clean_gate35 = [r for r in gate35_cases if r.get("blind_verdict") == "CLEAN"]
        gate35_spec = len(clean_gate35) / len(gate35_cases)
        assert gate35_spec >= 0.75, f"Expected Gate 3.5 specificity >= 75%, got {gate35_spec:.2%}"


class TestBlindWave2LedgerIntegrity:
    """Verifies empirical integrity of Wave 2 (2,000 studies) and zero-intersection with Wave 1."""

    def test_wave2_cohort_manifest_and_zero_intersection(self):
        """Verifies Wave 2 manifest exists, has 2,000 studies, and has strictly zero overlap with Wave 1."""
        w1_path = os.path.join("data", "cohort_2000_manifest.json")
        w2_path = os.path.join("data", "cohort_wave2_manifest.json")
        assert os.path.exists(w1_path), f"Wave 1 manifest missing: {w1_path}"
        assert os.path.exists(w2_path), f"Wave 2 manifest missing: {w2_path}"

        with open(w1_path, "r", encoding="utf-8") as f:
            w1 = json.load(f)
        with open(w2_path, "r", encoding="utf-8") as f:
            w2 = json.load(f)

        assert len(w1) == 2000, f"Expected 2000 studies in Wave 1, got {len(w1)}"
        assert len(w2) == 2000, f"Expected 2000 studies in Wave 2, got {len(w2)}"

        w1_pmcids = {s.get("pmcid") for s in w1 if s.get("pmcid")}
        w1_dois = {s.get("doi", "").strip().lower() for s in w1 if s.get("doi")}
        w2_pmcids = {s.get("pmcid") for s in w2 if s.get("pmcid")}
        w2_dois = {s.get("doi", "").strip().lower() for s in w2 if s.get("doi")}

        inter_pmcids = w1_pmcids.intersection(w2_pmcids)
        inter_dois = w1_dois.intersection(w2_dois)
        assert len(inter_pmcids) == 0, f"Detected {len(inter_pmcids)} overlapping PMCIDs between Wave 1 and Wave 2!"
        assert len(inter_dois) == 0, f"Detected {len(inter_dois)} overlapping DOIs between Wave 1 and Wave 2!"

    def test_wave2_ledger_metrics(self):
        """Verifies Wave 2 empirical ledger has 2,000 studies and replicates 5-gate performance."""
        ledger_path = os.path.join("data", "extracted_tables", "real_wave2_fulltext_blind_ledger.jsonl")
        assert os.path.exists(ledger_path), f"Wave 2 ledger missing: {ledger_path}"

        records = []
        with open(ledger_path, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    records.append(json.loads(line))

        assert len(records) == 2000, f"Expected 2000 studies in Wave 2 ledger, got {len(records)}"
        cases = [r for r in records if r.get("cohort") == "CASE"]
        controls = [r for r in records if r.get("cohort") == "CONTROL"]
        assert len(cases) == 1000
        assert len(controls) == 1000

        # Gate 3 Math Sensitivity: 36 / 124 = 29.03%
        g3 = [c for c in cases if c.get("retraction_tier") == "GATE_3_MATH_DATA"]
        assert len(g3) == 124
        g3_tp = sum(1 for c in g3 if c.get("blind_verdict") == "FLAGGED_FORENSIC_ANOMALY")
        g3_sens = g3_tp / len(g3)
        assert g3_sens >= 0.20, f"Expected Gate 3 sensitivity >= 20%, got {g3_sens:.2%}"

        # Gate 4 Governance Specificity: 549 / 678 = 80.97%
        g4 = [c for c in cases if c.get("retraction_tier") == "GATE_4_GOVERNANCE"]
        assert len(g4) == 678
        g4_clean = sum(1 for c in g4 if c.get("blind_verdict") == "CLEAN")
        g4_spec = g4_clean / len(g4)
        assert g4_spec >= 0.75, f"Expected Gate 4 specificity >= 75%, got {g4_spec:.2%}"

        # Control Specificity: 702 / 1000 = 70.20%
        ctrl_clean = sum(1 for c in controls if c.get("blind_verdict") == "CLEAN")
        ctrl_spec = ctrl_clean / len(controls)
        assert ctrl_spec >= 0.65, f"Expected Control specificity >= 65%, got {ctrl_spec:.2%}"

    def test_combined_4000_ledger_metrics(self):
        """Verifies pooled 4,000-study dataset has 0 mutual duplicates and stable meta-analytic metrics."""
        comb_path = os.path.join("docs", "data", "blind_combined_4000_ledger.json")
        assert os.path.exists(comb_path), f"Combined 4000 dataset missing: {comb_path}"

        with open(comb_path, "r", encoding="utf-8") as f:
            records = json.load(f)

        assert len(records) == 4000, f"Expected 4000 studies in pooled dataset, got {len(records)}"
        cases = [r for r in records if r.get("cohort") == "CASE"]
        controls = [r for r in records if r.get("cohort") == "CONTROL"]
        assert len(cases) == 2000
        assert len(controls) == 2000

        # Pooled Gate 3 Sensitivity: 58 / 212 = 27.36%
        g3_4k = [c for c in cases if c.get("retraction_tier") == "GATE_3_MATH_DATA"]
        assert len(g3_4k) == 212
        g3_tp_4k = sum(1 for c in g3_4k if c.get("blind_verdict") == "FLAGGED_FORENSIC_ANOMALY")
        assert (g3_tp_4k / len(g3_4k)) >= 0.20

        # Pooled Gate 4 Specificity: 1,144 / 1,439 = 79.50%
        g4_4k = [c for c in cases if c.get("retraction_tier") == "GATE_4_GOVERNANCE"]
        assert len(g4_4k) == 1439
        g4_clean_4k = sum(1 for c in g4_4k if c.get("blind_verdict") == "CLEAN")
        assert (g4_clean_4k / len(g4_4k)) >= 0.75

        # Pooled Control Specificity: 1,503 / 2,000 = 75.15%
        ctrl_clean_4k = sum(1 for c in controls if c.get("blind_verdict") == "CLEAN")
        assert (ctrl_clean_4k / len(controls)) >= 0.70


class TestAdvancedGate3Sieves:
    """Tests the 4 Advanced Gate 3 Deterministic Optimization Engines."""

    def test_regression_triangulation_consistent(self):
        """Verifies consistent Wald Z and p-value for valid Odds Ratio table row."""
        # OR = 1.80, 95% CI: [1.25, 2.59], true Wald p = 0.00157, reported p = 0.0016
        res = audit_regression_triangulation(
            estimate=1.80, lower_ci=1.25, upper_ci=2.59, reported_p=0.0016, is_log_scale=True
        )
        assert res["verdict"] == "CONSISTENT"
        assert res["decision_error"] is False
        assert res["p_discrepancy"] < 0.01

    def test_regression_triangulation_decision_error(self):
        """Flags primary decision error where reported p < 0.05 but 95% CI crosses 1.0."""
        # OR = 1.35, 95% CI: [0.92, 1.98], claimed p = 0.02
        res = audit_regression_triangulation(
            estimate=1.35, lower_ci=0.92, upper_ci=1.98, reported_p=0.02, is_log_scale=True
        )
        assert res["verdict"] == "REGRESSION_DECISION_ERROR"
        assert res["decision_error"] is True
        assert res["crosses_null"] is True

    def test_ai_confusion_matrix_impossible_triad(self):
        """Detects impossible metric triads where claimed accuracy is outside [Sens, Spec] bounds."""
        # Claimed Acc = 96%, but Sensitivity = 82% and Specificity = 85%
        res = verify_ai_confusion_matrix_triangulation(
            accuracy=96.0, sensitivity=82.0, specificity=85.0
        )
        assert res["verdict"] == "IMPOSSIBLE_AI_METRIC_TRIAD"
        assert len(res["anomalies"]) > 0

    def test_ai_confusion_matrix_consistent(self):
        """Passes coherent model metrics that satisfy Acc = Sens * P + Spec * (1 - P)."""
        # Sens = 90%, Spec = 80%, Prevalence = 50% -> Expected Acc = 85%, Claimed Acc = 85%
        res = verify_ai_confusion_matrix_triangulation(
            accuracy=85.0, sensitivity=90.0, specificity=80.0, prevalence=50.0
        )
        assert res["verdict"] == "CONSISTENT"
        assert len(res["anomalies"]) == 0

    def test_cross_table_marginal_count_mismatch(self):
        """Flags marginal percentage rounding discrepancies where reported count != round(pct * N)."""
        # Reported count = 45, percentage = 18.0%, N = 100 -> Expected = 18, mismatch = 27
        res = audit_cross_table_marginal_conservation(count=45, percentage=18.0, n_total=100)
        assert res["verdict"] == "MARGINAL_COUNT_ANOMALY"
        assert "MARGINAL_PERCENTAGE_MISMATCH" in res["anomalies"][0]

    def test_cross_table_subgroup_overflow(self):
        """Flags subgroup sample size exceeding parent baseline cohort."""
        # Subgroup N = 150, Baseline N = 100
        res = audit_cross_table_marginal_conservation(
            count=30, percentage=20.0, n_total=150, subgroup_name="Smokers", parent_n=100
        )
        assert res["verdict"] == "MARGINAL_COUNT_ANOMALY"
        assert "SUBGROUP_PARENT_OVERFLOW" in res["anomalies"][0]

    def test_physiological_variance_compression(self):
        """Flags extreme artificial variance compression (SD < 20% of clinical reference SD)."""
        # SBP reported SD = 2.0 mm Hg, reference min SD = 15.0 mm Hg
        res = audit_physiological_variance_bounds(
            variable_name="Systolic_BP", mean=125.0, sd=2.0, physiological_min_sd=15.0
        )
        assert res["verdict"] == "FLAGGED_PHYSIOLOGICAL_ANOMALY"
        assert any("EXTREME_VARIANCE_COMPRESSION" in a for a in res["anomalies"])

    def test_physiological_boundary_violation(self):
        """Flags non-negative biomarker boundary violation where Mean - 2*SD < 0."""
        # Troponin Mean = 10.0, SD = 8.0 -> 10 - 2*8 = -6 < 0 (10.6% negative values implied)
        res = audit_physiological_variance_bounds(
            variable_name="Serum_Troponin", mean=10.0, sd=8.0, is_strictly_positive=True
        )
        assert res["verdict"] == "FLAGGED_PHYSIOLOGICAL_ANOMALY"
        assert any("SKEWNESS_BOUNDARY_VIOLATION" in a for a in res["anomalies"])


class TestBlindWave3LedgerIntegrity:
    """Verifies empirical integrity of Wave 3 (2,000 studies) and dual zero-intersection with Waves 1 & 2."""

    def test_wave3_cohort_manifest_and_zero_intersection(self):
        """Verifies Wave 3 manifest exists, has 2,000 studies, and has strictly zero overlap with Waves 1 and 2."""
        w1_path = os.path.join("data", "cohort_2000_manifest.json")
        w2_path = os.path.join("data", "cohort_wave2_manifest.json")
        w3_path = os.path.join("data", "cohort_wave3_manifest.json")
        assert os.path.exists(w1_path), f"Wave 1 manifest missing: {w1_path}"
        assert os.path.exists(w2_path), f"Wave 2 manifest missing: {w2_path}"
        assert os.path.exists(w3_path), f"Wave 3 manifest missing: {w3_path}"

        with open(w1_path, "r", encoding="utf-8") as f:
            w1 = json.load(f)
        with open(w2_path, "r", encoding="utf-8") as f:
            w2 = json.load(f)
        with open(w3_path, "r", encoding="utf-8") as f:
            w3 = json.load(f)

        assert len(w1) == 2000
        assert len(w2) == 2000
        assert len(w3) == 2000

        w1_pmcids = {s.get("pmcid") for s in w1 if s.get("pmcid")}
        w1_dois = {s.get("doi", "").strip().lower() for s in w1 if s.get("doi")}
        w2_pmcids = {s.get("pmcid") for s in w2 if s.get("pmcid")}
        w2_dois = {s.get("doi", "").strip().lower() for s in w2 if s.get("doi")}
        w3_pmcids = {s.get("pmcid") for s in w3 if s.get("pmcid")}
        w3_dois = {s.get("doi", "").strip().lower() for s in w3 if s.get("doi")}

        assert len(w1_pmcids.intersection(w3_pmcids)) == 0, "Intersection between Wave 1 and Wave 3 PMCIDs!"
        assert len(w2_pmcids.intersection(w3_pmcids)) == 0, "Intersection between Wave 2 and Wave 3 PMCIDs!"
        assert len(w1_dois.intersection(w3_dois)) == 0, "Intersection between Wave 1 and Wave 3 DOIs!"
        assert len(w2_dois.intersection(w3_dois)) == 0, "Intersection between Wave 2 and Wave 3 DOIs!"

    def test_wave3_ledger_metrics(self):
        """Verifies Wave 3 empirical ledger has 2,000 studies and replicates upgraded 5-gate performance."""
        ledger_path = os.path.join("data", "extracted_tables", "real_wave3_fulltext_blind_ledger.jsonl")
        assert os.path.exists(ledger_path), f"Wave 3 ledger missing: {ledger_path}"

        records = []
        with open(ledger_path, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    records.append(json.loads(line))

        assert len(records) == 2000, f"Expected 2000 studies in Wave 3 ledger, got {len(records)}"
        cases = [r for r in records if r.get("cohort") == "CASE"]
        controls = [r for r in records if r.get("cohort") == "CONTROL"]
        assert len(cases) == 1000
        assert len(controls) == 1000

        # Gate 3 Math Sensitivity: 160 / 516 = 31.01%
        g3 = [c for c in cases if c.get("retraction_tier") == "GATE_3_MATH_DATA"]
        assert len(g3) == 516
        g3_tp = sum(1 for c in g3 if c.get("math_gate_triggered"))
        g3_sens = g3_tp / len(g3)
        assert g3_sens >= 0.25, f"Expected Gate 3 sensitivity >= 25%, got {g3_sens:.2%}"

        # Gate 4 Governance Specificity: 213 / 266 = 80.08%
        g4 = [c for c in cases if c.get("retraction_tier") == "GATE_4_GOVERNANCE"]
        assert len(g4) == 266
        g4_clean = sum(1 for c in g4 if not c.get("math_gate_triggered"))
        g4_spec = g4_clean / len(g4)
        assert g4_spec >= 0.75, f"Expected Gate 4 specificity >= 75%, got {g4_spec:.2%}"

        # Control Specificity: 682 / 1000 = 68.20%
        ctrl_clean = sum(1 for c in controls if c.get("blind_verdict") == "CLEAN")
        ctrl_spec = ctrl_clean / len(controls)
        assert ctrl_spec >= 0.65, f"Expected Control specificity >= 65%, got {ctrl_spec:.2%}"

    def test_combined_6000_ledger_metrics(self):
        """Verifies pooled 6,000-study dataset has 0 mutual duplicates and stable meta-analytic metrics."""
        comb_path = os.path.join("docs", "data", "blind_combined_6000_ledger.json")
        assert os.path.exists(comb_path), f"Combined 6000 dataset missing: {comb_path}"

        with open(comb_path, "r", encoding="utf-8") as f:
            records = json.load(f)

        assert len(records) == 6000, f"Expected 6000 studies in pooled dataset, got {len(records)}"
        cases = [r for r in records if r.get("cohort") == "CASE"]
        controls = [r for r in records if r.get("cohort") == "CONTROL"]
        assert len(cases) == 3000
        assert len(controls) == 3000

        # Pooled Gate 3 Sensitivity: 218 / 728 = 29.95%
        g3_6k = [c for c in cases if c.get("retraction_tier") == "GATE_3_MATH_DATA"]
        assert len(g3_6k) == 728
        g3_tp_6k = sum(1 for c in g3_6k if c.get("math_gate_triggered"))
        assert (g3_tp_6k / len(g3_6k)) >= 0.25

        # Pooled Gate 4 Specificity: 1,357 / 1,705 = 79.59%
        g4_6k = [c for c in cases if c.get("retraction_tier") == "GATE_4_GOVERNANCE"]
        assert len(g4_6k) == 1705
        g4_clean_6k = sum(1 for c in g4_6k if not c.get("math_gate_triggered"))
        assert (g4_clean_6k / len(g4_6k)) >= 0.75

        # Pooled Control Specificity: 2,185 / 3,000 = 72.83%
        ctrl_clean_6k = sum(1 for c in controls if c.get("blind_verdict") == "CLEAN")
        assert (ctrl_clean_6k / len(controls)) >= 0.70




