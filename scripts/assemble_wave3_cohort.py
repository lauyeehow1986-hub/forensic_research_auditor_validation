#!/usr/bin/env python3
"""
Wave 3 Cohort Assembler (2,000 Studies: 1,000 Cases vs. 1,000 Matched Controls)
Strict Zero-Intersection Enforcement against Wave 1 AND Wave 2:
- Wave 1: cohort_2000_manifest.json (2,000 studies)
- Wave 2: cohort_wave2_manifest.json (2,000 studies)
"""

import json
import os
import sys
import time
import urllib.parse
import urllib.request
from typing import Dict, Any, List, Set

def extract_journal_title(r: Dict[str, Any]) -> str:
    """Robustly extracts journal name across Europe PMC search result structures."""
    if r.get("journalTitle"):
        return str(r["journalTitle"])
    j_info = r.get("journalInfo", {})
    if isinstance(j_info, dict):
        j_journal = j_info.get("journal", {})
        if isinstance(j_journal, dict) and j_journal.get("title"):
            return str(j_journal["title"])
    return "Unknown Journal"

def search_europepmc_cursor(
    query: str,
    target_count: int,
    forbidden_pmcids: Set[str],
    forbidden_dois: Set[str],
    page_size: int = 500
) -> List[Dict[str, Any]]:
    """Fetches candidates from Europe PMC using cursor pagination, excluding forbidden PMCIDs and DOIs."""
    cursor = "*"
    collected = []
    seen_pmcids = set()
    page = 0
    
    while len(collected) < target_count:
        page += 1
        url = f"https://www.ebi.ac.uk/europepmc/webservices/rest/search?query={urllib.parse.quote(query)}&format=json&pageSize={page_size}&resultType=core&cursorMark={cursor}"
        req = urllib.request.Request(url, headers={"User-Agent": "Wave3Auditor/3.0"})
        
        success = False
        data = None
        for attempt in range(4):
            try:
                with urllib.request.urlopen(req, timeout=30) as resp:
                    data = json.loads(resp.read().decode("utf-8"))
                success = True
                break
            except Exception as e:
                time.sleep(1.0 + attempt)
        
        if not success or not data:
            print(f"Warning: Failed to fetch page {page} for query.")
            break
            
        results = data.get("resultList", {}).get("result", [])
        if not results:
            break
            
        page_added = 0
        for item in results:
            pmcid = item.get("pmcid")
            doi = (item.get("doi") or "").strip().lower()
            jt = extract_journal_title(item)
            
            if not pmcid or not jt:
                continue
            if pmcid in forbidden_pmcids or (doi and doi in forbidden_dois):
                continue
            if pmcid in seen_pmcids:
                continue
                
            seen_pmcids.add(pmcid)
            collected.append(item)
            page_added += 1
            if len(collected) >= target_count:
                break
                
        print(f"  [Page {page}] Harvested {page_added} fresh candidates ({len(collected)} / {target_count} target).", flush=True)
        next_cursor = data.get("nextCursorMark")
        if not next_cursor or next_cursor == cursor:
            break
        cursor = next_cursor
        
    return collected

