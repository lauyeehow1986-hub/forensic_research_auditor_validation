import os
import sys
import tempfile
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.vision.chart_fixture_generator import (
    generate_grim_fail_bar_chart,
    generate_clean_control_chart,
    generate_significance_inversion_chart,
    generate_zero_bound_truncation_chart
)


def test_audit_chart_figure_grim_fail():
    from mcp_servers.forensic_chart_mcp import audit_chart_figure

    with tempfile.TemporaryDirectory() as tmpdir:
        chart_path = os.path.join(tmpdir, "grim_fail.png")
        generate_grim_fail_bar_chart(chart_path)

        overlay_out = os.path.join(tmpdir, "overlay.png")
        result = audit_chart_figure(
            image_path=chart_path,
            caption="Response to Compound X (N=15)",
            output_overlay_path=overlay_out
        )

        assert isinstance(result, dict)
        assert result["verdict"] == "FLAGGED_FORENSIC_ANOMALY"
        assert len(result["discrepancies"]) > 0
        assert any("GRIM" in str(d) for d in result["discrepancies"])
        assert os.path.exists(overlay_out)
        assert result["overlay_path"] == overlay_out
        assert len(result["series"]) >= 2


def test_audit_chart_figure_clean_control():
    from mcp_servers.forensic_chart_mcp import audit_chart_figure

    with tempfile.TemporaryDirectory() as tmpdir:
        chart_path = os.path.join(tmpdir, "clean.png")
        generate_clean_control_chart(chart_path)

        overlay_out = os.path.join(tmpdir, "clean_overlay.png")
        result = audit_chart_figure(
            image_path=chart_path,
            caption="Control vs High Dose (N=10)",
            output_overlay_path=overlay_out
        )

        assert isinstance(result, dict)
        assert result["verdict"] == "CLEAN"
        assert len(result["discrepancies"]) == 0
        assert os.path.exists(overlay_out)
        assert result["overlay_path"] == overlay_out
        assert len(result["series"]) >= 2


def test_transcribe_and_pipe_to_table_math():
    from mcp_servers.forensic_chart_mcp import transcribe_and_pipe_to_table_math

    with tempfile.TemporaryDirectory() as tmpdir:
        chart_path = os.path.join(tmpdir, "grim_fail.png")
        generate_grim_fail_bar_chart(chart_path)

        result = transcribe_and_pipe_to_table_math(
            image_path=chart_path,
            caption="Severity Score (N=15)"
        )

        assert "table_rows" in result
        assert len(result["table_rows"]) >= 2
        assert "math_audits" in result
        # Check that grim failure was detected on Control (mean=1.42, N=15)
        control_audit = next((a for a in result["math_audits"] if a["group_name"] == "Control"), None)
        assert control_audit is not None
        assert control_audit["grim_result"]["grim_pass"] is False
        assert control_audit["grim_result"]["verdict"] == "GRIM_IMPOSSIBLE"

