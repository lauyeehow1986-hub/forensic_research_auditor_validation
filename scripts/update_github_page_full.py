import re

with open('docs/index.html', 'r', encoding='utf-8') as f:
    text = f.read()

# 1. Update Tab Navigation Buttons
old_tabs = '''    <!-- Tab Buttons -->
    <div class="tabs">
      <button class="tab-btn active" onclick="switchTab('blind-audit')">Blind 12,000-Study Full-Text Audit</button>
      <button class="tab-btn" onclick="switchTab('diagnostic-framework')">Clinical Reporting &amp; Editorial Matrix</button>
      <button class="tab-btn" onclick="switchTab('taxonomy')">4-Gate Forensic Architecture</button>
      <button class="tab-btn" onclick="switchTab('case-autopsy')">Case Autopsies &amp; Math</button>
      <button class="tab-btn" onclick="switchTab('axioms')">Mathematical Axioms &amp; Sieves</button>
      <button class="tab-btn" onclick="switchTab('reproduce')">FastMCP CLI &amp; Reproduction</button>
    </div>'''

new_tabs = '''    <!-- Tab Buttons -->
    <div class="tabs">
      <button class="tab-btn active" onclick="switchTab('blind-audit')">Blind 12,000-Study Full-Text Audit</button>
      <button class="tab-btn" onclick="switchTab('metascience-synthesis')">Metascience, Flaws &amp; Editor Guidelines</button>
      <button class="tab-btn" onclick="switchTab('diagnostic-framework')">Clinical Reporting &amp; Editorial Matrix</button>
      <button class="tab-btn" onclick="switchTab('taxonomy')">4-Gate Forensic Architecture</button>
      <button class="tab-btn" onclick="switchTab('case-autopsy')">Case Autopsies &amp; Math</button>
      <button class="tab-btn" onclick="switchTab('axioms')">Mathematical Axioms &amp; Sieves</button>
      <button class="tab-btn" onclick="switchTab('reproduce')">FastMCP CLI &amp; Reproduction</button>
    </div>'''

text = text.replace(old_tabs, new_tabs)

# 2. Update Header link for Metascience Synthesis
old_header_links = '''        <a href="#taxonomy" class="btn btn-secondary">
          5 Forensic Gates Architecture
        </a>'''

new_header_links = '''        <a href="#metascience-synthesis" class="btn btn-secondary" onclick="switchTab('metascience-synthesis')">
          Metascience &amp; Editor Guidelines
        </a>
        <a href="#taxonomy" class="btn btn-secondary">
          5 Forensic Gates Architecture
        </a>'''

text = text.replace(old_header_links, new_header_links)

# 3. Update static KPI description for Non-Math Cases in default HTML
text = text.replace(
    '2,562 / 3,138 Non-Data Cases Preserved Valid Math (82.4% authentic)',
    '3,364 / 4,031 Non-Data Cases Preserved Valid Math (83.5% authentic)'
)

# 4. Update Static Matrix Table Body for default pooled view (12,000 studies)
old_matrix_static = '''            <tr>
              <td>
                <span class="badge badge-tier1">Gate 3: Numerical &amp; Tabular Inconsistencies (N=1,862)</span><br>
                <small style="color: var(--text-dim);">Target condition: calculation errors, impossible means/SDs, and data integrity concerns</small>
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
            </tr>'''

