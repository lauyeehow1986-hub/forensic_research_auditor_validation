import json, math

def wilson_95_ci(k, n):
    if n == 0:
        return {'proportion': 0.0, 'lower_95': 0.0, 'upper_95': 0.0}
    z = 1.959964
    p = k / n
    denom = 1.0 + (z ** 2) / n
    center = (p + (z ** 2) / (2.0 * n)) / denom
    half_width = (z * math.sqrt((p * (1.0 - p) / n) + (z ** 2) / (4.0 * (n ** 2)))) / denom
    return {
        'proportion': round(p * 100.0, 2),
        'lower_95': round(max(0.0, center - half_width) * 100.0, 2),
        'upper_95': round(min(1.0, center + half_width) * 100.0, 2)
    }

files = [
    ('Wave 1', 'docs/data/blind_2000_ledger.json'),
    ('Wave 2', 'docs/data/blind_wave2_ledger.json'),
    ('Wave 3', 'docs/data/blind_wave3_ledger.json'),
    ('Wave 4', 'docs/data/blind_wave4_ledger.json'),
    ('Wave 5', 'docs/data/blind_wave5_ledger.json'),
    ('Pooled', 'docs/data/blind_combined_10000_ledger.json'),
]

row_studies = []
row_g3_sens = []
row_non_math_spec = []
row_ctrl_spec = []
row_ppv_cohort_math = []
row_ppv_cohort_any = []
row_ppv_sweep = []
row_ppv_whistle = []
row_lr = []

for name, p in files:
    with open(p, 'r', encoding='utf-8') as f:
        d = json.load(f)
    cases = [x for x in d if x.get('cohort') == 'CASE']
    ctrls = [x for x in d if x.get('cohort') == 'CONTROL']
    
    g3 = [x for x in cases if x.get('target_gate') == 'GATE_3_MATH_DATA']
    non_math = [x for x in cases if x.get('target_gate') != 'GATE_3_MATH_DATA']
    
    g3_flagged = sum(1 for x in g3 if x.get('blind_verdict') != 'CLEAN')
    non_math_clean = sum(1 for x in non_math if x.get('blind_verdict') == 'CLEAN')
    ctrl_clean = sum(1 for x in ctrls if x.get('blind_verdict') == 'CLEAN')
    ctrl_flagged = len(ctrls) - ctrl_clean
    cases_flagged = sum(1 for x in cases if x.get('blind_verdict') != 'CLEAN')
    
    g3_ci = wilson_95_ci(g3_flagged, len(g3))
    non_math_ci = wilson_95_ci(non_math_clean, len(non_math))
    ctrl_ci = wilson_95_ci(ctrl_clean, len(ctrls))
    
    sens = g3_flagged / len(g3)
    spec = ctrl_clean / len(ctrls)
    fpr = 1.0 - spec
    lr = sens / fpr if fpr > 0 else 0
    
    def calc_ppv(p_prev, se, sp):
        tp = se * p_prev
        fp = (1.0 - sp) * (1.0 - p_prev)
        return tp / (tp + fp) if (tp + fp) > 0 else 0
        
    ppv_math = (g3_flagged / (g3_flagged + ctrl_flagged)) * 100 if (g3_flagged + ctrl_flagged) > 0 else 0
    ppv_any = (cases_flagged / (cases_flagged + ctrl_flagged)) * 100 if (cases_flagged + ctrl_flagged) > 0 else 0
    ppv15 = calc_ppv(0.15, sens, spec) * 100
    ppv40 = calc_ppv(0.40, sens, spec) * 100
    
    row_studies.append(f"{len(d):,}")
    row_g3_sens.append(f"{g3_ci['proportion']}% ({g3_flagged}/{len(g3)})")
    row_non_math_spec.append(f"{non_math_ci['proportion']}% ({non_math_clean}/{len(non_math)})")
    row_ctrl_spec.append(f"{ctrl_ci['proportion']}% ({ctrl_clean}/{len(ctrls)})")
    row_ppv_cohort_math.append(f"{ppv_math:.2f}%")
    row_ppv_cohort_any.append(f"{ppv_any:.2f}%")
    row_ppv_sweep.append(f"{ppv15:.2f}%")
    row_ppv_whistle.append(f"{ppv40:.2f}%")
    row_lr.append(f"{lr:.2f}")

print("| Metric | Wave 1 | Wave 2 | Wave 3 | Wave 4 | Wave 5 | Pooled (10k) |")
print("| :--- | :---: | :---: | :---: | :---: | :---: | :---: |")
print("| Studies Evaluated | " + " | ".join(row_studies) + " |")
print("| Gate 3 Math Sensitivity | " + " | ".join(row_g3_sens) + " |")
print("| Non-Mathematical Retractions Specificity | " + " | ".join(row_non_math_spec) + " |")
print("| Clean Controls Specificity | " + " | ".join(row_ctrl_spec) + " |")
print("| Benchmark Cohort PPV (Math vs Ctrl) | " + " | ".join(row_ppv_cohort_math) + " |")
print("| Benchmark Cohort PPV (Any vs Ctrl) | " + " | ".join(row_ppv_cohort_any) + " |")
print("| Targeted Sweep PPV (P=15%) | " + " | ".join(row_ppv_sweep) + " |")
print("| Whistleblower PPV (P=40%) | " + " | ".join(row_ppv_whistle) + " |")
print("| Positive Likelihood Ratio (LR+) | " + " | ".join(row_lr) + " |")
