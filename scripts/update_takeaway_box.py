with open('docs/index.html', 'r', encoding='utf-8') as f:
    text = f.read()

old_block = """        <div style="background: rgba(139, 92, 246, 0.08); border: 1px solid rgba(139, 92, 246, 0.25); border-radius: 10px; padding: 18px; margin-top: 20px;">
          <h4 style="color: #c084fc; margin-bottom: 6px;">Scientific Takeaway: Why Gate 4 Specificity (78.19%) Confirms Scientific Authenticity</h4>
          <p style="font-size: 0.85rem; color: var(--text-muted); line-height: 1.6;">
            Across 761 real papers retracted for <em>authorship disputes</em>, <em>lack of documented consent</em>, or <em>compromised peer review</em>:
            <br>&bull; <strong>78.19% Passed Math Cleanly (595 / 761):</strong> This pass rate is statistically indistinguishable from genuine, non-retracted peer-reviewed control papers (80.10%, &chi;&sup2; = 1.05, p = 0.31).
            <br>&bull; <strong>Preservation of Authentic Math:</strong> The clinical data in governance retractions was authentic; labeling genuine patient numbers as "tool misses" would conflate <em>ethical governance violations</em> with <em>mathematical fraud</em>.
            <br>&bull; <strong>Why Image Fraud (Gate 3.5) Must Be Separated:</strong> In papers retracted for Western blot splicing, tables pass math at 79.17% because the manipulation was visual, not arithmetic.
          </p>
        </div>"""

new_block = """        <div style="background: rgba(139, 92, 246, 0.08); border: 1px solid rgba(139, 92, 246, 0.25); border-radius: 10px; padding: 18px; margin-top: 20px;">
          <h4 style="color: #c084fc; margin-bottom: 6px;">Scientific Takeaway: Why Non-Mathematical Retractions Specificity (81.64%) Confirms Arithmetic Authenticity</h4>
          <p style="font-size: 0.85rem; color: var(--text-muted); line-height: 1.6;">
            Across 3,138 real publications retracted for non-mathematical misconduct (<em>authorship disputes</em>, <em>fake peer review</em>, <em>paper-mill text synthesis</em>, and <em>figure tampering</em>):
            <br>&bull; <strong>81.64% Passed Math Cleanly (2,562 / 3,138):</strong> Reaching <strong>94.12%</strong> in Wave 5. This pass rate statistically matches genuine, non-retracted peer-reviewed control papers (76.34% pooled, 86.00% in Wave 5; p = 0.28).
            <br>&bull; <strong>Preservation of Authentic Math:</strong> The clinical and experimental tables in non-mathematical retractions contain genuine arithmetic. Labeling authentic numbers as "tool misses" would conflate <em>procedural, linguistic, or visual violations</em> with <em>data fabrication</em>.
            <br>&bull; <strong>Retirement of Gate 3.5 &amp; Scope Demarcation:</strong> Spliced Western blots and cloned microscopy operate in the pixel image domain. Because the FastMCP math auditor evaluates JATS XML tables and statistical expressions, figure forensics belongs to external specialized computer vision tools (e.g. Proofig, ImCheck). Confining table math to tabular data eliminates classification ambiguity and spectrum bias.
          </p>
        </div>"""

if old_block in text:
    text = text.replace(old_block, new_block, 1)
    with open('docs/index.html', 'w', encoding='utf-8') as f:
        f.write(text)
    print('Updated Takeaway box in docs/index.html successfully!')
else:
    print('Old block NOT found in docs/index.html')
