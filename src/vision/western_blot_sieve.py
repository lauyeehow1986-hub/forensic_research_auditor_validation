"""
Western Blot Lane & Band Clone Sieve (Gate 3.5 Phase 2).
Audits gel and Western blot images for intra-manuscript manipulation:
1. Cloned band patches duplicated across different lanes (Normalized Cross-Correlation).
2. Sharp vertical step-discontinuities across background lanes indicating cut-and-paste gel assembly.
"""

import os
from typing import Dict, Any, List, Union, Tuple
import numpy as np
import cv2


def _detect_lanes_and_bands(gray: np.ndarray) -> Tuple[List[int], List[Dict[str, Any]]]:
    """
    Detects vertical lane centers and extracts rectangular band patches along each lane.
    """
    h, w = gray.shape[:2]

    # Focus on the vertical band zone (exclude header labels and bottom borders)
    y_start = int(h * 0.25)
    y_end = int(h * 0.85)

    # Invert so dark bands have positive intensity
    inv = 255.0 - gray[y_start:y_end, :].astype(np.float32)

    # 1. Detect vertical lane centers
    col_sums = np.mean(inv, axis=0)
    # Smooth with box filter
    kernel_size = max(5, int(w * 0.04))
    if kernel_size % 2 == 0:
        kernel_size += 1
    col_smooth = cv2.GaussianBlur(col_sums.reshape(1, -1), (kernel_size, 1), 0)[0]

    # Find local maxima with minimum distance between lanes
    min_lane_dist = max(30, int(w * 0.12))
    lanes = []
    threshold = np.mean(col_smooth) - 0.2 * np.std(col_smooth)

    for x in range(kernel_size, w - kernel_size):
        if col_smooth[x] > threshold:
            if col_smooth[x] == np.max(col_smooth[max(0, x - min_lane_dist // 2) : min(w, x + min_lane_dist // 2) + 1]):
                if not any(abs(x - lx) < min_lane_dist for lx in lanes):
                    lanes.append(x)

    lanes.sort()
    if not lanes:
        # Fallback to 3 equally spaced lanes
        lanes = [int(w * 0.25), int(w * 0.50), int(w * 0.75)]

    # 2. Extract band patch for each lane
    bands = []
    patch_hw = min(20, int(h * 0.10))
    patch_ww = min(20, int(w * 0.06))

    for idx, lx in enumerate(lanes):
        # Look around central core window to avoid adjacent text annotations
        x1_core = max(0, lx - 15)
        x2_core = min(w, lx + 15)

        lane_strip = 255.0 - gray[y_start:y_end, x1_core:x2_core].astype(np.float32)
        row_profile = np.mean(lane_strip, axis=1)
        peak_y_rel = int(np.argmax(row_profile))
        peak_y = y_start + peak_y_rel

        py1 = max(0, peak_y - patch_hw)
        py2 = min(h, peak_y + patch_hw)
        px1 = max(0, lx - patch_ww)
        px2 = min(w, lx + patch_ww)

        patch = gray[py1:py2, px1:px2].copy()

        bands.append({
            "lane_index": idx,
            "lane_x": lx,
            "band_y": peak_y,
            "bbox": [py1, px1, py2, px2],
            "patch": patch
        })

    return lanes, bands


def audit_western_blot_splicing(image_input: Union[str, np.ndarray]) -> Dict[str, Any]:
    """
    Performs forensic audit of a Western blot image.
    Detects cloned bands across lanes and vertical background splicing step-discontinuities.
    """
    if isinstance(image_input, str):
        img = cv2.imread(image_input)
        if img is None:
            raise ValueError(f"Could not load image at {image_input}")
    else:
        img = image_input

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) if len(img.shape) == 3 else img.copy()
    h, w = gray.shape[:2]

    discrepancies = []

    # 1. Check for Vertical Background Step Discontinuity (Spliced Lane Border)
    # Compute horizontal background profile across mid-height
    bg_profile = np.median(gray[int(h * 0.2) : int(h * 0.8), :], axis=0).astype(np.float32)

    # Check for abrupt intensity step between x and x + 6
    step_window = 5
    for x in range(int(w * 0.15), int(w * 0.85) - step_window):
        left_val = np.median(bg_profile[max(0, x - step_window) : x])
        right_val = np.median(bg_profile[x : min(w, x + step_window)])
        contrast_step = abs(float(right_val - left_val))

        if contrast_step >= 18.0:
            discrepancies.append({
                "type": "SPLICED_LANE_BORDER",
                "severity": "FATAL",
                "splice_x": int(x),
                "contrast_step": round(contrast_step, 2),
                "bbox": [int(h * 0.1), x - 4, int(h * 0.9), x + 4],
                "explanation": (
                    f"Sharp vertical background step-discontinuity detected at X={x} "
                    f"(contrast step of {contrast_step:.1f} intensity units spanning gel height)."
                )
            })
            break  # Flag primary splice border

    # 2. Detect lanes and extract band patches
    lanes, bands = _detect_lanes_and_bands(gray)

    # 3. Pairwise Band Normalized Cross-Correlation (NCC)
    num_bands = len(bands)
    for i in range(num_bands):
        for j in range(i + 1, num_bands):
            b1 = bands[i]
            b2 = bands[j]

            p1 = b1["patch"].astype(np.float32)
            p2 = b2["patch"].astype(np.float32)

            # Ensure identical shape for NCC comparison
            min_h_p = min(p1.shape[0], p2.shape[0])
            min_w_p = min(p1.shape[1], p2.shape[1])
            if min_h_p < 10 or min_w_p < 10:
                continue

            p1_crop = p1[:min_h_p, :min_w_p]
            p2_crop = p2[:min_h_p, :min_w_p]

            std1 = np.std(p1_crop)
            std2 = np.std(p2_crop)

            if std1 > 3.0 and std2 > 3.0:
                norm1 = (p1_crop - np.mean(p1_crop)) / std1
                norm2 = (p2_crop - np.mean(p2_crop)) / std2
                ncc = float(np.mean(norm1 * norm2))

                # Cloned bands exhibit near-identical correlation AND near-zero pixel difference
                if ncc >= 0.95:
                    mean_abs_diff = float(np.mean(np.abs(p1_crop - p2_crop)))
                    if mean_abs_diff <= 12.0:
                        discrepancies.append({
                            "type": "CLONED_BAND",
                            "severity": "FATAL",
                            "lane_a": b1["lane_index"],
                            "lane_b": b2["lane_index"],
                            "ncc_score": round(ncc, 4),
                            "mean_abs_diff": round(mean_abs_diff, 2),
                            "bbox_a": b1["bbox"],
                            "bbox_b": b2["bbox"],
                            "explanation": (
                                f"Bands in Lane {b1['lane_index']+1} and Lane {b2['lane_index']+1} "
                                f"exhibit statistically impossible cross-correlation (NCC={ncc:.4f}, mean diff={mean_abs_diff:.2f}), "
                                f"confirming cloned band duplication."
                            )
                        })

    verdict = "FLAGGED_WESTERN_BLOT_ANOMALY" if len(discrepancies) > 0 else "CLEAN"

    return {
        "verdict": verdict,
        "discrepancies_count": len(discrepancies),
        "discrepancies": discrepancies,
        "lanes_detected": len(lanes),
        "lanes_x": lanes,
        "bands_detected": len(bands)
    }
