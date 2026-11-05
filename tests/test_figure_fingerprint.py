import os
import sys
import numpy as np
import cv2
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.vision.figure_fingerprint import (
    compute_phash,
    compute_dhash,
    hamming_distance,
    compute_figure_embedding
)


def test_phash_identical_and_scaled():
    # Create test image with distinct pattern
    img1 = np.zeros((200, 200, 3), dtype=np.uint8)
    cv2.circle(img1, (100, 100), 50, (255, 255, 255), -1)
    cv2.rectangle(img1, (30, 30), (80, 80), (128, 128, 128), -1)

    # Scale to different size
    img2 = cv2.resize(img1, (350, 350))

    h1 = compute_phash(img1)
    h2 = compute_phash(img2)

    assert isinstance(h1, str)
    assert len(h1) == 16
    assert isinstance(h2, str)
    # Scaled version should have Hamming distance near 0 (<= 2)
    dist = hamming_distance(h1, h2)
    assert dist <= 2


def test_dhash_different_images():
    img1 = np.zeros((200, 200, 3), dtype=np.uint8)
    cv2.circle(img1, (100, 100), 50, (255, 255, 255), -1)

    img2 = np.full((200, 200, 3), 255, dtype=np.uint8)
    cv2.line(img2, (0, 0), (200, 200), (0, 0, 0), 5)

    dh1 = compute_dhash(img1)
    dh2 = compute_dhash(img2)

    dist = hamming_distance(dh1, dh2)
    # Completely different patterns should have high Hamming distance
    assert dist >= 10


def test_figure_embedding_properties():
    img = np.random.randint(0, 255, (150, 150, 3), dtype=np.uint8)
    emb = compute_figure_embedding(img, embed_dim=256)

    assert isinstance(emb, list)
    assert len(emb) == 256
    # Vector should be L2-normalized (norm approx 1.0)
    norm = np.linalg.norm(np.array(emb))
    assert pytest.approx(norm, abs=1e-3) == 1.0


def test_fingerprint_file_path_and_exact_match(tmp_path):
    # Test file path input and exact match 0 distance
    img_path = str(tmp_path / "sample.png")
    test_img = np.zeros((100, 100, 3), dtype=np.uint8)
    cv2.circle(test_img, (50, 50), 30, (200, 200, 200), -1)
    cv2.imwrite(img_path, test_img)

    h_path = compute_phash(img_path)
    h_arr = compute_phash(test_img)
    assert h_path == h_arr
    assert hamming_distance(h_path, h_arr) == 0

    dh_path = compute_dhash(img_path)
    dh_arr = compute_dhash(test_img)
    assert dh_path == dh_arr
    assert hamming_distance(dh_path, dh_arr) == 0

    emb = compute_figure_embedding(img_path)
    assert len(emb) == 256

    with pytest.raises(FileNotFoundError):
        compute_phash("non_existent_image_path_12345.png")

