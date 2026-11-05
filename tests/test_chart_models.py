"""
Tests for Chart Data Models and Extraction Schema (Task 2).
Verifies dataclass serialization, coordinate-to-value scaling,
and conversion to standard FastMCP TableRow dictionary format.
"""

import os
import sys
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.vision.chart_models import (
    AxisCalibration,
    ChartDataPoint,
    PValueBracket,
    ExtractedChartData
)


def test_axis_calibration_linear_mapping():
    # Y-axis from 0.0 to 10.0, pixel height from 500 (bottom) to 100 (top)
    axis = AxisCalibration(label="Concentration (mg/L)", min_val=0.0, max_val=10.0, scale_type="LINEAR")
    
    # Bottom pixel (500) corresponds to 0.0
    val_bottom = axis.pixel_to_val(pixel_y=500, pixel_origin_y=500, pixel_top_y=100)
    assert pytest.approx(val_bottom, 0.01) == 0.0

    # Top pixel (100) corresponds to 10.0
    val_top = axis.pixel_to_val(pixel_y=100, pixel_origin_y=500, pixel_top_y=100)
    assert pytest.approx(val_top, 0.01) == 10.0

    # Midpoint pixel (300) corresponds to 5.0
    val_mid = axis.pixel_to_val(pixel_y=300, pixel_origin_y=500, pixel_top_y=100)
    assert pytest.approx(val_mid, 0.01) == 5.0


def test_extracted_chart_data_serialization_and_to_table_rows():
    axis = AxisCalibration(label="Score", min_val=0.0, max_val=5.0)
    p1 = ChartDataPoint(group_name="Control", mean=1.42, dispersion_val=0.40, dispersion_type="SD", n_sample=15, is_discrete=True)
    p2 = ChartDataPoint(group_name="Treated", mean=3.20, dispersion_val=0.50, dispersion_type="SD", n_sample=15, is_discrete=True)
    
    bracket = PValueBracket(group_a="Control", group_b="Treated", claimed_text="***", claimed_p_threshold=0.001)

    chart = ExtractedChartData(
        figure_id="FIG_01",
        chart_type="BAR_WITH_ERROR_BARS",
        y_axis=axis,
        series=[p1, p2],
        p_value_brackets=[bracket]
    )

    # Verify JSON serialization
    d = chart.to_dict()
    assert d["figure_id"] == "FIG_01"
    assert len(d["series"]) == 2
    assert d["p_value_brackets"][0]["claimed_text"] == "***"

    # Verify deserialization
    reconstructed = ExtractedChartData.from_dict(d)
    assert reconstructed.figure_id == "FIG_01"
    assert reconstructed.series[0].mean == 1.42

    # Verify conversion to standard FastMCP TableRows
    rows = chart.to_table_rows()
    assert len(rows) == 2
    assert rows[0]["group_name"] == "Control"
    assert rows[0]["mean"] == 1.42
    assert rows[0]["sd"] == 0.40
    assert rows[0]["n_sample"] == 15
    assert rows[0]["is_discrete"] is True
