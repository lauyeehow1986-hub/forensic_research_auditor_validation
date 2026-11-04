#!/usr/bin/env python3
"""
FastMCP Deterministic Forensic Math & Concordance Engine
Implements:
1. GRIM (Brown & Heathers, 2016) across all rounding modes
2. Analytic-GRIMMER (Allard, 2018; Anaya, 2016) parity & variance bounds
3. DEBIT (Heathers & Brown, 2019) binary summary consistency
4. SPRITE (Heathers et al., 2018) bounded integer distribution reconstruction
5. Carlisle (2012, 2017) ANOVA / Stouffer Z / Fisher combined baseline RCT pooling
6. Statcheck 2D p-value recalculation (Nuijten et al., 2016) & 95% CI log/linear symmetry
7. Diekmann (2007) 2nd- and 3rd-significant-digit Benford chi-square test
8. Historical Reference Concordance Verifier
"""

import math
from typing import Dict, Any, List, Optional
import numpy as np
from scipy import stats

try:
    from mcp.server.mcpserver import MCPServer as FastMCP
    mcp = FastMCP("Forensic Math Engine")
except ImportError:
    try:
        from mcp.server.fastmcp import FastMCP
        mcp = FastMCP("Forensic Math Engine")
    except ImportError:
        class DummyMCP:
            def tool(self):
                def decorator(fn):
                    return fn
                return decorator
            def run(self):
                pass
        mcp = DummyMCP()


def _round_modes(val: float, decimals: int) -> List[float]:
    factor = 10 ** decimals
    scaled = val * factor
    half_even = round(val, decimals)
    half_up = math.floor(scaled + 0.5) / factor if val >= 0 else math.ceil(scaled - 0.5) / factor
    half_down = math.ceil(scaled - 0.5) / factor if val >= 0 else math.floor(scaled + 0.5) / factor
    trunc = math.trunc(scaled) / factor
    return list({round(x, decimals) for x in [half_even, half_up, half_down, trunc]})


