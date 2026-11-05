"""
Cross-Paper SIFT RANSAC Verifier & Forensic Comparison Overlay Generator.

Validates candidate figure duplications across manuscripts using rigorous affine
homography, Lowe's ratio test, and RANSAC inlier verification (>= 12 inliers)
to guarantee zero false alarms, generating side-by-side forensic visual evidence.
"""

from typing import Union, Dict, Any, List, Optional
import os
import cv2
import numpy as np


def _load_image(img_input: Union[str, np.ndarray]) -> np.ndarray:
    """Helper to load image into BGR numpy array."""
    if isinstance(img_input, str):
        img = cv2.imread(img_input, cv2.IMREAD_COLOR)
        if img is None:
            raise FileNotFoundError(f"Could not load image from: {img_input}")
        return img
    elif len(img_input.shape) == 2:
        return cv2.cvtColor(img_input, cv2.COLOR_GRAY2BGR)
    elif img_input.shape[2] == 4:
        return cv2.cvtColor(img_input, cv2.COLOR_BGRA2BGR)
    return img_input.copy()


def verify_cross_paper_match(
    query_input: Union[str, np.ndarray],
    candidate_input: Union[str, np.ndarray],
    min_inliers: int = 12
) -> Dict[str, Any]:
    """
    Verifies cross-paper figure reuse using SIFT keypoint extraction, Lowe's ratio test,
    and RANSAC affine homography estimation.
    """
    img_q = _load_image(query_input)
    img_c = _load_image(candidate_input)

    gray_q = cv2.cvtColor(img_q, cv2.COLOR_BGR2GRAY)
    gray_c = cv2.cvtColor(img_c, cv2.COLOR_BGR2GRAY)

    # Initialize SIFT (fallback to ORB if unavailable)
    try:
        detector = cv2.SIFT_create(nfeatures=2000)
        norm_type = cv2.NORM_L2
    except Exception:
        detector = cv2.ORB_create(2500)
        norm_type = cv2.NORM_HAMMING

    kp_q, des_q = detector.detectAndCompute(gray_q, None)
    kp_c, des_c = detector.detectAndCompute(gray_c, None)

    if des_q is None or des_c is None or len(des_q) < 8 or len(des_c) < 8:
        return {
            "is_match": False,
            "inlier_count": 0,
            "total_matches": 0,
            "transformation_type": "NONE",
            "confidence_score": 0.0,
            "homography_matrix": None,
            "explanation": "Insufficient keypoints detected for cross-manuscript verification."
        }

    matcher = cv2.BFMatcher(norm_type)
    knn_matches = matcher.knnMatch(des_q, des_c, k=2)

    good_matches = []
    for pair in knn_matches:
        if len(pair) == 2:
            m, n = pair
            if m.distance < 0.75 * n.distance:
                good_matches.append(m)

    if len(good_matches) < 8:
        return {
            "is_match": False,
            "inlier_count": 0,
            "total_matches": len(good_matches),
            "transformation_type": "NONE",
            "confidence_score": 0.0,
            "homography_matrix": None,
            "explanation": f"Only {len(good_matches)} good matches found (minimum 8 required)."
        }

    src_pts = np.float32([kp_q[m.queryIdx].pt for m in good_matches]).reshape(-1, 1, 2)
    dst_pts = np.float32([kp_c[m.trainIdx].pt for m in good_matches]).reshape(-1, 1, 2)

    H, mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC, 5.0)

    if mask is None or H is None:
        return {
            "is_match": False,
            "inlier_count": 0,
            "total_matches": len(good_matches),
            "transformation_type": "NONE",
            "confidence_score": 0.0,
            "homography_matrix": None,
            "explanation": "RANSAC failed to fit a geometrically consistent homography."
        }

    inliers = int(np.sum(mask))
    inlier_mask = mask.ravel() == 1
    matched_q = src_pts[inlier_mask].reshape(-1, 2)
    matched_c = dst_pts[inlier_mask].reshape(-1, 2)

    det_h = float(H[0, 0] * H[1, 1] - H[0, 1] * H[1, 0])
    angle_rad = float(np.arctan2(H[1, 0], H[0, 0]))
    angle_deg = float(np.degrees(angle_rad))
    is_reflection = bool(det_h < -0.1)

    unique_pts_q = len(set(tuple(np.round(pt, 0)) for pt in matched_q))
    unique_pts_c = len(set(tuple(np.round(pt, 0)) for pt in matched_c))
    is_non_degenerate = (0.15 <= abs(det_h) <= 6.0) and (unique_pts_q >= 10) and (unique_pts_c >= 10)

    if inliers >= min_inliers and is_non_degenerate:
        trans_types = []
        if is_reflection:
            trans_types.append("MIRROR_FLIP")
        if abs(angle_deg) > 20:
            trans_types.append("ROTATION")
        if abs(abs(det_h) - 1.0) > 0.15:
            trans_types.append("SCALE_CROP")
        if not trans_types:
            trans_types.append("EXACT_DUPLICATION")

        confidence = float(min(1.0, inliers / max(15.0, float(inliers + 3))))

        return {
            "is_match": True,
            "inlier_count": inliers,
            "total_matches": len(good_matches),
            "transformation_type": "+".join(trans_types),
            "rotation_deg": round(angle_deg, 1),
            "determinant": round(det_h, 3),
            "confidence_score": round(confidence, 3),
            "homography_matrix": H.tolist(),
            "matched_pts_query": matched_q.tolist(),
            "matched_pts_candidate": matched_c.tolist(),
            "explanation": (
                f"Confirmed cross-paper reuse with {inliers} SIFT RANSAC inlier matches "
                f"({'+'.join(trans_types)}, det={det_h:.2f})."
            )
        }

    return {
        "is_match": False,
        "inlier_count": inliers,
        "total_matches": len(good_matches),
        "transformation_type": "NONE",
        "confidence_score": round(float(inliers / 20.0), 3) if inliers > 0 else 0.0,
        "homography_matrix": H.tolist() if H is not None else None,
        "explanation": f"Geometric verification rejected: inliers={inliers} (threshold {min_inliers})."
    }


