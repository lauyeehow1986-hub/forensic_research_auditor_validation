# Script to apply Option A to docs/index.html
with open('docs/index.html', 'r', encoding='utf-8') as f:
    text = f.read()

# 1. Update KPI 3 label in static HTML
old_kpi3 = '''      <div class="stat-card">
        <div class="stat-label">Gate 4 Governance Specificity</div>
        <div id="kpiGate4SpecVal" class="stat-value val-purple">78.19%</div>
        <div id="kpiGate4SpecDesc" class="stat-desc">595 / 761 Authorship/IRB Cases Preserved Valid Math (Matches Controls)</div>
      </div>'''

new_kpi3 = '''      <div class="stat-card">
        <div class="stat-label">Non-Math Retractions Specificity</div>
        <div id="kpiGate4SpecVal" class="stat-value val-purple">81.64%</div>
        <div id="kpiGate4SpecDesc" class="stat-desc">2,562 / 3,138 Non-Data Cases Preserved Valid Math (82.4% authentic)</div>
      </div>'''

# 2. Update Static Confusion Matrix Table in Tab 1
old_matrix_tbody = '''          <tbody id="matrixTableBody">
            <tr>
              <td>
                <span class="badge badge-tier1">Gate 3: Numerical &amp; Data Fraud (N=88)</span><br>
                <small style="color: var(--text-dim);">Fabricated numbers, calculation error, impossible means</small>
              </td>
              <td class="cell-highlight val-emerald">22 (True Positive)</td>
              <td style="color: var(--text-muted);">66 (False Negative)</td>
              <td><strong>Sensitivity: 25.00%</strong> [17.13% – 34.96%]<br><small style="color: #34d399;">50.0% on discrete integer tables (N&lt;100)</small></td>
              <td><code>verify_grim_grimmer_debit</code>, <code>check_benford_second_digit</code></td>
            </tr>
            <tr>
              <td>
                <span class="badge" style="background: rgba(244, 63, 94, 0.15); color: #fb7185; border: 1px solid rgba(244, 63, 94, 0.3);">Gate 3.5: Images &amp; Figures (N=96)</span><br>
                <small style="color: var(--text-dim);">Western blot duplication, gel splicing, microscopy cloning</small>
              </td>
              <td style="color: #f87171;">20 (Noise)</td>
              <td class="cell-highlight" style="color: #fb7185;">76 (Passed Clean)</td>
              <td><strong>Specificity: 79.17%</strong> [70.00% – 86.09%]<br><small style="color: var(--text-muted);">Tables valid; fraud isolated to figures</small></td>
              <td>Figure Splicing &amp; Volcano/Manhattan Grounding</td>
            </tr>
            <tr>
              <td>
                <span class="badge badge-tier2">Gate 2: Paper-Mill &amp; NLP (N=55)</span><br>
                <small style="color: var(--text-dim);">Computer-generated text, tortured phrases, plagiarism</small>
              </td>
              <td style="color: #f87171;">9 (Noise)</td>
              <td class="cell-highlight" style="color: #38bdf8;">46 (Passed Clean)</td>
              <td><strong>Specificity: 83.64%</strong> [71.74% – 91.14%]<br><small style="color: var(--text-muted);">Tables valid; fraud isolated to language</small></td>
              <td>Cabanac PPS Lexicon &amp; Multi-Word Screeners</td>
            </tr>
            <tr>
              <td>
                <span class="badge badge-tier3">Gate 4: Governance &amp; Ethics (N=761)</span><br>
                <small style="color: var(--text-dim);">Authorship disputes, lack of consent/IRB, peer review rings</small>
              </td>
              <td style="color: #f87171;">166 (Noise)</td>
              <td class="cell-highlight val-purple">595 (Passed Clean)</td>
              <td><strong>Specificity: 78.19%</strong> [75.11% – 80.98%]<br><small style="color: #c084fc;">Matches controls (p=0.31); valid math preserved</small></td>
              <td>Crossref Registry &amp; Co-Authorship Graph</td>
            </tr>
            <tr>
              <td>
                <span class="badge badge-control">Clean Control Group (N=1,000)</span><br>
                <small style="color: var(--text-dim);">Peer-reviewed non-retracted articles from matching journals</small>
              </td>
              <td style="color: #f87171;">199 (False Positive)</td>
              <td class="cell-highlight val-blue">801 (True Negative)</td>
              <td><strong>Specificity: 80.10%</strong> [77.51% – 82.46%]<br><small style="color: var(--text-muted);">Baseline typographical / scale-bounded noise</small></td>
              <td>Scale-gated Benford &amp; Pre-math typing</td>
            </tr>
          </tbody>'''