new_matrix_static = '''            <tr>
              <td>
                <span class="badge badge-tier1">Gate 3: Numerical &amp; Tabular Inconsistencies (N=1,969)</span><br>
                <small style="color: var(--text-dim);">Target condition: calculation errors, impossible means/SDs, and data integrity concerns</small>
              </td>
              <td class="cell-highlight val-emerald">390 (True Positive)</td>
              <td style="color: var(--text-muted);">1,579 (False Negative)</td>
              <td><strong>Sensitivity: 19.81%</strong> [18.09% – 21.64%]<br><small style="color: #34d399;">80.81% on verifiable tables (Strict N verified)</small></td>
              <td><code>verify_grim_grimmer_debit</code>, <code>check_benford_second_digit</code></td>
            </tr>
            <tr>
              <td>
                <span class="badge badge-tier3">Non-Mathematical Retractions (N=4,031)</span><br>
                <small style="color: var(--text-dim);">Control retractions: fake peer review, authorship disputes, paper mills, figure tampering</small>
              </td>
              <td style="color: #f87171;">667 (Noise)</td>
              <td class="cell-highlight val-purple">3,364 (Passed Clean)</td>
              <td><strong>Specificity: 83.45%</strong> [82.27% – 84.57%]<br><small style="color: #c084fc;">Matches clean controls; authentic table math preserved</small></td>
              <td>Registry Provenance &amp; Cabanac PPS Lexicon</td>
            </tr>
            <tr>
              <td>
                <span class="badge badge-control">Clean Control Group (N=6,000)</span><br>
                <small style="color: var(--text-dim);">Peer-reviewed non-retracted articles from matching journals</small>
              </td>
              <td style="color: #f87171;">1,271 (False Positive)</td>
              <td class="cell-highlight val-blue">4,729 (True Negative)</td>
              <td><strong>Specificity: 78.82%</strong> [77.77% – 79.83%]<br><small style="color: #34d399;">Surpassed 85% in Wave 5 (86.00%) &amp; Wave 6 Mode A (96.60%)</small></td>
              <td>Consensus-gated FastMCP math engines</td>
            </tr>'''

text = text.replace(old_matrix_static, new_matrix_static)

# 5. Update Diagnostic Framework text
text = text.replace(
    '20.73% Global Pooled Sieve (10,000 Studies)',
    '19.81% Global Pooled Sieve (12,000 Studies)'
)
text = text.replace(
    '1,862 Data-Related Retraction Cases',
    '1,969 Data-Related Retraction Cases'
)
text = text.replace(
    '1,862 studies retracted specifically for data integrity concerns, calculation errors, or numerical inconsistencies across 7,390 extracted tables and 60,232 audited rows:',
    '1,969 studies retracted specifically for data integrity concerns, calculation errors, or numerical inconsistencies across 7,850 extracted tables and 64,800 audited rows:'
)
text = text.replace(
    '<span class="badge badge-tier2">All 1,862 Cases</span>',
    '<span class="badge badge-tier2">All 1,969 Cases</span>'
)
text = text.replace(
    'Catches <strong>386 / 1,862</strong> data-related retracted papers unassisted (95% Wilson CI: 18.95% – 22.63%).',
    'Catches <strong>390 / 1,969</strong> data-related retracted papers unassisted (19.81%; 95% Wilson CI: 18.09% – 21.64%).'
)

# 6. Update Taxonomy text
text = text.replace(
    'Coverage:</strong> 100% on cataloged retractions (5,000 / 5,000 cases).',
    'Coverage:</strong> 100% on cataloged retractions (6,000 / 6,000 cases).'
)
text = text.replace(
    'Sensitivity:</strong> 20.73% Global Pooled (386 / 1,862) &bull; 80.81% on Verifiable Tables (Strict N).',
    'Sensitivity:</strong> 19.81% Global Pooled (390 / 1,969) &bull; 80.81% on Verifiable Tables (Strict N verified).'
)
text = text.replace(
    'Math Specificity:</strong> 82.38% (1,758 / 2,134 clean pooled; 96.35% in Wave 5). Matches controls (p=0.31).',
    'Math Specificity:</strong> 82.35% (1,815 / 2,204 clean pooled; 92.86% in Wave 6 Mode A). Matches controls (p=0.31).'
)
text = text.replace(
    'Across 3,138 real publications retracted for non-mathematical misconduct (<em>authorship disputes</em>, <em>fake peer review</em>, <em>paper-mill text synthesis</em>, and <em>figure tampering</em>):',
    'Across 4,031 real publications retracted for non-mathematical misconduct (<em>authorship disputes</em>, <em>fake peer review</em>, <em>paper-mill text synthesis</em>, and <em>figure tampering</em>):'
)
text = text.replace(
    '81.64% Passed Math Cleanly (2,562 / 3,138):',
    '83.45% Passed Math Cleanly (3,364 / 4,031):'
)

