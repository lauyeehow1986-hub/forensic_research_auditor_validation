#!/usr/bin/env python3
"""
FastMCP Visual Forensic Chart & Statistical Sieve Server (Gate 3.5).
Provides tools for:
1. audit_chart_figure: Extracts data from figure images (bar charts, scatter plots, error bars),
   runs p-value recalculation, zero-bound truncation audits, and modular GRIM/Popoviciu tests,
   and optionally outputs color-coded visual discrepancy overlays.
2. transcribe_and_pipe_to_table_math: Converts extracted visual chart points into standard FastMCP TableRow
   representations and validates against discrete/continuous arithmetic sieves.
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


if __name__ == "__main__":
    mcp.run()
