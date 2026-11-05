import os
import sys
import tempfile
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.vision.chart_fixture_generator import (
    generate_grim_fail_bar_chart,
    generate_significance_inversion_chart,
    generate_zero_bound_truncation_chart,
    generate_clean_control_chart
)
from mcp_servers.forensic_chart_mcp import audit_chart_figure


def test_end_to_end_grim_failure():
    """Validates end-to-end detection of impossible granular discrete averages in bar charts."""
    with tempfile.TemporaryDirectory() as tmpdir:
        chart_path = os.path.join(tmpdir, "grim_fail.png")
        overlay_path = os.path.join(tmpdir, "grim_fail_annotated.png")
        generate_grim_fail_bar_chart(chart_path)

        result = audit_chart_figure(
            image_path=chart_path,
            caption="Severity Score (N=15)",
            output_overlay_path=overlay_path
        )

        assert result["verdict"] == "FLAGGED_FORENSIC_ANOMALY"
        assert result["discrepancies_count"] >= 1
        assert any(d["type"] == "GRIM_INCONSISTENCY" for d in result["discrepancies"])
        assert os.path.exists(overlay_path)
        assert os.path.getsize(overlay_path) > 0


def test_end_to_end_significance_inversion():
    """Validates Welch's t-test recalculation catching non-significant bars with claimed p < 0.001."""
    with tempfile.TemporaryDirectory() as tmpdir:
        chart_path = os.path.join(tmpdir, "sig_inv.png")
        overlay_path = os.path.join(tmpdir, "sig_inv_annotated.png")
        generate_significance_inversion_chart(chart_path)

        result = audit_chart_figure(
            image_path=chart_path,
            caption="Response to Compound X (N=10)",
            output_overlay_path=overlay_path
        )

        assert result["verdict"] == "FLAGGED_FORENSIC_ANOMALY"
        assert result["discrepancies_count"] >= 1
        assert any(d["type"] == "SIGNIFICANCE_INVERSION" for d in result["discrepancies"])
        assert os.path.exists(overlay_path)
        assert os.path.getsize(overlay_path) > 0


def test_end_to_end_zero_bound_truncation():
    """Validates lower tail Gaussian probability detection for impossible negative values."""
    with tempfile.TemporaryDirectory() as tmpdir:
        chart_path = os.path.join(tmpdir, "trunc.png")
        overlay_path = os.path.join(tmpdir, "trunc_annotated.png")
        generate_zero_bound_truncation_chart(chart_path)

        result = audit_chart_figure(
            image_path=chart_path,
            caption="Serum Biomarker Concentration (N=20)",
            output_overlay_path=overlay_path
        )

        assert result["verdict"] == "FLAGGED_FORENSIC_ANOMALY"
        assert result["discrepancies_count"] >= 1
        assert any(d["type"] == "ZERO_BOUND_TRUNCATION" for d in result["discrepancies"])
        assert os.path.exists(overlay_path)
        assert os.path.getsize(overlay_path) > 0


def test_end_to_end_clean_control():
    """Validates that authentic, statistically consistent figures pass cleanly with zero false alarms."""
    with tempfile.TemporaryDirectory() as tmpdir:
        chart_path = os.path.join(tmpdir, "clean.png")
        overlay_path = os.path.join(tmpdir, "clean_annotated.png")
        generate_clean_control_chart(chart_path)

        result = audit_chart_figure(
            image_path=chart_path,
            caption="Control vs High Dose (N=10)",
            output_overlay_path=overlay_path
        )

        assert result["verdict"] == "CLEAN"
        assert result["discrepancies_count"] == 0
        assert len(result["discrepancies"]) == 0
        assert os.path.exists(overlay_path)
        assert os.path.getsize(overlay_path) > 0