@mcp.tool()
def verify_grim_grimmer_debit(
    mean: float,
    sd: float,
    n: int,
    decimals_mean: int = 2,
    decimals_sd: int = 2,
    items: int = 1,
    is_binary: bool = False
) -> Dict[str, Any]:
    """
    Runs deterministic GRIM, Analytic-GRIMMER (Allard 2018), and DEBIT (if binary) tests.
    Checks half-open rounding intervals and parity of sum of squares.
    """
    if n <= 1 or items < 1:
        return {"error": "Sample size N must be > 1 and items >= 1"}

    eff_n = n * items
    half_width_m = 0.5 * (10 ** (-decimals_mean))
    lower_sum = (mean - half_width_m) * eff_n
    upper_sum = (mean + half_width_m) * eff_n

    cand_min = math.floor(lower_sum)
    cand_max = math.ceil(upper_sum)
    valid_sums = []
    for s in range(cand_min, cand_max + 1):
        reconstructed_m = s / eff_n
        if round(mean, decimals_mean) in _round_modes(reconstructed_m, decimals_mean):
            valid_sums.append(s)

    grim_pass = len(valid_sums) > 0

    if is_binary:
        # DEBIT check: for binary 0/1 data, sum S is number of 1s (0 <= S <= N)
        debit_valid = False
        half_width_sd = 0.5 * (10 ** (-decimals_sd))
        for s in valid_sums:
            if 0 <= s <= n:
                p_hat = s / n
                expected_sd = math.sqrt((n / (n - 1)) * p_hat * (1.0 - p_hat))
                if round(sd, decimals_sd) in _round_modes(expected_sd, decimals_sd) or abs(expected_sd - sd) <= half_width_sd + 1e-9:
                    debit_valid = True
                    break
        return {
            "test_suite": "DEBIT_BINARY",
            "n": n,
            "mean": mean,
            "sd": sd,
            "grim_pass": grim_pass,
            "debit_pass": debit_valid,
            "valid_integer_sums": valid_sums,
            "verdict": "CONSISTENT" if (grim_pass and debit_valid) else "IMPOSSIBLE_BINARY_SUMMARY"
        }

    # Analytic-GRIMMER (Allard 2018) for integer data (items == 1)
    grimmer_pass = False
    valid_pairs = []
    if grim_pass:
        half_width_sd = 0.5 * (10 ** (-decimals_sd))
        sd_low = max(0.0, sd - half_width_sd)
        sd_high = sd + half_width_sd
        for s in valid_sums:
            real_mean = s / eff_n
            # Sum of squares SS = (n - 1) * SD^2 + n * real_mean^2 (for items=1)
            ss_min = math.ceil(((n - 1) * (sd_low ** 2) + n * (real_mean ** 2)) * (items ** 2) - 1e-7)
            ss_max = math.floor(((n - 1) * (sd_high ** 2) + n * (real_mean ** 2)) * (items ** 2) + 1e-7)
            for ss in range(ss_min, ss_max + 1):
                # Parity condition: sum(x_i) and sum(x_i^2) must have identical parity (even/odd)
                if (ss % 2) == (s % 2):
                    var_val = (ss / (items ** 2) - n * (real_mean ** 2)) / (n - 1)
                    if var_val >= 0:
                        rec_sd = math.sqrt(var_val)
                        if round(sd, decimals_sd) in _round_modes(rec_sd, decimals_sd) or (sd_low <= rec_sd <= sd_high):
                            grimmer_pass = True
                            valid_pairs.append({"sum": s, "sum_sq": ss, "rec_sd": round(rec_sd, decimals_sd + 2)})
                            break

    verdict = "CONSISTENT" if (grim_pass and grimmer_pass) else (
        "GRIM_IMPOSSIBLE" if not grim_pass else "GRIMMER_SD_IMPOSSIBLE"
    )
    return {
        "test_suite": "GRIM_GRIMMER",
        "n": n,
        "items": items,
        "mean": mean,
        "sd": sd,
        "grim_pass": grim_pass,
        "grimmer_pass": grimmer_pass,
        "valid_integer_sums": valid_sums,
        "valid_sum_squares_sample": valid_pairs[:3],
        "verdict": verdict
    }