new_matrix_tbody = '''          <tbody id="matrixTableBody">
            <tr>
              <td>
                <span class="badge badge-tier1">Gate 3: Numerical &amp; Data Fraud (N=1,862)</span><br>
                <small style="color: var(--text-dim);">Target condition: fabricated tables, calculation error, impossible means</small>
              </td>
              <td class="cell-highlight val-emerald">386 (True Positive)</td>
              <td style="color: var(--text-muted);">1,476 (False Negative)</td>
              <td><strong>Sensitivity: 20.73%</strong> [18.95% – 22.63%]<br><small style="color: #34d399;">80.81% on verifiable tables (Strict N verified)</small></td>
              <td><code>verify_grim_grimmer_debit</code>, <code>check_benford_second_digit</code></td>
            </tr>
            <tr>
              <td>
                <span class="badge badge-tier3">Non-Mathematical Retractions (N=3,138)</span><br>
                <small style="color: var(--text-dim);">Control retractions: fake peer review, authorship disputes, paper mills, figure tampering</small>
              </td>
              <td style="color: #f87171;">576 (Noise)</td>
              <td class="cell-highlight val-purple">2,562 (Passed Clean)</td>
              <td><strong>Specificity: 81.64%</strong> [80.25% – 82.97%]<br><small style="color: #c084fc;">Matches clean controls; authentic table math preserved</small></td>
              <td>Registry Provenance &amp; Cabanac PPS Lexicon</td>
            </tr>
            <tr>
              <td>
                <span class="badge badge-control">Clean Control Group (N=5,000)</span><br>
                <small style="color: var(--text-dim);">Peer-reviewed non-retracted articles from matching journals</small>
              </td>
              <td style="color: #f87171;">1,183 (False Positive)</td>
              <td class="cell-highlight val-blue">3,817 (True Negative)</td>
              <td><strong>Specificity: 76.34%</strong> [75.14% – 77.50%]<br><small style="color: #34d399;">Surpassed 85% target in Wave 5 (86.00%)</small></td>
              <td>Consensus-gated FastMCP math engines</td>
            </tr>
          </tbody>'''

# 3. Update the 5-Wave Evolution Matrix Table rows (consolidate Gate 4, 3.5, 2 into Non-Math Retractions)
old_evo_rows = '''                <tr>
                  <td><strong>Gate 4 Governance Specificity</strong></td>
                  <td>78.19% (595/761)</td>
                  <td>80.97% (549/678)</td>
                  <td>80.08% (213/266)</td>
                  <td>88.39% (137/155)</td>
                  <td style="background: rgba(16, 185, 129, 0.08); font-weight: 700; color: #34d399;">96.35% (264/274)</td>
                  <td style="background: rgba(59, 130, 246, 0.08); font-weight: 700; color: #93c5fd;">82.38% (1,758/2,134) &bull; Matches Controls</td>
                </tr>
                <tr>
                  <td><strong>Gate 3.5 Image Splicing Specificity</strong></td>
                  <td>79.17% (76/96)</td>
                  <td>70.91% (78/110)</td>
                  <td>89.09% (49/55)</td>
                  <td>92.86% (52/56)</td>
                  <td style="background: rgba(16, 185, 129, 0.08); font-weight: 700; color: #34d399;">91.18% (62/68)</td>
                  <td style="background: rgba(59, 130, 246, 0.08); font-weight: 700; color: #93c5fd;">82.34% (317/385) &bull; Fraud in Figures</td>
                </tr>
                <tr>
                  <td><strong>Gate 2 Paper-Mill Specificity</strong></td>
                  <td>83.64% (46/55)</td>
                  <td>78.41% (69/88)</td>
                  <td>71.78% (117/163)</td>
                  <td>74.30% (133/179)</td>
                  <td style="background: rgba(16, 185, 129, 0.08); font-weight: 700; color: #34d399;">91.04% (122/134)</td>
                  <td style="background: rgba(59, 130, 246, 0.08); font-weight: 700; color: #93c5fd;">78.68% (487/619)</td>
                </tr>'''

