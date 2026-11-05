# Visual Forensic Gate (Gate 3.5: Dual-Mode Chart Digitizer & Statistical Sieve) Design Specification

**Date:** 2026-11-06  
**Status:** Approved  
**Author:** Pair Programming (Antigravity + User)  
**Target Module:** `src/vision/`, `mcp_servers/forensic_chart_mcp.py`, `tests/test_forensic_chart_sieve.py`

---

## 1. Executive Summary & Problem Statement

In the 10,000-study quintuple-wave full-text forensic audit, **8.2% of data-related retracted studies (153 papers)** evaded automated table math screening because their primary numerical results were presented exclusively in bar charts, dot plots, and scatter curves rather than machine-readable JATS XML `<table>` tags. Furthermore, figure manipulation often occurs through visual misrepresentation:
1. **Significance Inversions:** Drawing `*** p < 0.001` or `* p < 0.05` brackets over bars whose means and standard deviations actually yield non-significant differences ($p > 0.10$).
2. **Zero-Bound Concealment:** Truncating lower error bars at $Y=0$ to mask that a normal distribution model yields impossible negative physiological concentrations ($Mean - 2 \times SD < 0$).
3. **Missing Value & Cohort Attrition Patterns:** Dropping control groups or experimental timepoints without explanation.

This specification defines **Gate 3.5: The Visual Forensic Chart Sieve**, a hybrid vision pipeline that transcribes visual figures into standardized tabular data, audits statistical integrity, and produces visual discrepancy overlays.

---

## 2. System Architecture

```
                      [ Input: Figure Image + Caption ]
                                      │
                                      ▼
               ┌──────────────────────────────────────────────┐
               │         Visual Pre-Processing Module         │
               │  • Image normalization & DPI upscaling (≥300)│
               │  • Panel segmentation & axis detection       │
               └──────────────────────┬───────────────────────┘
                                      │
                                      ▼
               ┌──────────────────────────────────────────────┐
               │        Hybrid Vision Extraction Engine       │
               │  • Primary: Gemini Multimodal Vision API     │
               │  • Fallback: Local OpenCV + RapidOCR         │
               └──────────────────────┬───────────────────────┘
                                      │
                                      ▼
               ┌──────────────────────────────────────────────┐
               │           Dual-Output Dispatcher             │
               │  1. Standard Normalized Table Rows           │
               │  2. Annotated Discrepancy Overlay (OpenCV)   │
               └──────────────────────┬───────────────────────┘
                                      │
                                      ▼
               ┌──────────────────────────────────────────────┐
               │        Visual Forensic Audit Sieves          │
               │  • Sieve A: FastMCP Math (GRIM/SPRITE/DEBIT) │
               │  • Sieve B: Welch's t-test Bracket Recalc    │
               │  • Sieve C: Outlier & Physical Bounds Check  │
               │  • Sieve D: Zero-Bound & Attrition Sieve     │
               └──────────────────────────────────────────────┘
```

---

## 3. Core Components & Module Contracts

### 3.1 `src/vision/chart_transcriber.py`
* **Input:** `image_path: str`, `caption: Optional[str] = None`, `sample_size_hint: Optional[int] = None`
* **Output:** `ExtractedChartData` dataclass containing:
  * `chart_type`: `BAR_WITH_ERROR_BARS`, `SCATTER_PLOT`, `BOX_PLOT`, `LINE_TIME_SERIES`
  * `y_axis`: `AxisCalibration` (`label`, `min_val`, `max_val`, `scale_type: LINEAR|LOG`)
  * `series`: List of `ChartDataPoint` (`group_name`, `mean`, `dispersion_val`, `dispersion_type: SD|SEM|CI95`, `n_sample`, `bbox: [ymin, xmin, ymax, xmax]`)
  * `p_value_brackets`: List of `PValueBracket` (`group_a`, `group_b`, `claimed_text`, `claimed_p_threshold`, `bbox`)
  * `raw_points`: List of individual coordinates for scatter plots (outlier detection)

