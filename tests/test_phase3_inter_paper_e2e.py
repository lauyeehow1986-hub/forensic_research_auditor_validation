import os
import sys
import numpy as np
import cv2
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.vision.figure_database import FigureDatabase
from mcp_servers.forensic_chart_mcp import (
    index_study_figure_set,
    audit_figure_against_retraction_database
)


def create_cell_field(seed: int, size: int = 320) -> np.ndarray:
    np.random.seed(seed)
    img = np.zeros((size, size, 3), dtype=np.uint8)
    for _ in range(35):
        cx = np.random.randint(40, size - 40)
        cy = np.random.randint(40, size - 40)
        r = np.random.randint(12, 26)
        color = (int(np.random.randint(100, 240)), int(np.random.randint(120, 220)), int(np.random.randint(90, 200)))
        cv2.circle(img, (cx, cy), r, color, -1)
        cv2.circle(img, (cx, cy), max(2, r // 3), (255, 255, 255), -1)
    noise = np.random.randint(0, 20, (size, size, 3), dtype=np.uint8)
    return cv2.add(img, noise)


def create_bar_chart(title: str, size: int = 320) -> np.ndarray:
    img = np.full((size, size, 3), 255, dtype=np.uint8)
    cv2.line(img, (50, 280), (290, 280), (0, 0, 0), 2)  # X-axis
    cv2.line(img, (50, 40), (50, 280), (0, 0, 0), 2)   # Y-axis
    # Draw two bars
    cv2.rectangle(img, (80, 120), (140, 280), (70, 130, 180), -1)
    cv2.rectangle(img, (180, 70), (240, 280), (205, 92, 92), -1)
    cv2.putText(img, title, (60, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 1)
    return img


def test_end_to_end_cross_paper_reuse_pipeline(tmp_path):
    db_path = str(tmp_path / "e2e_retracted_figures.duckdb")

    # 1. Prepare Seed Study PMC70001 (retracted paper with microscopy figure)
    micro_img_1 = create_cell_field(seed=404)
    path_pmc70001 = str(tmp_path / "PMC70001_Fig2.png")
    cv2.imwrite(path_pmc70001, micro_img_1)

    # 2. Prepare Seed Study PMC70002 (retracted paper with bar chart)
    chart_img_2 = create_bar_chart("Seed Retracted Chart")
    path_pmc70002 = str(tmp_path / "PMC70002_Fig1.png")
    cv2.imwrite(path_pmc70002, chart_img_2)

    # 3. Index both seed studies into DuckDB
    res1 = index_study_figure_set(
        pmcid="PMC70001",
        doi="10.1001/retracted.70001",
        figure_paths=[path_pmc70001],
        is_retracted=True,
        retraction_reasons="Paper-mill microscopy image recycling across journals",
        db_path=db_path
    )
    assert res1["indexed_count"] >= 1

    res2 = index_study_figure_set(
        pmcid="PMC70002",
        doi="10.1001/retracted.70002",
        figure_paths=[path_pmc70002],
        is_retracted=True,
        retraction_reasons="Falsified bar chart values",
        db_path=db_path
    )
    assert res2["indexed_count"] >= 1

    # Check stats
    db = FigureDatabase(db_path=db_path)
    stats_seed = db.get_stats()
    assert stats_seed["total_studies"] == 2
    db.close()

    # 4. Now, an audited new manuscript arrives: "Study X"
    # Study X Fig 1: A clean, authentic newly generated chart
    study_x_fig1 = create_bar_chart("Authentic Study X Chart")
    path_x_fig1 = str(tmp_path / "StudyX_Fig1.png")
    cv2.imwrite(path_x_fig1, study_x_fig1)

    # Study X Fig 2: Tampered/reused microscopy panel stolen from PMC70001 (cropped & rotated 90 deg)
    study_x_fig2 = cv2.rotate(micro_img_1[20:300, 20:300], cv2.ROTATE_90_COUNTERCLOCKWISE)
    path_x_fig2 = str(tmp_path / "StudyX_Fig2.png")
    cv2.imwrite(path_x_fig2, study_x_fig2)

    # 5. Audit Study X Fig 1 (Authentic)
    overlay_clean = str(tmp_path / "overlay_study_x_fig1.png")
    audit_fig1 = audit_figure_against_retraction_database(
        image_path=path_x_fig1,
        db_path=db_path,
        output_overlay_path=overlay_clean
    )
    assert audit_fig1["verdict"] == "CLEAN"
    assert audit_fig1["matched_study"] is None

    # 6. Audit Study X Fig 2 (Recycled from PMC70001)
    overlay_match = str(tmp_path / "overlay_study_x_fig2.png")
    audit_fig2 = audit_figure_against_retraction_database(
        image_path=path_x_fig2,
        db_path=db_path,
        output_overlay_path=overlay_match
    )
    assert audit_fig2["verdict"] == "FLAGGED_CROSS_PAPER_REUSE"
    assert audit_fig2["matched_study"] is not None
    assert audit_fig2["matched_study"]["pmcid"] == "PMC70001"
    assert audit_fig2["inliers"] >= 12
    assert "ROTATION" in audit_fig2["match_details"]["transformation_type"]
    assert os.path.exists(overlay_match)

    # 7. Test dynamic expansion to future studies (beyond 5,000)
    # Add Study 3 to database
    img_seed3 = create_cell_field(seed=808)
    path_pmc70003 = str(tmp_path / "PMC70003_Fig4.png")
    cv2.imwrite(path_pmc70003, img_seed3)

    res3 = index_study_figure_set(
        pmcid="PMC70003",
        doi="10.1001/retracted.70003",
        figure_paths=[path_pmc70003],
        is_retracted=True,
        retraction_reasons="Future incremental wave study",
        db_path=db_path
    )
    assert res3["indexed_count"] >= 1
    assert res3["stats"]["total_studies"] == 3