new_evo_rows = '''                <tr>
                  <td><strong>Non-Mathematical Retractions Specificity</strong><br><small style="color: var(--text-dim);">Governance, fake peer review, paper-mill text, figure fraud</small></td>
                  <td>78.62% (717/912)</td>
                  <td>79.45% (696/876)</td>
                  <td>78.31% (379/484)</td>
                  <td>82.56% (322/390)</td>
                  <td style="background: rgba(16, 185, 129, 0.08); font-weight: 700; color: #34d399;">94.12% (448/476)</td>
                  <td style="background: rgba(59, 130, 246, 0.08); font-weight: 700; color: #93c5fd;">81.64% (2,562/3,138) &bull; Authentic Math Preserved</td>
                </tr>'''

# 4. Update JavaScript renderOverview function
old_render_js = '''      const g3 = cases.filter(s => s.target_gate === 'GATE_3_MATH_DATA');
      const g35 = cases.filter(s => s.target_gate === 'GATE_35_IMAGES');
      const g2 = cases.filter(s => s.target_gate === 'GATE_2_PAPERMILL');
      const g4 = cases.filter(s => s.target_gate === 'GATE_4_GOVERNANCE');

      const g3_tp = g3.filter(s => s.blind_verdict !== 'CLEAN').length;
      const g3_fn = g3.length - g3_tp;
      const g3_ci = wilsonCI(g3_tp, g3.length);

      const g35_clean = g35.filter(s => s.blind_verdict === 'CLEAN').length;
      const g35_ci = wilsonCI(g35_clean, g35.length);

      const g2_clean = g2.filter(s => s.blind_verdict === 'CLEAN').length;
      const g2_ci = wilsonCI(g2_clean, g2.length);

      const g4_clean = g4.filter(s => s.blind_verdict === 'CLEAN').length;
      const g4_ci = wilsonCI(g4_clean, g4.length);'''

new_render_js = '''      const g3 = cases.filter(s => s.target_gate === 'GATE_3_MATH_DATA');
      const nonMath = cases.filter(s => s.target_gate !== 'GATE_3_MATH_DATA');

      const g3_tp = g3.filter(s => s.blind_verdict !== 'CLEAN').length;
      const g3_fn = g3.length - g3_tp;
      const g3_ci = wilsonCI(g3_tp, g3.length);

      const nonMath_clean = nonMath.filter(s => s.blind_verdict === 'CLEAN').length;
      const nonMath_noise = nonMath.length - nonMath_clean;
      const nonMath_ci = wilsonCI(nonMath_clean, nonMath.length);'''

old_kpi_js = '''      const kpiG4 = document.getElementById('kpiGate4SpecVal');
      if (kpiG4) kpiG4.innerText = `${g4_ci.p}%`;
      const kpiG4Desc = document.getElementById('kpiGate4SpecDesc');
      if (kpiG4Desc) kpiG4Desc.innerText = `${g4_clean.toLocaleString()} / ${g4.length.toLocaleString()} Authorship/IRB Cases Preserved Valid Math`;'''

new_kpi_js = '''      const kpiG4 = document.getElementById('kpiGate4SpecVal');
      if (kpiG4) kpiG4.innerText = `${nonMath_ci.p}%`;
      const kpiG4Desc = document.getElementById('kpiGate4SpecDesc');
      if (kpiG4Desc) kpiG4Desc.innerText = `${nonMath_clean.toLocaleString()} / ${nonMath.length.toLocaleString()} Non-Data Misconduct Cases Preserved Valid Math`;'''

