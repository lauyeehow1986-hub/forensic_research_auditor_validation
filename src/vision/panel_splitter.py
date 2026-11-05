"""
Multi-Panel Figure Splitter & Sub-Figure Segmenter (Gate 3.5 Phase 2).
Segments composite scientific figures (Panel A, B, C, D) into isolated sub-panels,
classifies panel types (Western Blot vs. Microscopy), and provides bounding box coordinates.
"""

import os
from typing import List, Dict, Any, Union
import numpy as np
import cv2


def classify_figure_type(image_input: Union[str, np.ndarray]) -> str:
    """
    Classifies a scientific figure or panel as WESTERN_BLOT, MICROSCOPY, or GENERAL.
    - WESTERN_BLOT: Light monochrome background (mean intensity > 165, low HSV saturation).
    - MICROSCOPY: Fluorescence (dark background mean < 80) or stained histology (rich texture, high keypoint density).
    - GENERAL: Other diagrams, charts, or clinical photos.
    """
    if isinstance(image_input, str):
        img = cv2.imread(image_input)
        if img is None:
            raise ValueError(f"Could not load image at {image_input}")
    else:
        img = image_input

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) if len(img.shape) == 3 else img
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV) if len(img.shape) == 3 else None

    mean_lum = float(np.mean(gray))
    std_lum = float(np.std(gray))
    mean_sat = float(np.mean(hsv[:, :, 1])) if hsv is not None else 0.0

    # Fluorescence microscopy: Dark background
    if mean_lum < 85:
        return "MICROSCOPY"

    # Western blot: Light background, very low color saturation
    if mean_lum > 165 and mean_sat < 35 and std_lum < 55:
        return "WESTERN_BLOT"

    # Stained histology or brightfield microscopy
    if mean_sat > 35:
        return "MICROSCOPY"

    return "GENERAL"


def split_figure_panels(image_input: Union[str, np.ndarray]) -> List[Dict[str, Any]]:
    """
    Detects and segments individual sub-panels in a composite manuscript figure.
    Returns a list of dicts with:
    - 'panel_id': e.g. 'Panel_A', 'Panel_B'
    - 'bbox': [ymin, xmin, ymax, xmax]
    - 'image': np.ndarray cropped panel
    - 'figure_type': 'WESTERN_BLOT' or 'MICROSCOPY'
    """
    if isinstance(image_input, str):
        img = cv2.imread(image_input)
        if img is None:
            raise ValueError(f"Could not load image at {image_input}")
    else:
        img = image_input.copy()

    h_img, w_img = img.shape[:2]
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) if len(img.shape) == 3 else img

    # Check for white gutter borders between panels
    # Threshold out content from white background
    _, thresh = cv2.threshold(gray, 248, 255, cv2.THRESH_BINARY_INV)
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    candidates = []
    min_w = int(w_img * 0.20)
    min_h = int(h_img * 0.20)
    max_area = int(w_img * h_img * 0.92)

    for cnt in contours:
        bx, by, bw, bh = cv2.boundingRect(cnt)
        area = bw * bh
        if bw >= min_w and bh >= min_h and area <= max_area:
            candidates.append((by, bx, by + bh, bx + bw))

    # If multiple candidates found, sort them reading order (top to bottom, left to right)
    if len(candidates) >= 2:
        # Sort by vertical bucket (row) then horizontal x
        row_bucket_h = max(50, int(h_img * 0.35))
        candidates.sort(key=lambda b: (b[0] // row_bucket_h, b[1]))

        panels = []
        labels = ["A", "B", "C", "D", "E", "F", "G", "H"]
        for idx, (ymin, xmin, ymax, xmax) in enumerate(candidates):
            cropped = img[ymin:ymax, xmin:xmax]
            lbl = f"Panel_{labels[idx]}" if idx < len(labels) else f"Panel_{idx+1}"
            fig_type = classify_figure_type(cropped)
            panels.append({
                "panel_id": lbl,
                "bbox": [ymin, xmin, ymax, xmax],
                "image": cropped,
                "figure_type": fig_type
            })
        return panels

    # Otherwise, treat the entire image as a single panel
    overall_type = classify_figure_type(img)
    return [{
        "panel_id": "Panel_1",
        "bbox": [0, 0, h_img, w_img],
        "image": img,
        "figure_type": overall_type
    }]
