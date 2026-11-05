"""
Synthetic Chart Test Fixture Generator.
Programmatically generates high-DPI matplotlib chart images with known ground-truth
forensic properties (GRIM failure, significance inversion, zero-bound truncation, clean control).
"""

import os
from typing import Dict, Any
import numpy as np
import scipy.stats as stats

# Enforce headless matplotlib backend
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt


def generate_grim_fail_bar_chart(output_path: str) -> Dict[str, Any]:
    """
    Renders a bar chart where Group 1 reports a mean (1.42) on a discrete integer scale
    with N=15, mathematically violating the GRIM test (1.42 * 15 = 21.3 != integer).
    """
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)

    fig, ax = plt.subplots(figsize=(6, 4.5), dpi=300)
    groups = ["Control (N=15)", "Treated (N=15)"]
    means = [1.42, 3.20]
    sds = [0.40, 0.50]
    n_sample = 15

    x = np.arange(len(groups))
    bars = ax.bar(x, means, yerr=sds, capsize=6, color=["#60a5fa", "#34d399"], edgecolor="black", width=0.5)

    ax.set_ylabel("Severity Score (1-5 Integer Scale)", fontsize=11, fontweight="bold")
    ax.set_title("Clinical Symptom Score by Group", fontsize=12, fontweight="bold")
    ax.set_xticks(x)
    ax.set_xticklabels(groups, fontsize=10)
    ax.set_ylim(0, 5.0)
    ax.grid(axis="y", linestyle="--", alpha=0.5)

    # Value labels
    for bar, m in zip(bars, means):
        ax.text(bar.get_x() + bar.get_width()/2, 0.1, f"Mean: {m:.2f}", 
                ha="center", va="bottom", color="black", fontweight="bold", fontsize=9)

    plt.tight_layout()
    plt.savefig(output_path, dpi=300)
    plt.close(fig)

    return {
        "target_anomaly": "GRIM_INCONSISTENCY",
        "chart_type": "BAR_WITH_ERROR_BARS",
        "y_axis_label": "Severity Score (1-5 Integer Scale)",
        "y_min": 0.0,
        "y_max": 5.0,
        "groups": [
            {"name": "Control", "mean": 1.42, "sd": 0.40, "n_sample": 15, "is_discrete": True},
            {"name": "Treated", "mean": 3.20, "sd": 0.50, "n_sample": 15, "is_discrete": True}
        ]
    }


def generate_significance_inversion_chart(output_path: str) -> Dict[str, Any]:
    """
    Renders a bar chart claiming high statistical significance (*** p < 0.001)
    over two groups whose means and SDs yield a non-significant Welch's t-test (p > 0.40).
    """
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)

    fig, ax = plt.subplots(figsize=(6, 4.5), dpi=300)
    groups = ["Vehicle", "Compound X"]
    means = [5.0, 5.6]
    sds = [2.0, 2.2]
    n_sample = 10

    # True Welch's t-test
    res = stats.ttest_ind_from_stats(means[0], sds[0], n_sample, means[1], sds[1], n_sample, equal_var=False)
    actual_p = float(res.pvalue)
    actual_t = float(res.statistic)

    x = np.arange(len(groups))
    bars = ax.bar(x, means, yerr=sds, capsize=6, color=["#94a3b8", "#f87171"], edgecolor="black", width=0.5)

    ax.set_ylabel("Enzyme Activity (U/L)", fontsize=11, fontweight="bold")
    ax.set_title("Response to Compound X (n=10/group)", fontsize=12, fontweight="bold")
    ax.set_xticks(x)
    ax.set_xticklabels(groups, fontsize=10)
    ax.set_ylim(0, 10.0)
    ax.grid(axis="y", linestyle="--", alpha=0.5)

    # Significance bracket claiming *** (p < 0.001) over a non-significant result
    y_bar = 8.5
    h = 0.3
    ax.plot([x[0], x[0], x[1], x[1]], [y_bar, y_bar + h, y_bar + h, y_bar], lw=1.5, c="black")
    ax.text((x[0] + x[1]) * 0.5, y_bar + h + 0.1, "***", ha="center", va="bottom", color="red", fontsize=14, fontweight="bold")

    plt.tight_layout()
    plt.savefig(output_path, dpi=300)
    plt.close(fig)

    return {
        "target_anomaly": "SIGNIFICANCE_INVERSION",
        "chart_type": "BAR_WITH_ERROR_BARS",
        "claimed_p_text": "***",
        "claimed_p_threshold": 0.001,
        "actual_welch_p": actual_p,
        "actual_welch_t": actual_t,
        "groups": [
            {"name": "Vehicle", "mean": 5.0, "sd": 2.0, "n_sample": 10},
            {"name": "Compound X", "mean": 5.6, "sd": 2.2, "n_sample": 10}
        ]
    }


