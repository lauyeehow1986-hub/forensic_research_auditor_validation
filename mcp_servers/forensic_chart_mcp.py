#!/usr/bin/env python3
"""
FastMCP Visual Forensic Chart & Statistical Sieve Server (Gate 3.5).
Provides tools for:
1. audit_chart_figure: Extracts data from figure images (bar charts, scatter plots, error bars),
   runs p-value recalculation, zero-bound truncation audits, and modular GRIM/Popoviciu tests,
   and optionally outputs color-coded visual discrepancy overlays.
2. transcribe_and_pipe_to_table_math: Converts extracted visual chart points into standard FastMCP TableRow
   representations and validates against discrete/continuous arithmetic sieves.
3. audit_figure_splicing: Detects intra-paper image tampering (Western blot cloned bands,
   cut-and-paste lane splice boundaries, rotated/flipped/cropped microscopy panel reuse).
"""

import os
from typing import Dict, Any, List, Optional
from dataclasses import asdict

try:
    from mcp.server.mcpserver import MCPServer as FastMCP
    mcp = FastMCP("Forensic Visual Chart Engine")
except ImportError:
    try:
        from mcp.server.fastmcp import FastMCP
        mcp = FastMCP("Forensic Visual Chart Engine")
    except ImportError:
        class DummyMCP:
            def tool(self):
                def decorator(fn):
                    return fn
                return decorator
            def run(self):
                pass
        mcp = DummyMCP()

from src.vision.chart_transcriber import transcribe_chart_figure
from src.vision.forensic_chart_sieves import audit_chart_statistics
from src.vision.visual_overlay_renderer import render_chart_visual_overlay
from src.vision.panel_splitter import split_figure_panels, classify_figure_type
from src.vision.western_blot_sieve import audit_western_blot_splicing
from src.vision.microscopy_sieve import audit_microscopy_splicing
from src.vision.splicing_overlay_renderer import render_splicing_visual_overlay
from src.vision.figure_database import FigureDatabase
from src.vision.cross_paper_matcher import (
    verify_cross_paper_match,
    render_cross_paper_comparison_overlay
)
from mcp_servers.forensic_math_mcp import verify_grim_grimmer_debit


@mcp.tool()
def audit_chart_figure(
    image_path: str,
    caption: Optional[str] = "",
    output_overlay_path: Optional[str] = None,
    sample_size_n: Optional[int] = None,
    force_local: bool = True
) -> Dict[str, Any]:
    """
    Performs forensic statistical auditing of scientific figure charts.
    Extracts numerical values, error bars, brackets, and tests for:
    - Significance inversions (Welch's t-test recalculation)
    - Zero-bound truncation (impossible negative concentrations)
    - Granularity / GRIM divisibility on discrete outcomes
    - Popoviciu variance bounds

    Returns structured forensic report and generates annotated visual overlay.
    """
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"Image not found at path: {image_path}")

    # 1. Transcribe chart
    chart_data = transcribe_chart_figure(
        image_path=image_path,
        caption=caption,
        sample_size_hint=sample_size_n,
        force_local=force_local
    )

    # 2. Audit statistics
    audit_report = audit_chart_statistics(chart_data)

    # 3. Generate visual overlay if requested or if output_overlay_path provided
    overlay_path = None
    if output_overlay_path:
        overlay_path = render_chart_visual_overlay(
            image_path=image_path,
            audit_report=audit_report,
            output_path=output_overlay_path
        )

    return {
        "figure_id": chart_data.figure_id,
        "verdict": audit_report["verdict"],
        "discrepancies_count": audit_report.get("discrepancies_count", len(audit_report["discrepancies"])),
        "discrepancies": audit_report["discrepancies"],
        "p_value_bracket_audits": audit_report.get("p_value_bracket_audits", []),
        "zero_bound_audits": audit_report.get("zero_bound_audits", []),
        "table_math_audits": audit_report.get("table_math_audits", []),
        "series": [asdict(p) for p in chart_data.series],
        "p_value_brackets": [asdict(b) for b in chart_data.p_value_brackets],
        "table_rows": chart_data.to_table_rows(),
        "overlay_path": overlay_path
    }


@mcp.tool()
def transcribe_and_pipe_to_table_math(
    image_path: str,
    caption: Optional[str] = "",
    sample_size_n: Optional[int] = None,
    force_local: bool = True
) -> Dict[str, Any]:
    """
    Extracts numerical data points from figure images and directly validates
    them using the core FastMCP Table Math consistency engine (GRIM, GRIMMER).
    """
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"Image not found at path: {image_path}")

    chart_data = transcribe_chart_figure(
        image_path=image_path,
        caption=caption,
        sample_size_hint=sample_size_n,
        force_local=force_local
    )

    table_rows = chart_data.to_table_rows()
    math_audits = []

    for row in table_rows:
        n_val = row.get("n_sample")
        if n_val and n_val > 0:
            grim_res = verify_grim_grimmer_debit(
                mean=row["mean"],
                sd=row["sd"],
                n=n_val,
                is_binary=False
            )
            math_audits.append({
                "group_name": row["group_name"],
                "mean": row["mean"],
                "sd": row["sd"],
                "n": n_val,
                "grim_result": grim_res
            })

    return {
        "figure_id": chart_data.figure_id,
        "table_rows": table_rows,
        "math_audits": math_audits
    }


