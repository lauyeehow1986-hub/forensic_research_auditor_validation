# Script to update the clinical reporting and editorial matrix tab to 10k numbers
with open('docs/index.html', 'r', encoding='utf-8') as f:
    text = f.read()

# 1. Update Pillar 1 table
old_p1_part1 = '''                  <td style="font-weight: 700; color: #34d399;">99.20% (8 / 1,000 clean controls flagged)</td>
                  <td style="font-weight: 600; color: #60a5fa;">77.20% (Wave 4 Calibrated Consensus)</td>
                  <td>Strict consensus protocol rebounded clean control specificity by +9.0% from Wave 3.</td>'''

new_p1_part1 = '''                  <td style="font-weight: 700; color: #34d399;">96.90% (Wave 5: 31/1,000 flagged) &bull; &gt;99% on discrete</td>
                  <td style="font-weight: 600; color: #60a5fa;">86.00% (Wave 5 High-Specificity Consensus)</td>
                  <td>Multi-cell consensus + decadic gating surged clean control specificity to 86.0% (Pooled 10k: 76.34%).</td>'''

old_p1_part2 = '''                  <td style="color: #93c5fd;">50.0% on Discrete Scales (N<100)</td>
                  <td style="color: #93c5fd;">25.34% Global Pooled Sieve</td>'''

new_p1_part2 = '''                  <td style="color: #93c5fd;">50.0% on Discrete Scales (N<100)</td>
                  <td style="color: #93c5fd;">20.73% Global Pooled Sieve (10,000 Studies)</td>'''

# 2. Update Pillar 2
old_p2 = '''                <h4 style="color: var(--cyan); font-size: 0.95rem;">A. Global Case Sensitivity (25.34%)</h4>
                <span class="badge badge-tier2">All 1,338 Cases</span>
              </div>
              <p style="font-size: 0.85rem; color: var(--text-muted); line-height: 1.55; margin-bottom: 10px;">
                Across all retracted papers with confirmed numerical fraud, FastMCP table math catches <strong>25.34%</strong> (339 / 1,338, 95% Wilson CI: 23.08% – 27.74%).
              </p>'''

new_p2 = '''                <h4 style="color: var(--cyan); font-size: 0.95rem;">A. Global Case Sensitivity (20.73%)</h4>
                <span class="badge badge-tier2">All 1,862 Math Cases</span>
              </div>
              <p style="font-size: 0.85rem; color: var(--text-muted); line-height: 1.55; margin-bottom: 10px;">
                Across all retracted papers with confirmed numerical fraud in the pooled 10,000-study benchmark, FastMCP table math catches <strong>20.73%</strong> (386 / 1,862, 95% Wilson CI: 18.95% – 22.63%).
              </p>'''

# 3. Update Pillar 4
old_p4_header = 'Pillar 4: Proof Against Spectrum Bias (4-Gate Specificity Validation)'
new_p4_header = 'Pillar 4: Proof Against Spectrum Bias (5-Gate Specificity Validation Across 10,000 Studies)'

old_p4_card1 = '''              <div style="font-size: 0.8rem; color: #34d399; text-transform: uppercase; font-weight: 700; margin-bottom: 4px;">Clean Controls</div>
              <div style="font-size: 1.6rem; font-weight: 800; color: #34d399;">77.20%</div>
              <div style="font-size: 0.8rem; color: var(--text-muted); margin-top: 4px;">
                772 / 1,000 verified clean control studies passed clean in Wave 4 (+9.0% rebound via consensus calibration).
              </div>'''

new_p4_card1 = '''              <div style="font-size: 0.8rem; color: #34d399; text-transform: uppercase; font-weight: 700; margin-bottom: 4px;">Clean Controls</div>
              <div style="font-size: 1.6rem; font-weight: 800; color: #34d399;">86.00%</div>
              <div style="font-size: 0.8rem; color: var(--text-muted); margin-top: 4px;">
                860 / 1,000 clean controls passed clean in Wave 5 (Pooled: 76.34%, 3,817 / 5,000 across all 5 waves; 95% CI: 75.14% – 77.50%).
              </div>'''

old_p4_card2 = '''              <div style="font-size: 0.8rem; color: #c084fc; text-transform: uppercase; font-weight: 700; margin-bottom: 4px;">Governance Retractions</div>
              <div style="font-size: 1.6rem; font-weight: 800; color: #c084fc;">80.32%</div>
              <div style="font-size: 0.8rem; color: var(--text-muted); margin-top: 4px;">
                1,494 / 1,860 authorship/IRB retractions passed clean. Matches clean controls (p=0.40); clinical math was authentic.
              </div>'''

new_p4_card2 = '''              <div style="font-size: 0.8rem; color: #c084fc; text-transform: uppercase; font-weight: 700; margin-bottom: 4px;">Governance Retractions</div>
              <div style="font-size: 1.6rem; font-weight: 800; color: #c084fc;">82.38%</div>
              <div style="font-size: 0.8rem; color: var(--text-muted); margin-top: 4px;">
                1,758 / 2,134 authorship/IRB retractions passed clean (96.35% in Wave 5). Matches clean controls (p=0.31); clinical math was authentic.
              </div>'''

old_p4_card3 = '''              <div style="font-size: 0.8rem; color: #fb7185; text-transform: uppercase; font-weight: 700; margin-bottom: 4px;">Image Splicing Retractions</div>
              <div style="font-size: 1.6rem; font-weight: 800; color: #fb7185;">80.44%</div>
              <div style="font-size: 0.8rem; color: var(--text-muted); margin-top: 4px;">
                255 / 317 image/figure fraud papers passed table math clean. Proves fraud was isolated to Western blots, not tables.
              </div>'''

new_p4_card3 = '''              <div style="font-size: 0.8rem; color: #fb7185; text-transform: uppercase; font-weight: 700; margin-bottom: 4px;">Image Splicing Retractions</div>
              <div style="font-size: 1.6rem; font-weight: 800; color: #fb7185;">82.34%</div>
              <div style="font-size: 0.8rem; color: var(--text-muted); margin-top: 4px;">
                317 / 385 image/figure fraud papers passed table math clean (91.18% in Wave 5). Proves fraud was isolated to Western blots, not tables.
              </div>'''

replacements = [
    (old_p1_part1, new_p1_part1),
    (old_p1_part2, new_p1_part2),
    (old_p2, new_p2),
    (old_p4_header, new_p4_header),
    (old_p4_card1, new_p4_card1),
    (old_p4_card2, new_p4_card2),
    (old_p4_card3, new_p4_card3),
]

for old, new in replacements:
    if old in text:
        text = text.replace(old, new, 1)
        print(f"Successfully replaced: {old[:40]}...")
    else:
        print(f"NOT FOUND: {old[:40]}...")

with open('docs/index.html', 'w', encoding='utf-8') as f:
    f.write(text)

print("Done updating docs/index.html")
