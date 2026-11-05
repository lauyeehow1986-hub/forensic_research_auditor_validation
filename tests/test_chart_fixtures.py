"""
Tests for synthetic chart test fixture generator.
Verifies that programmatically rendered chart fixtures are created properly,
have high resolution, and contain ground truth forensic labels.
"""

import os
import sys
import tempfile
import pytest
from PIL import Image

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.vision.chart_fixture_generator import (
    generate_grim_fail_bar_chart,
    generate_significance_inversion_chart,
    generate_zero_bound_truncation_chart,
    generate_clean_control_chart
)


@pytest.fixture
def temp_dir():
    with tempfile.TemporaryDirectory() as tmp:
        yield tmp


def test_generate_grim_fail_bar_chart(temp_dir):
    out_path = os.path.join(temp_dir, "grim_fail.png")
    meta = generate_grim_fail_bar_chart(out_path)

    assert os.path.exists(out_path)
    assert os.path.getsize(out_path) > 5000  # Valid non-empty PNG image
    
    # Verify image dimensions
    with Image.open(out_path) as img:
        assert img.width >= 600
        assert img.height >= 400

    # Verify ground truth metadata
    assert meta["target_anomaly"] == "GRIM_INCONSISTENCY"
    assert meta["groups"][0]["mean"] == 1.42
    assert meta["groups"][0]["n_sample"] == 15
    assert meta["groups"][0]["is_discrete"] is True


def test_generate_significance_inversion_chart(temp_dir):
    out_path = os.path.join(temp_dir, "significance_inversion.png")
    meta = generate_significance_inversion_chart(out_path)

    assert os.path.exists(out_path)
    assert os.path.getsize(out_path) > 5000

    assert meta["target_anomaly"] == "SIGNIFICANCE_INVERSION"
    assert meta["claimed_p_text"] in ["***", "*", "p < 0.05", "p < 0.001"]
    assert meta["actual_welch_p"] > 0.05  # Mathematically non-significant difference


def test_generate_zero_bound_truncation_chart(temp_dir):
    out_path = os.path.join(temp_dir, "zero_bound.png")
    meta = generate_zero_bound_truncation_chart(out_path)

    assert os.path.exists(out_path)
    assert os.path.getsize(out_path) > 5000

    assert meta["target_anomaly"] == "ZERO_BOUND_TRUNCATION"
    # Mean - 2*SD < 0 indicates negative normal tail
    grp = meta["groups"][0]
    assert grp["mean"] - 2 * grp["sd"] < 0
    assert meta["lower_error_bar_truncated"] is True


def test_generate_clean_control_chart(temp_dir):
    out_path = os.path.join(temp_dir, "clean_control.png")
    meta = generate_clean_control_chart(out_path)

    assert os.path.exists(out_path)
    assert os.path.getsize(out_path) > 5000

    assert meta["target_anomaly"] == "NONE"
    assert meta["is_clean"] is True
    # Claimed significance matches true Welch p-value
    assert meta["actual_welch_p"] < 0.001
    assert meta["claimed_p_text"] in ["***", "p < 0.001"]
