#!/usr/bin/env python3
"""
Ingests Retraction Watch CSV / OpenAlex matched pairs,
Europe PMC JATS XML tables, ClinicalTrials.gov API v2 registry metadata,
and Cabanac Problematic Paper Screener (PPS) tortured phrases.
"""

import json
import os
import re
import urllib.request
import xml.etree.ElementTree as ET
from typing import Dict, Any, List, Optional


def fetch_clinicaltrials_gov_v2(nct_id: str) -> Dict[str, Any]:
    """Queries ClinicalTrials.gov REST API v2 for registered enrollment and primary outcomes."""
    url = f"https://clinicaltrials.gov/api/v2/studies/{nct_id.strip()}"
    req = urllib.request.Request(url, headers={"User-Agent": "ForensicBenchmarkValidator/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        protocol = data.get("protocolSection", {})
        design = protocol.get("designModule", {})
        outcomes = protocol.get("outcomesModule", {})
        return {
            "nct_id": nct_id,
            "status": "SUCCESS",
            "enrollment_info": design.get("enrollmentInfo", {}),
            "primary_outcomes": outcomes.get("primaryOutcomes", []),
            "secondary_outcomes": outcomes.get("secondaryOutcomes", [])
        }
    except Exception as e:
        return {
            "nct_id": nct_id,
            "status": "ERROR",
            "error": str(e),
            "enrollment_info": {},
            "primary_outcomes": [],
            "secondary_outcomes": []
        }


def fetch_crossref_metadata(doi: str) -> Dict[str, Any]:
    """Fetches article metadata and update/retraction notices from Crossref REST API."""
    url = f"https://api.crossref.org/works/{doi.strip()}"
    req = urllib.request.Request(url, headers={"User-Agent": "ForensicBenchmarkValidator/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        msg = data.get("message", {})
        return {
            "doi": doi,
            "status": "SUCCESS",
            "title": msg.get("title", [""])[0],
            "update_to": msg.get("update-to", []),
            "is_referenced_by_count": msg.get("is-referenced-by-count", 0),
            "created": msg.get("created", {}).get("date-time", "")
        }
    except Exception as e:
        return {
            "doi": doi,
            "status": "ERROR",
            "error": str(e),
            "title": "",
            "update_to": [],
            "is_referenced_by_count": 0
        }


def fetch_europepmc_jats_xml(pmcid: str) -> Dict[str, Any]:
    """Fetches full-text JATS XML from Europe PMC REST API."""
    cleaned_id = pmcid.strip()
    if not cleaned_id.upper().startswith("PMC"):
        cleaned_id = f"PMC{cleaned_id}"
    url = f"https://www.ebi.ac.uk/europepmc/webservices/rest/{cleaned_id}/fullTextXML"
    req = urllib.request.Request(url, headers={"User-Agent": "ForensicBenchmarkValidator/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            xml_str = resp.read().decode("utf-8", errors="replace")
        return {
            "pmcid": cleaned_id,
            "status": "SUCCESS",
            "xml": xml_str,
            "tables": extract_jats_xml_tables(xml_str)
        }
    except Exception as e:
        return {
            "pmcid": cleaned_id,
            "status": "ERROR",
            "error": str(e),
            "xml": "",
            "tables": []
        }


def extract_jats_xml_tables(xml_str: str) -> List[Dict[str, Any]]:
    """Extracts tables, headers, and rows from JATS XML string."""
    tables = []
    if not xml_str:
        return tables
    try:
        root = ET.fromstring(xml_str)
        for tw in root.findall(".//table-wrap"):
            t_id = tw.get("id", "")
            label = tw.findtext("label", "").strip()
            title = tw.findtext(".//caption/title", "").strip()
            headers = []
            for th in tw.findall(".//thead//th"):
                headers.append("".join(th.itertext()).strip())
            
            rows = []
            for tr in tw.findall(".//tbody//tr"):
                cells = ["".join(td.itertext()).strip() for td in tr.findall("td")]
                if cells:
                    rows.append(cells)
            
            footnotes = []
            for fn in tw.findall(".//table-wrap-foot//p"):
                footnotes.append("".join(fn.itertext()).strip())

            tables.append({
                "table_id": t_id,
                "label": label,
                "title": title,
                "headers": headers,
                "rows": rows,
                "footnotes": footnotes
            })
    except Exception as e:
        pass
    return tables


def screen_tortured_phrases(
    text: str,
    lexicon_path: str = "architecture/03_tortured_phrases_lexicon.json"
) -> Dict[str, Any]:
    """Screens text against Cabanac PPS tortured phrases lexicon."""
    if not os.path.isabs(lexicon_path):
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
        lexicon_path = os.path.join(base_dir, lexicon_path)
    
    if not os.path.exists(lexicon_path):
        return {"error": f"Lexicon not found: {lexicon_path}", "detected_phrases": [], "verdict": "LEXICON_MISSING"}
    
    with open(lexicon_path, "r", encoding="utf-8") as f:
        lexicon_data = json.load(f)
    
    mapping = lexicon_data.get("tortured_phrases", {})
    lower_text = text.lower()
    matches = []
    
    for tortured, standard in mapping.items():
        pattern = r"\b" + re.escape(tortured.lower()) + r"\b"
        found = re.findall(pattern, lower_text)
        if found:
            matches.append({
                "tortured_phrase": tortured,
                "standard_term": standard,
                "occurrences": len(found)
            })
    
    return {
        "text_length": len(text),
        "total_tortured_phrases": len(matches),
        "detected_phrases": matches,
        "verdict": "TORTURED_PHRASES_DETECTED" if len(matches) > 0 else "CLEAN_LEXICON"
    }


def classify_variable_semantic_type(variable_name: str, sample_info: Optional[Dict[str, Any]] = None) -> str:
    """
    Implements strict variable typing and semantic filtering (Pre-Math Gate)
    per `.antigravity/skills/forensic-table-extractor/SKILL.md`:
    - CONTINUOUS_BIOMARKER: Age, BMI, BP, LVEF, Creatinine, etc. (Suppress GRIM/GRIMMER)
    - WEIGHTED_OR_SURVIVAL: IPTW, Propensity, Kaplan-Meier failure estimates (Suppress integer checks)
    - BINARY_SUMMARY: 0/1 proportions with mean and SD (Route to DEBIT)
    - LIKERT_COMPOSITE: Validated multi-item score with known item count k > 1 (GRIM with N*k)
    - DISCRETE_INTEGER_COUNT: Raw integer count or tally (Eligible for GRIM/GRIMMER)
    """
    v_lower = variable_name.strip().lower()
    info = sample_info or {}
    
    # Check for survival or weighted cohorts
    if info.get("is_weighted") or info.get("is_survival") or any(kw in v_lower for kw in [
        "kaplan-meier", "km estimate", "propensity", "iptw", "weighted", "cumulative incidence"
    ]):
        return "WEIGHTED_OR_SURVIVAL"

    # Continuous physiological measurements
    continuous_keywords = [
        "age", "bmi", "body mass", "lvef", "ejection fraction", "creatinine",
        "egfr", "blood pressure", "systolic", "diastolic", "sbp", "dbp",
        "troponin", "hemoglobin", "potassium", "sodium", "calcium",
        "weight", "height", "duration of surgery", "duration of anaesthesia",
        "heart rate", "pulse", "map", "mean arterial pressure", "cvp",
        "cholesterol", "hdl", "ldl", "triglycerides", "glucose", "hba1c"
    ]
    if any(kw in v_lower for kw in continuous_keywords):
        return "CONTINUOUS_BIOMARKER"

    # Binary summary indicator
    if info.get("is_binary") or "proportion" in v_lower or "prevalence" in v_lower:
        return "BINARY_SUMMARY"

    # Likert composite
    if info.get("items", 1) > 1 or any(kw in v_lower for kw in [
        "scale", "score", "survey", "questionnaire", "inventory", "index"
    ]):
        return "LIKERT_COMPOSITE"

    # Default to discrete integer count
    return "DISCRETE_INTEGER_COUNT"
