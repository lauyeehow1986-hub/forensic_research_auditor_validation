import os
import sys
import tempfile
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.vision.splicing_fixture_generator import (
    generate_western_blot_cloned_band_figure,
    generate_western_blot_spliced_lane_figure
)
from src.vision.western_blot_sieve import audit_western_blot_splicing


def test_audit_western_blot_cloned_bands():
    with tempfile.TemporaryDirectory() as tmpdir:
        out_path = os.path.join(tmpdir, "wb_cloned.png")
        generate_western_blot_cloned_band_figure(out_path)

        report = audit_western_blot_splicing(out_path)

        assert report["verdict"] == "FLAGGED_WESTERN_BLOT_ANOMALY"
        assert len(report["discrepancies"]) >= 1
        cloned_anomalies = [d for d in report["discrepancies"] if d["type"] == "CLONED_BAND"]
        assert len(cloned_anomalies) >= 1
        anomaly = cloned_anomalies[0]
        assert anomaly["ncc_score"] >= 0.95
        assert anomaly["lane_a"] == 0 or anomaly["lane_b"] == 0
        assert anomaly["lane_a"] == 2 or anomaly["lane_b"] == 2


def test_audit_western_blot_spliced_lane_border():
    with tempfile.TemporaryDirectory() as tmpdir:
        out_path = os.path.join(tmpdir, "wb_spliced.png")
        generate_western_blot_spliced_lane_figure(out_path)

        report = audit_western_blot_splicing(out_path)

        assert report["verdict"] == "FLAGGED_WESTERN_BLOT_ANOMALY"
        assert any(d["type"] == "SPLICED_LANE_BORDER" for d in report["discrepancies"])
