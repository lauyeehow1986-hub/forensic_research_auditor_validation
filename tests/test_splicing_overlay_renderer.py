import os
import sys
import tempfile
import cv2
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.vision.splicing_fixture_generator import (
    generate_western_blot_cloned_band_figure,
    generate_microscopy_flipped_crop_figure,
    generate_clean_control_figure
)
from src.vision.western_blot_sieve import audit_western_blot_splicing
from src.vision.microscopy_sieve import audit_microscopy_splicing
from src.vision.splicing_overlay_renderer import render_splicing_visual_overlay


def test_render_western_blot_anomaly_overlay():
    with tempfile.TemporaryDirectory() as tmpdir:
        img_path = os.path.join(tmpdir, "wb.png")
        generate_western_blot_cloned_band_figure(img_path)
        report = audit_western_blot_splicing(img_path)

        out_path = os.path.join(tmpdir, "wb_annotated.png")
        res = render_splicing_visual_overlay(img_path, report, out_path)

        assert os.path.exists(res)
        assert os.path.getsize(res) > 0
        img = cv2.imread(res)
        assert img is not None
        # Should have banner height added
        orig = cv2.imread(img_path)
        assert img.shape[0] > orig.shape[0]


def test_render_microscopy_anomaly_overlay():
    with tempfile.TemporaryDirectory() as tmpdir:
        img_path = os.path.join(tmpdir, "micro.png")
        generate_microscopy_flipped_crop_figure(img_path)
        report = audit_microscopy_splicing(img_path)

        out_path = os.path.join(tmpdir, "micro_annotated.png")
        res = render_splicing_visual_overlay(img_path, report, out_path)

        assert os.path.exists(res)
        assert os.path.getsize(res) > 0


def test_render_clean_overlay():
    with tempfile.TemporaryDirectory() as tmpdir:
        img_path = os.path.join(tmpdir, "clean.png")
        generate_clean_control_figure(img_path)
        report = audit_microscopy_splicing(img_path)

        out_path = os.path.join(tmpdir, "clean_annotated.png")
        res = render_splicing_visual_overlay(img_path, report, out_path)

        assert os.path.exists(res)
        assert os.path.getsize(res) > 0