@mcp.tool()
def audit_figure_splicing(
    image_path: str,
    output_overlay_path: Optional[str] = None
) -> Dict[str, Any]:
    """
    Audits biomedical figures for intra-manuscript tampering (Gate 3.5 Phase 2):
    - Multi-panel segmentation
    - Western blot cloned bands across lanes (Normalized Cross-Correlation)
    - Vertical background step-discontinuities (cut-and-paste gel assembly)
    - Reused, flipped, cropped, or rotated microscopy and histology fields (SIFT + RANSAC homography)
    
    Generates color-coded visual correspondence overlay.
    """
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"Image not found at path: {image_path}")

    panels = split_figure_panels(image_path)
    overall_fig_type = classify_figure_type(image_path)

    discrepancies = []

    # Run Western Blot Sieve if overall figure or single panel is a gel
    if overall_fig_type == "WESTERN_BLOT" or len(panels) == 1:
        wb_rep = audit_western_blot_splicing(image_path)
        discrepancies.extend(wb_rep.get("discrepancies", []))

    # Run Microscopy / Homography Sieve if multi-panel
    if len(panels) >= 2:
        micro_rep = audit_microscopy_splicing(image_path, panels=panels)
        discrepancies.extend(micro_rep.get("discrepancies", []))

    verdict = "FLAGGED_SPLICING_ANOMALY" if len(discrepancies) > 0 else "CLEAN"

    report = {
        "verdict": verdict,
        "discrepancies_count": len(discrepancies),
        "discrepancies": discrepancies,
        "panels_detected": len(panels),
        "figure_type": overall_fig_type
    }

    overlay_path = None
    if output_overlay_path:
        overlay_path = render_splicing_visual_overlay(
            image_path=image_path,
            audit_report=report,
            output_path=output_overlay_path
        )
    report["overlay_path"] = overlay_path

    return report


@mcp.tool()
def index_study_figure_set(
    pmcid: str,
    doi: str,
    figure_paths: List[str],
    is_retracted: bool = True,
    retraction_reasons: Optional[str] = "Literature integrity audit",
    db_path: Optional[str] = None,
    split_panels: bool = True
) -> Dict[str, Any]:
    """
    Indexes a set of study figures into the DuckDB cross-manuscript fingerprint database.
    Computes 64-bit pHash, dHash, and 256-dim dense embeddings.
    Supports dynamic corpus expansion (from 5,000 to 10k, 20k, 50k+ studies).
    """
    db = FigureDatabase(db_path=db_path or "data/retracted_figures.duckdb")
    try:
        count = db.index_study_figures(
            pmcid=pmcid,
            doi=doi,
            figure_paths=figure_paths,
            is_retracted=is_retracted,
            retraction_reasons=retraction_reasons or "Literature integrity audit",
            split_panels=split_panels
        )
        stats = db.get_stats()
        return {
            "pmcid": pmcid,
            "doi": doi,
            "indexed_count": count,
            "stats": stats
        }
    finally:
        db.close()


@mcp.tool()
def audit_figure_against_retraction_database(
    image_path: str,
    top_k: int = 5,
    db_path: Optional[str] = None,
    output_overlay_path: Optional[str] = None,
    min_inliers: int = 12
) -> Dict[str, Any]:
    """
    Audits a query figure against the retraction database for cross-manuscript figure reuse (The Lean ImageTwin).
    3-Stage Cascade:
    1. 64-bit DCT pHash/dHash Hamming filter.
    2. 256-dimensional dense embedding cosine similarity ranking in DuckDB.
    3. SIFT/RANSAC affine homography geometric verification (>= 12 inliers) for 0% false alarms.
    Generates side-by-side forensic comparative visual overlay.
    """
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"Image not found at path: {image_path}")

    db = FigureDatabase(db_path=db_path or "data/retracted_figures.duckdb")
    try:
        candidates = db.query_candidates(image_path, top_k=top_k)

        best_match = None
        best_match_result = None

        for cand in candidates:
            cand_path = cand.get("figure_path")
            if not cand_path or not os.path.exists(cand_path):
                continue

            match_res = verify_cross_paper_match(image_path, cand_path, min_inliers=min_inliers)
            if match_res["is_match"]:
                best_match = cand
                best_match_result = match_res
                break  # Confirmed fatal match found

        verdict = "FLAGGED_CROSS_PAPER_REUSE" if best_match else "CLEAN"

        overlay_path = None
        if output_overlay_path:
            if best_match and best_match_result:
                overlay_path = render_cross_paper_comparison_overlay(
                    query_input=image_path,
                    candidate_input=best_match["figure_path"],
                    match_result=best_match_result,
                    candidate_meta=best_match,
                    output_path=output_overlay_path
                )
            elif candidates and os.path.exists(candidates[0].get("figure_path", "")):
                # Clean overlay showing closest candidate
                dummy_res = {
                    "is_match": False,
                    "inlier_count": 0,
                    "transformation_type": "NONE",
                    "confidence_score": 0.0
                }
                overlay_path = render_cross_paper_comparison_overlay(
                    query_input=image_path,
                    candidate_input=candidates[0]["figure_path"],
                    match_result=dummy_res,
                    candidate_meta=candidates[0],
                    output_path=output_overlay_path
                )

        return {
            "verdict": verdict,
            "matched_study": best_match,
            "match_details": best_match_result,
            "candidates_evaluated": len(candidates),
            "inliers": best_match_result.get("inlier_count", 0) if best_match_result else 0,
            "confidence_score": best_match_result.get("confidence_score", 0.0) if best_match_result else 0.0,
            "overlay_path": overlay_path
        }
    finally:
        db.close()


if __name__ == "__main__":
    mcp.run()
