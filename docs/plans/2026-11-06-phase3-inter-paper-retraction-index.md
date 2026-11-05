# Implementation Plan: Phase 3 Inter-Paper Retraction Fingerprint Index (The Lean ImageTwin)

**Goal:** Build a dynamic, incrementally updatable DuckDB-backed visual fingerprint index (pHash + Dense Feature Vector + SIFT/RANSAC verification) that catches figure reuse across different manuscripts (e.g., seeding with 5,000 retracted studies and scaling to 10k, 20k, 50k+ in the future).

---

## Architecture Overview

```
              [ Query Figure from New Manuscript ]
                               │
                               ▼
        ┌──────────────────────────────────────────────┐
        │ Stage 1: Perceptual Hashes (pHash / dHash)   │
        │ 64-bit DCT perceptual hash.                  │
        │ Fast Hamming distance filter in DuckDB.      │
        └──────────────────────┬───────────────────────┘
                               ▼ Top 50 Candidates
        ┌──────────────────────────────────────────────┐
        │ Stage 2: Dense Feature Vector Cosine Search  │
        │ 256-dimensional normalized vision embedding  │
        │ (vectorized spatial-frequency filter bank).  │
        └──────────────────────┬───────────────────────┘
                               ▼ Top 5 Candidates
        ┌──────────────────────────────────────────────┐
        │ Stage 3: SIFT / RANSAC Geometric Verifier    │
        │ Computes affine homography against candidate │
        │ figure. Inliers ≥ 12 confirms reuse.         │
        └──────────────────────┬───────────────────────┘
                               ▼
     [ Matched PMCID, Retraction Reason, & Side-by-Side Visual Overlay ]
```

---

## Tasks

### Task 1: Perceptual Hash & Dense Embedding Engine
- **File:** `src/vision/figure_fingerprint.py`
- **Features:**
  - `compute_phash(img)`: 64-bit DCT perceptual hash (pure OpenCV/NumPy).
  - `compute_dhash(img)`: 64-bit difference gradient hash.
  - `compute_figure_embedding(img)`: 256-dimensional L2-normalized dense feature vector.
  - `hamming_distance(h1, h2)`: Bitwise XOR popcount.
- **Test:** `tests/test_figure_fingerprint.py`

### Task 2: DuckDB Dynamic Figure Store & Incremental Indexer
- **File:** `src/vision/figure_database.py`
- **Features:**
  - DuckDB table schema: `figure_index (figure_id, pmcid, doi, panel_id, is_retracted, retraction_reasons, phash, dhash, embedding, figure_path, indexed_at)`.
  - Upsert semantics (`INSERT OR REPLACE` / idempotence) for dynamic future expansion beyond 5,000 studies.
  - Fast query method: `query_candidates(phash, embedding, top_k=20, max_hamming=16)`.
- **Test:** `tests/test_figure_database.py`

### Task 3: Cross-Paper SIFT RANSAC Verifier & Comparison Overlay
- **File:** `src/vision/cross_paper_matcher.py`
- **Features:**
  - `verify_cross_paper_match(query_img, candidate_img)`: SIFT/ORB + RANSAC homography.
  - `render_cross_paper_comparison_overlay(query_path, match_meta, candidate_path, output_path)`: Generates side-by-side visual comparison with top banner (Coral Red for Retracted Match, Green for Unique).
- **Test:** `tests/test_cross_paper_matcher.py`

### Task 4: FastMCP Tool Integration
- **File:** `mcp_servers/forensic_chart_mcp.py`
- **Exposes:**
  - `audit_figure_against_retraction_database(image_path, top_k=5, db_path=None, output_overlay_path=None)`
  - `index_study_figure_set(pmcid, doi, figure_paths, retraction_reason=None, db_path=None)`
- **Test:** `tests/test_forensic_fingerprint_mcp.py`

### Task 5: End-to-End Cross-Paper Reuse Test Suite
- **File:** `tests/test_phase3_inter_paper_e2e.py`
- **Verifies:**
  - Indexing Study A (retracted for figure duplication).
  - Querying Study B (containing a cropped/rotated panel of Study A's figure): accurately flags cross-paper reuse, returns Study A's PMCID/DOI, and generates side-by-side overlay.
  - Querying clean Study C: returns `CLEAN` (zero false alarms).
- **Regression:** Run complete test suite (math + chart + splicing + fingerprinting).

### Task 6: Main Repository Synchronization & Documentation
- Mirror modules to `C:\Users\lauye\Downloads\forensic_research\`.
- Update `skills/forensic-auditor/SKILL.md` to document Tier 3 cross-paper indexing.
- Verify 100% test pass rate in both repositories and push to `main`.
