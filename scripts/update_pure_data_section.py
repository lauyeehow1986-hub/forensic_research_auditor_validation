# Script to update docs/index.html with the Pure Data & Tabular Fraud Deep-Dive section
with open('docs/index.html', 'r', encoding='utf-8') as f:
    text = f.read()

old_p2_section = '''        <!-- Pillar 2: Denominator-Conditioned Sensitivity -->
        <div style="margin-top: 32px; margin-bottom: 32px;">
          <h3 style="font-size: 1.15rem; color: #f1f5f9; display: flex; align-items: center; gap: 8px; margin-bottom: 8px;">
            <span style="display: inline-block; width: 8px; height: 8px; background: #10b981; border-radius: 50%; box-shadow: 0 0 8px #10b981;"></span>
            Pillar 2: Denominator-Conditioned Sensitivity (The "Excel Reality")
          </h3>
          <p style="font-size: 0.85rem; color: var(--text-muted); margin-bottom: 14px;">
            A common misconception in forensic AI is that summary-table math should catch 100% of data fraud. In reality, detection rates depend strictly on whether the underlying variable is testable.
          </p>

          <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(320px, 1fr)); gap: 16px;">
            <div style="background: var(--bg-card); border: 1px solid var(--border); border-radius: 10px; padding: 18px;">
              <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                <h4 style="color: var(--cyan); font-size: 0.95rem;">A. Global Case Sensitivity (20.73%)</h4>
                <span class="badge badge-tier2">All 1,862 Math Cases</span>
              </div>
              <p style="font-size: 0.85rem; color: var(--text-muted); line-height: 1.55; margin-bottom: 10px;">
                Across all retracted papers with confirmed numerical fraud in the pooled 10,000-study benchmark, FastMCP table math catches <strong>20.73%</strong> (386 / 1,862, 95% Wilson CI: 18.95% – 22.63%).
              </p>
              <div style="background: rgba(15, 23, 42, 0.6); border-left: 3px solid var(--cyan); padding: 10px; font-size: 0.8rem; color: var(--text-dim); line-height: 1.5;">
                <strong>The Spreadsheet Reality:</strong> When fraudsters synthesize fake patient rows in Excel and calculate <code>=AVERAGE()</code> and <code>=STDEV()</code>, the resulting summary numbers are mathematically self-consistent. Mathematical sieves cannot catch synthesized raw tables without access to raw data.
              </div>
            </div>

            <div style="background: var(--bg-card); border: 1px solid var(--border); border-radius: 10px; padding: 18px;">
              <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                <h4 style="color: #34d399; font-size: 0.95rem;">B. Discrete Applicable Sensitivity (50.00%)</h4>
                <span class="badge badge-clean">Discrete Scales (N &lt; 100)</span>
              </div>
              <p style="font-size: 0.85rem; color: var(--text-muted); line-height: 1.55; margin-bottom: 10px;">
                When evaluating the subset of papers that report <strong>discrete integer scales</strong> (Likert scores, symptom counts, teeth, integer survey items) with sample size N &lt; 100, the detection rate jumps to <strong>50.00%</strong> (10 / 20).
              </p>
              <div style="background: rgba(15, 23, 42, 0.6); border-left: 3px solid #10b981; padding: 10px; font-size: 0.8rem; color: var(--text-dim); line-height: 1.5;">
                <strong>Granularity Constraints:</strong> In discrete scales, fraudsters making manual adjustments or typing invented averages frequently violate integer modular granularity (e.g. <code>Mean = 3.42</code> across <code>N = 17</code> requires non-integer total score).
              </div>
            </div>
          </div>
        </div>'''

