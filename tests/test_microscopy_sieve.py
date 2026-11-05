import os
import sys
import tempfile
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.vision.splicing_fixture_generator import (
    generate_microscopy_flipped_crop_figure,
    generate_clean_control_figure
)
from src.vision.microscopy_sieve import audit_microscopy_splicing


def test_audit_microscopy_flipped_crop_duplication():
    with tempfile.TemporaryDirectory() as tmpdir:
        out_path = os.path.join(tmpdir, "microscopy_flipped.png")
        generate_microscopy_flipped_crop_figure(out_path)

        report = audit_microscopy_splicing(out_path)

        assert report["verdict"] == "FLAGGED_MICROSCOPY_ANOMALY"
        assert len(report["discrepancies"]) >= 1
        anom = report["discrepancies"][0]
        assert anom["type"] == "TRANSFORMED_MICROGRAPH_DUPLICATION"
        assert anom["inlier_matches"] >= 10
        assert anom["panel_a"] in ["Panel_A", "Panel_1"]
        assert anom["panel_b"] in ["Panel_B", "Panel_2"]


def test_audit_microscopy_clean_control():
    with tempfile.TemporaryDirectory() as tmpdir:
        out_path = os.path.join(tmpdir, "clean_control.png")
        generate_clean_control_figure(out_path)

        report = audit_microscopy_splicing(out_path)

        assert report["verdict"] == "CLEAN"
        assert len(report["discrepancies"]) == 0
