"""
Tests for Forensic Chart Statistical Sieves (Task 3).
Verifies detection of:
- Significance Inversion (claimed p < 0.05 / p < 0.001 vs actual Welch t-test p > 0.05)
- Zero-Bound Truncation (Mean - 2*SD < 0 on non-negative assay)
- Modular Table Math Inconsistencies (GRIM / SPRITE via FastMCP bridge)
- Full aggregated audit verdict
"""

import os
import sys
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.vision.chart_models import (
    AxisCalibration,
    ChartDataPoint,
    PValueBracket,
    ExtractedChartData
)
from src.vision.forensic_chart_sieves import (
    audit_p_value_brackets,
    audit_zero_bound_truncations,
    audit_modular_table_math,
    audit_chart_statistics
)


def test_audit_p_value_brackets_catches_inversion():
    # Two groups with almost identical means and high variance (p = 0.53)
    p1 = ChartDataPoint(group_name="Vehicle", mean=5.0, dispersion_val=2.0, dispersion_type="SD", n_sample=10)
    p2 = ChartDataPoint(group_name="Compound X", mean=5.6, dispersion_val=2.2, dispersion_type="SD", n_sample=10)
    
    # Author draws bracket claiming *** (p < 0.001)
    bracket = PValueBracket(group_a="Vehicle", group_b="Compound X", claimed_text="***", claimed_p_threshold=0.001)

    chart = ExtractedChartData(
        figure_id="FIG_INVERSION",
        chart_type="BAR_WITH_ERROR_BARS",
        y_axis=AxisCalibration(label="Activity (U/L)", min_val=0, max_val=10),
        series=[p1, p2],
        p_value_brackets=[bracket]
    )

    bracket_results = audit_p_value_brackets(chart)
    assert len(bracket_results) == 1
    res = bracket_results[0]
    assert res["status"] == "FAIL"
    assert res["discrepancy_type"] == "SIGNIFICANCE_INVERSION"
    assert res["computed_welch_p"] > 0.40
    assert res["claimed_p_threshold"] == 0.001


def test_audit_p_value_brackets_passes_clean_control():
    # Two groups with large separation (p < 0.0001)
    p1 = ChartDataPoint(group_name="WT", mean=2.0, dispersion_val=0.4, dispersion_type="SD", n_sample=10)
    p2 = ChartDataPoint(group_name="KO", mean=4.5, dispersion_val=0.5, dispersion_type="SD", n_sample=10)
    
    # Bracket claims *** (matches reality)
    bracket = PValueBracket(group_a="WT", group_b="KO", claimed_text="***", claimed_p_threshold=0.001)

    chart = ExtractedChartData(
        figure_id="FIG_CLEAN",
        chart_type="BAR_WITH_ERROR_BARS",
        y_axis=AxisCalibration(label="Fold Change", min_val=0, max_val=6),
        series=[p1, p2],
        p_value_brackets=[bracket]
    )

    bracket_results = audit_p_value_brackets(chart)
    assert len(bracket_results) == 1
    assert bracket_results[0]["status"] == "PASS"


def test_audit_zero_bound_truncation():
    # Mean = 2.0, SD = 3.0 on non-negative assay -> Mean - 2*SD = -4.0 < 0
    p1 = ChartDataPoint(group_name="Cardiac Troponin", mean=2.0, dispersion_val=3.0, dispersion_type="SD", n_sample=12)

    chart = ExtractedChartData(
        figure_id="FIG_TRUNCATION",
        chart_type="BAR_WITH_ERROR_BARS",
        y_axis=AxisCalibration(label="Troponin T (ng/mL)", min_val=0.0, max_val=6.0),
        series=[p1]
    )

    trunc_results = audit_zero_bound_truncations(chart)
    assert len(trunc_results) == 1
    assert trunc_results[0]["discrepancy_type"] == "ZERO_BOUND_TRUNCATION"
    assert trunc_results[0]["status"] == "FAIL"
    assert trunc_results[0]["lower_2sd_bound"] < 0.0


def test_audit_modular_table_math_catches_grim():
    # Discrete scale 1-5, Mean = 1.42 with N = 15 -> 1.42 * 15 = 21.3 -> GRIM fail!
    p1 = ChartDataPoint(group_name="Discrete Severity", mean=1.42, dispersion_val=0.40, dispersion_type="SD", n_sample=15, is_discrete=True)

    chart = ExtractedChartData(
        figure_id="FIG_GRIM",
        chart_type="BAR_WITH_ERROR_BARS",
        y_axis=AxisCalibration(label="Score (1-5)", min_val=0, max_val=5),
        series=[p1]
    )

    math_results = audit_modular_table_math(chart)
    assert len(math_results) >= 1
    grim_errors = [r for r in math_results if r.get("sieve") == "GRIM"]
    assert len(grim_errors) == 1
    assert grim_errors[0]["status"] == "FAIL"


def test_audit_chart_statistics_aggregated_verdict():
    # Clean chart should pass overall
    p1 = ChartDataPoint(group_name="WT", mean=2.0, dispersion_val=0.4, dispersion_type="SD", n_sample=10)
    p2 = ChartDataPoint(group_name="KO", mean=4.5, dispersion_val=0.5, dispersion_type="SD", n_sample=10)
    bracket = PValueBracket(group_a="WT", group_b="KO", claimed_text="***", claimed_p_threshold=0.001)
    
    clean_chart = ExtractedChartData(
        figure_id="FIG_CLEAN_ALL",
        chart_type="BAR_WITH_ERROR_BARS",
        y_axis=AxisCalibration(label="Fold Change", min_val=0, max_val=6),
        series=[p1, p2],
        p_value_brackets=[bracket]
    )

    report = audit_chart_statistics(clean_chart)
    assert report["verdict"] == "CLEAN"
    assert len(report["discrepancies"]) == 0

    # Inversion chart should fail overall
    inv_p1 = ChartDataPoint(group_name="Vehicle", mean=5.0, dispersion_val=2.0, dispersion_type="SD", n_sample=10)
    inv_p2 = ChartDataPoint(group_name="Drug", mean=5.6, dispersion_val=2.2, dispersion_type="SD", n_sample=10)
    inv_bracket = PValueBracket(group_a="Vehicle", group_b="Drug", claimed_text="***", claimed_p_threshold=0.001)
    
    inv_chart = ExtractedChartData(
        figure_id="FIG_INV_ALL",
        chart_type="BAR_WITH_ERROR_BARS",
        y_axis=AxisCalibration(label="Activity", min_val=0, max_val=10),
        series=[inv_p1, inv_p2],
        p_value_brackets=[inv_bracket]
    )

    report_inv = audit_chart_statistics(inv_chart)
    assert report_inv["verdict"] == "FLAGGED_FORENSIC_ANOMALY"
    assert len(report_inv["discrepancies"]) >= 1
    assert any("SIGNIFICANCE_INVERSION" in d["type"] for d in report_inv["discrepancies"])
