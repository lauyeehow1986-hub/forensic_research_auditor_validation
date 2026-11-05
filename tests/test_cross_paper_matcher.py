import os
import sys
import numpy as np
import cv2
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.vision.cross_paper_matcher import (
    verify_cross_paper_match,
    render_cross_paper_comparison_overlay
)


def create_synthetic_microscopy(seed: int = 42, size: int = 300) -> np.ndarray:
    """Creates a textured synthetic microscopy image with deterministic keypoints."""
    np.random.seed(seed)
    img = np.zeros((size, size, 3), dtype=np.uint8)
    # Add multiple circular cells with distinct internal granules
    for _ in range(25):
        cx = np.random.randint(40, size - 40)
        cy = np.random.randint(40, size - 40)
        radius = np.random.randint(12, 28)
        color = (int(np.random.randint(100, 255)), int(np.random.randint(80, 200)), int(np.random.randint(60, 180)))
        cv2.circle(img, (cx, cy), radius, color, -1)
        # Internal nucleus/granules
        cv2.circle(img, (cx, cy), max(2, radius // 3), (255, 255, 255), -1)
        cv2.circle(img, (cx + 4, cy - 3), 2, (30, 30, 30), -1)

    # Add background noise/texture
    noise = np.random.randint(0, 30, (size, size, 3), dtype=np.uint8)
    return cv2.add(img, noise)


def test_cross_paper_exact_and_rotated_match():
    img_retracted = create_synthetic_microscopy(seed=101, size=300)
    # Reused figure: cropped and rotated 90 degrees
    crop = img_retracted[30:270, 30:270]
    img_reused = cv2.rotate(crop, cv2.ROTATE_90_CLOCKWISE)

    res = verify_cross_paper_match(img_reused, img_retracted, min_inliers=12)

    assert res["is_match"] is True
    assert res["inlier_count"] >= 12
    assert res["transformation_type"] in ["ROTATION", "SCALE_CROP", "EXACT_DUPLICATION"]
    assert res["confidence_score"] > 0.5


def test_cross_paper_clean_negative():
    img_retracted = create_synthetic_microscopy(seed=101, size=300)
    # Completely independent study figure (different seed)
    img_clean = create_synthetic_microscopy(seed=999, size=300)

    res = verify_cross_paper_match(img_clean, img_retracted, min_inliers=12)

    assert res["is_match"] is False
    assert res["inlier_count"] < 12


def test_cross_paper_comparison_overlay_rendering(tmp_path):
    img_retracted = create_synthetic_microscopy(seed=101, size=300)
    img_reused = cv2.resize(img_retracted[20:280, 20:280], (300, 300))

    match_res = verify_cross_paper_match(img_reused, img_retracted, min_inliers=12)
    assert match_res["is_match"] is True

    candidate_meta = {
        "figure_id": "PMC54321_Fig3_A",
        "pmcid": "PMC54321",
        "doi": "10.1038/srep54321",
        "panel_id": "A",
        "retraction_reasons": "Microscopy panel duplication across manuscripts"
    }

    out_file = str(tmp_path / "cross_paper_match_overlay.png")
    render_cross_paper_comparison_overlay(
        query_input=img_reused,
        candidate_input=img_retracted,
        match_result=match_res,
        candidate_meta=candidate_meta,
        output_path=out_file
    )

    assert os.path.exists(out_file)
    assert os.path.getsize(out_file) > 1000