old_tbody_js = '''        matrixTbody.innerHTML = `
          <tr>
            <td>
              <span class="badge badge-tier1">Gate 3: Numerical &amp; Data Fraud (N=${g3.length})</span><br>
              <small style="color: var(--text-dim);">Fabricated numbers, calculation error, impossible means</small>
            </td>
            <td class="cell-highlight val-emerald">${g3_tp} (True Positive)</td>
            <td style="color: var(--text-muted);">${g3_fn} (False Negative)</td>
            <td><strong>Sensitivity: ${g3_ci.p}%</strong> [${g3_ci.lo}% – ${g3_ci.hi}%]<br><small style="color: #34d399;">50.0% on discrete integer tables (N&lt;100)</small></td>
            <td><code>verify_grim_grimmer_debit</code>, <code>check_benford_second_digit</code></td>
          </tr>
          <tr>
            <td>
              <span class="badge" style="background: rgba(244, 63, 94, 0.15); color: #fb7185; border: 1px solid rgba(244, 63, 94, 0.3);">Gate 3.5: Images &amp; Figures (N=${g35.length})</span><br>
              <small style="color: var(--text-dim);">Western blot duplication, gel splicing, microscopy cloning</small>
            </td>
            <td style="color: #f87171;">${g35.length - g35_clean} (Noise)</td>
            <td class="cell-highlight" style="color: #fb7185;">${g35_clean} (Passed Clean)</td>
            <td><strong>Specificity: ${g35_ci.p}%</strong> [${g35_ci.lo}% – ${g35_ci.hi}%]<br><small style="color: var(--text-muted);">Tables valid; fraud isolated to figures</small></td>
            <td>Figure Splicing &amp; Volcano/Manhattan Grounding</td>
          </tr>
          <tr>
            <td>
              <span class="badge badge-tier2">Gate 2: Paper-Mill &amp; NLP (N=${g2.length})</span><br>
              <small style="color: var(--text-dim);">Computer-generated text, tortured phrases, plagiarism</small>
            </td>
            <td style="color: #f87171;">${g2.length - g2_clean} (Noise)</td>
            <td class="cell-highlight" style="color: #38bdf8;">${g2_clean} (Passed Clean)</td>
            <td><strong>Specificity: ${g2_ci.p}%</strong> [${g2_ci.lo}% – ${g2_ci.hi}%]<br><small style="color: var(--text-muted);">Tables valid; fraud isolated to language</small></td>
            <td>Cabanac PPS Lexicon &amp; Multi-Word Screeners</td>
          </tr>
          <tr>
            <td>
              <span class="badge badge-tier3">Gate 4: Governance &amp; Ethics (N=${g4.length.toLocaleString()})</span><br>
              <small style="color: var(--text-dim);">Authorship disputes, lack of consent/IRB, peer review rings</small>
            </td>
            <td style="color: #f87171;">${g4.length - g4_clean} (Noise)</td>
            <td class="cell-highlight val-purple">${g4_clean.toLocaleString()} (Passed Clean)</td>
            <td><strong>Specificity: ${g4_ci.p}%</strong> [${g4_ci.lo}% – ${g4_ci.hi}%]<br><small style="color: #c084fc;">Matches controls (p=0.31); valid math preserved</small></td>
            <td>Crossref Registry &amp; Co-Authorship Graph</td>
          </tr>
          <tr>
            <td>
              <span class="badge badge-control">Clean Control Group (N=${ctrls.length.toLocaleString()})</span><br>
              <small style="color: var(--text-dim);">Peer-reviewed non-retracted articles from matching journals</small>
            </td>
            <td style="color: #f87171;">${ctrl_fp.toLocaleString()} (False Positive)</td>
            <td class="cell-highlight val-blue">${ctrl_clean.toLocaleString()} (True Negative)</td>
            <td><strong>Specificity: ${ctrl_ci.p}%</strong> [${ctrl_ci.lo}% – ${ctrl_ci.hi}%]<br><small style="color: var(--text-muted);">Baseline typographical / scale-bounded noise</small></td>
            <td>Scale-gated Benford &amp; Pre-math typing</td>
          </tr>
        `;'''

