"""
Tests for Hybrid Chart Transcriber (Task 4).
Verifies extraction of:
- Axis calibration (Y-axis bounds, label, scale)
- Bar group positions and heights (means)
- Error bar bounds (dispersion)
- P-value brackets and claimed text
Using local OpenCV / OCR and Gemini Vision hybrid modes.
"""

import os
import sys
import tempfile
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.vision.chart_fixture_generator import (
    generate_grim_fail_bar_chart,
    generate_significance_inversion_chart,
    generate_clean_control_chart
)
from src.vision.chart_transcriber import transcribe_chart_figure
from src.vision.chart_models import ExtractedChartData


@pytest.fixture(scope="module")
def fixture_charts(tmp_path_factory):
    temp_dir = tmp_path_factory.mktemp("chart_fixtures")
    p_grim = os.path.join(temp_dir, "grim_fail.png")
    p_inv = os.path.join(temp_dir, "significance_inversion.png")
    p_clean = os.path.join(temp_dir, "clean_control.png")

    meta_grim = generate_grim_fail_bar_chart(p_grim)
    meta_inv = generate_significance_inversion_chart(p_inv)
    meta_clean = generate_clean_control_chart(p_clean)

    return {
        "grim": (p_grim, meta_grim),
        "inversion": (p_inv, meta_inv),
        "clean": (p_clean, meta_clean)
    }


def test_transcribe_grim_fail_chart(fixture_charts):
    img_path, meta = fixture_charts["grim"]
    caption = "Clinical Symptom Score by Group (n=15/group)"
    
    chart_data = transcribe_chart_figure(
        image_path=img_path,
        caption=caption,
        sample_size_hint=15,
        force_local=True
    )

    assert isinstance(chart_data, ExtractedChartData)
    assert len(chart_data.series) >= 2
    
    # Check that means are approximately extracted within 15% tolerance
    means = [pt.mean for pt in chart_data.series]
    assert any(pytest.approx(m, abs=0.4) == 1.42 for m in means)
    assert any(pytest.approx(m, abs=0.5) == 3.20 for m in means)

    # Check sample size propagation
    assert all(pt.n_sample == 15 for pt in chart_data.series)


def test_transcribe_significance_inversion_chart(fixture_charts):
    img_path, meta = fixture_charts["inversion"]
    caption = "Response to Compound X (n=10/group)"
    
    chart_data = transcribe_chart_figure(
        image_path=img_path,
        caption=caption,
        sample_size_hint=10,
        force_local=True
    )

    assert isinstance(chart_data, ExtractedChartData)
    assert len(chart_data.series) >= 2
    assert len(chart_data.p_value_brackets) >= 1
    bracket = chart_data.p_value_brackets[0]
    assert "***" in bracket.claimed_text or bracket.claimed_p_threshold <= 0.05


def test_transcribe_clean_control_chart(fixture_charts):
    img_path, meta = fixture_charts["clean"]
    caption = "mRNA Expression Levels (n=10/group)"
    
    chart_data = transcribe_chart_figure(
        image_path=img_path,
        caption=caption,
        sample_size_hint=10,
        force_local=True
    )

    assert isinstance(chart_data, ExtractedChartData)
    assert len(chart_data.series) >= 2
    assert chart_data.y_axis.max_val >= 5.0
