# Visual Forensic Chart Sieve (Gate 3.5) Implementation Plan

> **For Agent:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build Gate 3.5 as a Dual-Mode Visual Forensic Sieve that transcribes charts into structured tables, audits p-value brackets and truncation anomalies, produces annotated visual overlays, and pipes numbers into FastMCP math sieves.

**Architecture:** A visual pipeline comprising synthetic chart test fixtures, an OpenCV/RapidOCR local fallback + Gemini Vision hybrid transcriber, an advanced statistical sieve (Welch's t-test, zero-bound truncation, GRIM/SPRITE), and a visual discrepancy overlay renderer exposed via FastMCP.

**Tech Stack:** Python 3.14, OpenCV (`cv2`), Pillow (`PIL`), `rapidocr-onnxruntime`, `numpy`, `scipy`, `matplotlib`, `pytest`.

---

## Task 1: Synthetic Chart Test Fixtures Generator

**Files:**
- Create: `src/vision/chart_fixture_generator.py`
- Test: `tests/test_chart_fixtures.py`

**Step 1: Write the failing test**
Create `tests/test_chart_fixtures.py` verifying that generator functions create valid image fixtures:
- `generate_grim_fail_bar_chart(path)` (Mean 1.42 with N=15)
- `generate_significance_inversion_chart(path)` (Claimed `***` over $p=0.40$ bars)
- `generate_zero_bound_truncation_chart(path)` (Mean 2.0, SD 3.0 truncated at Y=0)
- `generate_clean_control_chart(path)` (Consistent mean, SD, and valid bracket)

**Step 2: Run test to make sure it fails**
```powershell
pytest tests/test_chart_fixtures.py
```

**Step 3: Implement minimal fixture generator code**
In `src/vision/chart_fixture_generator.py`:
- Use `matplotlib.pyplot` without GUI backend (`matplotlib.use('Agg')`).
- Render clean bars, error bars, brackets, and labels.
- Save to PNG at 300 DPI.

**Step 4: Run tests to verify pass**
```powershell
pytest tests/test_chart_fixtures.py -v
```

**Step 5: Commit**
```powershell
git add src/vision/chart_fixture_generator.py tests/test_chart_fixtures.py
git commit -m "feat(vision): add synthetic chart test fixture generator"
```

---

## Task 2: Data Models & Extraction Schema

**Files:**
- Create: `src/vision/chart_models.py`
- Test: `tests/test_chart_models.py`

**Step 1: Write the failing test**
Create `tests/test_chart_models.py` verifying dataclass serialization and conversion:
- `AxisCalibration` (`min_val`, `max_val`, `scale_type`)
- `ChartDataPoint` (`group_name`, `mean`, `dispersion_val`, `dispersion_type`, `n_sample`, `bbox`)
- `PValueBracket` (`group_a`, `group_b`, `claimed_text`, `claimed_p_threshold`, `bbox`)
- `ExtractedChartData.to_table_rows()` produces standard dictionary format for FastMCP math engine.

**Step 2: Run test to make sure it fails**
```powershell
pytest tests/test_chart_models.py
```

**Step 3: Implement dataclasses**
In `src/vision/chart_models.py`:
- Define typed Pydantic or Dataclass models with JSON serialization and conversion methods.

**Step 4: Run tests to verify pass**
```powershell
pytest tests/test_chart_models.py -v
```

**Step 5: Commit**
```powershell
git add src/vision/chart_models.py tests/test_chart_models.py
git commit -m "feat(vision): define chart extraction data models and schema"
```

---

## Task 3: Forensic Statistical Sieve Engine

**Files:**
- Create: `src/vision/forensic_chart_sieves.py`
- Test: `tests/test_forensic_chart_sieves.py`

**Step 1: Write the failing test**
Create `tests/test_forensic_chart_sieves.py` testing the 4 core mathematical sieves on mock `ExtractedChartData`:
- `audit_p_value_brackets(chart_data)` catches significance inversion.
- `audit_zero_bound_truncations(chart_data)` catches truncated lower error bar when $Mean - 2 \times SD < 0$.
- `audit_modular_table_math(chart_data)` calls `verify_grim_grimmer_debit` logic.
- `audit_outliers_and_missingness(chart_data)` detects unexplained missing cohorts.

**Step 2: Run test to make sure it fails**
```powershell
pytest tests/test_forensic_chart_sieves.py
```

**Step 3: Implement forensic sieves**
In `src/vision/forensic_chart_sieves.py`:
- Implement Welch's t-test using `scipy.stats.ttest_ind_from_stats`.
- Implement zero-bound boundary rule.
- Bridge into existing GRIM / GRIMMER / SPRITE modules from `src/`.

**Step 4: Run tests to verify pass**
```powershell
pytest tests/test_forensic_chart_sieves.py -v
```

**Step 5: Commit**
```powershell
git add src/vision/forensic_chart_sieves.py tests/test_forensic_chart_sieves.py
git commit -m "feat(vision): implement forensic chart sieves for p-values, truncation, and modular math"
```

---

## Task 4: Hybrid Chart Transcriber

**Files:**
- Create: `src/vision/chart_transcriber.py`
- Test: `tests/test_chart_transcriber.py`

**Step 1: Write the failing test**
Create `tests/test_chart_transcriber.py` evaluating extraction against synthetic fixtures:
- Tests local fallback (OpenCV contour detection + `RapidOCR-ONNX` for axis and bar heights).
- Verifies extraction produces `ExtractedChartData` with $R^2 \ge 0.95$ axis calibration.

**Step 2: Run test to make sure it fails**
```powershell
pytest tests/test_chart_transcriber.py
```

**Step 3: Implement chart transcriber**
In `src/vision/chart_transcriber.py`:
- Implement image loading, grayscale conversion, Otsu thresholding, axis line detection using Hough transform or morphology.
- Implement bar contour detection and bounding box scaling.
- Integrate OCR using `rapidocr-onnxruntime` to read axis numbers, labels, and brackets.
- Add Gemini Vision API branch if API key is detected in environment.

**Step 4: Run tests to verify pass**
```powershell
pytest tests/test_chart_transcriber.py -v
```

**Step 5: Commit**
```powershell
git add src/vision/chart_transcriber.py tests/test_chart_transcriber.py
git commit -m "feat(vision): implement hybrid chart transcriber with local OCR fallback"
```

---

## Task 5: Visual Discrepancy Overlay Renderer

**Files:**
- Create: `src/vision/visual_overlay_renderer.py`
- Test: `tests/test_visual_overlay_renderer.py`

**Step 1: Write the failing test**
Create `tests/test_visual_overlay_renderer.py` testing image annotation:
- Input: Image path, list of anomalies, list of verified points.
- Output: Output image created with valid dimensions and non-empty rendered pixels.

**Step 2: Run test to make sure it fails**
```powershell
pytest tests/test_visual_overlay_renderer.py
```

**Step 3: Implement overlay renderer**
In `src/vision/visual_overlay_renderer.py`:
- Use `cv2.rectangle`, `cv2.putText`, and semi-transparent alpha overlays for clean callout banners.
- Red boxes (`#EF4444`) for arithmetic/bracket anomalies.
- Green boxes (`#10B981`) for verified points.

**Step 4: Run tests to verify pass**
```powershell
pytest tests/test_visual_overlay_renderer.py -v
```

**Step 5: Commit**
```powershell
git add src/vision/visual_overlay_renderer.py tests/test_visual_overlay_renderer.py
git commit -m "feat(vision): implement visual discrepancy overlay renderer"
```

---

## Task 6: FastMCP Server Integration (`forensic_chart_mcp.py`)

**Files:**
- Create: `mcp_servers/forensic_chart_mcp.py`
- Test: `tests/test_forensic_chart_mcp.py`

**Step 1: Write the failing test**
Create `tests/test_forensic_chart_mcp.py`:
- Tests `audit_chart_figure(image_path, caption)` directly via FastMCP call.
- Asserts returned verdict, extracted series, and overlay image path.

**Step 2: Run test to make sure it fails**
```powershell
pytest tests/test_forensic_chart_mcp.py
```

**Step 3: Implement FastMCP server**
In `mcp_servers/forensic_chart_mcp.py`:
- Define FastMCP tool `audit_chart_figure`.
- Wire `chart_transcriber` -> `forensic_chart_sieves` -> `visual_overlay_renderer`.

**Step 4: Run tests to verify pass**
```powershell
pytest tests/test_forensic_chart_mcp.py -v
```

**Step 5: Commit**
```powershell
git add mcp_servers/forensic_chart_mcp.py tests/test_forensic_chart_mcp.py
git commit -m "feat(mcp): expose audit_chart_figure in FastMCP server"
```

---

## Task 7: Full End-to-End Verification & Regression Suite

**Files:**
- Test: `tests/test_forensic_chart_sieve.py`

**Step 1: Write comprehensive end-to-end suite**
In `tests/test_forensic_chart_sieve.py`:
- Test each of the 4 synthetic fixtures through the complete pipeline.
- Assert GRIM failure caught on `grim_fail_bar.png`.
- Assert Significance Inversion caught on `significance_inversion.png`.
- Assert Truncation caught on `zero_bound_truncation.png`.
- Assert Clean pass on `clean_control.png`.

**Step 2: Run full test suite including math regression**
```powershell
pytest tests/test_forensic_chart_sieve.py -v
pytest tests/test_forensic_math_suite.py -v
```

**Step 3: Verify all tests pass (100%)**

**Step 4: Commit and merge feature branch**
```powershell
git add tests/test_forensic_chart_sieve.py
git commit -m "test(vision): complete end-to-end test suite for visual chart forensic sieve"
```
