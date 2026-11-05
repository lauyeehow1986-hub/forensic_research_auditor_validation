"""
Microscopy & Histology Rotation/Flip/Crop Sieve (Gate 3.5 Phase 2).
Performs pairwise affine homography and keypoint matching across figure panels
to detect duplicated, cropped, flipped, or rotated microscopy and histology fields.
"""

import os
from typing import Dict, Any, List, Optional, Union
import numpy as np
import cv2

from src.vision.panel_splitter import split_figure_panels


def audit_microscopy_splicing(
    image_input: Union[str, np.ndarray],
    panels: Optional[List[Dict[str, Any]]] = None
) -> Dict[str, Any]:
    """
    Audits multi-panel figures for duplicated microscopy/histology fields.
    Extracts SIFT features, applies Lowe's ratio test, and computes RANSAC homography
    to detect scale crops, rotations (90/180/270 deg), and mirror reflections (det < 0).
    """
    if panels is None:
        panels = split_figure_panels(image_input)

    if len(panels) < 2:
        return {
            "verdict": "CLEAN",
            "discrepancies_count": 0,
            "discrepancies": [],
            "message": "Fewer than 2 panels detected in figure."
        }

    # Initialize SIFT (fallback to ORB if SIFT is disabled)
    try:
        detector = cv2.SIFT_create(nfeatures=1500)
        norm_type = cv2.NORM_L2
    except Exception:
        detector = cv2.ORB_create(2000)
        norm_type = cv2.NORM_HAMMING

    panel_features = []
    for p in panels:
        p_img = p["image"]
        p_gray = cv2.cvtColor(p_img, cv2.COLOR_BGR2GRAY) if len(p_img.shape) == 3 else p_img
        kp, des = detector.detectAndCompute(p_gray, None)
        panel_features.append({
            "panel_id": p["panel_id"],
            "bbox": p["bbox"],
            "kp": kp,
            "des": des
        })

    matcher = cv2.BFMatcher(norm_type)
    discrepancies = []
    num_panels = len(panel_features)

    for i in range(num_panels):
        for j in range(i + 1, num_panels):
            f1 = panel_features[i]
            f2 = panel_features[j]

            if f1["des"] is None or f2["des"] is None:
                continue
            if len(f1["des"]) < 8 or len(f2["des"]) < 8:
                continue

            # K-Nearest Neighbors matching with k=2
            knn_matches = matcher.knnMatch(f1["des"], f2["des"], k=2)

            # Lowe's ratio test (threshold = 0.75)
            good_matches = []
            for match_pair in knn_matches:
                if len(match_pair) == 2:
                    m, n = match_pair
                    if m.distance < 0.75 * n.distance:
                        good_matches.append(m)

            if len(good_matches) >= 8:
                src_pts = np.float32([f1["kp"][m.queryIdx].pt for m in good_matches]).reshape(-1, 1, 2)
                dst_pts = np.float32([f2["kp"][m.trainIdx].pt for m in good_matches]).reshape(-1, 1, 2)

                # Estimate Homography with RANSAC
                H, mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC, 5.0)

                if mask is not None:
                    inliers = int(np.sum(mask))

                    # If at least 12 geometrically consistent inliers confirm the same field
                    if inliers >= 12 and H is not None:
                        inlier_mask = mask.ravel() == 1
                        matched_inliers_a = src_pts[inlier_mask].reshape(-1, 2)
                        matched_inliers_b = dst_pts[inlier_mask].reshape(-1, 2)

                        # Check transformation properties
                        det_h = float(H[0, 0] * H[1, 1] - H[0, 1] * H[1, 0])
                        angle_rad = float(np.arctan2(H[1, 0], H[0, 0]))
                        angle_deg = float(np.degrees(angle_rad))
                        is_reflection = bool(det_h < -0.1)

                        # Guard against degenerate / collapsed homographies
                        unique_pts_a = len(set(tuple(np.round(pt, 0)) for pt in matched_inliers_a))
                        unique_pts_b = len(set(tuple(np.round(pt, 0)) for pt in matched_inliers_b))
                        is_non_degenerate = (0.15 <= abs(det_h) <= 6.0) and (unique_pts_a >= 10) and (unique_pts_b >= 10)

                        if is_non_degenerate:
                            trans_desc = []
                            if is_reflection:
                                trans_desc.append("MIRROR_FLIP")
                            if abs(angle_deg) > 20:
                                trans_desc.append(f"ROTATION_{round(angle_deg)}°")
                            if not trans_desc:
                                trans_desc.append("IDENTICAL_OR_CROPPED")

                            discrepancies.append({
                                "type": "TRANSFORMED_MICROGRAPH_DUPLICATION",
                                "severity": "FATAL",
                                "panel_a": f1["panel_id"],
                                "panel_b": f2["panel_id"],
                                "inlier_matches": inliers,
                                "total_good_matches": len(good_matches),
                                "transformation_type": "+".join(trans_desc),
                                "is_reflection": is_reflection,
                                "rotation_deg": round(angle_deg, 1),
                                "determinant": round(det_h, 3),
                                "bbox_a": f1["bbox"],
                                "bbox_b": f2["bbox"],
                                "matched_coords_a": matched_inliers_a[:15].tolist(),
                                "matched_coords_b": matched_inliers_b[:15].tolist(),
                                "explanation": (
                                    f"{f1['panel_id']} and {f2['panel_id']} share {inliers} "
                                    f"geometrically consistent SIFT inlier matches "
                                    f"({'+'.join(trans_desc)}, det={det_h:.2f}), "
                                    f"confirming duplicated or transformed microscopy field reuse."
                                )
                            })

    verdict = "FLAGGED_MICROSCOPY_ANOMALY" if len(discrepancies) > 0 else "CLEAN"

    return {
        "verdict": verdict,
        "discrepancies_count": len(discrepancies),
        "discrepancies": discrepancies,
        "panels_analyzed": len(panels)
    }
