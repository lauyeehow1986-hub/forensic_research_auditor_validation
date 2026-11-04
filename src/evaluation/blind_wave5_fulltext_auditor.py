#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Blind Full-Text JATS XML & Table Forensic Auditor — Wave 5 (2,000 Real Studies: 1,000 Cases vs. 1,000 Controls)
Fully automated, unassisted, zero-registry-shortcut empirical forensic benchmark.
Evaluates across the UPGRADED & HIGH-SPECIFICITY MULTI-CELL CONSENSUS 5-Gate Forensic Architecture:
- Gate 1: Provenance & Retraction Hygiene
- Gate 2: Paper-Mill & Reagent Forensics
- Gate 3: Universal Table, Continuous Biomarker & Multivariate Math Forensics:
    * Sieve 1: Discrete Granularity (GRIM, GRIMMER, DEBIT) with Multi-Cell Consensus
    * Sieve 2: Continuous Biomarker Boundary & Physiological Bounds (audit_physiological_variance_bounds)
    * Sieve 3: SPRITE Bounded Discrete Distribution Reconstruction
    * Sieve 4: Correlation Matrix Positive Semi-Definiteness (all eigenvalues >= 0)
    * Sieve 5: Tabular & Inline NHST Statcheck Recalculations & P-Hacking Cliff Ratio
    * Sieve 6: Multivariable Regression Triangle (beta - SE - p Wald Recalculation)
    * Sieve 7: AI & Diagnostic Classifier Confusion Matrix Triangulation
    * Sieve 8: Cross-Table Sample Size & Marginal Conservation
    * Sieve 9: Carlisle Multi-Arm Table 1 Hyper-Homogeneity with Arm-Count Bonferroni Gating
    * Sieve 10: Multi-Magnitude Benford 2nd-Digit Conformity (Decadic Dynamic Span >= 2.0)
- Gate 3.5: Images, Figures & Multi-Omics Plots (Decoupled from Math)
- Gate 4: Governance, Editorial Ethics & Pre-Registration

Wave 5 High-Specificity Upgrade:
1. Multi-Cell Consensus Rule: Isolated single-cell anomalies are demoted to Tier 2 triage flags,
   preventing clerical author typos from triggering fatal fraud accusations.
2. Decadic Dynamic Span >= 2.0 decades (100-fold dynamic range) for Benford tests.
3. Enhanced Table 1 Non-Parametric & Percentage Filtering.
4. Carlisle ANOVA arm-count gating (>= 5 continuous variables, N >= 10, p < 1e-5).

