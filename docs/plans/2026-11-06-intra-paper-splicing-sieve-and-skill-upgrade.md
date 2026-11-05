# Implementation Plan: Intra-Paper Splicing Sieve (Gate 3.5 Phase 2) & Main Repo Skill Upgrade

**Goal:** Upgrade the primary repository (`forensic_research_auditor`) with the 10,000-study benchmark calibrations, port Gate 3.5 Chart Digitizer modules, and build the Phase 2 Intra-Paper Western Blot & Microscopy Splicing Sieve using OpenCV SIFT/ORB + RANSAC and patch cross-correlation.

---

## Architecture Overview

```
                          [ Input Figure Image ]
                                     │
                                     ▼
                      [ Task 4: Panel Splitter ]
                      (Isolates Sub-Panels A, B, C...)
                                     │
                 ┌───────────────────┴───────────────────┐
                 ▼                                       ▼
     [ Task 5: Western Blot Sieve ]        [ Task 6: Microscopy Sieve ]
     - Band patch extraction               - SIFT / ORB keypoint extraction
     - Normalized Cross-Correlation (NCC)  - RANSAC Affine Homography
     - Adjacent lane splice borders        - Flips (det < 0), 90°/180° rotations, crops
                 │                                       │
                 └───────────────────┬───────────────────┘
                                     ▼
                    [ Task 7: Visual Overlay Renderer ]
                    (Connecting lines between duplicated bands/crops,
                     red anomaly boxes, top status banner)
                                     │
                                     ▼
                    [ Task 8: FastMCP Tool Integration ]
                    (`audit_figure_splicing` exposed via MCP)
```

---

## Proposed Tasks

### Task 1: Upgrade `SKILL.md` in Main Repo (`forensic_research_auditor`)
- **Location:** `C:\Users\lauye\Downloads\forensic_research\skills\forensic-auditor\SKILL.md` and `C:\Users\lauye\.gemini\config\skills\forensic-auditor\SKILL.md`.
- **Changes:**
  - Incorporate findings from the 10,000-study quintuple-wave blind full-text benchmark (5,000 cases vs. 5,000 controls; 33,043 tables).
  - Document the multi-cell consensus calibration, decadic dynamic span ($\ge 2.0$), and Table 1 non-parametric filtering that achieved 86.00% clean control specificity.
  - Formally document the 3-Tier Gate 3.5 Visual Forensic architecture.
- **Verification:** Confirm syntax and alignment with project rules.

### Task 2: Port Gate 3.5 Chart Sieve & FastMCP to Main Repo
- **Location:** `C:\Users\lauye\Downloads\forensic_research`
- **Files to port:**
  - `src/vision/chart_models.py`
  - `src/vision/chart_fixture_generator.py`
  - `src/vision/chart_transcriber.py`
  - `src/vision/forensic_chart_sieves.py`
  - `src/vision/visual_overlay_renderer.py`
  - `mcp_servers/forensic_chart_mcp.py`
  - Associated unit tests (`tests/test_chart_*.py`, `tests/test_forensic_chart_*.py`).
- **Verification:** Run pytest in main repo; assert 23/23 tests pass.

### Task 3: Synthetic Splicing Fixture Generator
- **Location:** `src/vision/splicing_fixture_generator.py`
- **Generates 4 deterministic synthetic figure test fixtures:**
  1. `generate_western_blot_cloned_band_figure(output_path)`: 4 gel lanes where Lane 1 and Lane 3 contain identical cloned band patches.
  2. `generate_western_blot_spliced_lane_figure(output_path)`: 3 gel lanes with a vertical step-discontinuity splice border between Lane 1 and Lane 2.
  3. `generate_microscopy_flipped_crop_figure(output_path)`: Panel A and Panel B where Panel B is a $180^\circ$ rotated/flipped sub-crop of Panel A.
  4. `generate_clean_control_figure(output_path)`: Authentic multi-lane gel with independent noise across all lanes, and distinct microscopy fields.
- **Verification:** `tests/test_splicing_fixtures.py`.

### Task 4: Panel Splitter & Sub-Figure Segmenter
- **Location:** `src/vision/panel_splitter.py`
- **Functionality:**
  - Identifies multi-panel layouts (A, B, C, D) using border/gutter detection and panel label OCR.
  - Crops and isolates sub-panels with normalized coordinates `[ymin, xmin, ymax, xmax]`.
  - Detects if an image is a Western blot gel or a set of microscopy panels.
- **Verification:** `tests/test_panel_splitter.py`.

### Task 5: Western Blot Lane & Band Clone Sieve
- **Location:** `src/vision/western_blot_sieve.py`
- **Functionality:**
  - Vertical projection profile to locate lane boundaries.
  - Horizontal projection profile within lanes to locate band peaks.
  - Pairwise band patch Normalized Cross-Correlation (NCC): flags pairs with $R > 0.95$ and low pixel difference.
  - Vertical background gradient analysis across lane borders: flags sharp step-discontinuities.
- **Verification:** `tests/test_western_blot_sieve.py`.

### Task 6: Microscopy & Histology Rotation/Flip/Crop Sieve
- **Location:** `src/vision/microscopy_sieve.py`
- **Functionality:**
  - SIFT / ORB keypoint extraction and feature matching between pairwise panels.
  - RANSAC affine homography estimation $H$.
  - Analyzes transformation:
    - Homography inlier count $\ge 12$.
    - Negative determinant ($\det(H) < 0$) indicating mirror/flip.
    - Rotation angle ($\approx 90^\circ, 180^\circ, 270^\circ$).
- **Verification:** `tests/test_microscopy_sieve.py`.

### Task 7: Splicing Visual Discrepancy Overlay Renderer
- **Location:** `src/vision/splicing_overlay_renderer.py`
- **Functionality:**
  - Annotates input figures with coral red bounding boxes over cloned bands or matched fields.
  - Draws colored correspondence lines connecting duplicated elements.
  - Displays top forensic banner (Red for Anomaly, Green for Clean).
- **Verification:** `tests/test_splicing_overlay_renderer.py`.

### Task 8: FastMCP Tool Integration & End-to-End Regression Suite
- **Location:** `mcp_servers/forensic_chart_mcp.py` (or `mcp_servers/forensic_splicing_mcp.py`) and `tests/test_forensic_splicing_e2e.py`.
- **Functionality:**
  - Expose `audit_figure_splicing(image_path, output_overlay_path)`.
  - Comprehensive end-to-end tests evaluating all 4 synthetic fixtures.
  - Verify zero regression across all existing 58 math and chart tests.
