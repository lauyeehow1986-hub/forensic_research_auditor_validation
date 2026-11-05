"""
Synthetic Splicing Fixture Generator (Gate 3.5 Phase 2).
Generates realistic biological image figures for testing intra-paper tampering detection:
1. Western blot with cloned band patches across lanes.
2. Western blot with vertical background step-discontinuity splice borders.
3. Multi-panel microscopy figure with rotated/flipped sub-crop duplication.
4. Clean control figure with authentic independent noise and distinct biological morphology.
"""

import os
from typing import Dict, Any, List
import numpy as np
import cv2


def _draw_gaussian_band(img: np.ndarray, xc: int, yc: int, sigma_x: float, sigma_y: float, peak_darkness: int = 160):
    """Draws a realistic Western blot band using a 2D Gaussian profile."""
    h, w = img.shape[:2]
    y_min = max(0, int(yc - 3 * sigma_y))
    y_max = min(h, int(yc + 3 * sigma_y))
    x_min = max(0, int(xc - 3 * sigma_x))
    x_max = min(w, int(xc + 3 * sigma_x))

    y_grid, x_grid = np.ogrid[y_min:y_max, x_min:x_max]
    gauss = np.exp(-(((x_grid - xc) ** 2) / (2 * sigma_x ** 2) + ((y_grid - yc) ** 2) / (2 * sigma_y ** 2)))
    darkening = (gauss * peak_darkness).astype(np.uint8)

    if len(img.shape) == 3:
        for c in range(3):
            sub = img[y_min:y_max, x_min:x_max, c].astype(np.int16) - darkening
            img[y_min:y_max, x_min:x_max, c] = np.clip(sub, 0, 255).astype(np.uint8)
    else:
        sub = img[y_min:y_max, x_min:x_max].astype(np.int16) - darkening
        img[y_min:y_max, x_min:x_max] = np.clip(sub, 0, 255).astype(np.uint8)


def generate_western_blot_cloned_band_figure(output_path: str) -> Dict[str, Any]:
    """
    Renders a 4-lane Western blot where Lane 1 (Ctrl) and Lane 3 (High Dose)
    contain an identical cloned band patch with matching pixel micro-texture.
    """
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    np.random.seed(42)

    h, w = 240, 400
    # Background membrane with subtle gradient and noise
    bg = np.full((h, w, 3), 225, dtype=np.uint8)
    noise = np.random.normal(0, 3, (h, w, 3)).astype(np.int16)
    bg = np.clip(bg.astype(np.int16) + noise, 0, 255).astype(np.uint8)

    lanes_x = [70, 150, 230, 310]
    band_y = 110

    # Draw unique band on Lane 1
    _draw_gaussian_band(bg, lanes_x[0], band_y, sigma_x=22, sigma_y=8, peak_darkness=170)

    # Draw different bands on Lane 2 and Lane 4
    _draw_gaussian_band(bg, lanes_x[1], band_y, sigma_x=16, sigma_y=6, peak_darkness=130)
    _draw_gaussian_band(bg, lanes_x[3], band_y, sigma_x=24, sigma_y=10, peak_darkness=190)

    # Extract patch from Lane 1 and clone it directly onto Lane 3
    patch_hw = 25
    patch_ww = 35
    patch = bg[band_y - patch_hw : band_y + patch_hw, lanes_x[0] - patch_ww : lanes_x[0] + patch_ww].copy()
    bg[band_y - patch_hw : band_y + patch_hw, lanes_x[2] - patch_ww : lanes_x[2] + patch_ww] = patch

    # Add lane headers
    labels = ["Ctrl", "Low", "High", "Pos"]
    for lx, lbl in zip(lanes_x, labels):
        cv2.putText(bg, lbl, (lx - 18, 35), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (40, 40, 40), 1, cv2.LINE_AA)

    cv2.putText(bg, "p-ERK1/2", (10, band_y + 4), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (30, 30, 30), 1, cv2.LINE_AA)

    cv2.imwrite(output_path, bg)

    return {
        "target_anomaly": "CLONED_BAND",
        "figure_type": "WESTERN_BLOT",
        "cloned_lanes": [0, 2],
        "lanes_x": lanes_x,
        "band_y_center": band_y,
        "patch_size": (patch_hw * 2, patch_ww * 2)
    }


def generate_western_blot_spliced_lane_figure(output_path: str) -> Dict[str, Any]:
    """
    Renders a Western blot with a sharp vertical step-discontinuity in background
    intensity between Lane 1 and Lane 2, indicating cut-and-paste gel assembly.
    """
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    np.random.seed(101)

    h, w = 240, 360
    bg = np.full((h, w, 3), 228, dtype=np.uint8)

    # Introduce step discontinuity at x = 145: left side is 228, right side is 198
    splice_x = 145
    bg[:, splice_x:, :] = 198

    noise = np.random.normal(0, 3.5, (h, w, 3)).astype(np.int16)
    bg = np.clip(bg.astype(np.int16) + noise, 0, 255).astype(np.uint8)

    lanes_x = [75, 195, 290]
    band_y = 115

    _draw_gaussian_band(bg, lanes_x[0], band_y, sigma_x=22, sigma_y=8, peak_darkness=150)
    _draw_gaussian_band(bg, lanes_x[1], band_y, sigma_x=20, sigma_y=7, peak_darkness=160)
    _draw_gaussian_band(bg, lanes_x[2], band_y, sigma_x=25, sigma_y=9, peak_darkness=175)

    labels = ["Lane 1", "Lane 2", "Lane 3"]
    for lx, lbl in zip(lanes_x, labels):
        cv2.putText(bg, lbl, (lx - 22, 35), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (40, 40, 40), 1, cv2.LINE_AA)

    cv2.putText(bg, "GAPDH", (10, band_y + 4), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (30, 30, 30), 1, cv2.LINE_AA)

    cv2.imwrite(output_path, bg)

    return {
        "target_anomaly": "SPLICED_LANE_BORDER",
        "figure_type": "WESTERN_BLOT",
        "splice_x": splice_x,
        "lanes_x": lanes_x
    }


