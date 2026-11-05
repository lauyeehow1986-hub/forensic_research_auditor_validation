with open('docs/index.html', 'r', encoding='utf-8') as f:
    text = f.read()

# 1. Update lines around 1390
old_js_block = """      const g3 = cases.filter(s => s.retraction_tier === 'GATE_3_MATH_DATA');
      const g35 = cases.filter(s => s.retraction_tier === 'GATE_35_IMAGES');
      const g2 = cases.filter(s => s.retraction_tier === 'GATE_2_PAPERMILL');
      const g4 = cases.filter(s => s.retraction_tier === 'GATE_4_GOVERNANCE');

      const g3_tp = g3.filter(s => s.blind_verdict === 'FLAGGED_FORENSIC_ANOMALY').length;
      const g3_fn = g3.length - g3_tp;
      const g3_ci = wilsonCI(g3_tp, g3.length);

      const g35_clean = g35.filter(s => s.blind_verdict === 'CLEAN').length;
      const g35_ci = wilsonCI(g35_clean, g35.length);

      const g2_clean = g2.filter(s => s.blind_verdict === 'CLEAN').length;
      const g2_ci = wilsonCI(g2_clean, g2.length);

      const g4_clean = g4.filter(s => s.blind_verdict === 'CLEAN').length;
      const g4_ci = wilsonCI(g4_clean, g4.length);"""

new_js_block = """      const g3 = cases.filter(s => s.retraction_tier === 'GATE_3_MATH_DATA' || s.target_gate === 'GATE_3_MATH_DATA');
      const nonMath = cases.filter(s => s.retraction_tier !== 'GATE_3_MATH_DATA' && s.target_gate !== 'GATE_3_MATH_DATA');

      const g3_tp = g3.filter(s => s.blind_verdict === 'FLAGGED_FORENSIC_ANOMALY').length;
      const g3_fn = g3.length - g3_tp;
      const g3_ci = wilsonCI(g3_tp, g3.length);

      const nonMath_clean = nonMath.filter(s => s.blind_verdict === 'CLEAN').length;
      const nonMath_noise = nonMath.length - nonMath_clean;
      const nonMath_ci = wilsonCI(nonMath_clean, nonMath.length);"""

if old_js_block in text:
    text = text.replace(old_js_block, new_js_block)
    print("Replaced JS block around line 1390 successfully!")
else:
    print("Failed to replace JS block around line 1390")

# 2. Update Gate 3.5 card at line 1116
old_card = """          <div class="flow-card">
            <div class="flow-title" style="color: #fb7185;">Gate 3.5: Images &amp; Figures</div>
            <div class="flow-reasons"><code>+Western Blot Splicing</code>, <code>+Image Duplication</code>, <code>+Missing Raw Files</code></div>
            <p style="font-size: 0.85rem; color: var(--text-muted); margin-bottom: 12px;">
              Detects cloned microscopy panels, spliced gel bands, and volcano/Manhattan plot single-SNP chimneys.
            </p>
            <div class="flow-target"><strong>Math Pass Rate:</strong> 79.17% (76/96 clean; fraud is in figures).</div>
          </div>"""

new_card = """          <div class="flow-card" style="border: 1px solid rgba(244, 63, 94, 0.4);">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px;">
              <div class="flow-title" style="color: #fb7185; margin: 0;">Gate 3.5: Images &amp; Figures</div>
              <span class="badge" style="background: rgba(244, 63, 94, 0.2); color: #fb7185; font-size: 0.72rem; border: 1px solid rgba(244, 63, 94, 0.4);">External Figure Forensics</span>
            </div>
            <div class="flow-reasons"><code>Western Blot Splicing</code>, <code>Gel Duplication</code>, <code>Microscopy Cloning</code></div>
            <p style="font-size: 0.85rem; color: var(--text-muted); margin-bottom: 12px;">
              Visual feature matching for Western blot splicing, cloned gel lanes, and microscopy panels. <em>Note: Auditing image pixels requires external computer vision models (e.g. Proofig, ImCheck); tabular FastMCP sieves audit numerical tables and statistics, not pixel arrays.</em>
            </p>
            <div class="flow-target"><strong>Domain:</strong> Pixel/Raster Forensics (Decoupled from tabular FastMCP math).</div>
          </div>"""

if old_card in text:
    text = text.replace(old_card, new_card)
    print("Replaced Gate 3.5 card successfully!")
else:
    print("Failed to replace Gate 3.5 card")

with open('docs/index.html', 'w', encoding='utf-8') as f:
    f.write(text)

print("Done updating docs/index.html")
