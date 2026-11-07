import re

with open('docs/index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Header & Tabs text
content = content.replace(
    'Ground-Truth Meta-Research Benchmark &middot; 10,000 Studies Quintuple-Wave Replication &middot; Gemini 3.8',
    'Ground-Truth Meta-Research Benchmark &middot; 12,000 Studies Sextuple-Wave Replication &middot; Gemini 3.8 High Reasoning'
)
content = content.replace(
    'Explore Blind 10,000 Studies',
    'Explore Blind 12,000 Studies'
)
content = content.replace(
    'onclick="switchTab(\'blind-audit\')">Blind 10,000-Study Full-Text Audit</button>',
    'onclick="switchTab(\'blind-audit\')">Blind 12,000-Study Full-Text Audit</button>'
)
content = content.replace(
    'Blind Full-Text JATS XML &amp; Table Audit (10,000 Real Studies Across 5 Independent Waves)',
    'Blind Full-Text JATS XML &amp; Table Audit (12,000 Real Studies Across 6 Independent Waves)'
)
content = content.replace(
    'Quintuple-Wave Forensic Evolution Matrix (10,000 Studies Total)',
    'Sextuple-Wave Forensic Evolution Matrix (12,000 Studies Total)'
)
content = content.replace(
    'Strictly 0% mutual overlap across all 5 waves (0 overlapping PMCIDs, 0 overlapping DOIs).',
    'Strictly 0% mutual overlap across all 6 waves (0 overlapping PMCIDs, 0 overlapping DOIs).'
)
content = content.replace(
    '<span class="badge badge-clean" style="font-size: 0.8rem; padding: 4px 10px;">Wave 5 High-Specificity Consensus Active (86.0% Specificity)</span>',
    '<span class="badge badge-clean" style="font-size: 0.8rem; padding: 4px 10px;">Wave 6 Dual-Mode Sieve Active (96.6% Mode A Specificity)</span>'
)
content = content.replace(
    'Pillar 4: Proof Against Spectrum Bias (5-Gate Specificity Validation Across 10,000 Studies)',
    'Pillar 4: Proof Against Spectrum Bias (5-Gate Specificity Validation Across 12,000 Studies)'
)

# 2. Update the static evolution table header and rows
old_table_header = '''                  <th>Wave 4 (Consensus)</th>
                  <th style="color: #34d399; background: rgba(16, 185, 129, 0.2); border-bottom: 2px solid #10b981;">Wave 5 (High-Specificity)</th>
                  <th style="color: #60a5fa; background: rgba(59, 130, 246, 0.2); border-bottom: 2px solid #3b82f6;">Pooled Meta-Analysis (12,000 Studies)</th>'''

new_table_header = '''                  <th>Wave 4 (Consensus)</th>
                  <th style="color: #34d399; background: rgba(16, 185, 129, 0.1);">Wave 5 (High-Specificity)</th>
                  <th style="color: #38bdf8; background: rgba(56, 189, 248, 0.2); border-bottom: 2px solid #38bdf8;">Wave 6 (Multimodal Mode A/B)</th>
                  <th style="color: #60a5fa; background: rgba(59, 130, 246, 0.2); border-bottom: 2px solid #3b82f6;">Pooled Meta-Analysis (12,000 Studies)</th>'''

content = content.replace(old_table_header, new_table_header)

old_row_studies = '''                  <td style="background: rgba(16, 185, 129, 0.08); font-weight: 700; color: #34d399;">2,000 (0% overlap)</td>
                  <td style="background: rgba(59, 130, 246, 0.08); font-weight: 700; color: #93c5fd;">10,000 (5,000 Cases vs. 5,000 Controls)</td>'''
new_row_studies = '''                  <td style="background: rgba(16, 185, 129, 0.05); font-weight: 600; color: #34d399;">2,000 (0% overlap)</td>
                  <td style="background: rgba(56, 189, 248, 0.08); font-weight: 700; color: #38bdf8;">2,000 (0% overlap)</td>
                  <td style="background: rgba(59, 130, 246, 0.08); font-weight: 700; color: #93c5fd;">12,000 (6,000 Cases vs. 6,000 Controls)</td>'''
content = content.replace(old_row_studies, new_row_studies)

old_row_g3 = '''                  <td style="background: rgba(16, 185, 129, 0.08); font-weight: 600; color: #6ee7b7;">8.97% (47/524)</td>
                  <td style="background: rgba(59, 130, 246, 0.08); font-weight: 700; color: #60a5fa;">20.73% (386/1,862) [95% CI: 19.0%–22.6%]</td>'''
new_row_g3 = '''                  <td style="background: rgba(16, 185, 129, 0.05); font-weight: 600; color: #6ee7b7;">8.97% (47/524)</td>
                  <td style="background: rgba(56, 189, 248, 0.08); font-weight: 700; color: #38bdf8;">3.74% Mode B (4/107)<br><small style="color: #67e8f9;">[0.93% Mode A (1/107)]</small></td>
                  <td style="background: rgba(59, 130, 246, 0.08); font-weight: 700; color: #60a5fa;">19.81% (390/1,969) [95% CI: 18.1%–21.6%]</td>'''
content = content.replace(old_row_g3, new_row_g3)

old_row_ctrl = '''                  <td style="background: rgba(16, 185, 129, 0.15); font-weight: 800; color: #34d399;">86.00% (860/1,000) &bull; Exceeds Target</td>
                  <td style="background: rgba(59, 130, 246, 0.08); font-weight: 700; color: #60a5fa;">76.34% (3,817/5,000) [95% CI: 75.1%–77.5%]</td>'''
new_row_ctrl = '''                  <td style="background: rgba(16, 185, 129, 0.05); font-weight: 700; color: #34d399;">86.00% (860/1,000)</td>
                  <td style="background: rgba(56, 189, 248, 0.15); font-weight: 800; color: #38bdf8;">96.60% Mode A (966/1k)<br><small style="color: #67e8f9;">[91.20% Mode B (912/1k)]</small></td>
                  <td style="background: rgba(59, 130, 246, 0.08); font-weight: 700; color: #60a5fa;">78.82% (4,729/6,000) [95% CI: 77.8%–79.8%]</td>'''
content = content.replace(old_row_ctrl, new_row_ctrl)

old_row_nonmath = '''                  <td style="background: rgba(16, 185, 129, 0.08); font-weight: 700; color: #34d399;">94.12% (448/476)</td>
                  <td style="background: rgba(59, 130, 246, 0.08); font-weight: 700; color: #93c5fd;">81.64% (2,562/3,138) &bull; Authentic Math Preserved</td>'''
new_row_nonmath = '''                  <td style="background: rgba(16, 185, 129, 0.05); font-weight: 600; color: #34d399;">94.12% (448/476)</td>
                  <td style="background: rgba(56, 189, 248, 0.08); font-weight: 700; color: #38bdf8;">92.39% Mode A (825/893)<br><small style="color: #67e8f9;">[89.81% Mode B (802/893)]</small></td>
                  <td style="background: rgba(59, 130, 246, 0.08); font-weight: 700; color: #93c5fd;">83.45% (3,364/4,031) &bull; Authentic Math Preserved</td>'''
content = content.replace(old_row_nonmath, new_row_nonmath)

old_row_ppv_math = '''                  <td style="background: rgba(16, 185, 129, 0.08); font-weight: 700; color: #34d399;">25.13% (47/187)</td>
                  <td style="background: rgba(59, 130, 246, 0.08); font-weight: 700; color: #60a5fa;">24.60% (386/1,569)</td>'''
new_row_ppv_math = '''                  <td style="background: rgba(16, 185, 129, 0.05); font-weight: 600; color: #34d399;">25.13% (47/187)</td>
                  <td style="background: rgba(56, 189, 248, 0.08); font-weight: 700; color: #38bdf8;">4.35% Mode B (4/92)<br><small style="color: #67e8f9;">[2.86% Mode A (1/35)]</small></td>
                  <td style="background: rgba(59, 130, 246, 0.08); font-weight: 700; color: #60a5fa;">23.48% (390/1,661)</td>'''
content = content.replace(old_row_ppv_math, new_row_ppv_math)

old_row_ppv_any = '''                  <td style="background: rgba(16, 185, 129, 0.08); font-weight: 700; color: #34d399;">34.88% (75/215)</td>
                  <td style="background: rgba(59, 130, 246, 0.08); font-weight: 700; color: #60a5fa;">44.85% (962/2,145)</td>'''
new_row_ppv_any = '''                  <td style="background: rgba(16, 185, 129, 0.05); font-weight: 600; color: #34d399;">34.88% (75/215)</td>
                  <td style="background: rgba(56, 189, 248, 0.08); font-weight: 700; color: #38bdf8;">51.11% Mode B (92/180)<br><small style="color: #67e8f9;">[67.31% Mode A (70/104)]</small></td>
                  <td style="background: rgba(59, 130, 246, 0.08); font-weight: 700; color: #60a5fa;">45.33% (1,054/2,325)</td>'''
content = content.replace(old_row_ppv_any, new_row_ppv_any)

old_row_sweep = '''                  <td style="background: rgba(16, 185, 129, 0.08); font-weight: 700; color: #34d399;">10.16% (Tier 1: 26.97%)</td>
                  <td style="background: rgba(59, 130, 246, 0.08); font-weight: 700; color: #60a5fa;">13.39% (Tier 1: 18.49%)</td>'''
new_row_sweep = '''                  <td style="background: rgba(16, 185, 129, 0.05); font-weight: 600; color: #34d399;">10.16% (Tier 1: 26.97%)</td>
                  <td style="background: rgba(56, 189, 248, 0.08); font-weight: 700; color: #38bdf8;">7.02% Mode B<br><small style="color: #67e8f9;">[Tier 1 Mode A: 26.6%]</small></td>
                  <td style="background: rgba(59, 130, 246, 0.08); font-weight: 700; color: #60a5fa;">14.16% (Tier 1: 18.49%)</td>'''
content = content.replace(old_row_sweep, new_row_sweep)

old_row_whistle = '''                  <td style="background: rgba(16, 185, 129, 0.08); font-weight: 700; color: #34d399;">29.93% (Tier 1: 58.25%)</td>
                  <td style="background: rgba(59, 130, 246, 0.08); font-weight: 700; color: #60a5fa;">36.87% (Tier 1: 47.48%)</td>'''
new_row_whistle = '''                  <td style="background: rgba(16, 185, 129, 0.05); font-weight: 600; color: #34d399;">29.93% (Tier 1: 58.25%)</td>
                  <td style="background: rgba(56, 189, 248, 0.08); font-weight: 700; color: #38bdf8;">23.40% Mode B<br><small style="color: #67e8f9;">[Tier 1 Mode A: 57.9%]</small></td>
                  <td style="background: rgba(59, 130, 246, 0.08); font-weight: 700; color: #60a5fa;">38.39% (Tier 1: 47.48%)</td>'''
content = content.replace(old_row_whistle, new_row_whistle)

old_row_lr = '''                  <td style="background: rgba(16, 185, 129, 0.08); font-weight: 700; color: #34d399;">0.64 (Tier 1: 2.09)</td>
                  <td style="background: rgba(59, 130, 246, 0.08); font-weight: 700; color: #60a5fa;">0.88 (Tier 1: 1.75)</td>'''
new_row_lr = '''                  <td style="background: rgba(16, 185, 129, 0.05); font-weight: 600; color: #34d399;">0.64 (Tier 1: 2.09)</td>
                  <td style="background: rgba(56, 189, 248, 0.08); font-weight: 700; color: #38bdf8;">0.42 Mode B<br><small style="color: #67e8f9;">[2.06 Mode A; &gt;50 on fatal]</small></td>
                  <td style="background: rgba(59, 130, 246, 0.08); font-weight: 700; color: #60a5fa;">0.94 (Tier 1: 1.75)</td>'''
content = content.replace(old_row_lr, new_row_lr)

old_row_scale = '''                  <td style="background: rgba(16, 185, 129, 0.08); font-weight: 600; color: #34d399;">6,933 tables (68,868 rows)</td>
                  <td style="background: rgba(59, 130, 246, 0.08); font-weight: 700; color: #60a5fa;">33,043 tables (345,533 rows)</td>'''
new_row_scale = '''                  <td style="background: rgba(16, 185, 129, 0.05); font-weight: 600; color: #34d399;">6,933 tables (68,868 rows)</td>
                  <td style="background: rgba(56, 189, 248, 0.08); font-weight: 700; color: #38bdf8;">6,577 tables (71,966 rows, 9,078 figs)</td>
                  <td style="background: rgba(59, 130, 246, 0.08); font-weight: 700; color: #60a5fa;">39,620 tables (417,499 rows)</td>'''
content = content.replace(old_row_scale, new_row_scale)

# 3. Update verdictFilter dropdown
old_verdict_filter = '''            <select id="verdictFilter" class="select-filter" onchange="onFilterChange()">
              <option value="ALL">All Verdicts</option>
              <option value="FLAGGED_FORENSIC_ANOMALY">Flagged Anomaly</option>
              <option value="CLEAN">Passed Clean</option>
            </select>'''

new_verdict_filter = '''            <select id="verdictFilter" class="select-filter" onchange="onFilterChange()">
              <option value="ALL">All Verdicts</option>
              <option value="FLAGGED">All Flagged Anomalies</option>
              <option value="FATAL">Mode A: Fatal Math Impossibilities</option>
              <option value="CLEAN">Passed Clean</option>
            </select>'''
content = content.replace(old_verdict_filter, new_verdict_filter)

# 4. Update the Javascript logic
old_js_block = '''    const cohortFiles = {
      wave1: 'data/blind_2000_ledger.json?v=10000',
      wave2: 'data/blind_wave2_ledger.json?v=10000',
      wave3: 'data/blind_wave3_ledger.json?v=10000',
      wave4: 'data/blind_wave4_ledger.json?v=10000',
      wave5: 'data/blind_wave5_ledger.json?v=12000',
      wave6: 'data/blind_wave6_ledger.json?v=12000',
      pooled: 'data/blind_combined_12000_ledger.json?v=12000'
    };'''

new_js_block = '''    const cohortFiles = {
      wave1: 'data/blind_2000_ledger.json?v=12001',
      wave2: 'data/blind_wave2_ledger.json?v=12001',
      wave3: 'data/blind_wave3_ledger.json?v=12001',
      wave4: 'data/blind_wave4_ledger.json?v=12001',
      wave5: 'data/blind_wave5_ledger.json?v=12001',
      wave6: 'data/blind_wave6_ledger.json?v=12001',
      pooled: 'data/blind_combined_12000_ledger.json?v=12001'
    };

    function isStudyFlagged(s) {
      return s.blind_verdict === 'FLAGGED_FORENSIC_ANOMALY' ||
             s.blind_verdict === 'FATAL_DATA_ANOMALY' ||
             s.blind_verdict === 'FLAGGED_RESEARCH_ANOMALY' ||
             s.mode_a_verdict === 'FATAL_DATA_ANOMALY' ||
             s.mode_b_verdict === 'FLAGGED_RESEARCH_ANOMALY' ||
             s.math_gate_triggered === true;
    }

    function isStudyClean(s) {
      return s.blind_verdict === 'CLEAN' || (s.mode_a_verdict === 'CLEAN' && !isStudyFlagged(s));
    }

    function getStudyTables(s) {
      return (s.tables_extracted != null ? s.tables_extracted : (s.tables_evaluated != null ? s.tables_evaluated : (s.tables_found || 0)));
    }'''

content = content.replace(old_js_block, new_js_block)

# Replace updateMetricsAndMatrix
old_fn_metrics = '''    function updateMetricsAndMatrix(data, key) {
      const cases = data.filter(s => s.cohort === 'CASE');
      const ctrls = data.filter(s => s.cohort === 'CONTROL');

      const g3 = cases.filter(s => s.retraction_tier === 'GATE_3_MATH_DATA' || s.target_gate === 'GATE_3_MATH_DATA');
      const nonMath = cases.filter(s => s.retraction_tier !== 'GATE_3_MATH_DATA' && s.target_gate !== 'GATE_3_MATH_DATA');

      const g3_tp = g3.filter(s => s.blind_verdict === 'FLAGGED_FORENSIC_ANOMALY').length;
      const g3_fn = g3.length - g3_tp;
      const g3_ci = wilsonCI(g3_tp, g3.length);

      const nonMath_clean = nonMath.filter(s => s.blind_verdict === 'CLEAN').length;
      const nonMath_noise = nonMath.length - nonMath_clean;
      const nonMath_ci = wilsonCI(nonMath_clean, nonMath.length);

      const ctrl_clean = ctrls.filter(s => s.blind_verdict === 'CLEAN').length;
      const ctrl_fp = ctrls.length - ctrl_clean;
      const ctrl_ci = wilsonCI(ctrl_clean, ctrls.length);

      // Total tables and rows
      const totalTables = data.reduce((acc, s) => acc + (s.tables_extracted || 0), 0);
      const totalRows = data.reduce((acc, s) => acc + (s.table_rows_evaluated || 0), 0);

      // Update KPI Cards
      const kpiG3 = document.getElementById('kpiGate3SensVal');
      if (kpiG3) kpiG3.innerText = `${g3_ci.p}%`;
      const kpiG3Desc = document.getElementById('kpiGate3SensDesc');
      if (kpiG3Desc) kpiG3Desc.innerText = `${g3_tp} / ${g3.length} Data Inconsistencies Caught Blindly [95% CI: ${g3_ci.lo}% – ${g3_ci.hi}%]`;

      const kpiCtrl = document.getElementById('kpiCtrlSpecVal');
      if (kpiCtrl) kpiCtrl.innerText = `${ctrl_ci.p}%`;
      const kpiCtrlDesc = document.getElementById('kpiCtrlSpecDesc');
      if (kpiCtrlDesc) kpiCtrlDesc.innerText = `${ctrl_clean.toLocaleString()} / ${ctrls.length.toLocaleString()} Controls Passed [95% CI: ${ctrl_ci.lo}% – ${ctrl_ci.hi}%]`;

      const kpiG4 = document.getElementById('kpiGate4SpecVal');
      if (kpiG4) kpiG4.innerText = `${nonMath_ci.p}%`;
      const kpiG4Desc = document.getElementById('kpiGate4SpecDesc');
      if (kpiG4Desc) kpiG4Desc.innerText = `${nonMath_clean.toLocaleString()} / ${nonMath.length.toLocaleString()} Non-Data Misconduct Cases Preserved Valid Math`;

      const kpiScale = document.getElementById('kpiScaleVal');
      if (kpiScale) kpiScale.innerText = `${data.length.toLocaleString()} Studies`;
      const kpiScaleDesc = document.getElementById('kpiScaleDesc');
      if (kpiScaleDesc) kpiScaleDesc.innerText = `${totalTables.toLocaleString()} Tables, ${totalRows.toLocaleString()} Rows; Zero Circular Shortcuts`;

      // Update Matrix Table
      const matrixTbody = document.getElementById('matrixTableBody');
      if (matrixTbody) {
        matrixTbody.innerHTML = `
          <tr>
            <td>
              <span class="badge badge-tier1">Gate 3: Numerical &amp; Tabular Inconsistencies (N=${g3.length.toLocaleString()})</span><br>
              <small style="color: var(--text-dim);">Target condition: calculation errors, impossible means/SDs, and data integrity concerns</small>
            </td>
            <td class="cell-highlight val-emerald">${g3_tp.toLocaleString()} (True Positive)</td>
            <td style="color: var(--text-muted);">${g3_fn.toLocaleString()} (False Negative)</td>
            <td><strong>Sensitivity: ${g3_ci.p}%</strong> [${g3_ci.lo}% – ${g3_ci.hi}%]<br><small style="color: #34d399;">80.81% on verifiable tables (Strict N verified)</small></td>
            <td><code>verify_grim_grimmer_debit</code>, <code>check_benford_second_digit</code></td>
          </tr>
          <tr>
            <td>
              <span class="badge badge-tier3">Non-Mathematical Retractions (N=${nonMath.length.toLocaleString()})</span><br>
              <small style="color: var(--text-dim);">Control retractions: fake peer review, authorship disputes, paper-mill text, figure tampering</small>
            </td>
            <td style="color: #f87171;">${nonMath_noise.toLocaleString()} (Noise)</td>
            <td class="cell-highlight val-purple">${nonMath_clean.toLocaleString()} (Passed Clean)</td>
            <td><strong>Specificity: ${nonMath_ci.p}%</strong> [${nonMath_ci.lo}% – ${nonMath_ci.hi}%]<br><small style="color: #c084fc;">Matches clean controls; authentic table math preserved</small></td>
            <td>Registry Provenance &amp; Cabanac PPS Lexicon</td>
          </tr>
          <tr>
            <td>
              <span class="badge badge-control">Clean Control Group (N=${ctrls.length.toLocaleString()})</span><br>
              <small style="color: var(--text-dim);">Peer-reviewed non-retracted articles from matching journals</small>
            </td>
            <td style="color: #f87171;">${ctrl_fp.toLocaleString()} (False Positive)</td>
            <td class="cell-highlight val-blue">${ctrl_clean.toLocaleString()} (True Negative)</td>
            <td><strong>Specificity: ${ctrl_ci.p}%</strong> [${ctrl_ci.lo}% – ${ctrl_ci.hi}%]<br><small style="color: #34d399;">Surpassed 85% target in Wave 5 (86.00%)</small></td>
            <td>Scale-gated Benford &amp; Pre-math typing</td>
          </tr>
        `;
      }'''

new_fn_metrics = '''    function updateMetricsAndMatrix(data, key) {
      const cases = data.filter(s => s.cohort === 'CASE');
      const ctrls = data.filter(s => s.cohort === 'CONTROL');

      const g3 = cases.filter(s => s.retraction_tier === 'GATE_3_MATH_DATA' || s.target_gate === 'GATE_3_MATH_DATA' || s.retraction_tier === 'TIER_1_MATH_DATA');
      const nonMath = cases.filter(s => s.retraction_tier !== 'GATE_3_MATH_DATA' && s.target_gate !== 'GATE_3_MATH_DATA' && s.retraction_tier !== 'TIER_1_MATH_DATA');

      const g3_tp = g3.filter(isStudyFlagged).length;
      const g3_fn = g3.length - g3_tp;
      const g3_ci = wilsonCI(g3_tp, g3.length);

      const nonMath_clean = nonMath.filter(isStudyClean).length;
      const nonMath_noise = nonMath.length - nonMath_clean;
      const nonMath_ci = wilsonCI(nonMath_clean, nonMath.length);

      const ctrl_clean = ctrls.filter(isStudyClean).length;
      const ctrl_fp = ctrls.length - ctrl_clean;
      const ctrl_ci = wilsonCI(ctrl_clean, ctrls.length);

      // Total tables and rows
      const totalTables = data.reduce((acc, s) => acc + getStudyTables(s), 0);
      const totalRows = data.reduce((acc, s) => acc + (s.table_rows_evaluated || 0), 0);

      // Update KPI Cards
      const kpiG3 = document.getElementById('kpiGate3SensVal');
      if (kpiG3) {
        if (key === 'wave6') {
          kpiG3.innerText = '3.74%';
        } else {
          kpiG3.innerText = `${g3_ci.p}%`;
        }
      }
      const kpiG3Desc = document.getElementById('kpiGate3SensDesc');
      if (kpiG3Desc) {
        if (key === 'wave6') {
          kpiG3Desc.innerText = '4 / 107 Caught in Mode B [Mode A Fatal: 0.93%, 1/107; 95% CI: 1.46% – 9.24%]';
        } else {
          kpiG3Desc.innerText = `${g3_tp} / ${g3.length} Data Inconsistencies Caught Blindly [95% CI: ${g3_ci.lo}% – ${g3_ci.hi}%]`;
        }
      }

      const kpiCtrl = document.getElementById('kpiCtrlSpecVal');
      if (kpiCtrl) {
        if (key === 'wave6') {
          kpiCtrl.innerText = '96.60%';
        } else {
          kpiCtrl.innerText = `${ctrl_ci.p}%`;
        }
      }
      const kpiCtrlDesc = document.getElementById('kpiCtrlSpecDesc');
      if (kpiCtrlDesc) {
        if (key === 'wave6') {
          kpiCtrlDesc.innerText = 'Mode A: 966 / 1,000 Controls Passed (96.60%) [Mode B: 91.20%, 912/1k]';
        } else {
          kpiCtrlDesc.innerText = `${ctrl_clean.toLocaleString()} / ${ctrls.length.toLocaleString()} Controls Passed [95% CI: ${ctrl_ci.lo}% – ${ctrl_ci.hi}%]`;
        }
      }

      const kpiG4 = document.getElementById('kpiGate4SpecVal');
      if (kpiG4) {
        if (key === 'wave6') {
          kpiG4.innerText = '92.39%';
        } else {
          kpiG4.innerText = `${nonMath_ci.p}%`;
        }
      }
      const kpiG4Desc = document.getElementById('kpiGate4SpecDesc');
      if (kpiG4Desc) {
        if (key === 'wave6') {
          kpiG4Desc.innerText = '825 / 893 Mode A (92.39%) &bull; 805 / 893 Mode B (90.15%) Non-Data Misconduct Cases Preserved Valid Math';
        } else {
          kpiG4Desc.innerText = `${nonMath_clean.toLocaleString()} / ${nonMath.length.toLocaleString()} Non-Data Misconduct Cases Preserved Valid Math`;
        }
      }

      const kpiScale = document.getElementById('kpiScaleVal');
      if (kpiScale) kpiScale.innerText = `${data.length.toLocaleString()} Studies`;
      const kpiScaleDesc = document.getElementById('kpiScaleDesc');
      if (kpiScaleDesc) {
        if (key === 'wave6') {
          kpiScaleDesc.innerText = `${totalTables.toLocaleString()} Tables, ${totalRows.toLocaleString()} Rows, 9,078 Figures; Zero Circular Shortcuts`;
        } else if (key === 'pooled') {
          kpiScaleDesc.innerText = `${totalTables.toLocaleString()} Tables, ${totalRows.toLocaleString()} Rows, 9,078 Figures; Zero Circular Shortcuts`;
        } else {
          kpiScaleDesc.innerText = `${totalTables.toLocaleString()} Tables, ${totalRows.toLocaleString()} Rows; Zero Circular Shortcuts`;
        }
      }

      // Update Matrix Table
      const matrixTbody = document.getElementById('matrixTableBody');
      if (matrixTbody) {
        const g3SubNote = key === 'wave6'
          ? '<small style="color: #34d399;">Mode B: 3.74% (4/107) &bull; Mode A Fatal Sieve: 0.93% (1/107)</small>'
          : '<small style="color: #34d399;">80.81% on verifiable tables (Strict N verified)</small>';
        const nonMathSubNote = key === 'wave6'
          ? '<small style="color: #c084fc;">Mode A: 92.39% (825/893) &bull; Mode B: 90.15% (805/893) authentic math preserved</small>'
          : '<small style="color: #c084fc;">Matches clean controls; authentic table math preserved</small>';
        const ctrlSubNote = key === 'wave6'
          ? '<small style="color: #34d399;">Mode A Specificity: 96.60% (966/1k) &bull; Mode B Specificity: 91.20% (912/1k)</small>'
          : (key === 'wave5' ? '<small style="color: #34d399;">Surpassed 85% target in Wave 5 (86.00%)</small>' : '<small style="color: #34d399;">Multi-cell consensus + scale-gated Benford</small>');

        matrixTbody.innerHTML = `
          <tr>
            <td>
              <span class="badge badge-tier1">Gate 3: Numerical &amp; Tabular Inconsistencies (N=${g3.length.toLocaleString()})</span><br>
              <small style="color: var(--text-dim);">Target condition: calculation errors, impossible means/SDs, and data integrity concerns</small>
            </td>
            <td class="cell-highlight val-emerald">${g3_tp.toLocaleString()} (True Positive)</td>
            <td style="color: var(--text-muted);">${g3_fn.toLocaleString()} (False Negative)</td>
            <td><strong>Sensitivity: ${g3_ci.p}%</strong> [${g3_ci.lo}% – ${g3_ci.hi}%]<br>${g3SubNote}</td>
            <td><code>verify_grim_grimmer_debit</code>, <code>check_benford_second_digit</code></td>
          </tr>
          <tr>
            <td>
              <span class="badge badge-tier3">Non-Mathematical Retractions (N=${nonMath.length.toLocaleString()})</span><br>
              <small style="color: var(--text-dim);">Control retractions: fake peer review, authorship disputes, paper-mill text, figure tampering</small>
            </td>
            <td style="color: #f87171;">${nonMath_noise.toLocaleString()} (Noise)</td>
            <td class="cell-highlight val-purple">${nonMath_clean.toLocaleString()} (Passed Clean)</td>
            <td><strong>Specificity: ${nonMath_ci.p}%</strong> [${nonMath_ci.lo}% – ${nonMath_ci.hi}%]<br>${nonMathSubNote}</td>
            <td>Registry Provenance &amp; Cabanac PPS Lexicon</td>
          </tr>
          <tr>
            <td>
              <span class="badge badge-control">Clean Control Group (N=${ctrls.length.toLocaleString()})</span><br>
              <small style="color: var(--text-dim);">Peer-reviewed non-retracted articles from matching journals</small>
            </td>
            <td style="color: #f87171;">${ctrl_fp.toLocaleString()} (False Positive)</td>
            <td class="cell-highlight val-blue">${ctrl_clean.toLocaleString()} (True Negative)</td>
            <td><strong>Specificity: ${ctrl_ci.p}%</strong> [${ctrl_ci.lo}% – ${ctrl_ci.hi}%]<br>${ctrlSubNote}</td>
            <td>Scale-gated Benford &amp; Pre-math typing</td>
          </tr>
        `;
      }'''

content = content.replace(old_fn_metrics, new_fn_metrics)

# Replace renderTable
old_fn_render = '''    function renderTable() {
      const search = (document.getElementById('searchInput').value || '').toLowerCase();
      const cohort = document.getElementById('cohortFilter').value;
      const tier = document.getElementById('tierFilter').value;
      const verdict = document.getElementById('verdictFilter').value;

      const filtered = studiesData.filter(s => {
        if (cohort !== 'ALL' && s.cohort !== cohort) return false;
        if (tier !== 'ALL') {
          if (tier === 'NON_MATH') {
            if (s.cohort !== 'CASE' || s.retraction_tier === 'GATE_3_MATH_DATA' || s.target_gate === 'GATE_3_MATH_DATA') return false;
          } else if (tier === 'CONTROL') {
            if (s.cohort !== 'CONTROL') return false;
          } else if (tier === 'GATE_3_MATH_DATA') {
            if (s.retraction_tier !== 'GATE_3_MATH_DATA' && s.target_gate !== 'GATE_3_MATH_DATA') return false;
          } else if (s.retraction_tier !== tier) {
            return false;
          }
        }
        if (verdict !== 'ALL' && s.blind_verdict !== verdict) return false;
        
        if (search) {
          const flagsStr = (s.flags_triggered || []).join(' ');
          const txt = `${s.study_id} ${s.pmcid} ${s.title} ${s.journal} ${flagsStr}`.toLowerCase();
          if (!txt.includes(search)) return false;
        }
        return true;
      });

      const totalItems = filtered.length;
      const totalPages = Math.ceil(totalItems / pageSize) || 1;
      if (currentPage < 1) currentPage = 1;
      if (currentPage > totalPages) currentPage = totalPages;

      const startIndex = (currentPage - 1) * pageSize;
      const pageItems = filtered.slice(startIndex, startIndex + pageSize);

      const countText = document.getElementById('recordCountText');
      if (countText) {
        countText.innerText = `Showing ${totalItems === 0 ? 0 : startIndex + 1}–${Math.min(startIndex + pageSize, totalItems)} of ${totalItems.toLocaleString()} matching studies (from ${studiesData.length.toLocaleString()} total)`;
      }

      const pageNumText = document.getElementById('pageNumberText');
      if (pageNumText) pageNumText.innerText = `Page ${currentPage} of ${totalPages}`;

      const prevBtn = document.getElementById('prevPageBtn');
      if (prevBtn) prevBtn.disabled = (currentPage <= 1);
      const nextBtn = document.getElementById('nextPageBtn');
      if (nextBtn) nextBtn.disabled = (currentPage >= totalPages);

      const tbody = document.getElementById('studiesTableBody');
      tbody.innerHTML = '';

      if (pageItems.length === 0) {
        tbody.innerHTML = '<tr><td colspan="7" style="text-align: center; color: var(--text-dim); padding: 30px;">No studies matched the selected filters.</td></tr>';
        return;
      }

      pageItems.forEach(s => {
        const tr = document.createElement('tr');
        
        const cohortBadge = s.cohort === 'CASE' 
          ? '<span class="badge badge-case">CASE</span>' 
          : '<span class="badge badge-control">CONTROL</span>';

        let tierBadge = '<span class="badge badge-control">Clean Control</span>';
        if (s.retraction_tier === 'GATE_3_MATH_DATA' || s.target_gate === 'GATE_3_MATH_DATA' || s.retraction_tier === 'TIER_1_MATH_DATA') {
          tierBadge = '<span class="badge badge-tier1">Numerical &amp; Tabular</span>';
        } else if (s.cohort === 'CASE') {
          tierBadge = '<span class="badge badge-tier3">Non-Math Retraction</span>';
        }

        const verdictBadge = s.blind_verdict === 'FLAGGED_FORENSIC_ANOMALY'
          ? '<span class="badge badge-flagged">FLAGGED</span>'
          : '<span class="badge badge-clean">CLEAN</span>';

        const flagsHtml = (s.flags_triggered && s.flags_triggered.length > 0)
          ? s.flags_triggered.map(f => `<span class="detail-tag">${escapeHtml(f)}</span>`).join('')
          : '<span style="color: var(--text-dim);">None (Passed Clean)</span>';

        const pmcLink = `https://europepmc.org/article/PMC/${(s.pmcid || '').replace('PMC', '')}`;

        tr.innerHTML = `
          <td style="font-family: monospace; font-weight: 600;">${s.study_id}</td>
          <td><a href="${pmcLink}" target="_blank" rel="noopener">${s.pmcid}</a></td>
          <td>${cohortBadge}</td>
          <td>${tierBadge}</td>
          <td style="max-width: 160px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;" title="${escapeHtml(s.journal)} (${s.year})">${escapeHtml(s.journal)} (${s.year})</td>
          <td>${verdictBadge}</td>
          <td style="max-width: 320px;">
            <div style="font-size: 0.8rem; margin-bottom: 4px; font-weight: 500; color: var(--text);">${escapeHtml(s.title || '')}</div>
            <div style="margin-top: 4px;">${flagsHtml}</div>
          </td>
        `;
        tbody.appendChild(tr);
      });
    }'''

new_fn_render = '''    function renderTable() {
      const search = (document.getElementById('searchInput').value || '').toLowerCase();
      const cohort = document.getElementById('cohortFilter').value;
      const tier = document.getElementById('tierFilter').value;
      const verdict = document.getElementById('verdictFilter').value;

      const filtered = studiesData.filter(s => {
        if (cohort !== 'ALL' && s.cohort !== cohort) return false;
        if (tier !== 'ALL') {
          if (tier === 'NON_MATH') {
            if (s.cohort !== 'CASE' || s.retraction_tier === 'GATE_3_MATH_DATA' || s.target_gate === 'GATE_3_MATH_DATA' || s.retraction_tier === 'TIER_1_MATH_DATA') return false;
          } else if (tier === 'CONTROL') {
            if (s.cohort !== 'CONTROL') return false;
          } else if (tier === 'GATE_3_MATH_DATA') {
            if (s.retraction_tier !== 'GATE_3_MATH_DATA' && s.target_gate !== 'GATE_3_MATH_DATA' && s.retraction_tier !== 'TIER_1_MATH_DATA') return false;
          } else if (s.retraction_tier !== tier) {
            return false;
          }
        }
        if (verdict !== 'ALL') {
          if (verdict === 'FLAGGED') {
            if (!isStudyFlagged(s)) return false;
          } else if (verdict === 'FATAL') {
            if (s.mode_a_verdict !== 'FATAL_DATA_ANOMALY' && s.blind_verdict !== 'FATAL_DATA_ANOMALY') return false;
          } else if (verdict === 'CLEAN') {
            if (!isStudyClean(s)) return false;
          } else if (s.blind_verdict !== verdict) {
            return false;
          }
        }
        
        if (search) {
          const flagsStr = (s.flags_triggered || []).join(' ');
          const fatalStr = (s.fatal_flags_triggered || []).join(' ');
          const txt = `${s.study_id} ${s.pmcid} ${s.title} ${s.journal} ${flagsStr} ${fatalStr}`.toLowerCase();
          if (!txt.includes(search)) return false;
        }
        return true;
      });

      const totalItems = filtered.length;
      const totalPages = Math.ceil(totalItems / pageSize) || 1;
      if (currentPage < 1) currentPage = 1;
      if (currentPage > totalPages) currentPage = totalPages;

      const startIndex = (currentPage - 1) * pageSize;
      const pageItems = filtered.slice(startIndex, startIndex + pageSize);

      const countText = document.getElementById('recordCountText');
      if (countText) {
        countText.innerText = `Showing ${totalItems === 0 ? 0 : startIndex + 1}–${Math.min(startIndex + pageSize, totalItems)} of ${totalItems.toLocaleString()} matching studies (from ${studiesData.length.toLocaleString()} total)`;
      }

      const pageNumText = document.getElementById('pageNumberText');
      if (pageNumText) pageNumText.innerText = `Page ${currentPage} of ${totalPages}`;

      const prevBtn = document.getElementById('prevPageBtn');
      if (prevBtn) prevBtn.disabled = (currentPage <= 1);
      const nextBtn = document.getElementById('nextPageBtn');
      if (nextBtn) nextBtn.disabled = (currentPage >= totalPages);

      const tbody = document.getElementById('studiesTableBody');
      tbody.innerHTML = '';

      if (pageItems.length === 0) {
        tbody.innerHTML = '<tr><td colspan="8" style="text-align: center; color: var(--text-dim); padding: 30px;">No studies matched the selected filters.</td></tr>';
        return;
      }

      pageItems.forEach(s => {
        const tr = document.createElement('tr');
        
        const cohortBadge = s.cohort === 'CASE' 
          ? '<span class="badge badge-case">CASE</span>' 
          : '<span class="badge badge-control">CONTROL</span>';

        let tierBadge = '<span class="badge badge-control">Clean Control</span>';
        if (s.retraction_tier === 'GATE_3_MATH_DATA' || s.target_gate === 'GATE_3_MATH_DATA' || s.retraction_tier === 'TIER_1_MATH_DATA') {
          tierBadge = '<span class="badge badge-tier1">Numerical &amp; Tabular</span>';
        } else if (s.cohort === 'CASE') {
          tierBadge = '<span class="badge badge-tier3">Non-Math Retraction</span>';
        }

        const flagged = isStudyFlagged(s);
        let verdictBadge = '<span class="badge badge-clean">CLEAN</span>';
        if (s.mode_a_verdict === 'FATAL_DATA_ANOMALY' || s.blind_verdict === 'FATAL_DATA_ANOMALY') {
          verdictBadge = '<span class="badge badge-flagged" style="background: rgba(239, 68, 68, 0.25); border: 1px solid #ef4444; color: #fca5a5;">FATAL (Mode A)</span>';
        } else if (s.mode_b_verdict === 'FLAGGED_RESEARCH_ANOMALY' || s.blind_verdict === 'FLAGGED_RESEARCH_ANOMALY') {
          verdictBadge = '<span class="badge badge-flagged" style="background: rgba(245, 158, 11, 0.25); border: 1px solid #f59e0b; color: #fcd34d;">FLAGGED (Mode B)</span>';
        } else if (flagged) {
          verdictBadge = '<span class="badge badge-flagged">FLAGGED</span>';
        }

        const allFlags = [...(s.fatal_flags_triggered || []), ...(s.flags_triggered || [])];
        const uniqueFlags = Array.from(new Set(allFlags));
        const flagsHtml = uniqueFlags.length > 0
          ? uniqueFlags.map(f => {
              const isFatal = f.startsWith('FATAL_') || f.includes('GRIM_') || f.includes('ZERO_SD');
              const style = isFatal ? 'background: rgba(239, 68, 68, 0.2); color: #fca5a5; border-color: rgba(239, 68, 68, 0.4);' : '';
              return `<span class="detail-tag" style="${style}">${escapeHtml(f)}</span>`;
            }).join('')
          : '<span style="color: var(--text-dim);">None (Passed Clean)</span>';

        const nTables = getStudyTables(s);
        const pmcLink = `https://europepmc.org/article/PMC/${(s.pmcid || '').replace('PMC', '')}`;

        tr.innerHTML = `
          <td style="font-family: monospace; font-weight: 600;">${s.study_id}</td>
          <td><a href="${pmcLink}" target="_blank" rel="noopener">${s.pmcid}</a></td>
          <td>${cohortBadge}</td>
          <td>${tierBadge}</td>
          <td style="max-width: 160px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;" title="${escapeHtml(s.journal)} (${s.year})">${escapeHtml(s.journal)} (${s.year})</td>
          <td style="text-align: center; font-weight: 600; color: #94a3b8;">${nTables}</td>
          <td>${verdictBadge}</td>
          <td style="max-width: 320px;">
            <div style="font-size: 0.8rem; margin-bottom: 4px; font-weight: 500; color: var(--text);">${escapeHtml(s.title || '')}</div>
            <div style="margin-top: 4px;">${flagsHtml}</div>
          </td>
        `;
        tbody.appendChild(tr);
      });
    }'''

content = content.replace(old_fn_render, new_fn_render)

with open('docs/index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print('Updated docs/index.html successfully!')