### 3.2 `src/vision/forensic_chart_sieves.py`
Implements the 4 analytical sieves:
1. **Modular Table Math Sieve:** Converts series to standard `TableRows` and passes them to `verify_grim_grimmer_debit` and `SPRITE`.
2. **P-Value Bracket Recalculation:** Re-computes two-sample Welch's $t$-test:
   $$t = \frac{\bar{X}_1 - \bar{X}_2}{\sqrt{\frac{s_1^2}{n_1} + \frac{s_2^2}{n_2}}}, \quad \nu \approx \frac{\left(\frac{s_1^2}{n_1} + \frac{s_2^2}{n_2}\right)^2}{\frac{(s_1^2/n_1)^2}{n_1-1} + \frac{(s_2^2/n_2)^2}{n_2-1}}$$
   Flags **Significance Inversion** if claimed $p < 0.05$ but calculated $p \ge 0.05$ (or vice versa).
3. **Outlier & Physical Boundary Sieve:** Evaluates points against Tukey's rule ($3 \times \text{IQR}$) and physical assay limits (e.g. concentrations $< 0$).
4. **Missingness & Truncation Sieve:** Detects lower error bar truncation at $Y=0$ where $Mean - 2 \times SD < 0$, and unexplained group drops in longitudinal series.

### 3.3 `src/vision/visual_overlay_renderer.py`
* Draws color-coded visual annotations directly on a copy of the figure:
  * **Green bounding box:** Validated statistical points / consistent comparisons.
  * **Red bounding box & flag callout:** Detected arithmetic failure, significance inversion, or truncated bound.
  * **Yellow warning banner:** Unexplained missing group or high-deviation outlier.
* Saves to `data/overlays/{figure_id}_audit_overlay.png`.

### 3.4 `mcp_servers/forensic_chart_mcp.py`
Exposes FastMCP tool `audit_chart_figure`:
* **Parameters:** `image_path` (str), `caption` (str, optional), `sample_size_hint` (int, optional)
* **Returns:** JSON summary with `verdict`, `discrepancies_found`, `extracted_table`, and `overlay_image_path`.

---

## 4. Error Handling & Graceful Degradation

1. **Dual Engine Fallback:**
   * If Gemini Multimodal API is available (via `GEMINI_API_KEY` or IDE auth), use structured JSON vision extraction.
   * If offline or no key, gracefully fall back to local `RapidOCR-ONNX` + `OpenCV` contour detection for axis ticks and bar heights.
2. **Confidence Calibration:**
   * Axis fit $R^2 < 0.95$ yields `UNRESOLVABLE_CHART_AXIS` without triggering a false positive anomaly.
   * If sample size $N$ cannot be parsed from figure labels or captions, modular divisibility (GRIM) is gracefully skipped while variance bounds (SPRITE) and bracket $t$-tests continue with conservative bounds.

---

## 5. Testing & Verification Strategy (TDD)

* **Test Suite:** `tests/test_forensic_chart_sieve.py`
* **Fixtures (programmatically generated via `matplotlib`):**
  1. `fixture_grim_fail_bar_chart.png`: Mean 1.42 with $N=15$ on discrete integer scale.
  2. `fixture_significance_inversion.png`: Claimed `*** p < 0.001` bracket between bars where Welch's $t$-test yields $t=0.85, p=0.40$.
  3. `fixture_zero_bound_truncation.png`: Bar height $2.0$, upper error bar $+3.0$, lower error bar truncated flat at $0.0$.
  4. `fixture_clean_control_chart.png`: Perfectly self-consistent biological assay with genuine $p$-value and symmetric error bars.
* **Success Criteria:**
  * 100% of synthetic test fixtures correctly evaluated by `pytest tests/test_forensic_chart_sieve.py`.
  * Zero regressions in `tests/test_forensic_math_suite.py` (all 35 existing tests pass).
