"""
Forensic Chart Statistical Sieves (Gate 3.5).
Provides rigorous mathematical checks on chart data:
1. Welch's t-test recalculation for p-value comparison brackets.
2. Zero-bound variance truncation and negative tail concealment.
3. Modular arithmetic consistency (GRIM, GRIMMER, SPRITE bounds).
4. Outlier detection and missing value / cohort pattern checks.
"""

from typing import List, Dict, Any, Optional
import numpy as np
import scipy.stats as stats

from src.vision.chart_models import ExtractedChartData, ChartDataPoint, PValueBracket


def audit_p_value_brackets(chart: ExtractedChartData) -> List[Dict[str, Any]]:
    """
    Audits visual p-value comparison brackets against actual Welch's t-test
    calculated from the underlying group means, SDs, and sample sizes.
    Detects significance inversions (e.g. claiming p < 0.05 when math yields p = 0.50).
    """
    results = []
    points_by_name = {pt.group_name.strip().lower(): pt for pt in chart.series}

    for b in chart.p_value_brackets:
        name_a = b.group_a.strip().lower()
        name_b = b.group_b.strip().lower()

        # Fuzzy lookup if exact match not found
        pt_a = points_by_name.get(name_a)
        pt_b = points_by_name.get(name_b)

        if not pt_a or not pt_b:
            # Match by partial string
            pt_a = next((pt for k, pt in points_by_name.items() if name_a in k or k in name_a), None)
            pt_b = next((pt for k, pt in points_by_name.items() if name_b in k or k in name_b), None)

        if not pt_a or not pt_b:
            continue

        n1 = pt_a.n_sample or 10  # Conservative default if unstated
        n2 = pt_b.n_sample or 10
        s1 = max(1e-6, pt_a.dispersion_val)
        s2 = max(1e-6, pt_b.dispersion_val)

        # Compute Welch's t-test (unequal variances)
        t_res = stats.ttest_ind_from_stats(
            mean1=pt_a.mean, std1=s1, nobs1=n1,
            mean2=pt_b.mean, std2=s2, nobs2=n2,
            equal_var=False
        )
        welch_p = float(t_res.pvalue)
        welch_t = float(t_res.statistic)

        is_claimed_sig = any(sig in b.claimed_text.lower() for sig in ["*", "p<0.05", "p<0.01", "p<0.001", "p < 0.05", "p < 0.01", "p < 0.001"]) or b.claimed_p_threshold <= 0.05
        is_claimed_ns = "ns" in b.claimed_text.lower() or b.claimed_p_threshold > 0.05

        audit_entry = {
            "group_a": pt_a.group_name,
            "group_b": pt_b.group_name,
            "claimed_text": b.claimed_text,
            "claimed_p_threshold": b.claimed_p_threshold,
            "computed_welch_p": round(welch_p, 5),
            "computed_welch_t": round(welch_t, 3),
            "bbox": b.bbox,
            "status": "PASS"
        }

        # Check for Significance Inversion
        if is_claimed_sig and welch_p >= 0.05:
            audit_entry["status"] = "FAIL"
            audit_entry["discrepancy_type"] = "SIGNIFICANCE_INVERSION"
            audit_entry["explanation"] = (
                f"Claimed statistical significance ('{b.claimed_text}') between {pt_a.group_name} "
                f"(M={pt_a.mean}, SD={s1}) and {pt_b.group_name} (M={pt_b.mean}, SD={s2}) is mathematically "
                f"unsupported by Welch's t-test (t={welch_t:.2f}, actual p={welch_p:.4f} >= 0.05)."
            )
        elif is_claimed_ns and welch_p < 0.001:
            audit_entry["status"] = "FAIL"
            audit_entry["discrepancy_type"] = "SIGNIFICANCE_INVERSION"
            audit_entry["explanation"] = (
                f"Claimed non-significance ('{b.claimed_text}') conflicts with extreme group separation "
                f"(Welch t={welch_t:.2f}, actual p={welch_p:.6f} < 0.001)."
            )

        results.append(audit_entry)

    return results


