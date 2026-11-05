import os
import sys
import tempfile
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.vision.splicing_fixture_generator import (
    generate_western_blot_cloned_band_figure,
    generate_western_blot_spliced_lane_figure,
    generate_microscopy_flipped_crop_figure,
    generate_clean_control_figure
)
from mcp_servers.forensic_chart_mcp import audit_figure_splicing


def test_e2e_western_blot_cloned_band():
    with tempfile.TemporaryDirectory() as tmpdir:
        img_p = os.path.join(tmpdir, "wb_cloned.png")
        generate_western_blot_cloned_band_figure(img_p)
        overlay_p = os.path.join(tmpdir, "wb_cloned_annotated.png")

        result = audit_figure_splicing(img_p, output_overlay_path=overlay_p)

        assert result["verdict"] == "FLAGGED_SPLICING_ANOMALY"
        assert result["discrepancies_count"] >= 1
        assert any(d["type"] == "CLONED_BAND" for d in result["discrepancies"])
        assert os.path.exists(overlay_p)
        assert os.path.getsize(overlay_p) > 0


def test_e2e_western_blot_spliced_lane():
    with tempfile.TemporaryDirectory() as tmpdir:
        img_p = os.path.join(tmpdir, "wb_spliced.png")
        generate_western_blot_spliced_lane_figure(img_p)
        overlay_p = os.path.join(tmpdir, "wb_spliced_annotated.png")

        result = audit_figure_splicing(img_p, output_overlay_path=overlay_p)

        assert result["verdict"] == "FLAGGED_SPLICING_ANOMALY"
        assert any(d["type"] == "SPLICED_LANE_BORDER" for d in result["discrepancies"])
        assert os.path.exists(overlay_p)


def test_e2e_microscopy_flipped_crop():
    with tempfile.TemporaryDirectory() as tmpdir:
        img_p = os.path.join(tmpdir, "micro_flipped.png")
        generate_microscopy_flipped_crop_figure(img_p)
        overlay_p = os.path.join(tmpdir, "micro_flipped_annotated.png")

        result = audit_figure_splicing(img_p, output_overlay_path=overlay_p)

        assert result["verdict"] == "FLAGGED_SPLICING_ANOMALY"
        assert any(d["type"] == "TRANSFORMED_MICROGRAPH_DUPLICATION" for d in result["discrepancies"])
        assert os.path.exists(overlay_p)


def test_e2e_clean_control():
    with tempfile.TemporaryDirectory() as tmpdir:
        img_p = os.path.join(tmpdir, "clean.png")
        generate_clean_control_figure(img_p)
        overlay_p = os.path.join(tmpdir, "clean_annotated.png")

        result = audit_figure_splicing(img_p, output_overlay_path=overlay_p)

        assert result["verdict"] == "CLEAN"
        assert result["discrepancies_count"] == 0
        assert os.path.exists(overlay_p)
