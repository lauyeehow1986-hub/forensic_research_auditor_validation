import os
import sys
import tempfile
import cv2
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.vision.splicing_fixture_generator import (
    generate_microscopy_flipped_crop_figure,
    generate_western_blot_cloned_band_figure
)
from src.vision.panel_splitter import split_figure_panels, classify_figure_type


def test_split_multi_panel_microscopy_figure():
    with tempfile.TemporaryDirectory() as tmpdir:
        out_path = os.path.join(tmpdir, "multi_panel.png")
        generate_microscopy_flipped_crop_figure(out_path)

        panels = split_figure_panels(out_path)
        assert len(panels) == 2
        p1, p2 = panels[0], panels[1]
        assert p1["panel_id"] in ["Panel_A", "Panel_1"]
        assert p2["panel_id"] in ["Panel_B", "Panel_2"]
        assert p1["image"].shape[0] > 100
        assert p2["image"].shape[0] > 100
        # Check bounding box format [ymin, xmin, ymax, xmax]
        for p in panels:
            ymin, xmin, ymax, xmax = p["bbox"]
            assert ymax > ymin and xmax > xmin


def test_split_single_western_blot_figure():
    with tempfile.TemporaryDirectory() as tmpdir:
        out_path = os.path.join(tmpdir, "wb.png")
        generate_western_blot_cloned_band_figure(out_path)

        panels = split_figure_panels(out_path)
        assert len(panels) >= 1
        fig_type = classify_figure_type(out_path)
        assert fig_type == "WESTERN_BLOT"