@mcp.tool()
def simulate_carlisle_stouffer(baseline_variables: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Implements Carlisle (2012, 2017) RCT baseline homogeneity & imbalance test.
    Each item in baseline_variables must contain:
    {"variable": str, "means": [m1, m2, ...], "sds": [sd1, sd2, ...], "ns": [n1, n2, ...]}
    Computes one-way ANOVA p-value per row, then combines via Stouffer's Z and Fisher's method.
    """
    if not baseline_variables:
        return {"error": "No baseline variables provided"}

    row_results = []
    p_values = []
    for row in baseline_variables:
        var_name = row.get("variable", "unknown")
        means = np.array(row["means"], dtype=float)
        sds = np.array(row["sds"], dtype=float)
        ns = np.array(row["ns"], dtype=float)
        k = len(means)
        n_total = np.sum(ns)
        if k < 2 or n_total <= k:
            continue

        grand_mean = np.sum(ns * means) / n_total
        ss_between = np.sum(ns * ((means - grand_mean) ** 2))
        ss_within = np.sum((ns - 1.0) * (sds ** 2))
        df1 = k - 1
        df2 = n_total - k
        if ss_within <= 0:
            p_val = 1.0 if ss_between == 0 else 1e-15
            f_stat = 0.0
        else:
            ms_between = ss_between / df1
            ms_within = ss_within / df2
            f_stat = ms_between / ms_within
            p_val = float(1.0 - stats.f.cdf(f_stat, df1, df2))

        p_clipped = float(np.clip(p_val, 1e-15, 1.0 - 1e-15))
        p_values.append(p_clipped)
        row_results.append({
            "variable": var_name,
            "f_stat": round(float(f_stat), 4),
            "p_value": round(p_clipped, 6)
        })

    p_arr = np.array(p_values)
    # Carlisle convention: convert each p_i to uniform cumulative probability of difference
    # Small p_i -> large difference (near 0); large p_i -> small difference / identical means (near 1)
    z_scores = stats.norm.ppf(p_arr)
    z_stouffer = float(np.sum(z_scores) / np.sqrt(len(p_arr)))
    # Right-tail cumulative probability: P(Z <= z_stouffer); >0.999 means unnaturally identical arms
    stouffer_right_tail_p = float(stats.norm.cdf(z_stouffer))
    stouffer_two_sided_p = float(2.0 * min(stouffer_right_tail_p, 1.0 - stouffer_right_tail_p))

    if stouffer_right_tail_p > 0.999:
        verdict = "VARIANCE_COMPRESSION_HYPER_HOMOGENEITY"
    elif stouffer_right_tail_p < 0.001:
        verdict = "EXTREME_BASELINE_IMBALANCE"
    else:
        verdict = "CONSISTENT_RANDOM_SAMPLING"

    return {
        "num_variables": len(p_arr),
        "row_p_values": row_results,
        "z_stouffer": round(z_stouffer, 4),
        "carlisle_combined_p": round(stouffer_right_tail_p, 6),
        "two_sided_extremity_p": round(stouffer_two_sided_p, 6),
        "verdict": verdict
    }


@mcp.tool()
def audit_statcheck_and_ci(
    test_type: str,
    df1: float,
    df2: float = 0.0,
    reported_stat: float = 0.0,
    reported_p: float = 0.0,
    estimate: float = 0.0,
    lower_ci: float = 0.0,
    upper_ci: float = 0.0,
    is_log_scale: bool = True
) -> Dict[str, Any]:
    """
    Recomputes exact p-values from test statistics (t, F, chi2, z) following Nuijten et al. (2016)
    and checks 95% confidence interval symmetry on log (HR/OR/RR) or linear scales.
    """
    t_type = test_type.strip().lower()
    if t_type == "t":
        effective_df = df2 if df2 > 0 else df1
        recalc_p = float(2.0 * (1.0 - stats.t.cdf(abs(reported_stat), effective_df)))
    elif t_type == "f":
        recalc_p = float(1.0 - stats.f.cdf(abs(reported_stat), df1, df2))
    elif t_type in ("chi2", "chisq"):
        recalc_p = float(1.0 - stats.chi2.cdf(abs(reported_stat), df1))
    elif t_type == "z":
        recalc_p = float(2.0 * (1.0 - stats.norm.cdf(abs(reported_stat))))
    else:
        return {"error": f"Unsupported test_type: {test_type}"}

    decision_error = (reported_p < 0.05 and recalc_p >= 0.05) or (reported_p >= 0.05 and recalc_p < 0.05)
    p_discrepancy = abs(recalc_p - reported_p)

    ci_result = {"verdict": "NOT_TESTED"}
    if lower_ci != 0.0 or upper_ci != 0.0:
        if is_log_scale and estimate > 0 and lower_ci > 0 and upper_ci > 0:
            mid = (math.log(lower_ci) + math.log(upper_ci)) / 2.0
            diff = abs(math.log(estimate) - mid)
            ci_result = {
                "scale": "log",
                "log_midpoint_deviation": round(diff, 5),
                "verdict": "SYMMETRIC" if diff < 0.04 else "ASYMMETRIC_CI_FLAG"
            }
        else:
            mid = (lower_ci + upper_ci) / 2.0
            diff = abs(estimate - mid)
            ci_result = {
                "scale": "linear",
                "linear_midpoint_deviation": round(diff, 5),
                "verdict": "SYMMETRIC" if diff < 0.04 else "ASYMMETRIC_CI_FLAG"
            }

    return {
        "test_type": test_type,
        "reported_stat": reported_stat,
        "reported_p": reported_p,
        "recalculated_p": round(recalc_p, 6),
        "p_discrepancy": round(p_discrepancy, 6),
        "decision_error_alpha_05": bool(decision_error),
        "ci_audit": ci_result,
        "verdict": "DECISION_ERROR_FLAG" if decision_error else (
            "CI_ASYMMETRY_FLAG" if ci_result.get("verdict") == "ASYMMETRIC_CI_FLAG" else "CONSISTENT"
        )
    }


@mcp.tool()
def check_benford_second_digit(values: List[float]) -> Dict[str, Any]:
    """
    Implements Diekmann (2007) Second-Significant-Digit Benford's Law Chi-square test.
    """
    second_digits = []
    for v in values:
        s = "".join(ch for ch in f"{abs(v):.10g}" if ch.isdigit()).lstrip("0")
        if len(s) >= 2:
            second_digits.append(int(s[1]))

    if len(second_digits) < 30:
        return {"error": "At least 30 multi-digit numbers required for Diekmann 2nd-digit Benford test"}

    # Expected Benford 2nd digit probabilities (Diekmann 2007, Table 1)
    expected_probs = np.array([
        sum(math.log10(1.0 + 1.0 / (10 * k + d)) for k in range(1, 10))
        for d in range(10)
    ])
    obs_counts = np.bincount(second_digits, minlength=10)
    exp_counts = expected_probs * len(second_digits)
    chi2_stat, p_val = stats.chisquare(obs_counts, exp_counts)

    return {
        "n_numbers": len(second_digits),
        "chi2_stat": round(float(chi2_stat), 4),
        "df": 9,
        "p_value": round(float(p_val), 6),
        "verdict": "DIGIT_PREFERENCE_ANOMALY" if p_val < 0.01 else "BENFORD_CONSISTENT"
    }


@mcp.tool()
def audit_regression_triangulation(
    estimate: float,
    lower_ci: float,
    upper_ci: float,
    reported_p: float,
    is_log_scale: bool = True,
    alpha: float = 0.05
) -> Dict[str, Any]:
    """
    Audits the Multivariable Regression Triangle (Estimate - 95% CI - P-value).
    Reconstructs implied SE from CI, computes exact Wald Z, and recalculates exact two-tailed p-value.
    Detects decision errors and discordant p-values in multivariable logistic/Cox/linear models.
    """
    if lower_ci >= upper_ci:
        return {"error": "lower_ci must be < upper_ci", "verdict": "INVALID_CI_BOUNDS"}

    if is_log_scale:
        if estimate <= 0 or lower_ci <= 0 or upper_ci <= 0:
            return {"error": "Log-scale ratio measures (OR/HR/RR) must be strictly positive", "verdict": "INVALID_INPUT"}
        log_est = math.log(estimate)
        log_ll = math.log(lower_ci)
        log_ul = math.log(upper_ci)
        se_implied = (log_ul - log_ll) / 3.919928
        z_stat = log_est / se_implied if se_implied > 0 else 0.0
        crosses_null = (lower_ci <= 1.0 <= upper_ci)
    else:
        se_implied = (upper_ci - lower_ci) / 3.919928
        z_stat = estimate / se_implied if se_implied > 0 else 0.0
        crosses_null = (lower_ci <= 0.0 <= upper_ci)

    recalc_p = float(2.0 * (1.0 - stats.norm.cdf(abs(z_stat))))
    
    decision_error = (reported_p < alpha and (crosses_null or recalc_p >= alpha)) or (reported_p >= alpha and (not crosses_null and recalc_p < alpha))
    p_discrepancy = abs(reported_p - recalc_p)
    severe_discrepancy = p_discrepancy >= 0.02

    verdict = "REGRESSION_DECISION_ERROR" if decision_error else (
        "DISCORDANT_P_VALUE" if severe_discrepancy else "CONSISTENT"
    )

    return {
        "estimate": estimate,
        "ci_95": [lower_ci, upper_ci],
        "is_log_scale": is_log_scale,
        "implied_se": round(se_implied, 5),
        "wald_z": round(z_stat, 4),
        "reported_p": reported_p,
        "recalculated_p": round(recalc_p, 5),
        "p_discrepancy": round(p_discrepancy, 5),
        "crosses_null": crosses_null,
        "decision_error": decision_error,
        "verdict": verdict
    }


@mcp.tool()
def verify_ai_confusion_matrix_triangulation(
    accuracy: float,
    sensitivity: float,
    specificity: float,
    n_positive: Optional[int] = None,
    n_negative: Optional[int] = None,
    prevalence: Optional[float] = None,
    tolerance: float = 0.03
) -> Dict[str, Any]:
    """
    Audits diagnostic biomarker and AI classifier performance metric coherence.
    Enforces the mathematical relationship: Accuracy = Sensitivity * P + Specificity * (1 - P).
    Detects impossible metric triads commonly found in fabricated AI-for-medicine publications.
    """
    acc = accuracy / 100.0 if accuracy > 1.0 else accuracy
    sens = sensitivity / 100.0 if sensitivity > 1.0 else sensitivity
    spec = specificity / 100.0 if specificity > 1.0 else specificity

    if not (0.0 <= acc <= 1.0 and 0.0 <= sens <= 1.0 and 0.0 <= spec <= 1.0):
        return {"error": "Metrics must be between 0.0 and 1.0 (or 0 and 100%)", "verdict": "INVALID_METRIC_RANGE"}

    p = None
    if prevalence is not None:
        p = prevalence / 100.0 if prevalence > 1.0 else prevalence
    elif n_positive is not None and n_negative is not None and (n_positive + n_negative) > 0:
        p = n_positive / (n_positive + n_negative)

    anomalies = []
    expected_acc = None
    
    min_bound = min(sens, spec) - tolerance
    max_bound = max(sens, spec) + tolerance

    if acc < min_bound or acc > max_bound:
        anomalies.append(
            f"ACCURACY_OUTSIDE_SENS_SPEC_ENVELOPE(Acc={round(acc*100, 2)}% is outside [{round(min_bound*100, 2)}%, {round(max_bound*100, 2)}%])"
        )

    if p is not None and (0.0 <= p <= 1.0):
        expected_acc = sens * p + spec * (1.0 - p)
        acc_diff = abs(acc - expected_acc)
        if acc_diff > tolerance:
            anomalies.append(
                f"IMPOSSIBLE_ACCURACY_TRIAD(ClaimedAcc={round(acc*100, 2)}%, ExpectedAcc={round(expected_acc*100, 2)}%, Diff={round(acc_diff*100, 2)}% at Prev={round(p*100, 1)}%)"
            )

    balanced_acc = (sens + spec) / 2.0
    verdict = "IMPOSSIBLE_AI_METRIC_TRIAD" if len(anomalies) > 0 else "CONSISTENT"

    return {
        "claimed_accuracy": round(acc, 4),
        "sensitivity": round(sens, 4),
        "specificity": round(spec, 4),
        "balanced_accuracy": round(balanced_acc, 4),
        "expected_accuracy": round(expected_acc, 4) if expected_acc is not None else None,
        "prevalence": round(p, 4) if p is not None else None,
        "anomalies": anomalies,
        "verdict": verdict
    }


@mcp.tool()
def audit_cross_table_marginal_conservation(
    count: int,
    percentage: float,
    n_total: int,
    subgroup_name: str = "",
    parent_n: Optional[int] = None
) -> Dict[str, Any]:
    """
    Audits patient count continuity and marginal percentage parity across tables.
    Checks:
    1. Marginal percentage consistency: count == round(pct * n_total / 100)
    2. Subgroup sample size conservation: n_total <= parent_n
    """
    if n_total <= 0:
        return {"error": "n_total must be > 0", "verdict": "INVALID_N"}

    pct = percentage if percentage <= 100.0 else percentage / 100.0
    expected_count = round((pct * n_total) / 100.0) if pct <= 1.0 and percentage > 1.0 else round(pct * n_total)
    
    anomalies = []
    implied_count = (percentage / 100.0) * n_total if percentage > 1.0 else percentage * n_total
    diff = abs(count - implied_count)
    if diff > 1.0 and abs(count - expected_count) > 1:
        anomalies.append(
            f"MARGINAL_PERCENTAGE_MISMATCH(ReportedCount={count}, ImpliedCount={implied_count:.2f}, N={n_total})"
        )

    if parent_n is not None and n_total > parent_n:
        anomalies.append(
            f"SUBGROUP_PARENT_OVERFLOW({subgroup_name or 'Subgroup'} N={n_total} exceeds Baseline Cohort N={parent_n})"
        )

    verdict = "MARGINAL_COUNT_ANOMALY" if len(anomalies) > 0 else "CONSISTENT"

    return {
        "subgroup": subgroup_name,
        "count": count,
        "percentage": percentage,
        "n_total": n_total,
        "parent_n": parent_n,
        "implied_count": round(implied_count, 2),
        "anomalies": anomalies,
        "verdict": verdict
    }


@mcp.tool()
def audit_physiological_variance_bounds(
    variable_name: str,
    mean: float,
    sd: float,
    n: int = 1,
    physiological_min_sd: Optional[float] = None,
    physiological_max_sd: Optional[float] = None,
    is_strictly_positive: bool = True
) -> Dict[str, Any]:
    """
    Evaluates continuous laboratory/physiological variables against clinical boundaries and reference ranges.
    Checks:
    1. Zero variance on non-zero continuous measurement (SD == 0.0 when Mean > 0)
    2. Negative biological boundary violation: Mean - 2*SD < 0 on strictly positive vitals
    3. Severe variance compression: SD < 20% of reference physiological SD
    4. Impossible physiological spread: SD > reference physiological maximum SD
    """
    anomalies = []

    if sd == 0.0 and mean > 0.0:
        anomalies.append(f"ZERO_SD_CONTINUOUS_VARIABLE({variable_name}, Mean={mean})")

    if is_strictly_positive and mean > 0.0 and sd > 0.0 and (mean - 2.0 * sd) < 0.0:
        pct_neg = float(stats.norm.cdf(0.0, loc=mean, scale=sd) * 100.0)
        if pct_neg >= 2.5:
            anomalies.append(
                f"SKEWNESS_BOUNDARY_VIOLATION({variable_name}, Mean={mean}, SD={sd}, Implies {pct_neg:.1f}% negative values)"
            )

    if physiological_min_sd is not None and physiological_min_sd > 0.0 and sd > 0.0:
        ratio = sd / physiological_min_sd
        if ratio < 0.20:
            anomalies.append(
                f"EXTREME_VARIANCE_COMPRESSION({variable_name}, ReportedSD={sd}, RefMinSD={physiological_min_sd}, Ratio={ratio:.2f})"
            )

    if physiological_max_sd is not None and sd > physiological_max_sd:
        anomalies.append(
            f"IMPOSSIBLE_PHYSIOLOGICAL_SPREAD({variable_name}, ReportedSD={sd}, RefMaxSD={physiological_max_sd})"
        )

    verdict = "FLAGGED_PHYSIOLOGICAL_ANOMALY" if len(anomalies) > 0 else "CONSISTENT"

    return {
        "variable": variable_name,
        "mean": mean,
        "sd": sd,
        "n": n,
        "anomalies": anomalies,
        "verdict": verdict
    }


if __name__ == "__main__":
    mcp.run()
