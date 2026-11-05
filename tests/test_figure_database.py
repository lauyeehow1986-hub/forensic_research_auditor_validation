import os
import sys
import numpy as np
import cv2
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.vision.figure_database import FigureDatabase


def create_synthetic_panel(pattern_type: str, size: int = 150) -> np.ndarray:
    img = np.zeros((size, size, 3), dtype=np.uint8)
    if pattern_type == "circle_rect":
        cv2.circle(img, (size // 2, size // 2), size // 3, (255, 255, 255), -1)
        cv2.rectangle(img, (20, 20), (size // 3, size // 3), (128, 128, 128), -1)
    elif pattern_type == "diagonal_stripes":
        for i in range(0, size, 15):
            cv2.line(img, (0, i), (i, 0), (200, 200, 200), 3)
    elif pattern_type == "noise":
        img = np.random.randint(0, 256, (size, size, 3), dtype=np.uint8)
    return img


def test_database_initialization_and_schema(tmp_path):
    db_file = str(tmp_path / "test_figures.duckdb")
    db = FigureDatabase(db_path=db_file)
    stats = db.get_stats()
    assert stats["total_figures"] == 0
    assert stats["total_studies"] == 0
    db.close()


def test_idempotent_upsert_and_expansion(tmp_path):
    db_file = str(tmp_path / "test_figures.duckdb")
    db = FigureDatabase(db_path=db_file)

    img1 = create_synthetic_panel("circle_rect")
    img_path1 = str(tmp_path / "fig1.png")
    cv2.imwrite(img_path1, img1)

    # First insert: Seed Study 1
    db.index_figure(
        figure_id="PMC1001_Fig1_A",
        pmcid="PMC1001",
        doi="10.1001/test.1",
        panel_id="A",
        is_retracted=True,
        retraction_reasons="Image duplication and splicing",
        img_input=img_path1,
        figure_path=img_path1
    )

    stats = db.get_stats()
    assert stats["total_figures"] == 1
    assert stats["total_studies"] == 1

    # Idempotent re-index of the exact same figure (should update, not duplicate)
    db.index_figure(
        figure_id="PMC1001_Fig1_A",
        pmcid="PMC1001",
        doi="10.1001/test.1",
        panel_id="A",
        is_retracted=True,
        retraction_reasons="Confirmed paper-mill figure reuse",
        img_input=img_path1,
        figure_path=img_path1
    )

    stats = db.get_stats()
    assert stats["total_figures"] == 1

    # Expand database with Study 2 (dynamic future expansion)
    img2 = create_synthetic_panel("diagonal_stripes")
    img_path2 = str(tmp_path / "fig2.png")
    cv2.imwrite(img_path2, img2)

    db.index_figure(
        figure_id="PMC2002_Fig2_B",
        pmcid="PMC2002",
        doi="10.2002/test.2",
        panel_id="B",
        is_retracted=True,
        retraction_reasons="Falsified microscopy figures",
        img_input=img_path2,
        figure_path=img_path2
    )

    stats = db.get_stats()
    assert stats["total_figures"] == 2
    assert stats["total_studies"] == 2
    db.close()


def test_query_candidates_matching(tmp_path):
    db_file = str(tmp_path / "test_figures.duckdb")
    db = FigureDatabase(db_path=db_file)

    img_circle = create_synthetic_panel("circle_rect", size=180)
    p_circle = str(tmp_path / "target_retracted.png")
    cv2.imwrite(p_circle, img_circle)

    img_stripes = create_synthetic_panel("diagonal_stripes", size=180)
    p_stripes = str(tmp_path / "unrelated.png")
    cv2.imwrite(p_stripes, img_stripes)

    db.index_figure("PMC111_Fig1_A", "PMC111", "10.111/r1", "A", True, "Duplication", p_circle, p_circle)
    db.index_figure("PMC222_Fig2_A", "PMC222", "10.222/r2", "A", True, "Data anomaly", p_stripes, p_stripes)

    # Query with a scaled and cropped version of img_circle
    query_img = cv2.resize(img_circle, (240, 240))
    candidates = db.query_candidates(query_img, top_k=5, max_hamming=16)

    assert len(candidates) >= 1
    top_match = candidates[0]
    assert top_match["figure_id"] == "PMC111_Fig1_A"
    assert top_match["pmcid"] == "PMC111"
    assert top_match["hamming_phash"] <= 2
    assert top_match["cosine_similarity"] > 0.85
    db.close()


def test_index_study_figures_and_manifest_expansion(tmp_path):
    import json
    db_file = str(tmp_path / "test_figures.duckdb")
    db = FigureDatabase(db_path=db_file)

    # Create composite multi-panel figure
    composite = np.full((300, 300, 3), 255, dtype=np.uint8)
    # Panel 1 (left)
    cv2.circle(composite, (75, 150), 40, (100, 100, 100), -1)
    # Panel 2 (right)
    cv2.rectangle(composite, (180, 50), (280, 250), (50, 50, 50), -1)

    fig_path = str(tmp_path / "Fig1_composite.png")
    cv2.imwrite(fig_path, composite)

    count = db.index_study_figures(
        pmcid="PMC9999",
        doi="10.9999/paper",
        figure_paths=[fig_path],
        is_retracted=True,
        retraction_reasons="Manipulated panels",
        split_panels=True
    )
    # Should index full figure + any detected panels
    assert count >= 1

    # Test bulk indexing via JSON manifest (future expansion to 10k+)
    manifest_data = [{
        "pmcid": "PMC8888",
        "doi": "10.8888/retracted",
        "figure_paths": [fig_path],
        "is_retracted": True,
        "retraction_reasons": "Batch imported retraction"
    }]
    manifest_file = str(tmp_path / "seed_manifest.json")
    with open(manifest_file, "w", encoding="utf-8") as f:
        json.dump(manifest_data, f)

    batch_count = db.bulk_index_from_manifest(manifest_file)
    assert batch_count >= 1

    stats = db.get_stats()
    assert stats["total_studies"] == 2
    assert stats["total_retracted_studies"] == 2
    db.close()