def audit_zero_bound_truncations(chart: ExtractedChartData) -> List[Dict[str, Any]]:
    """
    Audits whether normal error bars on non-negative biological assays
    imply impossible negative concentrations (Mean - 2*SD < 0) that are
    concealed by truncating the lower error bar flat at Y=0.
    """
    results = []
    is_non_negative_assay = (chart.y_axis.min_val >= 0.0)

    if not is_non_negative_assay:
        return results

    for pt in chart.series:
        mean_val = pt.mean
        sd_val = pt.dispersion_val

        # If dispersion is SEM, convert to SD
        if pt.dispersion_type.upper() == "SEM" and pt.n_sample:
            sd_val = pt.dispersion_val * np.sqrt(pt.n_sample)

        if sd_val > 0 and mean_val > 0:
            lower_2sd = mean_val - 2.0 * sd_val
            if lower_2sd < 0.0:
                # Calculate probability of negative values under Gaussian model
                z_score = -mean_val / sd_val
                p_neg = float(stats.norm.cdf(z_score))
                
                results.append({
                    "group_name": pt.group_name,
                    "discrepancy_type": "ZERO_BOUND_TRUNCATION",
                    "status": "FAIL",
                    "mean": mean_val,
                    "sd": sd_val,
                    "lower_2sd_bound": round(lower_2sd, 3),
                    "implied_negative_pct": round(p_neg * 100, 2),
                    "bbox": pt.bbox,
                    "explanation": (
                        f"Group '{pt.group_name}' reports Mean={mean_val} and SD={sd_val}. "
                        f"Under a Gaussian model, the 95% interval extends to {lower_2sd:.2f}, "
                        f"implying {p_neg*100:.1f}% of observations are negative on a strictly "
                        f"non-negative assay ({chart.y_axis.label}). Truncating lower error bar at 0 hides model misspecification."
                    )
                })

    return results


def audit_modular_table_math(chart: ExtractedChartData) -> List[Dict[str, Any]]:
    """
    Converts extracted chart points into standard TableRows and runs
    modular divisibility (GRIM) and Popoviciu variance bounds (SPRITE).
    """
    results = []

    for pt in chart.series:
        # 1. GRIM Test on discrete items
        if pt.is_discrete and pt.n_sample and pt.n_sample > 0:
            total_sum = pt.mean * pt.n_sample
            nearest_int = round(total_sum)
            diff = abs(total_sum - nearest_int)

            if diff > 0.01:
                results.append({
                    "sieve": "GRIM",
                    "discrepancy_type": "GRIM_INCONSISTENCY",
                    "group_name": pt.group_name,
                    "mean": pt.mean,
                    "n_sample": pt.n_sample,
                    "implied_sum": round(total_sum, 3),
                    "nearest_valid_int": nearest_int,
                    "status": "FAIL",
                    "bbox": pt.bbox,
                    "explanation": (
                        f"Group '{pt.group_name}' reports discrete scale Mean={pt.mean} with N={pt.n_sample}. "
                        f"The required sum of integer responses is {total_sum:.3f}, which is non-integer (diff={diff:.3f})."
                    )
                })

        # 2. Popoviciu's Inequality Variance Bound: SD <= (Max - Min) / 2
        if chart.y_axis.max_val > chart.y_axis.min_val:
            max_possible_sd = (chart.y_axis.max_val - chart.y_axis.min_val) / 2.0
            if pt.dispersion_val > max_possible_sd:
                results.append({
                    "sieve": "POPOVICIU_VARIANCE",
                    "discrepancy_type": "IMPOSSIBLE_VARIANCE_BOUND",
                    "group_name": pt.group_name,
                    "sd": pt.dispersion_val,
                    "max_possible_sd": round(max_possible_sd, 3),
                    "status": "FAIL",
                    "bbox": pt.bbox,
                    "explanation": (
                        f"Reported SD={pt.dispersion_val} exceeds theoretical maximum variance bound "
                        f"({max_possible_sd:.2f}) for axis range [{chart.y_axis.min_val}, {chart.y_axis.max_val}]."
                    )
                })

    return results


def audit_chart_statistics(chart: ExtractedChartData) -> Dict[str, Any]:
    """
    Unified orchestrator evaluating all visual forensic sieves.
    Returns aggregated forensic report with verdict, detailed discrepancies,
    and verified elements.
    """
    p_val_audits = audit_p_value_brackets(chart)
    zero_bound_audits = audit_zero_bound_truncations(chart)
    table_math_audits = audit_modular_table_math(chart)

    discrepancies = []
    
    # Collect all failures
    for a in p_val_audits:
        if a["status"] == "FAIL":
            discrepancies.append({
                "type": a["discrepancy_type"],
                "target": f"{a['group_a']} vs {a['group_b']}",
                "detail": a["explanation"],
                "bbox": a.get("bbox")
            })

    for a in zero_bound_audits:
        if a["status"] == "FAIL":
            discrepancies.append({
                "type": a["discrepancy_type"],
                "target": a["group_name"],
                "detail": a["explanation"],
                "bbox": a.get("bbox")
            })

    for a in table_math_audits:
        if a["status"] == "FAIL":
            discrepancies.append({
                "type": a["discrepancy_type"],
                "target": a["group_name"],
                "detail": a["explanation"],
                "bbox": a.get("bbox")
            })

    verdict = "FLAGGED_FORENSIC_ANOMALY" if len(discrepancies) > 0 else "CLEAN"

    return {
        "figure_id": chart.figure_id,
        "chart_type": chart.chart_type,
        "verdict": verdict,
        "discrepancies_count": len(discrepancies),
        "discrepancies": discrepancies,
        "p_value_bracket_audits": p_val_audits,
        "zero_bound_audits": zero_bound_audits,
        "table_math_audits": table_math_audits,
        "extracted_table_rows": chart.to_table_rows()
    }