def _generate_synthetic_micrograph(h: int, w: int, seed: int) -> np.ndarray:
    """Generates a textured synthetic fluorescence micrograph with cell colonies."""
    rng = np.random.RandomState(seed)
    # Dark background with Poisson/Gaussian noise
    panel = np.full((h, w, 3), 20, dtype=np.uint8)
    noise = rng.normal(0, 5, (h, w, 3)).astype(np.int16)
    panel = np.clip(panel.astype(np.int16) + noise, 0, 255).astype(np.uint8)

    # Draw 40 cell colonies
    for _ in range(40):
        cx = rng.randint(30, w - 30)
        cy = rng.randint(30, h - 30)
        rad = rng.randint(6, 16)
        color_g = rng.randint(140, 255)
        color_b = rng.randint(80, 180)
        # Draw gradient circle
        cv2.circle(panel, (cx, cy), rad, (color_b // 2, color_g, 30), -1)
        cv2.circle(panel, (cx, cy), max(2, rad // 2), (color_b, min(255, color_g + 40), 80), -1)

    panel = cv2.GaussianBlur(panel, (5, 5), 1.2)
    return panel


def generate_microscopy_flipped_crop_figure(output_path: str) -> Dict[str, Any]:
    """
    Renders a multi-panel figure where Panel B is a rotated 180-degree sub-crop
    of Panel A, simulating recycled microscopy fields with altered orientation.
    """
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)

    panel_size = 320
    # Panel A: Original micrograph
    panel_a = _generate_synthetic_micrograph(panel_size, panel_size, seed=202)

    # Panel B: Take 240x240 center crop from Panel A, rotate 180 degrees, and resize
    crop = panel_a[40:280, 40:280].copy()
    crop_rot = cv2.rotate(crop, cv2.ROTATE_180)
    panel_b = cv2.resize(crop_rot, (panel_size, panel_size), interpolation=cv2.INTER_LINEAR)

    # Combine into a 2-panel figure with white margins and labels
    margin = 30
    header = 40
    fig_w = panel_size * 2 + margin * 3
    fig_h = panel_size + header + margin * 2

    canvas = np.full((fig_h, fig_w, 3), 255, dtype=np.uint8)

    # Place Panel A
    y1 = header + margin
    y2 = y1 + panel_size
    x1_a = margin
    x2_a = x1_a + panel_size
    canvas[y1:y2, x1_a:x2_a] = panel_a
    cv2.putText(canvas, "A: Vehicle (Control)", (x1_a, header), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (20, 20, 20), 2, cv2.LINE_AA)

    # Place Panel B
    x1_b = x2_a + margin
    x2_b = x1_b + panel_size
    canvas[y1:y2, x1_b:x2_b] = panel_b
    cv2.putText(canvas, "B: Compound 5a Treated", (x1_b, header), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (20, 20, 20), 2, cv2.LINE_AA)

    cv2.imwrite(output_path, canvas)

    return {
        "target_anomaly": "TRANSFORMED_MICROGRAPH_DUPLICATION",
        "figure_type": "MICROSCOPY",
        "panels": ["Panel_A", "Panel_B"],
        "panel_boxes": [
            [y1, x1_a, y2, x2_a],
            [y1, x1_b, y2, x2_b]
        ],
        "transformation": "ROTATION_180"
    }


def generate_clean_control_figure(output_path: str) -> Dict[str, Any]:
    """
    Renders a multi-panel figure where Panel A and Panel B are independent authentic
    biological micrographs with independent seeds and no shared sub-regions.
    """
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)

    panel_size = 320
    panel_a = _generate_synthetic_micrograph(panel_size, panel_size, seed=505)
    panel_b = _generate_synthetic_micrograph(panel_size, panel_size, seed=909)

    margin = 30
    header = 40
    fig_w = panel_size * 2 + margin * 3
    fig_h = panel_size + header + margin * 2

    canvas = np.full((fig_h, fig_w, 3), 255, dtype=np.uint8)

    y1 = header + margin
    y2 = y1 + panel_size
    x1_a = margin
    x2_a = x1_a + panel_size
    canvas[y1:y2, x1_a:x2_a] = panel_a
    cv2.putText(canvas, "A: Wild Type Baseline", (x1_a, header), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (20, 20, 20), 2, cv2.LINE_AA)

    x1_b = x2_a + margin
    x2_b = x1_b + panel_size
    canvas[y1:y2, x1_b:x2_b] = panel_b
    cv2.putText(canvas, "B: Knockout Baseline", (x1_b, header), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (20, 20, 20), 2, cv2.LINE_AA)

    cv2.imwrite(output_path, canvas)

    return {
        "target_anomaly": "NONE",
        "is_clean": True,
        "figure_type": "MICROSCOPY",
        "panels": ["Panel_A", "Panel_B"],
        "panel_boxes": [
            [y1, x1_a, y2, x2_a],
            [y1, x1_b, y2, x2_b]
        ]
    }