# 7. Add the new Tab: metascience-synthesis right before diagnostic-framework tab
metascience_tab_html = '''    <!-- TAB: METASCIENCE SYNTHESIS, SUBMISSION FLAWS & EDITORIAL ROADMAP -->
    <div id="metascience-synthesis" class="tab-content">
      <div class="panel">
        <div class="panel-header">
          <div>
            <h2 class="panel-title">Metascience Synthesis: 6-Wave Evolutionary Dialectic &amp; Editorial Roadmap</h2>
            <p class="panel-subtitle">Evidence-based insights from auditing 12,000 studies (39,620 tables, 417,499 rows, and 9,078 figures) across six non-overlapping replication waves.</p>
          </div>
          <div>
            <span class="badge badge-tier1" style="font-size: 0.8rem; padding: 4px 10px;">12,000-Study Meta-Analysis</span>
          </div>
        </div>

        <!-- Section 1: The 6-Wave Evolutionary Dialectic -->
        <div style="margin-top: 16px; margin-bottom: 32px;">
          <h3 style="font-size: 1.15rem; color: #f1f5f9; display: flex; align-items: center; gap: 8px; margin-bottom: 8px;">
            <span style="display: inline-block; width: 8px; height: 8px; background: #38bdf8; border-radius: 50%; box-shadow: 0 0 8px #38bdf8;"></span>
            1. The 6-Wave Evolutionary Dialectic: Why Each Wave Failed and What It Taught Us
          </h3>
          <p style="font-size: 0.85rem; color: var(--text-muted); margin-bottom: 16px;">
            Developing an automated integrity auditor is not a linear optimization of sensitivity. Naive models fail catastrophically in real-world deployment due to alert fatigue. Each of our 2,000-study waves isolated a fundamental failure mode:
          </p>

          <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(320px, 1fr)); gap: 16px;">
            <div style="background: var(--bg-card); border: 1px solid var(--border); border-radius: 10px; padding: 18px;">
              <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                <strong style="color: #60a5fa; font-size: 0.95rem;">Wave 1 (Baseline Feasibility)</strong>
                <span class="badge" style="background: rgba(59, 130, 246, 0.15); color: #93c5fd; font-size: 0.72rem;">Sens: 25.00% | Spec: 80.10%</span>
              </div>
              <p style="font-size: 0.82rem; color: var(--text-muted); line-height: 1.5; margin-bottom: 8px;">
                <strong>Failure Mode:</strong> Subgroup sample sparsity (only 88 math retractions) yielded unstable confidence intervals. Naive Benford tests on narrow ranges (chemical yields 70%–95%, patient ages 45–65) caused false-positive digit clustering. Parsing un-typed percentages ($12\%$) as raw means triggered false GRIM failures.
              </p>
              <div style="font-size: 0.76rem; color: #34d399; border-top: 1px solid var(--border); padding-top: 6px;">
                &bull; <em>Lesson:</em> Tables must be pre-typed to distinguish discrete counts from continuous rates and percentages.
              </div>
            </div>

            <div style="background: var(--bg-card); border: 1px solid var(--border); border-radius: 10px; padding: 18px;">
              <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                <strong style="color: #f87171; font-size: 0.95rem;">Wave 2 (The Alert Fatigue Trap)</strong>
                <span class="badge" style="background: rgba(239, 68, 68, 0.15); color: #fca5a5; font-size: 0.72rem;">Sens: 29.03% | Spec: 70.20%</span>
              </div>
              <p style="font-size: 0.82rem; color: var(--text-muted); line-height: 1.5; margin-bottom: 8px;">
                <strong>Failure Mode:</strong> Spectrum bias and single-cell alert fatigue. A single rounded cell in an innocent 50-row Table 1 flagged the entire paper as fraudulent. A 29.8% false-alarm rate on clean peer-reviewed papers made the tool operationally unusable for editorial offices.
              </p>
              <div style="font-size: 0.76rem; color: #fca5a5; border-top: 1px solid var(--border); padding-top: 6px;">
                &bull; <em>Lesson:</em> Single-cell thresholds cannot be used to condemn manuscripts; editorial action requires multi-cell consensus.
              </div>
            </div>

            <div style="background: var(--bg-card); border: 1px solid var(--border); border-radius: 10px; padding: 18px;">
              <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                <strong style="color: #fb923c; font-size: 0.95rem;">Wave 3 (Over-Aggressive Upgrades)</strong>
                <span class="badge" style="background: rgba(251, 146, 60, 0.15); color: #fdba74; font-size: 0.72rem;">Sens: 31.01% | Spec: 68.20%</span>
              </div>
              <p style="font-size: 0.82rem; color: var(--text-muted); line-height: 1.5; margin-bottom: 8px;">
                <strong>Failure Mode:</strong> Over-aggressive screening crisis. Adding uncalibrated Cabanac tortured-phrase regexes and aggressive variance tests produced an intolerable 31.8% false-positive rate on clean controls. When 1 in 3 clean papers is flagged, editors dismiss all alerts.
              </p>
              <div style="font-size: 0.76rem; color: #fdba74; border-top: 1px solid var(--border); padding-top: 6px;">
                &bull; <em>Lesson:</em> Maximizing unassisted sensitivity degrades specificity below the operational safety threshold.
              </div>
            </div>

            <div style="background: var(--bg-card); border: 1px solid var(--border); border-radius: 10px; padding: 18px;">
              <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                <strong style="color: #facc15; font-size: 0.95rem;">Wave 4 (Consensus Calibration)</strong>
                <span class="badge" style="background: rgba(250, 204, 21, 0.15); color: #fef08a; font-size: 0.72rem;">Sens: 19.84% | Spec: 77.20%</span>
              </div>
              <p style="font-size: 0.82rem; color: var(--text-muted); line-height: 1.5; margin-bottom: 8px;">
                <strong>Discovery:</strong> Requiring multi-cell corroboration rebounded specificity to 77.20%, but exposed the "Excel Reality": formula-generated fabricated patient rows yield internally consistent summary averages that pass summary math.
              </p>
              <div style="font-size: 0.76rem; color: #fef08a; border-top: 1px solid var(--border); padding-top: 6px;">
                &bull; <em>Lesson:</em> Summary-level tables have a hard mathematical sensitivity ceiling; raw microdata is required.
              </div>
            </div>

            <div style="background: var(--bg-card); border: 1px solid var(--border); border-radius: 10px; padding: 18px;">
              <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                <strong style="color: #34d399; font-size: 0.95rem;">Wave 5 (Decadic Span Gating)</strong>
                <span class="badge" style="background: rgba(52, 211, 153, 0.15); color: #6ee7b7; font-size: 0.72rem;">Sens: 8.97% | Spec: 86.00%</span>
              </div>
              <p style="font-size: 0.82rem; color: var(--text-muted); line-height: 1.5; margin-bottom: 8px;">
                <strong>Breakthrough:</strong> Decadic dynamic range gating (&ge; 2.0 orders of magnitude for Benford) and Table 1 non-parametric filters pushed clean specificity to 86.00%, surpassing the target. Yet, a 14% FPR remained too noisy for desk rejections.
              </p>
              <div style="font-size: 0.76rem; color: #6ee7b7; border-top: 1px solid var(--border); padding-top: 6px;">
                &bull; <em>Lesson:</em> A single threshold cannot serve both accusation (desk reject) and triage (reviewer checklist).
              </div>
            </div>

            <div style="background: rgba(56, 189, 248, 0.08); border: 1px solid rgba(56, 189, 248, 0.35); border-radius: 10px; padding: 18px;">
              <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                <strong style="color: #38bdf8; font-size: 0.95rem;">Wave 6 (Mode A/B &amp; Vision Engine)</strong>
                <span class="badge" style="background: rgba(56, 189, 248, 0.2); color: #7dd3fc; font-size: 0.72rem;">Mode A Spec: 96.60% | 9,078 Figs</span>
              </div>
              <p style="font-size: 0.82rem; color: var(--text-muted); line-height: 1.5; margin-bottom: 8px;">
                <strong>Solution:</strong> Bifurcated screening into Mode A (Fatal Sieve; 96.60% specificity, FPR=3.4%, LR⁺ &gt; 50) and Mode B (Consensus Dragnet; 91.20% specificity). Audited 9,078 figures to prove figure-table decoupling across 823 image retractions.
              </p>
              <div style="font-size: 0.76rem; color: #38bdf8; border-top: 1px solid rgba(56, 189, 248, 0.3); padding-top: 6px;">
                &bull; <em>Outcome:</em> Immediate desk rejections become legally and scientifically defensible.
              </div>
            </div>
          </div>
        </div>

        <!-- Section 2: Inherent Boundary Conditions -->
        <div style="margin-top: 32px; margin-bottom: 32px; border-top: 1px solid var(--border); padding-top: 28px;">
          <h3 style="font-size: 1.15rem; color: #f1f5f9; display: flex; align-items: center; gap: 8px; margin-bottom: 8px;">
            <span style="display: inline-block; width: 8px; height: 8px; background: #ef4444; border-radius: 50%; box-shadow: 0 0 8px #ef4444;"></span>
            2. Inherent Forensic Boundary Conditions: What Automated Auditing Cannot Solve
          </h3>
          <p style="font-size: 0.85rem; color: var(--text-muted); margin-bottom: 16px;">
            Rigorous metascience requires defining what automated table and heuristic screening cannot do:
          </p>

          <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(260px, 1fr)); gap: 14px;">
            <div style="background: rgba(15, 23, 42, 0.6); padding: 16px; border-radius: 10px; border-left: 3px solid #ef4444;">
              <strong style="color: #fca5a5; font-size: 0.9rem;">1. Formula-Generated Rows (The "Excel Reality")</strong>
              <p style="font-size: 0.8rem; color: var(--text-muted); line-height: 1.5; margin-top: 6px; margin-bottom: 0;">
                When fraudulent authors generate 100 fake patient rows in Excel and calculate summary columns using <code>=AVERAGE()</code> and <code>=STDEV.S()</code>, the resulting published numbers satisfy mathematical laws. Summary-level tests cannot detect raw-row fabrication without row-level CSV microdata.
              </p>
            </div>

            <div style="background: rgba(15, 23, 42, 0.6); padding: 16px; border-radius: 10px; border-left: 3px solid #f59e0b;">
              <strong style="color: #fcd34d; font-size: 0.9rem;">2. Missing Sample Sizes (N) in Tables</strong>
              <p style="font-size: 0.8rem; color: var(--text-muted); line-height: 1.5; margin-top: 6px; margin-bottom: 0;">
                GRIM, GRIMMER, and DEBIT tests require an exact integer denominator $N$. When tables report percentages or odds ratios without column-level sample sizes, Mode A safely defaults to <code>PASS</code> to avoid guessing, resulting in false negatives.
              </p>
            </div>

            <div style="background: rgba(15, 23, 42, 0.6); padding: 16px; border-radius: 10px; border-left: 3px solid #8b5cf6;">
              <strong style="color: #c084fc; font-size: 0.9rem;">3. Continuous Assays Without Known Precision</strong>
              <p style="font-size: 0.8rem; color: var(--text-muted); line-height: 1.5; margin-top: 6px; margin-bottom: 0;">
                GRIM operates exclusively on discrete integer-scale variables (Likert scales 1–5, teeth counts, symptom checklists). Continuous biomarkers (blood glucose, ELISA optical densities) cannot be audited without knowing the instrument's analog-to-digital measurement step size.
              </p>
            </div>

            <div style="background: rgba(15, 23, 42, 0.6); padding: 16px; border-radius: 10px; border-left: 3px solid #ec4899;">
              <strong style="color: #f472b6; font-size: 0.9rem;">4. Procedural &amp; Ethical Misconduct</strong>
              <p style="font-size: 0.8rem; color: var(--text-muted); line-height: 1.5; margin-top: 6px; margin-bottom: 0;">
                Fake peer-review networks, paper-mill authorship brokerage, gift authorship, and forged IRB approval numbers leave zero trace in table arithmetic or image pixels; they are purely institutional governance violations.
              </p>
            </div>
          </div>
        </div>

        <!-- Section 3: Structural Submission Flaws -->
        <div style="margin-top: 32px; margin-bottom: 32px; border-top: 1px solid var(--border); padding-top: 28px;">
          <h3 style="font-size: 1.15rem; color: #f1f5f9; display: flex; align-items: center; gap: 8px; margin-bottom: 8px;">
            <span style="display: inline-block; width: 8px; height: 8px; background: #f59e0b; border-radius: 50%; box-shadow: 0 0 8px #f59e0b;"></span>
            3. The 5 Structural Flaws in Current Journal Submissions
          </h3>
          <p style="font-size: 0.85rem; color: var(--text-muted); margin-bottom: 16px;">
            Auditing 39,620 real published tables and 9,078 figures revealed that academic publishing suffers from preventable formatting flaws that cripple pre-publication verification:
          </p>

          <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 14px;">
            <div style="background: var(--bg-card); border: 1px solid var(--border); border-radius: 8px; padding: 14px;">
              <strong style="color: #fbbf24; font-size: 0.85rem;">1. Omission of Sample Size (N) in Headers:</strong>
              <p style="font-size: 0.78rem; color: var(--text-muted); line-height: 1.45; margin-top: 4px; margin-bottom: 0;">
                Authors publish demographic tables without specifying group sizes ($N$) in each column header, or state $N=30$ in the caption while pooling subgroups of unknown sizes in individual rows.
              </p>
            </div>

            <div style="background: var(--bg-card); border: 1px solid var(--border); border-radius: 8px; padding: 14px;">
              <strong style="color: #fbbf24; font-size: 0.85rem;">2. Percentages Reported Without Counts (n):</strong>
              <p style="font-size: 0.78rem; color: var(--text-muted); line-height: 1.45; margin-top: 4px; margin-bottom: 0;">
                Authors report figures such as "33.3%" without stating whether this corresponds to $1/3$, $33/100$, or $333/1,000$. This prevents binomial verification, DEBIT bounds checks, and cross-tabulation consistency audits.
              </p>
            </div>

            <div style="background: var(--bg-card); border: 1px solid var(--border); border-radius: 8px; padding: 14px;">
              <strong style="color: #fbbf24; font-size: 0.85rem;">3. Flattened Vector PDFs (Non-Semantic):</strong>
              <p style="font-size: 0.78rem; color: var(--text-muted); line-height: 1.45; margin-top: 4px; margin-bottom: 0;">
                Many journals still accept and publish tables as flattened PDF vectors or rasterized images rather than semantic, structured JATS XML tables with explicit cell attributes (<code>&lt;th&gt;</code>, <code>&lt;td&gt;</code>, data types).
              </p>
            </div>

            <div style="background: var(--bg-card); border: 1px solid var(--border); border-radius: 8px; padding: 14px;">
              <strong style="color: #fbbf24; font-size: 0.85rem;">4. Concealment of Line-Level Microdata:</strong>
              <p style="font-size: 0.78rem; color: var(--text-muted); line-height: 1.45; margin-top: 4px; margin-bottom: 0;">
                Journals routinely allow authors to submit only high-level summary tables without depositing raw row-level CSV/Parquet files, concealing spreadsheet calculation anomalies and copy-paste errors.
              </p>
            </div>

            <div style="background: var(--bg-card); border: 1px solid var(--border); border-radius: 8px; padding: 14px;">
              <strong style="color: #fbbf24; font-size: 0.85rem;">5. Lossy, Compressed Figure Files (JPEG/PNG):</strong>
              <p style="font-size: 0.78rem; color: var(--text-muted); line-height: 1.45; margin-top: 4px; margin-bottom: 0;">
                Authors submit compressed images where blot lanes and microscopy fields suffer from compression artifacts, destroying pixel metadata and making forensic verification ambiguous.
              </p>
            </div>
          </div>
        </div>

        <!-- Section 4: Actionable Recommendations for Journal Editors -->
        <div style="margin-top: 32px; margin-bottom: 16px; border-top: 1px solid var(--border); padding-top: 28px;">
          <h3 style="font-size: 1.15rem; color: #f1f5f9; display: flex; align-items: center; gap: 8px; margin-bottom: 8px;">
            <span style="display: inline-block; width: 8px; height: 8px; background: #10b981; border-radius: 50%; box-shadow: 0 0 8px #10b981;"></span>
            4. Actionable Recommendations for Journal Editors &amp; Publishers
          </h3>
          <p style="font-size: 0.85rem; color: var(--text-muted); margin-bottom: 16px;">
            To eliminate editorial bottlenecks, protect innocent authors from defamation, and accelerate reproducible science, journals should adopt this evidence-based workflow:
          </p>

          <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 14px;">
            <div style="background: var(--bg-card); border: 1px solid rgba(16, 185, 129, 0.3); border-radius: 10px; padding: 16px;">
              <strong style="color: #34d399; font-size: 0.9rem;">Recommendation 1: Enforce Structured JATS XML Tables</strong>
              <p style="font-size: 0.78rem; color: var(--text-muted); line-height: 1.5; margin-top: 6px; margin-bottom: 0;">
                <strong>Submission Requirement:</strong> Reject submissions that embed tables as images or vector PDFs. Mandate explicit column sample sizes (e.g. <code>Control (N=45)</code>) and format all percentages as <code>n (col%)</code> (e.g. <code>15 (33.3%)</code>). This enables instantaneous deterministic verification.
              </p>
            </div>

            <div style="background: var(--bg-card); border: 1px solid rgba(59, 130, 246, 0.3); border-radius: 10px; padding: 16px;">
              <strong style="color: #60a5fa; font-size: 0.9rem;">Recommendation 2: Mandate De-Identified Line-Level Microdata</strong>
              <p style="font-size: 0.78rem; color: var(--text-muted); line-height: 1.5; margin-top: 6px; margin-bottom: 0;">
                <strong>Bypassing the "Excel Reality":</strong> Summary tables alone cannot detect formula-generated synthetic patient cohorts. Requiring anonymized raw patient/sample microdata in <code>.csv</code> or <code>.parquet</code> format allows automated Carlisle ANOVA and covariance sieves to audit row-level validity in &lt; 1 second.
              </p>
            </div>

            <div style="background: var(--bg-card); border: 1px solid rgba(245, 158, 11, 0.3); border-radius: 10px; padding: 16px;">
              <strong style="color: #fbbf24; font-size: 0.9rem;">Recommendation 3: Integrate Dual-Mode Automated Editorial Sieve</strong>
              <p style="font-size: 0.78rem; color: var(--text-muted); line-height: 1.5; margin-top: 6px; margin-bottom: 0;">
                <strong>Editorial Manager / ScholarOne Hook:</strong> Run <strong>Mode A (Fatal Sieve)</strong> on manuscript upload. If double GRIM failure or continuous SD=0 triggers (LR⁺ &gt; 50), issue an immediate <em>Editorial Desk Hold</em> before assigning reviewers. Run <strong>Mode B</strong> to generate a standardized checklist for peer reviewers.
              </p>
            </div>

            <div style="background: var(--bg-card); border: 1px solid rgba(168, 85, 247, 0.3); border-radius: 10px; padding: 16px;">
              <strong style="color: #c084fc; font-size: 0.9rem;">Recommendation 4: Mandate Full-Resolution Instrument TIFFs</strong>
              <p style="font-size: 0.78rem; color: var(--text-muted); line-height: 1.5; margin-top: 6px; margin-bottom: 0;">
                <strong>Uncompressed Blot Deposition:</strong> Spliced gel lanes and microscopy cloning operate in the pixel domain. Mandate deposition of uncropped, unadjusted original camera/instrument TIFF files in public repositories (Zenodo/Dryad) with intact EXIF acquisition metadata.
              </p>
            </div>

            <div style="background: var(--bg-card); border: 1px solid rgba(244, 63, 94, 0.3); border-radius: 10px; padding: 16px;">
              <strong style="color: #fb7185; font-size: 0.9rem;">Recommendation 5: Decouple Figure and Table Review Pipelines</strong>
              <p style="font-size: 0.78rem; color: var(--text-muted); line-height: 1.5; margin-top: 6px; margin-bottom: 0;">
                <strong>Independent Specialist Routing:</strong> With Wave 6 confirming that 92.4% of image retractions preserve valid table math, editors must route figures through perceptual hash vector databases and tables through deterministic math engines, recognizing they represent independent risk domains.
              </p>
            </div>
          </div>
        </div>

      </div>
    </div>
'''

# Insert the new tab before diagnostic-framework tab
text = text.replace('    <!-- TAB: CLINICAL REPORTING & EDITORIAL DECISION MATRIX -->', metascience_tab_html + '\n    <!-- TAB: CLINICAL REPORTING & EDITORIAL DECISION MATRIX -->')

with open('docs/index.html', 'w', encoding='utf-8') as f:
    f.write(text)

print('Updated docs/index.html successfully with dedicated metascience tab and pooled numbers!')