Strict Quadruple Non-Intersection Guarantee:
Zero overlap with Wave 1 (cohort_2000_manifest.json), Wave 2 (cohort_wave2_manifest.json),
Wave 3 (cohort_wave3_manifest.json), AND Wave 4 (cohort_wave4_manifest.json).
Total benchmark scale: 10,000 studies (5,000 cases vs. 5,000 controls).
"""

import concurrent.futures
import json
import math
import os
import re
import sys
import time
import urllib.parse
import urllib.request
import urllib.error
import xml.etree.ElementTree as ET
from typing import Dict, Any, List, Optional, Tuple, Set

import numpy as np
from scipy import stats

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from mcp_servers.forensic_math_mcp import (
    verify_grim_grimmer_debit,
    simulate_carlisle_stouffer,
    audit_statcheck_and_ci,
    check_benford_second_digit,
    audit_regression_triangulation,
    verify_ai_confusion_matrix_triangulation,
    audit_cross_table_marginal_conservation,
    audit_physiological_variance_bounds
)
from src.ingestion.api_connectors import (
    classify_variable_semantic_type,
    screen_tortured_phrases,
    classify_retraction_tier
)

# Statistical regex patterns
MEAN_SD_REGEX = re.compile(r"(\d+(?:\.\d+)?)\s*(?:±|\+/-|\s*\(\s*SD\s*[:=]?\s*|\s*[\xb1\u00b1]\s*)\s*(\d+(?:\.\d+)?)\)?")
COUNT_PCT_REGEX = re.compile(r"(\d+)\s*\(([\d\.]+)%?\)")
STATCHECK_T_REGEX = re.compile(r"t\s*\(\s*(\d+(?:\.\d+)?)\s*\)\s*=\s*(-?\d+(?:\.\d+)?)[,\s]+p\s*([<>=])\s*(\d+(?:\.\d+)?)", re.IGNORECASE)
STATCHECK_F_REGEX = re.compile(r"F\s*\(\s*(\d+(?:\.\d+)?)\s*,\s*(\d+(?:\.\d+)?)\s*\)\s*=\s*(\d+(?:\.\d+)?)[,\s]+p\s*([<>=])\s*(\d+(?:\.\d+)?)", re.IGNORECASE)
STATCHECK_CHI2_REGEX = re.compile(r"(?:χ2|chi2?|chi-square)\s*\(\s*(\d+(?:\.\d+)?)\s*\)\s*=\s*(\d+(?:\.\d+)?)[,\s]+p\s*([<>=])\s*(\d+(?:\.\d+)?)", re.IGNORECASE)
LOG_CI_REGEX = re.compile(r"\b(OR|HR|RR)\s*(?:=|:|\s)\s*(\d+(?:\.\d+)?)[,\s]+(?:95%\s*CI\s*[:=\[\]\s]+|\(\s*95%\s*CI\s*[:=\s]+)(\d+(?:\.\d+)?)\s*(?:-|–|to|,)\s*(\d+(?:\.\d+)?)\)?", re.IGNORECASE)
SAMPLE_SIZE_REGEX = re.compile(r"\b(?:n|N)\s*[:=]\s*(\d+)\b|\b(?:n|N)\s*=\s*(\d+)\b|\((\d+)\s*(?:patients|subjects|cases|participants|eyes|rats|mice)\)", re.IGNORECASE)

AI_ACCURACY_REGEX = re.compile(r"\b(?:accuracy|acc)\s*[:=]?\s*(\d+(?:\.\d+)?)\s*%?", re.IGNORECASE)
AI_SENSITIVITY_REGEX = re.compile(r"\b(?:sensitivity|recall|tpr|sens)\s*[:=]?\s*(\d+(?:\.\d+)?)\s*%?", re.IGNORECASE)
AI_SPECIFICITY_REGEX = re.compile(r"\b(?:specificity|tnr|spec)\s*[:=]?\s*(\d+(?:\.\d+)?)\s*%?", re.IGNORECASE)

XML_CACHE_DIR = os.path.join("data", "xml_cache")
os.makedirs(XML_CACHE_DIR, exist_ok=True)


def wilson_95_ci(k: int, n: int) -> Dict[str, float]:
    """Calculates Wilson score 95% confidence interval for proportion k/n."""
    if n <= 0:
        return {"proportion": 0.0, "lower_95": 0.0, "upper_95": 0.0}
    z = 1.959963984540054
    p = k / n
    denom = 1.0 + (z ** 2) / n
    center = (p + (z ** 2) / (2.0 * n)) / denom
    half_width = (z * math.sqrt((p * (1.0 - p) / n) + (z ** 2) / (4.0 * (n ** 2)))) / denom
    return {
        "proportion": round(p * 100.0, 2),
        "lower_95": round(max(0.0, center - half_width) * 100.0, 2),
        "upper_95": round(min(1.0, center + half_width) * 100.0, 2)
    }


def get_or_download_xml(pmcid: str) -> Optional[str]:
    """Retrieves full-text JATS XML from disk cache or downloads from Europe PMC REST API."""
    if not pmcid or not pmcid.startswith("PMC"):
        return None
    
    clean_id = pmcid.replace("PMC", "").strip()
    cache_path = os.path.join(XML_CACHE_DIR, f"PMC{clean_id}.xml")
    if os.path.exists(cache_path) and os.path.getsize(cache_path) > 500:
        try:
            with open(cache_path, "r", encoding="utf-8") as f:
                return f.read()
        except Exception:
            pass

    url = f"https://www.ebi.ac.uk/europepmc/webservices/rest/PMC{clean_id}/fullTextXML"
    req = urllib.request.Request(url, headers={"User-Agent": "Wave5Auditor/5.0"})
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=25) as resp:
                content = resp.read().decode("utf-8")
                if len(content) > 500 and "<article" in content:
                    with open(cache_path, "w", encoding="utf-8") as f:
                        f.write(content)
                    return content
        except Exception:
            time.sleep(0.5 + attempt * 0.5)
            
    return None


def extract_table_arm_ns(table_elem: ET.Element) -> Tuple[List[str], Dict[int, int], Optional[int]]:
    """Extracts column headers, arm sample sizes (N), and overall study N from table markup."""
    headers = []
    col_to_n = {}
    overall_n = None

    caption_text = ""
    for cap in table_elem.findall(".//caption"):
        caption_text += " " + "".join(cap.itertext())
    m_cap = SAMPLE_SIZE_REGEX.search(caption_text)
    if m_cap:
        for g in m_cap.groups():
            if g:
                try:
                    overall_n = int(g)
                    break
                except ValueError:
                    pass

    for th in table_elem.findall(".//thead//th"):
        h_text = "".join(th.itertext()).strip()
        headers.append(h_text)
        col_idx = len(headers) - 1
        m_th = SAMPLE_SIZE_REGEX.search(h_text)
        if m_th:
            for g in m_th.groups():
                if g:
                    try:
                        n_val = int(g)
                        col_to_n[col_idx] = n_val
                        if overall_n is None or n_val > overall_n:
                            overall_n = n_val
                    except ValueError:
                        pass

    return headers, col_to_n, overall_n


def check_correlation_matrix_psd(rows: List[List[float]]) -> Optional[Dict[str, Any]]:
    """Evaluates whether an extracted correlation matrix is positive semi-definite (all eigenvalues >= 0)."""
    try:
        arr = np.array(rows, dtype=float)
        p = arr.shape[0]
        if p < 3 or arr.shape[1] != p:
            return None
        if not np.allclose(arr, arr.T, atol=0.05):
            return None
        if not np.allclose(np.diag(arr), 1.0, atol=0.05):
            return None
        eigenvals = np.linalg.eigvalsh(arr)
        min_eig = float(np.min(eigenvals))
        if min_eig < -0.05:
            return {
                "verdict": "NON_POSITIVE_DEFINITE",
                "min_eigenvalue": round(min_eig, 5),
                "p_dim": p
            }
        return {"verdict": "CONSISTENT_POSITIVE_DEFINITE", "min_eigenvalue": round(min_eig, 5), "p_dim": p}
    except Exception:
        return None


def parse_and_audit_xml_wave5(study: Dict[str, Any], xml_str: Optional[str]) -> Dict[str, Any]:
    """
    Evaluates study full text across the Wave 5 UPGRADED 5-Gate Forensic Architecture with Multi-Cell Consensus.
    """
    result = {
        "study_id": study["study_id"],
        "wave": 5,
        "cohort": study["cohort"],
        "pmcid": study["pmcid"],
        "journal": study["journal"],
        "year": study["year"],
        "title": study["title"],
        "doi": study.get("doi", ""),
        "xml_downloaded": bool(xml_str),
        "retraction_tier": "CONTROL" if study["cohort"] == "CONTROL" else "GATE_4_GOVERNANCE",
        "target_gate": "CONTROL" if study["cohort"] == "CONTROL" else "GATE_4_GOVERNANCE",
        "retraction_notice_info": "",
        "tortured_phrases_found": 0,
        "tortured_phrases": [],
        "benford_chi2": 0.0,
        "benford_p": 1.0,
        "benford_verdict": "NOT_TESTED",
        "statcheck_tests_mined": 0,
        "statcheck_errors": 0,
        "log_ci_tests": 0,
        "log_ci_asymmetries": 0,
        "regression_models_tested": 0,
        "regression_decision_errors": 0,
        "regression_p_discrepancies": 0,
        "ai_metric_triads_tested": 0,
        "ai_metric_triad_failures": 0,
        "marginal_cells_tested": 0,
        "marginal_conservation_failures": 0,
        "physiological_bounds_tested": 0,
        "physiological_variance_failures": 0,
        "tables_extracted": 0,
        "table_rows_evaluated": 0,
        "strict_n_verified_tests": 0,
        "grim_failures": 0,
        "grimmer_failures": 0,
        "debit_failures": 0,
        "biomarker_boundary_failures": 0,
        "sprite_variance_failures": 0,
        "correlation_psd_failures": 0,
        "carlisle_stouffer_z": 0.0,
        "carlisle_combined_p": 0.5,
        "carlisle_hyper_homogeneous": False,
        "fatal_flags": [],
        "consensus_flags": [],
        "warnings_triggered": [],
        "blind_verdict": "CLEAN",
        "math_gate_triggered": False,
        "nlp_gate_triggered": False,
        "flags_triggered": []
    }

    if not xml_str:
        return result

    try:
        clean_xml = re.sub(r'\sxmlns="[^"]+"', '', xml_str, count=1)
        root = ET.fromstring(clean_xml)

        # 1. Metadata and Retraction Lineage
        for aid in root.findall(".//article-id"):
            id_type = aid.attrib.get("pub-id-type")
            if id_type == "doi" and aid.text:
                result["doi"] = aid.text.strip()
            elif id_type == "pmid" and aid.text:
                result["pmid"] = aid.text.strip()

        for ra in root.findall(".//related-article"):
            ra_type = ra.attrib.get("related-article-type", "")
            if "retract" in ra_type:
                result["retraction_notice_info"] = "".join(ra.itertext()).strip()

        # Extract full text
        text_paragraphs = []
        for p in root.findall(".//body//p") + root.findall(".//abstract//p"):
            t = "".join(p.itertext()).strip()
            if t:
                text_paragraphs.append(t)
        full_text = " ".join(text_paragraphs)

        # 2. Gate 2: Cabanac Tortured Phrases Screener
        tp_res = screen_tortured_phrases(full_text)
        if isinstance(tp_res, dict) and tp_res.get("verdict") == "TORTURED_PHRASES_DETECTED":
            genuine_tps = [p for p in tp_res.get("detected_phrases", []) if " " in p or p.lower() not in ["vitality", "cloud"]]
            if len(genuine_tps) > 0:
                result["tortured_phrases_found"] = len(genuine_tps)
                result["tortured_phrases"] = genuine_tps
                flag_str = f"CABANAC_TORTURED_PHRASES({len(genuine_tps)})"
                result["flags_triggered"].append(flag_str)
                result["nlp_gate_triggered"] = True
                if len(genuine_tps) >= 2:
                    result["fatal_flags"].append(flag_str)
                else:
                    result["consensus_flags"].append(flag_str)

        # 3. Gate 3 Sieve 10: Diekmann 2nd-Digit Benford's Law Chi-Square Test (Decadic Span >= 2.0)
        table_numbers = []
        for td in root.findall(".//table-wrap//tbody//td"):
            cell_txt = "".join(td.itertext()).strip()
            for m in re.finditer(r"\b\d+(?:\.\d+)?\b", cell_txt):
                try:
                    val = float(m.group(0))
                    if val >= 10.0 and not (1950.0 <= val <= 2030.0):
                        table_numbers.append(val)
                except ValueError:
                    pass
        
        if len(table_numbers) >= 40:
            pos_vals = [abs(x) for x in table_numbers if abs(x) > 0]
            if pos_vals:
                min_v = min(pos_vals)
                max_v = max(pos_vals)
                span = math.log10(max_v / min_v) if min_v > 0 else 0.0
                # Enforce decadic dynamic span >= 2.0 (100-fold dynamic range)
                if span >= 2.0:
                    benford_res = check_benford_second_digit(table_numbers[:300])
                    result["benford_chi2"] = benford_res.get("chi2_stat", 0.0)
                    result["benford_p"] = benford_res.get("p_value", 1.0)
                    result["benford_verdict"] = benford_res.get("verdict", "BENFORD_CONSISTENT")
                    if result["benford_verdict"] == "DIGIT_PREFERENCE_ANOMALY" and result["benford_p"] < 0.001:
                        flag_str = f"BENFORD_2ND_DIGIT_ANOMALY(p={result['benford_p']:.6f})"
                        result["flags_triggered"].append(flag_str)
                        result["consensus_flags"].append(flag_str)
                else:
                    result["benford_verdict"] = "NARROW_DYNAMIC_RANGE_INAPPLICABLE"

        # 4. Gate 3 Sieve 5: Statcheck Inline Text Mining (t, F, chi2) & P-Hacking Cliff
        p_values_found = []
        for m in STATCHECK_T_REGEX.finditer(full_text):
            result["statcheck_tests_mined"] += 1
            df_val = float(m.group(1))
            t_val = float(m.group(2))
            p_val = float(m.group(4))
            p_values_found.append(p_val)
            sc_res = audit_statcheck_and_ci(test_type="t", df1=df_val, reported_stat=t_val, reported_p=p_val)
            if sc_res.get("decision_error_alpha_05"):
                result["statcheck_errors"] += 1
                flag_str = f"STATCHECK_DECISION_ERROR_T(t={t_val},df={df_val},rep_p={p_val},calc_p={sc_res.get('recalculated_p')})"
                result["flags_triggered"].append(flag_str)
                if p_val < 0.005 and sc_res.get("recalculated_p", 0.0) >= 0.15:
                    result["fatal_flags"].append(flag_str)
                else:
                    result["consensus_flags"].append(flag_str)

        for m in STATCHECK_F_REGEX.finditer(full_text):
            result["statcheck_tests_mined"] += 1
            df1_val = float(m.group(1))
            df2_val = float(m.group(2))
            f_val = float(m.group(3))
            p_val = float(m.group(5))
            p_values_found.append(p_val)
            sc_res = audit_statcheck_and_ci(test_type="f", df1=df1_val, df2=df2_val, reported_stat=f_val, reported_p=p_val)
            if sc_res.get("decision_error_alpha_05"):
                result["statcheck_errors"] += 1
                flag_str = f"STATCHECK_DECISION_ERROR_F(F={f_val},df1={df1_val},df2={df2_val},rep_p={p_val})"
                result["flags_triggered"].append(flag_str)
                result["consensus_flags"].append(flag_str)

        for m in STATCHECK_CHI2_REGEX.finditer(full_text):
            result["statcheck_tests_mined"] += 1
            df_val = float(m.group(1))
            chi2_val = float(m.group(2))
            p_val = float(m.group(4))
            p_values_found.append(p_val)
            sc_res = audit_statcheck_and_ci(test_type="chi2", df1=df_val, reported_stat=chi2_val, reported_p=p_val)
            if sc_res.get("decision_error_alpha_05"):
                result["statcheck_errors"] += 1
                flag_str = f"STATCHECK_DECISION_ERROR_CHI2(chi2={chi2_val},df={df_val},rep_p={p_val})"
                result["flags_triggered"].append(flag_str)
                result["consensus_flags"].append(flag_str)

        # P-Hacking Cliff Ratio
        if len(p_values_found) >= 8:
            just_below = sum(1 for p in p_values_found if 0.041 <= p <= 0.049)
            just_above = sum(1 for p in p_values_found if 0.051 <= p <= 0.059)
            if just_below >= 4 and (just_above == 0 or (just_below / max(1, just_above)) >= 3.5):
                flag_str = f"P_HACKING_CLIFF_ANOMALY(p_below_05={just_below},p_above_05={just_above})"
                result["flags_triggered"].append(flag_str)
                result["consensus_flags"].append(flag_str)

        # 5. Multivariable Regression Triangle
        for m in LOG_CI_REGEX.finditer(full_text):
            result["log_ci_tests"] += 1
            metric_type = m.group(1)
            est_val = float(m.group(2))
            lo_val = float(m.group(3))
            hi_val = float(m.group(4))
            
            start_pos = max(0, m.start() - 30)
            end_pos = min(len(full_text), m.end() + 50)
            window = full_text[start_pos:end_pos]
            p_match = re.search(r"p\s*([<>=])\s*(\d+(?:\.\d+)?)", window, re.IGNORECASE)
            rep_p = float(p_match.group(2)) if p_match else 0.05

            if est_val > 0 and lo_val > 0 and hi_val > 0:
                result["regression_models_tested"] += 1
                reg_eval = audit_regression_triangulation(
                    estimate=est_val,
                    lower_ci=lo_val,
                    upper_ci=hi_val,
                    reported_p=rep_p,
                    is_log_scale=True
                )
                if reg_eval.get("decision_error"):
                    result["regression_decision_errors"] += 1
                    flag_str = f"REGRESSION_DECISION_ERROR({metric_type}={est_val},CI=[{lo_val},{hi_val}],p={rep_p},Z={reg_eval.get('wald_z')})"
                    result["flags_triggered"].append(flag_str)
                    if rep_p < 0.001 and (lo_val <= 0.50 and hi_val >= 1.50):
                        result["fatal_flags"].append(flag_str)
                    else:
                        result["consensus_flags"].append(flag_str)
                elif reg_eval.get("verdict") == "REGRESSION_P_DISCREPANCY":
                    result["regression_p_discrepancies"] += 1
                    flag_str = f"REGRESSION_P_DISCREPANCY({metric_type}={est_val},rep_p={rep_p},recalc_p={reg_eval.get('recalculated_p')})"
                    result["flags_triggered"].append(flag_str)
                    result["consensus_flags"].append(flag_str)

        # 6. AI & Diagnostic Classifier Confusion Matrix Triangulation
        m_acc = AI_ACCURACY_REGEX.search(full_text)
        m_sens = AI_SENSITIVITY_REGEX.search(full_text)
        m_spec = AI_SPECIFICITY_REGEX.search(full_text)
        if m_acc and m_sens and m_spec:
            try:
                acc_v = float(m_acc.group(1))
                sens_v = float(m_sens.group(1))
                spec_v = float(m_spec.group(1))
                # Ensure they are in the same relative text window (within 400 chars)
                pos_span = max(m_acc.start(), m_sens.start(), m_spec.start()) - min(m_acc.start(), m_sens.start(), m_spec.start())
                if pos_span <= 400:
                    result["ai_metric_triads_tested"] += 1
                    ai_res = verify_ai_confusion_matrix_triangulation(
                        accuracy=acc_v, sensitivity=sens_v, specificity=spec_v
                    )
                    if ai_res.get("verdict") == "IMPOSSIBLE_AI_METRIC_TRIAD":
                        result["ai_metric_triad_failures"] += 1
                        for anom in ai_res.get("anomalies", []):
                            result["flags_triggered"].append(anom)
                            result["fatal_flags"].append(anom)
            except ValueError:
                pass

        # 7. Gate 3: Universal Table Extraction & Multi-Sieve Execution
        tables = root.findall(".//table-wrap")
        result["tables_extracted"] = len(tables)

        for tw in tables:
            headers, col_to_n, overall_n = extract_table_arm_ns(tw)
            
            all_trs = tw.findall(".//tbody//tr")
            if not all_trs:
                all_trs = tw.findall(".//tr")
            if not headers and all_trs:
                all_trs = all_trs[1:]

            carlisle_candidates = []
            possible_corr_rows = []

            for tr in all_trs:
                cells = ["".join(td.itertext()).strip() for td in tr.findall("td")]
                if len(cells) < 2:
                    continue
                
                var_name = cells[0]
                if not var_name or var_name.lower().startswith("variable") or var_name.lower().startswith("characteristic"):
                    continue

                sem_type = classify_variable_semantic_type(var_name)
                result["table_rows_evaluated"] += 1

                # High-Specificity Table 1 Filter
                is_categorical = any(k in var_name.lower() for k in [
                    "n (%)", "(%)", "no. (%)", "number (%)", "percent", "pct", "n/n", "proportion", "ratio", "rate"
                ])
                is_non_parametric = any(k in var_name.lower() for k in [
                    "median", "iqr", "interquartile", "range", "[iqr]", "(iqr)", "min-max", "min to max", "q1-q3", "q1, q3", "95% ci", "95%", "p-value", "p value", "se", "sem", "std err"
                ])

                # Extract Mean +- SD and Counts/Percentages
                cell_stats = []
                corr_vals = []
                for c_idx in range(1, len(cells)):
                    c_text = cells[c_idx]
                    
                    # Mean +- SD (only for true continuous parametric rows with explicit ± symbol)
                    if not is_categorical and not is_non_parametric and "%" not in c_text and "[" not in c_text:
                        m_stat = MEAN_SD_REGEX.search(c_text)
                        if m_stat:
                            try:
                                mean_val = float(m_stat.group(1))
                                sd_val = float(m_stat.group(2))
                                n_for_col = col_to_n.get(c_idx) or overall_n
                                cell_stats.append((c_idx, mean_val, sd_val, n_for_col))
                            except ValueError:
                                pass

                    # Categorical Count and Percentage Marginal Conservation
                    if is_categorical or "%" in c_text:
                        m_cp = COUNT_PCT_REGEX.search(c_text)
                        if m_cp:
                            try:
                                cnt_val = int(m_cp.group(1))
                                pct_val = float(m_cp.group(2))
                                n_for_col = col_to_n.get(c_idx) or overall_n
                                if n_for_col and n_for_col >= 15:
                                    result["marginal_cells_tested"] += 1
                                    mc_res = audit_cross_table_marginal_conservation(
                                        count=cnt_val,
                                        percentage=pct_val,
                                        n_total=n_for_col,
                                        subgroup_name=var_name,
                                        parent_n=overall_n
                                    )
                                    if mc_res.get("verdict") == "MARGINAL_COUNT_ANOMALY":
                                        result["marginal_conservation_failures"] += 1
                                        for anom in mc_res.get("anomalies", []):
                                            result["flags_triggered"].append(anom)
                                            result["consensus_flags"].append(anom)
                                    elif mc_res.get("verdict") == "SUBGROUP_EXCEEDS_PARENT":
                                        result["marginal_conservation_failures"] += 1
                                        for anom in mc_res.get("anomalies", []):
                                            result["flags_triggered"].append(anom)
                                            result["consensus_flags"].append(anom)
                            except ValueError:
                                pass

                    # Correlation row values in [-1.0, 1.0]
                    try:
                        f_c = float(re.sub(r"[^\d\.\-]", "", c_text))
                        if -1.0 <= f_c <= 1.0:
                            corr_vals.append(f_c)
                    except ValueError:
                        pass

                if len(corr_vals) >= 3 and len(corr_vals) == len(cells) - 1:
                    possible_corr_rows.append(corr_vals)

                # Continuous Biomarker Boundary & Physiological Bounds
                if sem_type == "CONTINUOUS_BIOMARKER":
                    for _, m_val, s_val, n_col in cell_stats:
                        result["physiological_bounds_tested"] += 1
                        phys_eval = audit_physiological_variance_bounds(
                            variable_name=var_name,
                            mean=m_val,
                            sd=s_val,
                            n=n_col or 1,
                            is_strictly_positive=True
                        )
                        if phys_eval.get("verdict") == "FLAGGED_PHYSIOLOGICAL_ANOMALY":
                            result["physiological_variance_failures"] += 1
                            for anom in phys_eval.get("anomalies", []):
                                result["flags_triggered"].append(anom)
                                if "ZERO_SD" in anom:
                                    # Zero SD on continuous biomarker: fatal if multiple cells or N >= 20
                                    if (n_col or 0) >= 20:
                                        result["fatal_flags"].append(anom)
                                    else:
                                        result["consensus_flags"].append(anom)
                                else:
                                    result["consensus_flags"].append(anom)

                    multi_arm_carlisle = [cs for cs in cell_stats if cs[3] is not None and cs[3] >= 10]
                    if len(multi_arm_carlisle) >= 2:
                        carlisle_candidates.append({
                            "variable": var_name,
                            "means": [cs[1] for cs in multi_arm_carlisle],
                            "sds": [cs[2] for cs in multi_arm_carlisle],
                            "ns": [cs[3] for cs in multi_arm_carlisle]
                        })

                # Gate 3 Sieve 1: Discrete Granularity (GRIM & GRIMMER)
                elif sem_type == "DISCRETE_INTEGER_COUNT":
                    for _, m_val, s_val, n_val in cell_stats:
                        if n_val is not None and n_val >= 5:
                            result["strict_n_verified_tests"] += 1
                            grim_res = verify_grim_grimmer_debit(m_val, s_val, n_val, decimals_mean=2, decimals_sd=2, items=1, is_binary=False)
                            if grim_res.get("verdict") == "GRIM_IMPOSSIBLE":
                                result["grim_failures"] += 1
                                flag_str = f"GRIM_IMPOSSIBLE_MEAN({var_name},M={m_val},N={n_val})"
                                result["flags_triggered"].append(flag_str)
                                result["consensus_flags"].append(flag_str)
                            elif grim_res.get("verdict") == "GRIMMER_SD_IMPOSSIBLE":
                                result["grimmer_failures"] += 1
                                flag_str = f"GRIMMER_SD_PARITY_IMPOSSIBLE({var_name},SD={s_val},N={n_val})"
                                result["flags_triggered"].append(flag_str)
                                result["consensus_flags"].append(flag_str)

                            # SPRITE Scale Envelope Check
                            if 0.0 <= m_val <= 100.0 and s_val > 0.0:
                                max_possible_var = (100.0 - m_val) * (m_val - 0.0)
                                if (s_val ** 2) > max_possible_var + 1e-3:
                                    result["sprite_variance_failures"] += 1
                                    flag_str = f"SPRITE_VARIANCE_EXCEEDS_BOUNDS({var_name},SD={s_val},MaxSD={math.sqrt(max_possible_var):.2f})"
                                    result["flags_triggered"].append(flag_str)
                                    result["consensus_flags"].append(flag_str)

                # Gate 3 Sieve 1: DEBIT Binary Proportion Consistency
                elif sem_type == "BINARY_SUMMARY":
                    for _, m_val, s_val, n_val in cell_stats:
                        if n_val is not None and n_val >= 5:
                            result["strict_n_verified_tests"] += 1
                            debit_res = verify_grim_grimmer_debit(m_val, s_val, n_val, is_binary=True)
                            if debit_res.get("verdict") == "IMPOSSIBLE_BINARY_SUMMARY":
                                result["debit_failures"] += 1
                                flag_str = f"DEBIT_BINARY_SD_IMPOSSIBLE({var_name},M={m_val},SD={s_val},N={n_val})"
                                result["flags_triggered"].append(flag_str)
                                result["consensus_flags"].append(flag_str)

            # Gate 3 Sieve 4: Correlation Matrix Positive Semi-Definiteness Sieve
            if len(possible_corr_rows) >= 3 and all(len(r) == len(possible_corr_rows) for r in possible_corr_rows):
                psd_eval = check_correlation_matrix_psd(possible_corr_rows)
                if psd_eval and psd_eval.get("verdict") == "NON_POSITIVE_DEFINITE":
                    result["correlation_psd_failures"] += 1
                    flag_str = f"NON_POSITIVE_DEFINITE_CORRELATION_MATRIX(min_lambda={psd_eval['min_eigenvalue']})"
                    result["flags_triggered"].append(flag_str)
                    if psd_eval['min_eigenvalue'] < -0.15:
                        result["fatal_flags"].append(flag_str)
                    else:
                        result["consensus_flags"].append(flag_str)

            # Gate 3 Sieve 9: Carlisle Multi-Arm RCT Baseline Uniformity (>= 5 variables, p < 1e-5)
            if len(carlisle_candidates) >= 5:
                carlisle_res = simulate_carlisle_stouffer(carlisle_candidates)
                result["carlisle_stouffer_z"] = carlisle_res.get("z_stouffer", 0.0)
                result["carlisle_combined_p"] = carlisle_res.get("carlisle_combined_p", 0.5)
                if carlisle_res.get("verdict") == "VARIANCE_COMPRESSION_HYPER_HOMOGENEITY" and result["carlisle_combined_p"] < 1e-5:
                    result["carlisle_hyper_homogeneous"] = True
                    flag_str = f"CARLISLE_VARIANCE_COMPRESSION(Z={result['carlisle_stouffer_z']},p={result['carlisle_combined_p']})"
                    result["flags_triggered"].append(flag_str)
                    result["fatal_flags"].append(flag_str)

        # Elevate multiple GRIM/GRIMMER errors to fatal (multi-cell consensus)
        if (result["grim_failures"] + result["grimmer_failures"]) >= 2:
            result["fatal_flags"].append(f"MULTIPLE_GRIM_GRIMMER_FAILURES(grim={result['grim_failures']},grimmer={result['grimmer_failures']})")

        # 8. Anti-Incorporation Bias Categorization (Independent Europe PMC Metadata & Notice Text)
        if study["cohort"] == "CASE":
            notice_text = (result["retraction_notice_info"] + " " + study["title"]).lower()
            is_image = any(k in notice_text for k in ["image", "western blot", "gel", "microscop", "splic", "figure duplication", "clon"])
            is_math_data = any(k in notice_text for k in [
                "fabricat", "falsif", "unreliable data", "concerns/issues about data",
                "error in analyses", "error in data", "statistical error", "arithmetic", "numerical",
                "inaccurate calculation", "data manipulation"
            ])
            is_mill = any(k in notice_text for k in ["paper mill", "computer-generated", "computer-aided", "tortured phrase", "plagiarism"])

            if is_math_data and not is_image:
                result["retraction_tier"] = "GATE_3_MATH_DATA"
                result["target_gate"] = "GATE_3_MATH_DATA"
            elif is_image:
                result["retraction_tier"] = "GATE_35_IMAGES"
                result["target_gate"] = "GATE_35_IMAGES"
            elif is_mill:
                result["retraction_tier"] = "GATE_2_PAPERMILL"
                result["target_gate"] = "GATE_2_PAPERMILL"
            else:
                result["retraction_tier"] = "GATE_4_GOVERNANCE"
                result["target_gate"] = "GATE_4_GOVERNANCE"

        # 9. Wave 5 High-Specificity Multi-Cell Consensus Decision Rule:
        # Trigger FLAGGED_FORENSIC_ANOMALY only if:
        # Condition A: >= 2 Fatal Structural Impossibilities (Multi-cell confirmed), OR
        # Condition B: >= 1 Fatal Structural Impossibility AND >= 1 Consensus Anomaly, OR
        # Condition C: A catastrophic single-source failure (Multiple tortured phrases, severe AI triad failure), OR
        # Condition D: >= 2 Distinct Consensus Anomalies across different tests
        unique_fatal = list(dict.fromkeys(result["fatal_flags"]))
        unique_consensus = list(dict.fromkeys(result["consensus_flags"]))

        has_catastrophic = any("MULTIPLE" in f or "IMPOSSIBLE_AI_METRIC_TRIAD" in f for f in unique_fatal)
        is_fatal_confirmed = (len(unique_fatal) >= 2) or (len(unique_fatal) >= 1 and len(unique_consensus) >= 1) or has_catastrophic

        if is_fatal_confirmed:
            result["math_gate_triggered"] = True
            result["blind_verdict"] = "FLAGGED_FORENSIC_ANOMALY"
        elif len(unique_consensus) >= 2:
            result["math_gate_triggered"] = True
            result["blind_verdict"] = "FLAGGED_FORENSIC_ANOMALY"
        else:
            result["math_gate_triggered"] = False
            result["blind_verdict"] = "CLEAN"
            if len(unique_fatal) == 1:
                result["warnings_triggered"].append(f"UNCONFIRMED_SINGLE_CELL_FATAL({unique_fatal[0]})")
            elif len(unique_consensus) == 1:
                result["warnings_triggered"].append(f"SINGLE_HEURISTIC_WARNING({unique_consensus[0]})")

    except Exception as e:
        result["flags_triggered"].append(f"AUDIT_PARSER_EXCEPTION({type(e).__name__}: {str(e)[:80]})")

    return result


def audit_study_worker_wave5(study: Dict[str, Any]) -> Dict[str, Any]:
    """Downloads XML (cached) and executes blind 5-gate audit."""
    pmcid = study.get("pmcid", "")
    xml_str = get_or_download_xml(pmcid)
    return parse_and_audit_xml_wave5(study, xml_str)


def run_blind_wave5_orchestrator(
    wave1_manifest_path: str = "data/cohort_2000_manifest.json",
    wave2_manifest_path: str = "data/cohort_wave2_manifest.json",
    wave3_manifest_path: str = "data/cohort_wave3_manifest.json",
    wave4_manifest_path: str = "data/cohort_wave4_manifest.json",
    wave5_manifest_path: str = "data/cohort_wave5_manifest.json",
    wave5_ledger_path: str = "data/extracted_tables/real_wave5_fulltext_blind_ledger.jsonl",
    target_pairs: int = 1000
):
    """Main orchestrator for Wave 5 2,000 blind study audit."""
    print("=" * 80, flush=True)
    print(f"STARTING WAVE 5 BLIND FULL-TEXT AUDIT ({target_pairs} Cases vs. {target_pairs} Controls = 2,000 Studies)", flush=True)
    print("Zero-Intersection Protocol with Waves 1, 2, 3, AND 4 strictly enforced.", flush=True)
    print("High-Specificity Multi-Cell Consensus Architecture Active.", flush=True)
    print("=" * 80, flush=True)

    t0 = time.time()

    # 1. Load or assemble Wave 5 cohort
    from scripts.assemble_wave5_cohort import assemble_wave5_cohort
    cohort = assemble_wave5_cohort(
        wave1_manifest_path=wave1_manifest_path,
        wave2_manifest_path=wave2_manifest_path,
        wave3_manifest_path=wave3_manifest_path,
        wave4_manifest_path=wave4_manifest_path,
        wave5_manifest_path=wave5_manifest_path,
        target_pairs=target_pairs
    )

    # 2. Strict Quadruple Non-Intersection Verification
    with open(wave1_manifest_path, "r", encoding="utf-8") as f:
        w1_data = json.load(f)
    with open(wave2_manifest_path, "r", encoding="utf-8") as f:
        w2_data = json.load(f)
    with open(wave3_manifest_path, "r", encoding="utf-8") as f:
        w3_data = json.load(f)
    with open(wave4_manifest_path, "r", encoding="utf-8") as f:
        w4_data = json.load(f)

    w1_pmcids = {s.get("pmcid") for s in w1_data if s.get("pmcid")}
    w1_dois = {s.get("doi", "").strip().lower() for s in w1_data if s.get("doi")}
    w2_pmcids = {s.get("pmcid") for s in w2_data if s.get("pmcid")}
    w2_dois = {s.get("doi", "").strip().lower() for s in w2_data if s.get("doi")}
    w3_pmcids = {s.get("pmcid") for s in w3_data if s.get("pmcid")}
    w3_dois = {s.get("doi", "").strip().lower() for s in w3_data if s.get("doi")}
    w4_pmcids = {s.get("pmcid") for s in w4_data if s.get("pmcid")}
    w4_dois = {s.get("doi", "").strip().lower() for s in w4_data if s.get("doi")}
    
    w5_pmcids = {s.get("pmcid") for s in cohort if s.get("pmcid")}
    w5_dois = {s.get("doi", "").strip().lower() for s in cohort if s.get("doi")}
    
    assert len(w1_pmcids.intersection(w5_pmcids)) == 0, "Intersection detected with Wave 1 PMCIDs!"
    assert len(w2_pmcids.intersection(w5_pmcids)) == 0, "Intersection detected with Wave 2 PMCIDs!"
    assert len(w3_pmcids.intersection(w5_pmcids)) == 0, "Intersection detected with Wave 3 PMCIDs!"
    assert len(w4_pmcids.intersection(w5_pmcids)) == 0, "Intersection detected with Wave 4 PMCIDs!"
    assert len(w1_dois.intersection(w5_dois)) == 0, "Intersection detected with Wave 1 DOIs!"
    assert len(w2_dois.intersection(w5_dois)) == 0, "Intersection detected with Wave 2 DOIs!"
    assert len(w3_dois.intersection(w5_dois)) == 0, "Intersection detected with Wave 3 DOIs!"
    assert len(w4_dois.intersection(w5_dois)) == 0, "Intersection detected with Wave 4 DOIs!"

    print(f"Quadruple Zero Intersection Confirmed: Wave 5 has 0 overlapping PMCIDs and 0 overlapping DOIs with Waves 1, 2, 3, and 4.", flush=True)

    # 3. Check existing Wave 5 ledger for resumability
    os.makedirs(os.path.dirname(wave5_ledger_path), exist_ok=True)
    existing_audited = {}
    if os.path.exists(wave5_ledger_path):
        with open(wave5_ledger_path, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    try:
                        rec = json.loads(line)
                        existing_audited[rec["study_id"]] = rec
                    except Exception:
                        pass
        print(f"Resuming: Found {len(existing_audited)} already audited studies in Wave 5 ledger.", flush=True)

    results = list(existing_audited.values())
    remaining_studies = [s for s in cohort if s["study_id"] not in existing_audited]
    print(f"Studies remaining to audit in Wave 5: {len(remaining_studies)}", flush=True)

    # 4. Stream audit execution with concurrent worker pool
    print(f"Launching high-throughput worker pool (max_workers=32) for {len(remaining_studies)} studies...", flush=True)
    completed_count = len(existing_audited)
    batch_size = 100

    with open(wave5_ledger_path, "a", encoding="utf-8") as ledger_out:
        with concurrent.futures.ThreadPoolExecutor(max_workers=32) as executor:
            future_to_study = {executor.submit(audit_study_worker_wave5, s): s for s in remaining_studies}
            for future in concurrent.futures.as_completed(future_to_study):
                res = future.result()
                results.append(res)
                ledger_out.write(json.dumps(res) + "\n")
                ledger_out.flush()
                completed_count += 1
                if completed_count % batch_size == 0 or completed_count == len(cohort):
                    elapsed = time.time() - t0
                    rate = completed_count / elapsed if elapsed > 0 else 0
                    print(f"  [Progress] Audited {completed_count}/{len(cohort)} studies ({rate:.1f} studies/sec, {elapsed:.1f}s elapsed)...", flush=True)

    print("=" * 80, flush=True)
    print(f"WAVE 5 FULL-TEXT AUDIT COMPLETE: {len(results)} studies evaluated.", flush=True)
    print("=" * 80, flush=True)
    return results

if __name__ == "__main__":
    run_blind_wave5_orchestrator()
