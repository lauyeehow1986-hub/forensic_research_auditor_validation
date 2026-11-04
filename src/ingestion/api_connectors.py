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


def classify_retraction_tier(reasons: Any, text: str = "") -> Optional[Dict[str, Any]]:
    """
    Classifies retraction reasons and notices into a 3-tier forensic taxonomy:
    - TIER_1_MATH_DATA: Fabrication, falsification, manipulation, or error in numbers/data.
      -> Target for deterministic math tools (GRIM, GRIMMER, DEBIT, Carlisle, Statcheck).
    - TIER_2_PAPERMILL: Paper mills, machine-generated text, tortured phrases, text plagiarism.
      -> Target for NLP, lexical sieves, and tortured phrase screeners.
    - TIER_3_EDITORIAL_GOVERNANCE: Authorship disputes, lack of consent/authorization, fake peer review, rogue editors.
      -> Target for registry cross-checks, co-authorship graphs, and editorial provenance.
    """
    if reasons is None:
        reasons_list = []
    elif isinstance(reasons, str):
        reasons_list = [reasons]
    else:
        reasons_list = list(reasons)

    clean_reasons = [r.lstrip("+").strip().lower() for r in reasons_list if r]
    text_lower = text.lower() if text else ""

    if not clean_reasons and not text_lower:
        return None
    
    tier_1_keywords = [
        "falsification/fabrication of data", "concerns/issues about data",
        "unreliable data", "error in data", "error in analyses",
        "manipulation of data", "unreliable results", "results not reproducible",
        "falsification/fabrication of results", "plagiarism of data",
        "data fabrication", "data falsification", "fabricated data",
        "data manipulation", "inconsistent numbers", "arithmetic error",
        "falsification of data", "fabrication of data"
    ]
    
    tier_2_keywords = [
        "paper mill", "computer-aided content", "computer-generated content",
        "tortured phrase", "plagiarism of text", "plagiarism of article",
        "euphemisms for plagiarism", "duplication of/in article",
        "machine-translated", "machine translation", "paraphrase"
    ]
    
    tier_3_keywords = [
        "author dispute", "authorship dispute", "forged authorship", "compromised peer review",
        "fake peer review", "rogue editor", "breach of policy",
        "lack of consent", "authorization", "ethical violations",
        "conflict of interest", "duplicate publication", "redundant publication",
        "investigation by journal", "institutional cohort", "institutional authorization"
    ]
    
    has_tier_1 = any(any(kw in r for kw in tier_1_keywords) for r in clean_reasons) or any(kw in text_lower for kw in [
        "data fabrication", "fabricated data", "data falsification", "manipulated data", "unreliable data", "numerical error"
    ])
    
    has_tier_2 = any(any(kw in r for kw in tier_2_keywords) for r in clean_reasons) or any(kw in text_lower for kw in [
        "paper mill", "computer-generated", "tortured phrase"
    ])
    
    has_tier_3 = any(any(kw in r for kw in tier_3_keywords) for r in clean_reasons) or any(kw in text_lower for kw in [
        "authorization for use could not be documented", "without consent", "author dispute", "peer review ring"
    ])
    
    # Determine primary tier
    if has_tier_1:
        primary_tier = "TIER_1_MATH_DATA"
    elif has_tier_2:
        primary_tier = "TIER_2_PAPERMILL"
    elif has_tier_3:
        primary_tier = "TIER_3_EDITORIAL_GOVERNANCE"
    else:
        primary_tier = "TIER_3_EDITORIAL_GOVERNANCE"  # Default generic retractions without data concerns to governance
        
    return {
        "primary_tier": primary_tier,
        "is_math_data_fraud": has_tier_1,
        "is_papermill": has_tier_2,
        "is_editorial_governance": has_tier_3,
        "matched_reasons": reasons_list
    }

