"""
Visual Discrepancy Overlay Renderer (Gate 3.5).
Annotates figure images with color-coded bounding boxes and banners:
- Emerald Green (#10B981): Statistically verified points and clean comparisons.
- Coral Red (#EF4444): Arithmetic failures, significance inversions, and truncated bounds.
- Amber Yellow (#F59E0B): Warning flags and outlier indicators.
"""

import os
from typing import Dict, Any, Optional
import cv2
import numpy as np


def render_chart_visual_overlay(
    image_path: str,
    audit_report: Dict[str, Any],
    output_path: Optional[str] = None
) -> str:
    """
    Renders an annotated forensic audit overlay onto the input figure image.
    Adds a top status banner and draws color-coded bounding boxes with discrepancy callouts.
    """
    img = cv2.imread(image_path)
    if img is None:
        raise ValueError(f"Could not load image at {image_path}")

    h_img, w_img = img.shape[:2]
    verdict = audit_report.get("verdict", "CLEAN")
    discrepancies = audit_report.get("discrepancies", [])

    # 1. Create a Top Header Banner
    banner_h = 70
    banner = np.zeros((banner_h, w_img, 3), dtype=np.uint8)

    if verdict == "FLAGGED_FORENSIC_ANOMALY":
        # Red banner: BGR (30, 30, 200)
        banner[:] = (40, 40, 220)
        banner_text = f"FORENSIC ANOMALY DETECTED: {len(discrepancies)} Discrepancy Flag(s)"
        sub_text = "FastMCP Gate 3.5: Statistical & Visual Consistency Violation"
    else:
        # Green banner: BGR (50, 160, 40)
        banner[:] = (40, 175, 40)
        banner_text = "VERIFIED: STATISTICALLY SELF-CONSISTENT"
        sub_text = "FastMCP Gate 3.5: Clean Divisibility & Consistent Comparisons"

    cv2.putText(banner, banner_text, (20, 32), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2, cv2.LINE_AA)
    cv2.putText(banner, sub_text, (20, 56), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (230, 245, 230), 1, cv2.LINE_AA)

    # 2. Draw annotations on the main image
    annotated = img.copy()

    # Draw discrepancy bounding boxes
    for idx, disc in enumerate(discrepancies):
        bbox = disc.get("bbox")
        d_type = disc.get("type", "ANOMALY")
        
        if bbox and len(bbox) == 4:
            ymin, xmin, ymax, xmax = bbox
            # Ensure valid bounds
            ymin, ymax = max(0, ymin), min(h_img, ymax)
            xmin, xmax = max(0, xmin), min(w_img, xmax)

            # Red box with thickness 3
            cv2.rectangle(annotated, (xmin, ymin), (xmax, ymax), (0, 0, 235), 3)

            # Callout tag
            tag_text = f"FAIL: {d_type}"
            tag_y = max(20, ymin - 8)
            cv2.rectangle(annotated, (xmin, tag_y - 18), (xmin + len(tag_text) * 11, tag_y + 4), (0, 0, 200), -1)
            cv2.putText(annotated, tag_text, (xmin + 4, tag_y - 2), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (255, 255, 255), 1, cv2.LINE_AA)
        else:
            # If no exact bbox, draw callout badge on the right
            callout_y = 100 + idx * 40
            callout_txt = f"! {d_type}: {disc.get('target', '')}"
            cv2.rectangle(annotated, (w_img - 380, callout_y - 20), (w_img - 20, callout_y + 10), (0, 0, 200), -1)
            cv2.putText(annotated, callout_txt[:40], (w_img - 370, callout_y), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (255, 255, 255), 1, cv2.LINE_AA)

    # If clean, draw subtle green verification indicator in bottom corner
    if verdict == "CLEAN":
        cv2.rectangle(annotated, (w_img - 240, h_img - 40), (w_img - 15, h_img - 10), (40, 160, 40), -1)
        cv2.putText(annotated, "[+] Math & Brackets PASS", (w_img - 230, h_img - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (255, 255, 255), 1, cv2.LINE_AA)

    # 3. Stack banner above annotated figure
    final_img = np.vstack([banner, annotated])

    if not output_path:
        base_name = os.path.splitext(os.path.basename(image_path))[0]
        out_dir = os.path.join("data", "overlays")
        os.makedirs(out_dir, exist_ok=True)
        output_path = os.path.join(out_dir, f"{base_name}_audit_overlay.png")

    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    cv2.imwrite(output_path, final_img)

    return output_path
