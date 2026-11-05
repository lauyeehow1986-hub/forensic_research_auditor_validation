"""
Visual Splicing Overlay Renderer (Gate 3.5 Phase 2).
Renders publication-ready annotated images highlighting intra-paper tampering:
- Coral Red (#EF4444): Cloned band patches, cut-and-paste borders, and transformed microscopy fields.
- Emerald Green (#10B981): Statistically verified clean figures.
- Correspondence lines connecting duplicated elements across lanes or panels.
"""

import os
from typing import Dict, Any, Optional
import numpy as np
import cv2


def render_splicing_visual_overlay(
    image_path: str,
    audit_report: Dict[str, Any],
    output_path: Optional[str] = None
) -> str:
    """
    Renders an annotated forensic overlay onto the input figure.
    Adds a top status banner, draws bounding boxes, callouts, and correspondence lines.
    """
    img = cv2.imread(image_path)
    if img is None:
        raise ValueError(f"Could not load image at {image_path}")

    h_img, w_img = img.shape[:2]
    verdict = audit_report.get("verdict", "CLEAN")
    discrepancies = audit_report.get("discrepancies", [])
    is_anomaly = verdict.startswith("FLAGGED")

    # 1. Top Header Banner
    banner_h = 70
    banner = np.zeros((banner_h, w_img, 3), dtype=np.uint8)

    if is_anomaly:
        banner[:] = (40, 40, 220)  # Coral Red
        banner_text = f"INTRA-PAPER TAMPERING DETECTED: {len(discrepancies)} Splicing Anomaly(s)"
        sub_text = "FastMCP Gate 3.5 Phase 2: Band Cloning, Splice Border, or Recycled Microscopy"
    else:
        banner[:] = (40, 175, 40)  # Emerald Green
        banner_text = "VERIFIED: CLEAN INTRA-FIGURE CONTINUITY"
        sub_text = "FastMCP Gate 3.5 Phase 2: Independent Biological Noise & Unique Panels"

    cv2.putText(banner, banner_text, (20, 32), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (255, 255, 255), 2, cv2.LINE_AA)
    cv2.putText(banner, sub_text, (20, 56), cv2.FONT_HERSHEY_SIMPLEX, 0.50, (230, 245, 230), 1, cv2.LINE_AA)

    annotated = img.copy()

    # 2. Draw annotations for each discrepancy
    for disc in discrepancies:
        d_type = disc.get("type", "ANOMALY")

        if d_type == "CLONED_BAND":
            b_a = disc.get("bbox_a")
            b_b = disc.get("bbox_b")
            ncc = disc.get("ncc_score", 1.0)

            if b_a and b_b:
                cv2.rectangle(annotated, (b_a[1], b_a[0]), (b_a[3], b_a[2]), (40, 40, 230), 2)
                cv2.rectangle(annotated, (b_b[1], b_b[0]), (b_b[3], b_b[2]), (40, 40, 230), 2)

                # Correspondence line
                pt_a = ((b_a[1] + b_a[3]) // 2, (b_a[0] + b_a[2]) // 2)
                pt_b = ((b_b[1] + b_b[3]) // 2, (b_b[0] + b_b[2]) // 2)
                cv2.line(annotated, pt_a, pt_b, (20, 180, 240), 2, cv2.LINE_AA)

                # Badge
                badge_txt = f"CLONED BAND (NCC={ncc:.2f})"
                cv2.putText(annotated, badge_txt, (b_a[1], max(15, b_a[0] - 6)),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 0, 200), 1, cv2.LINE_AA)

        elif d_type == "SPLICED_LANE_BORDER":
            sx = disc.get("splice_x", 0)
            c_step = disc.get("contrast_step", 0.0)
            cv2.line(annotated, (sx, 0), (sx, h_img), (30, 30, 220), 2, cv2.LINE_AA)
            cv2.putText(annotated, f"SPLICE BORDER (step={c_step:.1f})", (max(10, sx - 80), 20),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 0, 200), 1, cv2.LINE_AA)

        elif d_type == "TRANSFORMED_MICROGRAPH_DUPLICATION":
            b_a = disc.get("bbox_a")
            b_b = disc.get("bbox_b")
            inliers = disc.get("inlier_matches", 0)
            trans_type = disc.get("transformation_type", "DUPLICATE")

            if b_a and b_b:
                cv2.rectangle(annotated, (b_a[1], b_a[0]), (b_a[3], b_a[2]), (30, 30, 220), 3)
                cv2.rectangle(annotated, (b_b[1], b_b[0]), (b_b[3], b_b[2]), (30, 30, 220), 3)

                pt_a = ((b_a[1] + b_a[3]) // 2, (b_a[0] + b_a[2]) // 2)
                pt_b = ((b_b[1] + b_b[3]) // 2, (b_b[0] + b_b[2]) // 2)
                cv2.line(annotated, pt_a, pt_b, (0, 165, 255), 2, cv2.LINE_AA)

                badge_txt = f"RECYCLED FIELD ({trans_type}, {inliers} inliers)"
                cv2.putText(annotated, badge_txt, (b_b[1] + 10, b_b[0] + 25),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.50, (0, 0, 220), 2, cv2.LINE_AA)

    # Combine Banner and Annotated Image
    final_img = np.vstack([banner, annotated])

    if output_path is None:
        base, ext = os.path.splitext(image_path)
        output_path = f"{base}_splicing_audit{ext}"

    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    cv2.imwrite(output_path, final_img)

    return output_path