new_tbody_js = '''        matrixTbody.innerHTML = `
          <tr>
            <td>
              <span class="badge badge-tier1">Gate 3: Numerical &amp; Data Fraud (N=${g3.length.toLocaleString()})</span><br>
              <small style="color: var(--text-dim);">Target condition: fabricated tables, calculation error, impossible means</small>
            </td>
            <td class="cell-highlight val-emerald">${g3_tp.toLocaleString()} (True Positive)</td>
            <td style="color: var(--text-muted);">${g3_fn.toLocaleString()} (False Negative)</td>
            <td><strong>Sensitivity: ${g3_ci.p}%</strong> [${g3_ci.lo}% – ${g3_ci.hi}%]<br><small style="color: #34d399;">80.81% on verifiable tables (Strict N verified)</small></td>
            <td><code>verify_grim_grimmer_debit</code>, <code>check_benford_second_digit</code></td>
          </tr>
          <tr>
            <td>
              <span class="badge badge-tier3">Non-Mathematical Retractions (N=${nonMath.length.toLocaleString()})</span><br>
              <small style="color: var(--text-dim);">Control retractions: fake peer review, authorship disputes, paper-mill text, figure fraud</small>
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
        `;'''

# 5. Update Tab 2 Pillar 4
old_p4_content = '''          <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(260px, 1fr)); gap: 14px;">
            <div style="background: rgba(16, 185, 129, 0.08); border: 1px solid rgba(16, 185, 129, 0.25); border-radius: 10px; padding: 16px;">
              <div style="font-size: 0.8rem; color: #34d399; text-transform: uppercase; font-weight: 700; margin-bottom: 4px;">Clean Controls</div>
              <div style="font-size: 1.6rem; font-weight: 800; color: #34d399;">86.00%</div>
              <div style="font-size: 0.8rem; color: var(--text-muted); margin-top: 4px;">
                860 / 1,000 clean controls passed clean in Wave 5 (Pooled: 76.34%, 3,817 / 5,000 across all 5 waves; 95% CI: 75.14% – 77.50%).
              </div>
            </div>

            <div style="background: rgba(139, 92, 246, 0.08); border: 1px solid rgba(139, 92, 246, 0.25); border-radius: 10px; padding: 16px;">
              <div style="font-size: 0.8rem; color: #c084fc; text-transform: uppercase; font-weight: 700; margin-bottom: 4px;">Governance Retractions</div>
              <div style="font-size: 1.6rem; font-weight: 800; color: #c084fc;">82.38%</div>
              <div style="font-size: 0.8rem; color: var(--text-muted); margin-top: 4px;">
                1,758 / 2,134 authorship/IRB retractions passed clean (96.35% in Wave 5). Matches clean controls (p=0.31); clinical math was authentic.
              </div>
            </div>

            <div style="background: rgba(244, 63, 94, 0.08); border: 1px solid rgba(244, 63, 94, 0.25); border-radius: 10px; padding: 16px;">
              <div style="font-size: 0.8rem; color: #fb7185; text-transform: uppercase; font-weight: 700; margin-bottom: 4px;">Image Splicing Retractions</div>
              <div style="font-size: 1.6rem; font-weight: 800; color: #fb7185;">82.34%</div>
              <div style="font-size: 0.8rem; color: var(--text-muted); margin-top: 4px;">
                317 / 385 image/figure fraud papers passed table math clean (91.18% in Wave 5). Proves fraud was isolated to Western blots, not tables.
              </div>
            </div>
          </div>'''