def generate_zero_bound_truncation_chart(output_path: str) -> Dict[str, Any]:
    """
    Renders a bar chart where Mean = 2.0 and SD = 3.0 on a strictly non-negative biological assay.
    The lower error bar is truncated flat at Y=0 to conceal that normal variance entails negative values.
    """
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)

    fig, ax = plt.subplots(figsize=(6, 4.5), dpi=300)
    group_name = "Patient Cohort"
    mean_val = 2.0
    sd_val = 3.0
    n_sample = 12

    # Draw bar
    x = [0]
    ax.bar(x, [mean_val], color="#fbbf24", edgecolor="black", width=0.4)

    # Manually draw upper error bar (extends to 2.0 + 3.0 = 5.0)
    ax.plot([0, 0], [mean_val, mean_val + sd_val], color="black", lw=1.5)
    ax.plot([-0.08, 0.08], [mean_val + sd_val, mean_val + sd_val], color="black", lw=1.5)

    # Draw truncated lower error bar that stops flat exactly at 0.0
    ax.plot([0, 0], [mean_val, 0.0], color="black", lw=1.5)
    ax.plot([-0.08, 0.08], [0.0, 0.0], color="black", lw=1.5)

    # Value label
    ax.text(0, 0.2, f"Mean: {mean_val:.1f}, SD: {sd_val:.1f}",
            ha="center", va="bottom", color="black", fontweight="bold", fontsize=9)

    ax.set_ylabel("Troponin T (ng/mL)", fontsize=11, fontweight="bold")
    ax.set_title("Baseline Cardiac Troponin (n=12)", fontsize=12, fontweight="bold")
    ax.set_xticks([0])
    ax.set_xticklabels([group_name], fontsize=10)
    ax.set_ylim(0, 6.0)
    ax.grid(axis="y", linestyle="--", alpha=0.5)

    plt.tight_layout()
    plt.savefig(output_path, dpi=300)
    plt.close(fig)

    return {
        "target_anomaly": "ZERO_BOUND_TRUNCATION",
        "chart_type": "BAR_WITH_ERROR_BARS",
        "lower_error_bar_truncated": True,
        "assay_physically_bounded": True,
        "groups": [
            {"name": group_name, "mean": mean_val, "sd": sd_val, "n_sample": n_sample}
        ]
    }


def generate_clean_control_chart(output_path: str) -> Dict[str, Any]:
    """
    Renders a clean, mathematically self-consistent chart where Mean and SD
    divide cleanly, error bars are symmetric and well away from zero, and claimed
    bracket significance matches the true Welch t-test.
    """
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)

    fig, ax = plt.subplots(figsize=(6, 4.5), dpi=300)
    groups = ["Wild Type", "Knockout"]
    means = [2.0, 4.5]
    sds = [0.4, 0.5]
    n_sample = 10

    res = stats.ttest_ind_from_stats(means[0], sds[0], n_sample, means[1], sds[1], n_sample, equal_var=False)
    actual_p = float(res.pvalue)
    actual_t = float(res.statistic)

    x = np.arange(len(groups))
    bars = ax.bar(x, means, yerr=sds, capsize=6, color=["#60a5fa", "#3b82f6"], edgecolor="black", width=0.5)

    ax.set_ylabel("Gene Expression Fold Change", fontsize=11, fontweight="bold")
    ax.set_title("mRNA Expression Levels (n=10/group)", fontsize=12, fontweight="bold")
    ax.set_xticks(x)
    ax.set_xticklabels(groups, fontsize=10)
    ax.set_ylim(0, 6.0)
    ax.grid(axis="y", linestyle="--", alpha=0.5)

    # Valid significance bracket matching actual p < 0.0001
    y_bar = 5.2
    h = 0.2
    ax.plot([x[0], x[0], x[1], x[1]], [y_bar, y_bar + h, y_bar + h, y_bar], lw=1.5, c="black")
    ax.text((x[0] + x[1]) * 0.5, y_bar + h + 0.05, "***", ha="center", va="bottom", color="black", fontsize=13, fontweight="bold")

    plt.tight_layout()
    plt.savefig(output_path, dpi=300)
    plt.close(fig)

    return {
        "target_anomaly": "NONE",
        "is_clean": True,
        "chart_type": "BAR_WITH_ERROR_BARS",
        "claimed_p_text": "***",
        "claimed_p_threshold": 0.001,
        "actual_welch_p": actual_p,
        "actual_welch_t": actual_t,
        "groups": [
            {"name": "Wild Type", "mean": 2.0, "sd": 0.4, "n_sample": 10},
            {"name": "Knockout", "mean": 4.5, "sd": 0.5, "n_sample": 10}
        ]
    }
