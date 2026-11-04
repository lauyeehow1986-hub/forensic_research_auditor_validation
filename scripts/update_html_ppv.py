# Script to update docs/index.html with PPV rows
with open('docs/index.html', 'r', encoding='utf-8') as f:
    content = f.read()

target = '''                <tr>
                  <td><strong>Real Literature Scale Audited</strong></td>'''

ppv_rows = '''                <tr>
                  <td><strong>Benchmark Cohort PPV (Math vs Ctrl)</strong><br><small style="color: var(--text-dim);">Enriched 1:1 study cohort</small></td>
                  <td>9.95% (22/221)</td>
                  <td>10.78% (36/334)</td>
                  <td>33.47% (160/478)</td>
                  <td>34.67% (121/349)</td>
                  <td style="background: rgba(16, 185, 129, 0.08); font-weight: 700; color: #34d399;">25.13% (47/187)</td>
                  <td style="background: rgba(59, 130, 246, 0.08); font-weight: 700; color: #60a5fa;">24.60% (386/1,569)</td>
                </tr>
                <tr>
                  <td><strong>Benchmark Cohort PPV (Any vs Ctrl)</strong><br><small style="color: var(--text-dim);">All retractions in 1:1 cohort</small></td>
                  <td>52.16% (217/416)</td>
                  <td>42.02% (216/514)</td>
                  <td>45.45% (265/583)</td>
                  <td>45.32% (189/417)</td>
                  <td style="background: rgba(16, 185, 129, 0.08); font-weight: 700; color: #34d399;">34.88% (75/215)</td>
                  <td style="background: rgba(59, 130, 246, 0.08); font-weight: 700; color: #60a5fa;">44.85% (962/2,145)</td>
                </tr>
                <tr>
                  <td><strong>Targeted Sweep PPV (P = 15%)</strong><br><small style="color: var(--text-dim);">Paper-mill rings, suspicious domains</small></td>
                  <td>18.15%</td>
                  <td>14.67%</td>
                  <td>14.68%</td>
                  <td>13.31% (Tier 1: 18.17%)</td>
                  <td style="background: rgba(16, 185, 129, 0.08); font-weight: 700; color: #34d399;">10.16% (Tier 1: 26.97%)</td>
                  <td style="background: rgba(59, 130, 246, 0.08); font-weight: 700; color: #60a5fa;">13.39% (Tier 1: 18.49%)</td>
                </tr>
                <tr>
                  <td><strong>Whistleblower PPV (P = 40%)</strong><br><small style="color: var(--text-dim);">Pre-screened PubPeer allegations</small></td>
                  <td>45.58%</td>
                  <td>39.38%</td>
                  <td>39.40%</td>
                  <td>36.71% (Tier 1: 45.61%)</td>
                  <td style="background: rgba(16, 185, 129, 0.08); font-weight: 700; color: #34d399;">29.93% (Tier 1: 58.25%)</td>
                  <td style="background: rgba(59, 130, 246, 0.08); font-weight: 700; color: #60a5fa;">36.87% (Tier 1: 47.48%)</td>
                </tr>
                <tr>
                  <td><strong>Positive Likelihood Ratio (LR⁺)</strong><br><small style="color: var(--text-dim);">Prevalence-invariant diagnostic gain</small></td>
                  <td>1.26</td>
                  <td>0.97</td>
                  <td>0.98</td>
                  <td>0.87 (Tier 1: 1.26)</td>
                  <td style="background: rgba(16, 185, 129, 0.08); font-weight: 700; color: #34d399;">0.64 (Tier 1: 2.09)</td>
                  <td style="background: rgba(59, 130, 246, 0.08); font-weight: 700; color: #60a5fa;">0.88 (Tier 1: 1.75)</td>
                </tr>
'''

if target in content:
    new_content = content.replace(target, ppv_rows + target, 1)
    with open('docs/index.html', 'w', encoding='utf-8') as f:
        f.write(new_content)
    print('Successfully inserted PPV rows into docs/index.html')
else:
    print('Target not found in docs/index.html')