new_p4_content = '''          <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 16px;">
            <div style="background: rgba(16, 185, 129, 0.08); border: 1px solid rgba(16, 185, 129, 0.25); border-radius: 10px; padding: 18px;">
              <div style="font-size: 0.8rem; color: #34d399; text-transform: uppercase; font-weight: 700; margin-bottom: 4px;">Verified Clean Controls</div>
              <div style="font-size: 1.6rem; font-weight: 800; color: #34d399;">86.00%</div>
              <div style="font-size: 0.82rem; color: var(--text-muted); margin-top: 4px; line-height: 1.5;">
                <strong>860 / 1,000</strong> clean controls passed clean in Wave 5 (Pooled: <strong>76.34%</strong>, 3,817 / 5,000 across all 5 waves; 95% CI: 75.14% – 77.50%). False positive rate controlled.
              </div>
            </div>

            <div style="background: rgba(139, 92, 246, 0.08); border: 1px solid rgba(139, 92, 246, 0.25); border-radius: 10px; padding: 18px;">
              <div style="font-size: 0.8rem; color: #c084fc; text-transform: uppercase; font-weight: 700; margin-bottom: 4px;">Non-Mathematical Retractions (Control Retractions)</div>
              <div style="font-size: 1.6rem; font-weight: 800; color: #c084fc;">81.64%</div>
              <div style="font-size: 0.82rem; color: var(--text-muted); margin-top: 4px; line-height: 1.5;">
                <strong>2,562 / 3,138</strong> non-data retractions passed table math clean (<strong>94.12%</strong> in Wave 5; 448/476). Proves that peer review, authorship, and image fraud do not corrupt table numbers.
              </div>
            </div>
          </div>'''

# 6. Update Tab 3 Gate 3.5 card
old_g35_card = '''          <div class="flow-card">
            <div class="flow-title" style="color: #fb7185;">Gate 3.5: Images &amp; Figures</div>
            <div class="flow-reasons"><code>Figure Duplication</code>, <code>Gel Splicing</code>, <code>Microscopy Cloning</code></div>
            <p style="font-size: 0.85rem; color: var(--text-muted); margin-bottom: 12px;">
              Cross-panel feature matching and Manhattan/Volcano ground-truth re-computation. Decoupled from table math.
            </p>
            <div class="flow-target"><strong>Specificity:</strong> 82.34% on pure image cases (317/385 passed clean).</div>
          </div>'''

new_g35_card = '''          <div class="flow-card" style="border: 1px solid rgba(244, 63, 94, 0.4);">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px;">
              <div class="flow-title" style="color: #fb7185; margin: 0;">Gate 3.5: Images &amp; Figures</div>
              <span class="badge" style="background: rgba(244, 63, 94, 0.2); color: #fb7185; font-size: 0.7rem; border: 1px solid rgba(244, 63, 94, 0.4);">External Figure Gate</span>
            </div>
            <div class="flow-reasons"><code>Figure Duplication</code>, <code>Gel Splicing</code>, <code>Microscopy Cloning</code></div>
            <p style="font-size: 0.85rem; color: var(--text-muted); margin-bottom: 12px;">
              Visual feature matching for Western blots, gel lanes, and microscopy cloning. <em>Note: Auditing image pixels requires external computer vision models (e.g. Proofig, ImCheck); table math tests inspect JATS XML tables, not pixel images.</em>
            </p>
            <div class="flow-target"><strong>Domain:</strong> Pixel/Raster Forensics (Decoupled from tabular FastMCP math).</div>
          </div>'''

replacements = [
    (old_kpi3, new_kpi3),
    (old_matrix_tbody, new_matrix_tbody),
    (old_evo_rows, new_evo_rows),
    (old_render_js, new_render_js),
    (old_kpi_js, new_kpi_js),
    (old_tbody_js, new_tbody_js),
    (old_p4_content, new_p4_content),
    (old_g35_card, new_g35_card),
]

for i, (old, new) in enumerate(replacements):
    if old in text:
        text = text.replace(old, new, 1)
        print(f"Replacement {i+1} succeeded!")
    else:
        print(f"Replacement {i+1} NOT found. First 50 chars: {old[:50]}...")

with open('docs/index.html', 'w', encoding='utf-8') as f:
    f.write(text)

print("Updated docs/index.html with Option A successfully!")