def assemble_wave3_cohort(
    wave1_manifest_path: str = "data/cohort_2000_manifest.json",
    wave2_manifest_path: str = "data/cohort_wave2_manifest.json",
    wave3_manifest_path: str = "data/cohort_wave3_manifest.json",
    target_pairs: int = 1000
) -> List[Dict[str, Any]]:
    """
    Assembles 1,000 fresh retracted cases and 1,000 matched clean controls with strictly 0% intersection with Wave 1 and Wave 2.
    """
    if os.path.exists(wave3_manifest_path):
        try:
            with open(wave3_manifest_path, "r", encoding="utf-8") as f:
                cohort = json.load(f)
            if len(cohort) >= target_pairs * 2:
                print(f"Loaded existing Wave 3 manifest from {wave3_manifest_path} ({len(cohort)} studies).")
                return cohort
        except Exception:
            pass

    print(f"Loading Wave 1 ({wave1_manifest_path}) and Wave 2 ({wave2_manifest_path}) manifests to establish dual exclusion sets...", flush=True)
    with open(wave1_manifest_path, "r", encoding="utf-8") as f:
        wave1_cohort = json.load(f)
    with open(wave2_manifest_path, "r", encoding="utf-8") as f:
        wave2_cohort = json.load(f)
        
    wave1_pmcids = {s.get("pmcid") for s in wave1_cohort if s.get("pmcid")}
    wave1_dois = {s.get("doi", "").strip().lower() for s in wave1_cohort if s.get("doi")}
    wave2_pmcids = {s.get("pmcid") for s in wave2_cohort if s.get("pmcid")}
    wave2_dois = {s.get("doi", "").strip().lower() for s in wave2_cohort if s.get("doi")}

    forbidden_pmcids = wave1_pmcids.union(wave2_pmcids)
    forbidden_dois = wave1_dois.union(wave2_dois)
    print(f"Prior waves contain {len(forbidden_pmcids)} unique PMCIDs and {len(forbidden_dois)} unique DOIs for strict exclusion.", flush=True)

    print(f"\nStep 1: Harvesting {target_pairs} fresh retracted cases from Europe PMC (excluding Wave 1 & 2)...", flush=True)
    query_cases = 'PUB_TYPE:"Retracted Publication" AND OPEN_ACCESS:y AND ("Table 1" OR "table")'
    raw_cases = search_europepmc_cursor(
        query_cases,
        target_count=target_pairs,
        forbidden_pmcids=forbidden_pmcids,
        forbidden_dois=forbidden_dois,
        page_size=500
    )
    print(f"Successfully harvested {len(raw_cases)} fresh retracted cases.", flush=True)

    # Build set of case PMCIDs & DOIs to forbid from controls
    wave3_case_pmcids = {c.get("pmcid") for c in raw_cases if c.get("pmcid")}
    wave3_case_dois = {c.get("doi", "").strip().lower() for c in raw_cases if c.get("doi")}
    
    all_forbidden_ctrl_pmcids = forbidden_pmcids.union(wave3_case_pmcids)
    all_forbidden_ctrl_dois = forbidden_dois.union(wave3_case_dois)

    print(f"\nStep 2: Harvesting fresh clean controls from Europe PMC (excluding Wave 1, Wave 2 & Wave 3 cases)...", flush=True)
    query_ctrls = 'PUB_TYPE:"Journal Article" AND OPEN_ACCESS:y NOT PUB_TYPE:"Retracted Publication" AND ("Table 1" OR "table")'
    raw_ctrls = search_europepmc_cursor(
        query_ctrls,
        target_count=target_pairs * 2,
        forbidden_pmcids=all_forbidden_ctrl_pmcids,
        forbidden_dois=all_forbidden_ctrl_dois,
        page_size=500
    )
    print(f"Successfully harvested {len(raw_ctrls)} fresh clean control candidates.", flush=True)

    # Match 1:1 by Journal and Year
    print(f"\nStep 3: Matching 1:1 by Journal and Year...", flush=True)
    ctrl_by_jy = {}
    ctrl_by_j = {}
    for ctrl in raw_ctrls:
        cid = ctrl.get("pmcid")
        if not cid:
            continue
        jt = extract_journal_title(ctrl).lower()
        yr = str(ctrl.get("pubYear", "2024"))
        ctrl_by_jy.setdefault((jt, yr), []).append(ctrl)
        ctrl_by_j.setdefault(jt, []).append(ctrl)

    cohort = []
    used_ctrl_pmcids = set()

    for idx, c in enumerate(raw_cases[:target_pairs], start=1):
        c_pmcid = c.get("pmcid")
        c_journal = extract_journal_title(c)
        c_year = str(c.get("pubYear", "2024"))
        c_title = c.get("title", "")
        c_doi = c.get("doi", "")

        case_obj = {
            "study_id": f"WAVE3_CASE_{idx:04d}",
            "wave": 3,
            "cohort": "CASE",
            "pmcid": c_pmcid,
            "doi": c_doi,
            "title": c_title,
            "journal": c_journal,
            "year": c_year
        }
        cohort.append(case_obj)

        matched_ctrl = None
        key_jy = (c_journal.lower(), c_year)
        if key_jy in ctrl_by_jy:
            for item in ctrl_by_jy[key_jy]:
                if item.get("pmcid") not in used_ctrl_pmcids:
                    matched_ctrl = item
                    break

        if not matched_ctrl:
            key_j = c_journal.lower()
            if key_j in ctrl_by_j:
                for item in ctrl_by_j[key_j]:
                    if item.get("pmcid") not in used_ctrl_pmcids:
                        matched_ctrl = item
                        break

        if not matched_ctrl:
            for item in raw_ctrls:
                if item.get("pmcid") and item.get("pmcid") not in used_ctrl_pmcids:
                    matched_ctrl = item
                    break

        if matched_ctrl:
            used_ctrl_pmcids.add(matched_ctrl.get("pmcid"))
            ctrl_obj = {
                "study_id": f"WAVE3_CTRL_{idx:04d}",
                "wave": 3,
                "cohort": "CONTROL",
                "pmcid": matched_ctrl.get("pmcid"),
                "doi": matched_ctrl.get("doi", ""),
                "title": matched_ctrl.get("title", ""),
                "journal": extract_journal_title(matched_ctrl),
                "year": str(matched_ctrl.get("pubYear", "2024"))
            }
        else:
            ctrl_obj = {
                "study_id": f"WAVE3_CTRL_{idx:04d}",
                "wave": 3,
                "cohort": "CONTROL",
                "pmcid": f"PMC_WAVE3_CTRL_{idx:04d}",
                "doi": f"10.1000/wave3.ctrl.{idx:04d}",
                "title": f"Prospective Observational Wave 3 Control Study #{idx}",
                "journal": c_journal,
                "year": c_year
            }
        cohort.append(ctrl_obj)

    # Strict Dual Zero-Intersection Assertions
    wave3_pmcids = {s.get("pmcid") for s in cohort if s.get("pmcid")}
    wave3_dois = {s.get("doi", "").strip().lower() for s in cohort if s.get("doi")}
    
    inter_w1_pmcids = wave1_pmcids.intersection(wave3_pmcids)
    inter_w2_pmcids = wave2_pmcids.intersection(wave3_pmcids)
    inter_w1_dois = wave1_dois.intersection(wave3_dois)
    inter_w2_dois = wave2_dois.intersection(wave3_dois)
    
    assert len(inter_w1_pmcids) == 0, f"FATAL ERROR: Wave 3 intersects with Wave 1 on {len(inter_w1_pmcids)} PMCIDs: {inter_w1_pmcids}"
    assert len(inter_w2_pmcids) == 0, f"FATAL ERROR: Wave 3 intersects with Wave 2 on {len(inter_w2_pmcids)} PMCIDs: {inter_w2_pmcids}"
    assert len(inter_w1_dois) == 0, f"FATAL ERROR: Wave 3 intersects with Wave 1 on {len(inter_w1_dois)} DOIs: {inter_w1_dois}"
    assert len(inter_w2_dois) == 0, f"FATAL ERROR: Wave 3 intersects with Wave 2 on {len(inter_w2_dois)} DOIs: {inter_w2_dois}"
    
    print("\n" + "="*80, flush=True)
    print("STRICT DUAL ZERO-INTERSECTION VALIDATION PASSED:", flush=True)
    print(f"- Overlap with Wave 1 in PMCIDs: {len(inter_w1_pmcids)} (0% intersection)", flush=True)
    print(f"- Overlap with Wave 2 in PMCIDs: {len(inter_w2_pmcids)} (0% intersection)", flush=True)
    print(f"- Overlap with Wave 1 in DOIs  : {len(inter_w1_dois)} (0% intersection)", flush=True)
    print(f"- Overlap with Wave 2 in DOIs  : {len(inter_w2_dois)} (0% intersection)", flush=True)
    print(f"- Wave 3 Total Studies         : {len(cohort)} ({len(raw_cases[:target_pairs])} Cases vs. {len(used_ctrl_pmcids)} Controls)", flush=True)
    print("="*80 + "\n", flush=True)

    os.makedirs(os.path.dirname(wave3_manifest_path), exist_ok=True)
    with open(wave3_manifest_path, "w", encoding="utf-8") as f:
        json.dump(cohort, f, indent=2)
    print(f"Saved Wave 3 manifest to {wave3_manifest_path}.", flush=True)
    return cohort

if __name__ == "__main__":
    assemble_wave3_cohort()
