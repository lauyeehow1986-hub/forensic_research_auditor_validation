import json
import csv
import math
import os
import sys

sys.path.insert(0, os.path.abspath("."))

def wilson_95_ci(k, n):
    if n <= 0:
        return {'proportion': 0.0, 'lower_95': 0.0, 'upper_95': 0.0}
    z = 1.959963984540054
    p = k / n
    denom = 1.0 + (z ** 2) / n
    center = (p + (z ** 2) / (2.0 * n)) / denom
    half_width = (z * math.sqrt((p * (1.0 - p) / n) + (z ** 2) / (4.0 * (n ** 2)))) / denom
    return {
        'proportion': round(p * 100.0, 2),
        'lower_95': round(max(0.0, center - half_width) * 100.0, 2),
        'upper_95': round(min(1.0, center + half_width) * 100.0, 2)
    }

def main():
    print("Loading Retraction Watch Database (73,597 records) for objective reason mapping...")
    rw_by_doi = {}
    with open('data/raw_benchmarks/retraction_watch_full.csv', 'r', encoding='utf-8', errors='replace') as f:
        reader = csv.DictReader(f)
        for r in reader:
            doi = (r.get('OriginalPaperDOI') or '').strip().lower()
            if doi:
                rw_by_doi[doi] = r.get('Reason', '')

    with open('data/extracted_tables/real_wave3_fulltext_blind_ledger.jsonl', 'r', encoding='utf-8') as f:
        wave3 = [json.loads(line) for line in f if line.strip()]

    cases = [r for r in wave3 if r['cohort'] == 'CASE']
    ctrls = [r for r in wave3 if r['cohort'] == 'CONTROL']

    matched_reasons = 0
    for c in cases:
        doi = (c.get('doi') or '').strip().lower()
        rw_r = rw_by_doi.get(doi, '')
        if rw_r:
            matched_reasons += 1
            
        text = (rw_r + ' ' + c.get('retraction_notice_info', '') + ' ' + c.get('title', '')).lower()
        
        is_image = any(k in text for k in ['image', 'western blot', 'gel', 'microscop', 'splic', 'figure duplication', 'clon'])
        is_math_data = any(k in text for k in [
            'fabricat', 'falsif', 'unreliable data', 'concerns/issues about data',
            'error in analyses', 'error in data', 'statistical error', 'arithmetic', 'numerical',
            'inaccurate calculation', 'data manipulation'
        ])
        is_mill = any(k in text for k in ['paper mill', 'computer-generated', 'computer-aided', 'tortured phrase', 'plagiarism'])
        
        if is_math_data and not is_image:
            c['retraction_tier'] = 'GATE_3_MATH_DATA'
            c['target_gate'] = 'GATE_3_MATH_DATA'
        elif is_image:
            c['retraction_tier'] = 'GATE_35_IMAGES'
            c['target_gate'] = 'GATE_35_IMAGES'
        elif is_mill:
            c['retraction_tier'] = 'GATE_2_PAPERMILL'
            c['target_gate'] = 'GATE_2_PAPERMILL'
        else:
            c['retraction_tier'] = 'GATE_4_GOVERNANCE'
            c['target_gate'] = 'GATE_4_GOVERNANCE'

    print(f"Matched objective Retraction Watch reasons for {matched_reasons} / {len(cases)} cases.")

    # Save updated Wave 3 ledger with grounded Retraction Watch reasons
    with open('data/extracted_tables/real_wave3_fulltext_blind_ledger.jsonl', 'w', encoding='utf-8') as f:
        for r in wave3:
            f.write(json.dumps(r) + '\n')

    g3 = [c for c in cases if c['retraction_tier'] == 'GATE_3_MATH_DATA']
    g35 = [c for c in cases if c['retraction_tier'] == 'GATE_35_IMAGES']
    g2 = [c for c in cases if c['retraction_tier'] == 'GATE_2_PAPERMILL']
    g4 = [c for c in cases if c['retraction_tier'] == 'GATE_4_GOVERNANCE']

    g3_tp = sum(1 for c in g3 if c.get('math_gate_triggered'))
    g3_fn = len(g3) - g3_tp
    g3_sens = wilson_95_ci(g3_tp, len(g3))

    g35_clean = sum(1 for c in g35 if not c.get('math_gate_triggered'))
    g35_spec = wilson_95_ci(g35_clean, len(g35))

    g2_clean = sum(1 for c in g2 if not c.get('math_gate_triggered'))
    g2_spec = wilson_95_ci(g2_clean, len(g2))

    g4_clean = sum(1 for c in g4 if not c.get('math_gate_triggered'))
    g4_spec = wilson_95_ci(g4_clean, len(g4))

    ctrl_clean = sum(1 for c in ctrls if c.get('blind_verdict') == 'CLEAN')
    ctrl_fp = len(ctrls) - ctrl_clean
    ctrl_spec = wilson_95_ci(ctrl_clean, len(ctrls))

    tot_tables = sum(r.get("tables_extracted", 0) for r in wave3)
    tot_rows = sum(r.get("table_rows_evaluated", 0) for r in wave3)

    print('=' * 80)
    print('WAVE 3 GROUNDED METRICS (2,000 INDEPENDENT STUDIES):')
    print('=' * 80)
    print(f'Gate 3 (Math/Data Fraud) : {len(g3)} cases -> TP={g3_tp}, FN={g3_fn}, Sens={g3_sens["proportion"]}% [{g3_sens["lower_95"]}% - {g3_sens["upper_95"]}%]')
    print(f'Gate 3.5 (Images/Figures): {len(g35)} cases -> Clean={g35_clean}, Noise={len(g35)-g35_clean}, Spec={g35_spec["proportion"]}% [{g35_spec["lower_95"]}% - {g35_spec["upper_95"]}%]')
    print(f'Gate 2 (Paper-Mill/NLP)  : {len(g2)} cases -> Clean={g2_clean}, Noise={len(g2)-g2_clean}, Spec={g2_spec["proportion"]}% [{g2_spec["lower_95"]}% - {g2_spec["upper_95"]}%]')
    print(f'Gate 4 (Governance/Ethics): {len(g4)} cases -> Clean={g4_clean}, Noise={len(g4)-g4_clean}, Spec={g4_spec["proportion"]}% [{g4_spec["lower_95"]}% - {g4_spec["upper_95"]}%]')
    print(f'Controls (Clean Group)   : {len(ctrls)} studies -> TN={ctrl_clean}, FP={ctrl_fp}, Spec={ctrl_spec["proportion"]}% [{ctrl_spec["lower_95"]}% - {ctrl_spec["upper_95"]}%]')
    print(f'Total Tables Extracted   : {tot_tables:,}')
    print(f'Total Table Rows Audited : {tot_rows:,}')
    print('=' * 80)

    # Save to docs/data/blind_wave3_ledger.json
    with open('docs/data/blind_wave3_ledger.json', 'w', encoding='utf-8') as f:
        json.dump(wave3, f)
    print("Saved docs/data/blind_wave3_ledger.json.")

    # Write Wave 3 Markdown Report
    from src.evaluation.blind_wave3_fulltext_auditor import generate_wave3_markdown_report, generate_combined_6000_meta_analysis
    generate_wave3_markdown_report(
        results=wave3,
        output_path="reports/BLIND_WAVE3_FULLTEXT_AUDIT_REPORT.md",
        g3_sens=g3_sens,
        g3_flagged=g3_tp,
        g3_total=len(g3),
        g35_spec=g35_spec,
        g35_clean=g35_clean,
        g35_total=len(g35),
        g2_spec=g2_spec,
        g2_clean=g2_clean,
        g2_total=len(g2),
        g4_spec=g4_spec,
        g4_clean=g4_clean,
        g4_total=len(g4),
        ctrl_spec=ctrl_spec,
        ctrl_clean=ctrl_clean,
        ctrl_flagged=ctrl_fp,
        ctrl_total=len(ctrls),
        tot_tables=tot_tables,
        tot_rows=tot_rows
    )

    # Generate Combined 6,000 Meta-Analysis
    generate_combined_6000_meta_analysis(
        wave1_ledger_path="data/extracted_tables/real_2000_fulltext_blind_ledger.jsonl",
        wave2_ledger_path="data/extracted_tables/real_wave2_fulltext_blind_ledger.jsonl",
        wave3_results=wave3,
        output_report_path="reports/BLIND_COMBINED_6000_FULLTEXT_AUDIT_REPORT.md",
        output_json_path="docs/data/blind_combined_6000_ledger.json"
    )

if __name__ == '__main__':
    main()
