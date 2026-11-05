"""
Tests for Visual Discrepancy Overlay Renderer (Task 5).
Verifies that color-coded OpenCV overlays are rendered onto figures,
highlighting verified points in green and forensic discrepancies in red.
"""

import os
import sys
import tempfile
import pytest
from PIL import Image

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.vision.chart_fixture_generator import generate_significance_inversion_chart, generate_clean_control_chart
from src.vision.chart_transcriber import transcribe_chart_figure
from src.vision.forensic_chart_sieves import audit_chart_statistics
from src.vision.visual_overlay_renderer import render_chart_visual_overlay


@pytest.fixture
def temp_dir():
    with tempfile.TemporaryDirectory() as tmp:
        yield tmp


def test_render_anomaly_overlay(temp_dir):
    raw_img = os.path.join(temp_dir, "raw_inversion.png")
    out_overlay = os.path.join(temp_dir, "overlay_inversion.png")
    
    generate_significance_inversion_chart(raw_img)
    chart_data = transcribe_chart_figure(raw_img, force_local=True)
    report = audit_chart_statistics(chart_data)

    assert report["verdict"] == "FLAGGED_FORENSIC_ANOMALY"

    res_path = render_chart_visual_overlay(
        image_path=raw_img,
        audit_report=report,
        output_path=out_overlay
    )

    assert os.path.exists(res_path)
    assert os.path.getsize(res_path) > 5000
    
    with Image.open(res_path) as img:
        assert img.width >= 600
        assert img.height >= 400


def test_render_clean_overlay(temp_dir):
    raw_img = os.path.join(temp_dir, "raw_clean.png")
    out_overlay = os.path.join(temp_dir, "overlay_clean.png")
    
    generate_clean_control_chart(raw_img)
    chart_data = transcribe_chart_figure(raw_img, force_local=True)
    report = audit_chart_statistics(chart_data)

    assert report["verdict"] == "CLEAN"

    res_path = render_chart_visual_overlay(
        image_path=raw_img,
        audit_report=report,
        output_path=out_overlay
    )

    assert os.path.exists(res_path)
    assert os.path.getsize(res_path) > 5000
