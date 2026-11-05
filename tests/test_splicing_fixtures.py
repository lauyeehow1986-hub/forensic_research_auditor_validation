import os
import sys
import tempfile
import cv2
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.vision.splicing_fixture_generator import (
    generate_western_blot_cloned_band_figure,
    generate_western_blot_spliced_lane_figure,
    generate_microscopy_flipped_crop_figure,
    generate_clean_control_figure
)


def test_generate_western_blot_cloned_band_fixture():
    with tempfile.TemporaryDirectory() as tmpdir:
        out_path = os.path.join(tmpdir, "wb_cloned.png")
        meta = generate_western_blot_cloned_band_figure(out_path)

        assert os.path.exists(out_path)
        assert os.path.getsize(out_path) > 0
        img = cv2.imread(out_path)
        assert img is not None
        assert img.shape[0] > 100 and img.shape[1] > 100
        assert meta["target_anomaly"] == "CLONED_BAND"
        assert len(meta["cloned_lanes"]) == 2


def test_generate_western_blot_spliced_lane_fixture():
    with tempfile.TemporaryDirectory() as tmpdir:
        out_path = os.path.join(tmpdir, "wb_spliced.png")
        meta = generate_western_blot_spliced_lane_figure(out_path)

        assert os.path.exists(out_path)
        assert os.path.getsize(out_path) > 0
        img = cv2.imread(out_path)
        assert img is not None
        assert meta["target_anomaly"] == "SPLICED_LANE_BORDER"
        assert "splice_x" in meta


def test_generate_microscopy_flipped_crop_fixture():
    with tempfile.TemporaryDirectory() as tmpdir:
        out_path = os.path.join(tmpdir, "microscopy_flipped.png")
        meta = generate_microscopy_flipped_crop_figure(out_path)

        assert os.path.exists(out_path)
        assert os.path.getsize(out_path) > 0
        img = cv2.imread(out_path)
        assert img is not None
        assert meta["target_anomaly"] == "TRANSFORMED_MICROGRAPH_DUPLICATION"
        assert meta["transformation"] == "ROTATION_180"


def test_generate_clean_control_fixture():
    with tempfile.TemporaryDirectory() as tmpdir:
        out_path = os.path.join(tmpdir, "clean_control.png")
        meta = generate_clean_control_figure(out_path)

        assert os.path.exists(out_path)
        assert os.path.getsize(out_path) > 0
        img = cv2.imread(out_path)
        assert img is not None
        assert meta["target_anomaly"] == "NONE"
        assert meta["is_clean"] is True
