"""
Figure Fingerprint Module: Perceptual Hashes (pHash, dHash) & Dense Embedding Engine.

Provides rapid, robust fingerprinting for scientific figures and panels to detect
figure duplication, cropping, scaling, and reuse across manuscripts.
"""

from typing import Union, List
import cv2
import numpy as np


def _to_gray_array(img_input: Union[str, np.ndarray]) -> np.ndarray:
    """Helper to convert a file path or image array to grayscale uint8."""
    if isinstance(img_input, str):
        img = cv2.imread(img_input, cv2.IMREAD_COLOR)
        if img is None:
            raise FileNotFoundError(f"Failed to load image from path: {img_input}")
    else:
        img = img_input

    if len(img.shape) == 3:
        if img.shape[2] == 4:
            img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
        return cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    return img.copy()


def compute_phash(img_input: Union[str, np.ndarray], hash_size: int = 8, highfreq_factor: int = 4) -> str:
    """
    Computes a 64-bit DCT perceptual hash (pHash) represented as a 16-character hex string.

    Resizes to (hash_size * highfreq_factor)^2, computes 2D DCT, extracts top-left
    low frequencies, and computes median binary mask.
    """
    gray = _to_gray_array(img_input)
    img_size = hash_size * highfreq_factor
    resized = cv2.resize(gray, (img_size, img_size), interpolation=cv2.INTER_AREA)

    # 2D DCT
    dct = cv2.dct(np.float32(resized))

    # Extract low frequency coefficients (top-left hash_size x hash_size)
    low_freq = dct[0:hash_size, 0:hash_size]

    # Calculate median excluding DC term (0,0) for robust frequency comparison
    ac_terms = low_freq.flatten()[1:]
    median_val = float(np.median(ac_terms))

    # Generate 64-bit mask
    mask = low_freq > median_val

    # Convert 64 booleans to 16-character hex string
    bit_str = "".join("1" if b else "0" for b in mask.flatten())
    int_val = int(bit_str, 2)
    return f"{int_val:016x}"


def compute_dhash(img_input: Union[str, np.ndarray], hash_size: int = 8) -> str:
    """
    Computes a 64-bit Difference Hash (dHash) based on horizontal pixel gradients.

    Resizes to (hash_size + 1, hash_size), checks adjacent horizontal differences.
    """
    gray = _to_gray_array(img_input)
    # Width is hash_size + 1 (9), Height is hash_size (8)
    resized = cv2.resize(gray, (hash_size + 1, hash_size), interpolation=cv2.INTER_AREA)

    diff = resized[:, 1:] > resized[:, :-1]
    bit_str = "".join("1" if b else "0" for b in diff.flatten())
    int_val = int(bit_str, 2)
    return f"{int_val:016x}"


def hamming_distance(h1: str, h2: str) -> int:
    """Computes the Hamming distance between two hex hash strings."""
    v1 = int(h1, 16)
    v2 = int(h2, 16)
    xor_val = v1 ^ v2
    return xor_val.bit_count()


def compute_figure_embedding(img_input: Union[str, np.ndarray], embed_dim: int = 256) -> List[float]:
    """
    Computes a dense, L2-normalized 256-dimensional feature vector.

    Fuses spatial pyramid gradient orientation histograms (128 dims) with
    low-frequency discrete cosine transform power spectrum (128 dims).
    """
    gray = _to_gray_array(img_input)
    standardized = cv2.resize(gray, (128, 128), interpolation=cv2.INTER_AREA)

    # 1. Spatial Pyramid HOG Descriptor (4x4 spatial grid, 8 orientation bins = 128 dims)
    grad_x = cv2.Sobel(standardized, cv2.CV_32F, 1, 0, ksize=3)
    grad_y = cv2.Sobel(standardized, cv2.CV_32F, 0, 1, ksize=3)
    mag, ang = cv2.cartToPolar(grad_x, grad_y, angleInDegrees=True)

    # Map angles 0-180 into 8 bins (each 22.5 deg)
    ang_unsigned = np.mod(ang, 180.0)
    bin_idx = (ang_unsigned / 22.5).astype(np.int32)
    bin_idx = np.clip(bin_idx, 0, 7)

    cell_h, cell_w = 32, 32  # 4x4 grid of 32x32 cells
    hog_features = []
    for r in range(4):
        for c in range(4):
            cell_mag = mag[r * cell_h : (r + 1) * cell_h, c * cell_w : (c + 1) * cell_w]
            cell_bins = bin_idx[r * cell_h : (r + 1) * cell_h, c * cell_w : (c + 1) * cell_w]
            hist = np.zeros(8, dtype=np.float32)
            for b in range(8):
                hist[b] = np.sum(cell_mag[cell_bins == b])
            # Local cell normalization
            norm = np.linalg.norm(hist) + 1e-6
            hog_features.extend((hist / norm).tolist())

    # 2. Low-frequency 2D DCT Spectrum (128 dims)
    dct = cv2.dct(np.float32(standardized))
    # Extract 16x8 block = 128 coefficients, taking absolute magnitude
    dct_block = np.abs(dct[0:16, 0:8]).flatten()
    dct_norm = np.linalg.norm(dct_block) + 1e-6
    dct_features = (dct_block / dct_norm).tolist()

    # Fuse features
    raw_vec = np.array(hog_features + dct_features, dtype=np.float32)
    if len(raw_vec) != embed_dim:
        # Resize or pad/trim if embed_dim differs
        if len(raw_vec) > embed_dim:
            raw_vec = raw_vec[:embed_dim]
        else:
            raw_vec = np.pad(raw_vec, (0, embed_dim - len(raw_vec)))

    # Global L2 Normalization
    total_norm = np.linalg.norm(raw_vec) + 1e-9
    normalized_vec = raw_vec / total_norm
    return [float(x) for x in normalized_vec]
