import os
import sys
import numpy as np
import cv2
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from mcp_servers.forensic_chart_mcp import (
    index_study_figure_set,
    audit_figure_against_retraction_database
)


def create_synthetic_field(seed: int = 55, size: int = 300) -> np.ndarray:
    np.random.seed(seed)
    img = np.zeros((size, size, 3), dtype=np.uint8)
    for _ in range(30):
        cx = np.random.randint(40, size - 40)
        cy = np.random.randint(40, size - 40)
        r = np.random.randint(10, 25)
        color = (int(np.random.randint(120, 250)), int(np.random.randint(100, 220)), int(np.random.randint(80, 180)))
        cv2.circle(img, (cx, cy), r, color, -1)
        cv2.circle(img, (cx, cy), max(2, r // 3), (255, 255, 255), -1)
    noise = np.random.randint(0, 25, (size, size, 3), dtype=np.uint8)
    return cv2.add(img, noise)


def test_mcp_figure_indexing_and_audit(tmp_path):
    db_file = str(tmp_path / "test_mcp_figures.duckdb")

    # 1. Create retracted study figure
    retracted_img = create_synthetic_field(seed=777)
    retracted_path = str(tmp_path / "PMC3333_Fig1.png")
    cv2.imwrite(retracted_path, retracted_img)

    # 2. Index retracted study
    idx_res = index_study_figure_set(
        pmcid="PMC3333",
        doi="10.1038/example3333",
        figure_paths=[retracted_path],
        is_retracted=True,
        retraction_reasons="Plagiarized microscopy images",
        db_path=db_file,
        split_panels=False
    )
    assert idx_res["indexed_count"] >= 1
    assert idx_res["stats"]["total_figures"] >= 1

    # 3. Create query image (reused panel: rotated 90 deg)
    reused_query = cv2.rotate(retracted_img, cv2.ROTATE_90_CLOCKWISE)
    query_path = str(tmp_path / "query_manuscript_fig.png")
    cv2.imwrite(query_path, reused_query)

    overlay_out = str(tmp_path / "overlay_cross_paper.png")

    # 4. Audit query figure against retraction database
    audit_res = audit_figure_against_retraction_database(
        image_path=query_path,
        top_k=5,
        db_path=db_file,
        output_overlay_path=overlay_out
    )

    assert audit_res["verdict"] == "FLAGGED_CROSS_PAPER_REUSE"
    assert audit_res["matched_study"]["pmcid"] == "PMC3333"
    assert audit_res["matched_study"]["doi"] == "10.1038/example3333"
    assert audit_res["inliers"] >= 12
    assert audit_res["overlay_path"] is not None
    assert os.path.exists(overlay_out)

    # 5. Audit unrelated clean figure
    clean_img = create_synthetic_field(seed=12345)
    clean_path = str(tmp_path / "clean_manuscript_fig.png")
    cv2.imwrite(clean_path, clean_img)

    clean_audit = audit_figure_against_retraction_database(
        image_path=clean_path,
        top_k=5,
        db_path=db_file
    )
    assert clean_audit["verdict"] == "CLEAN"
    assert clean_audit["matched_study"] is None
