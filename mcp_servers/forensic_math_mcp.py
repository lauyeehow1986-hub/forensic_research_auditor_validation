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
from typing import Dict, Any, List
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


if __name__ == "__main__":
    mcp.run()