new_p2_section = '''        <!-- Pillar 2: Pure Data & Tabular Fraud Deep-Dive (Gate 3 Sub-Cohort) -->
        <div style="margin-top: 32px; margin-bottom: 32px;">
          <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 8px; margin-bottom: 8px;">
            <h3 style="font-size: 1.15rem; color: #f1f5f9; display: flex; align-items: center; gap: 8px; margin: 0;">
              <span style="display: inline-block; width: 8px; height: 8px; background: #10b981; border-radius: 50%; box-shadow: 0 0 8px #10b981;"></span>
              Pillar 2: Pure Numerical &amp; Tabular Fraud Deep-Dive (The Gate 3 Sub-Cohort)
            </h3>
            <span class="badge badge-case" style="font-size: 0.8rem; padding: 4px 10px;">1,862 Confirmed Data Fraud Cases</span>
          </div>
          <p style="font-size: 0.85rem; color: var(--text-muted); margin-bottom: 16px;">
            To measure how well the tool detects genuine tabular misconduct without confounding by non-mathematical retractions, we isolate the <strong>1,862 studies retracted specifically for fabricated, falsified, or manipulated data</strong> across 7,390 extracted tables and 60,232 audited rows:
          </p>

          <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 16px; margin-bottom: 20px;">
            <!-- Card A: Global Sensitivity -->
            <div style="background: var(--bg-card); border: 1px solid var(--border); border-radius: 10px; padding: 18px;">
              <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                <h4 style="color: var(--cyan); font-size: 0.95rem;">A. Global Data Fraud Sensitivity</h4>
                <span class="badge badge-tier2">All 1,862 Cases</span>
              </div>
              <div style="font-size: 1.6rem; font-weight: 800; color: var(--cyan); margin-bottom: 6px;">20.73%</div>
              <p style="font-size: 0.83rem; color: var(--text-muted); line-height: 1.5; margin-bottom: 10px;">
                Catches <strong>386 / 1,862</strong> retracted data fraud papers unassisted (95% Wilson CI: 18.95% – 22.63%).
              </p>
              <div style="background: rgba(15, 23, 42, 0.6); border-left: 3px solid var(--cyan); padding: 10px; font-size: 0.78rem; color: var(--text-dim); line-height: 1.45;">
                Includes all real-world data fraud cases, even those where tables were formula-generated in Excel or omitted entirely (153 papers had no tables).
              </div>
            </div>

            <!-- Card B: Verifiable Tables Sensitivity -->
            <div style="background: rgba(16, 185, 129, 0.08); border: 1px solid rgba(16, 185, 129, 0.35); border-radius: 10px; padding: 18px;">
              <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                <h4 style="color: #34d399; font-size: 0.95rem;">B. Mathematically Verifiable Tables</h4>
                <span class="badge badge-clean">Strict N Verified (N=344)</span>
              </div>
              <div style="font-size: 1.6rem; font-weight: 800; color: #34d399; margin-bottom: 6px;">80.81%</div>
              <p style="font-size: 0.83rem; color: var(--text-muted); line-height: 1.5; margin-bottom: 10px;">
                Catches <strong>278 / 344</strong> data fraud papers where sample size N is reported alongside summary statistics.
              </p>
              <div style="background: rgba(15, 23, 42, 0.6); border-left: 3px solid #10b981; padding: 10px; font-size: 0.78rem; color: var(--text-dim); line-height: 1.45;">
                <strong>Verifiability Threshold:</strong> When tabular rows provide sample size <code>N</code> alongside Means, SDs, or counts, math sieves expose typographic fabrications in over 4 out of 5 papers.
              </div>
            </div>

            <!-- Card C: Discrete Scales -->
            <div style="background: var(--bg-card); border: 1px solid var(--border); border-radius: 10px; padding: 18px;">
              <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                <h4 style="color: #f59e0b; font-size: 0.95rem;">C. Discrete Integer Scales</h4>
                <span class="badge" style="background: rgba(245, 158, 11, 0.15); color: #fbbf24; border: 1px solid rgba(245, 158, 11, 0.3);">Discrete (N &lt; 100)</span>
              </div>
              <div style="font-size: 1.6rem; font-weight: 800; color: #fbbf24; margin-bottom: 6px;">50.00%</div>
              <p style="font-size: 0.83rem; color: var(--text-muted); line-height: 1.5; margin-bottom: 10px;">
                Catches <strong>10 / 20</strong> papers reporting Likert scores, tooth counts, symptom checklists, or integer survey items.
              </p>
              <div style="background: rgba(15, 23, 42, 0.6); border-left: 3px solid #f59e0b; padding: 10px; font-size: 0.78rem; color: var(--text-dim); line-height: 1.45;">
                <strong>Modular Arithmetic:</strong> On integer scales, invented averages violate modular granularity (e.g. <code>Mean = 3.42</code> across <code>N = 17</code> requires a non-integer total score).
              </div>
            </div>
          </div>

          <!-- Anatomies of Data Fraud Breakdown -->
          <div style="background: var(--bg-card); border: 1px solid var(--border); border-radius: 10px; padding: 18px; margin-bottom: 16px;">
            <h4 style="color: #f1f5f9; font-size: 0.95rem; margin-bottom: 10px; display: flex; align-items: center; gap: 8px;">
              <span>Why Do 79.27% of Data Fraud Summary Tables Pass Math? The 4 Anatomies of Real Data Fraud:</span>
            </h4>
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: 12px; font-size: 0.82rem;">
              <div style="background: rgba(15, 23, 42, 0.5); padding: 12px; border-radius: 8px; border-left: 3px solid #3b82f6;">
                <strong style="color: #93c5fd;">1. The "Excel Reality" (Formula Generation):</strong><br>
                <span style="color: var(--text-muted);">Fraudsters who fabricate synthetic raw patient rows in Excel and use <code>=AVERAGE()</code> and <code>=STDEV()</code> produce mathematically self-consistent summary numbers. Summary tables cannot expose raw-row synthesis without raw line data.</span>
              </div>
              <div style="background: rgba(15, 23, 42, 0.5); padding: 12px; border-radius: 8px; border-left: 3px solid #8b5cf6;">
                <strong style="color: #c084fc;">2. Continuous Unbounded Assays:</strong><br>
                <span style="color: var(--text-muted);">Assays like optical density (OD 450nm), Western blot densitometry, and qPCR fold changes have infinite degrees of freedom; any decimal mean is mathematically possible unless variance bounds are violated.</span>
              </div>
              <div style="background: rgba(15, 23, 42, 0.5); padding: 12px; border-radius: 8px; border-left: 3px solid #f59e0b;">
                <strong style="color: #fbbf24;">3. Sample Size Omission:</strong><br>
                <span style="color: var(--text-muted);">Many clinical tables report percentages or means without specifying per-group <code>N</code> in the column header, preventing modular tests like GRIM from calculating integer divisibility.</span>
              </div>
              <div style="background: rgba(15, 23, 42, 0.5); padding: 12px; border-radius: 8px; border-left: 3px solid #ef4444;">
                <strong style="color: #fca5a5;">4. Narrative-Only Fraud (153 Papers):</strong><br>
                <span style="color: var(--text-muted);">8.2% of data fraud papers presented their fabricated data exclusively in running text or bar charts, with zero formal <code>&lt;table&gt;</code> elements in the XML full text.</span>
              </div>
            </div>
          </div>

          <!-- FastMCP Sieves Distribution in Data Fraud -->
          <div style="background: rgba(30, 41, 59, 0.4); border: 1px solid rgba(59, 130, 246, 0.2); border-radius: 10px; padding: 16px;">
            <div style="font-size: 0.85rem; font-weight: 700; color: #93c5fd; margin-bottom: 8px;">
              FastMCP Mathematical Sieves Triggered Across Detected Data Fraud Papers (N=386):
            </div>
            <div style="display: flex; flex-wrap: wrap; gap: 8px;">
              <span class="badge" style="background: rgba(16, 185, 129, 0.15); color: #34d399; border: 1px solid rgba(16, 185, 129, 0.3);">SPRITE Variance Bounds: 158 papers</span>
              <span class="badge badge-tier1">GRIM Inviolable Means: 146 papers</span>
              <span class="badge" style="background: rgba(59, 130, 246, 0.15); color: #60a5fa; border: 1px solid rgba(59, 130, 246, 0.3);">GRIMMER SD Parity: 125 papers</span>
              <span class="badge" style="background: rgba(244, 63, 94, 0.15); color: #fb7185; border: 1px solid rgba(244, 63, 94, 0.3);">Biomarker Bounds: 13 papers</span>
              <span class="badge badge-tier2">Carlisle Hyper-Homogeneity: 6 papers</span>
              <span class="badge" style="background: rgba(245, 158, 11, 0.15); color: #fbbf24; border: 1px solid rgba(245, 158, 11, 0.3);">DEBIT Proportions: 3 papers</span>
              <span class="badge" style="background: rgba(168, 85, 247, 0.15); color: #c084fc; border: 1px solid rgba(168, 85, 247, 0.3);">Statcheck Decision Errors: 2 papers</span>
            </div>
          </div>
        </div>'''

if old_p2_section in text:
    text = text.replace(old_p2_section, new_p2_section, 1)
    with open('docs/index.html', 'w', encoding='utf-8') as f:
        f.write(text)
    print('Successfully updated Pillar 2 in docs/index.html')
else:
    print('old_p2_section NOT found')