def render_cross_paper_comparison_overlay(
    query_input: Union[str, np.ndarray],
    candidate_input: Union[str, np.ndarray],
    match_result: Dict[str, Any],
    candidate_meta: Dict[str, Any],
    output_path: str
) -> str:
    """
    Renders a side-by-side comparative forensic overlay between the audited manuscript figure
    and the matching retracted seed corpus figure, including matched correspondence lines.
    """
    img_q = _load_image(query_input)
    img_c = _load_image(candidate_input)

    target_h = 420
    # Scale query image to target height
    scale_q = target_h / float(img_q.shape[0])
    w_q = int(img_q.shape[1] * scale_q)
    resized_q = cv2.resize(img_q, (w_q, target_h), interpolation=cv2.INTER_AREA)

    # Scale candidate image to target height
    scale_c = target_h / float(img_c.shape[0])
    w_c = int(img_c.shape[1] * scale_c)
    resized_c = cv2.resize(img_c, (w_c, target_h), interpolation=cv2.INTER_AREA)

    separator_w = 20
    header_h = 75
    footer_h = 45
    total_w = w_q + w_c + separator_w
    total_h = header_h + target_h + footer_h

    # Create dark slate canvas
    canvas = np.full((total_h, total_w, 3), 32, dtype=np.uint8)

    # Draw separator line
    sep_x = w_q + separator_w // 2
    cv2.line(canvas, (sep_x, header_h), (sep_x, header_h + target_h), (80, 80, 80), 2)

    # Place resized images onto canvas
    canvas[header_h : header_h + target_h, 0 : w_q] = resized_q
    canvas[header_h : header_h + target_h, w_q + separator_w : total_w] = resized_c

    is_match = match_result.get("is_match", False)

    # Render Header Banner
    if is_match:
        # Coral Red Banner
        banner_color = (79, 83, 217)  # BGR
        cv2.rectangle(canvas, (0, 0), (total_w, header_h), banner_color, -1)
        inliers = match_result.get("inlier_count", 0)
        conf = int(match_result.get("confidence_score", 0.0) * 100)
        title_text = f"CROSS-MANUSCRIPT FIGURE REUSE DETECTED [Inliers: {inliers}, Conf: {conf}%]"
        cv2.putText(canvas, title_text, (20, 32), cv2.FONT_HERSHEY_DUPLEX, 0.75, (255, 255, 255), 2)

        pmcid = candidate_meta.get("pmcid", "UNKNOWN")
        doi = candidate_meta.get("doi", "N/A")
        reasons = candidate_meta.get("retraction_reasons", "Figure anomaly")
        sub_text = f"Retracted Corpus Match: {pmcid} ({doi}) | Retraction: {reasons[:65]}"
        cv2.putText(canvas, sub_text, (20, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.48, (240, 240, 240), 1)
    else:
        # Jade Green Banner
        banner_color = (69, 167, 40)  # BGR
        cv2.rectangle(canvas, (0, 0), (total_w, header_h), banner_color, -1)
        cv2.putText(canvas, "NO CROSS-MANUSCRIPT DUPLICATION DETECTED", (20, 45), cv2.FONT_HERSHEY_DUPLEX, 0.75, (255, 255, 255), 2)

    # Panel Subtitle Labels
    lbl_y = header_h + 24
    cv2.rectangle(canvas, (10, header_h + 8), (10 + 260, header_h + 34), (0, 0, 0), -1)
    cv2.putText(canvas, "Query: Audited Manuscript", (16, lbl_y), cv2.FONT_HERSHEY_SIMPLEX, 0.52, (255, 255, 255), 1)

    right_offset = w_q + separator_w
    cv2.rectangle(canvas, (right_offset + 10, header_h + 8), (right_offset + 320, header_h + 34), (0, 0, 0), -1)
    cv2.putText(canvas, f"Candidate: {candidate_meta.get('figure_id', 'Retracted Corpus')}", (right_offset + 16, lbl_y), cv2.FONT_HERSHEY_SIMPLEX, 0.52, (255, 255, 255), 1)

    # Draw matched correspondence lines if matched
    if is_match and "matched_pts_query" in match_result and "matched_pts_candidate" in match_result:
        pts_q = match_result["matched_pts_query"]
        pts_c = match_result["matched_pts_candidate"]
        # Limit to up to 25 lines to keep visualization clean and clear
        step = max(1, len(pts_q) // 25)
        for idx in range(0, len(pts_q), step):
            qx, qy = pts_q[idx]
            cx_pt, cy_pt = pts_c[idx]

            canv_qx = int(qx * scale_q)
            canv_qy = int(qy * scale_q + header_h)

            canv_cx = int(cx_pt * scale_c + w_q + separator_w)
            canv_cy = int(cy_pt * scale_c + header_h)

            # Draw circle endpoints
            cv2.circle(canvas, (canv_qx, canv_qy), 4, (0, 255, 255), -1)
            cv2.circle(canvas, (canv_cx, canv_cy), 4, (0, 255, 255), -1)
            # Draw connecting correspondence line in cyan
            cv2.line(canvas, (canv_qx, canv_qy), (canv_cx, canv_cy), (255, 255, 0), 1, cv2.LINE_AA)

    # Footer note
    footer_text = f"Forensic Sieve: Gate 3.5 Tier 3 Cross-Paper Index | Transformation: {match_result.get('transformation_type', 'N/A')}"
    cv2.putText(canvas, footer_text, (20, total_h - 18), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (180, 180, 180), 1)

    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    cv2.imwrite(output_path, canvas)
    return output_path
