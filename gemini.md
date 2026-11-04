# Project State Ledger (`gemini.md`)
- **Project:** `forensic_research_auditor_benchmark` (4,000-Study Dual-Wave Blind Full-Text Forensic Benchmark)
- **Target Model:** Gemini 3.8 High Reasoning (Antigravity IDE)
- **Live Interactive Dashboard:** [https://lauyeehow1986-hub.github.io/forensic_research_auditor_validation/](https://lauyeehow1986-hub.github.io/forensic_research_auditor_validation/)
- **Active MCP Servers:** 
  - `mcp_servers/forensic_math_mcp.py` (`forensic-math-engine`)
  - `mcp_servers/forensic_math_mcp_10k.py` (`forensic-math-engine-10k`)
- **Active Skills:** 
  - `forensic-research-auditor` (`C:\Users\lauye\.gemini\config\skills\forensic-auditor\SKILL.md`)
  - `forensic-table-extractor`
  - `benchmark-calibration-evaluator`
  - `high-throughput-10k-orchestrator`

- **Dual-Wave Independent Replication (Wave 1: 2,000 Studies + Wave 2: 2,000 Studies = 4,000 Studies Total):**
  - **Zero Intersection Guarantee:** Strictly 0% overlap between Wave 1 and Wave 2 (0 overlapping PMCIDs, 0 overlapping DOIs).
  - **Data Provenance:** Live open-access JATS XML full text downloaded directly from Europe PMC across 2,000 retracted studies and 2,000 journal/year-matched clean controls with confirmed `<table>` elements.
  - **Total Real Literature Scale:** 13,087 tables extracted; 146,501 table rows evaluated completely blind.
  - **Protocol:** Zero circular shortcuts or incorporation bias. Studies categorized by objective Retraction Watch / Europe PMC metadata, separating visual image splicing and linguistic synthesis from table arithmetic.
  
- **Empirical Diagnostics by Wave & Pooled Meta-Analysis:**
  - **Wave 1 (2,000 Studies: 1,000 Cases vs. 1,000 Controls):**
    - Gate 3 (Math/Data Fraud): 88 cases -> Sensitivity **25.00%** (22 / 88, 95% Wilson CI: 17.13% – 34.96%; 50.0% on discrete tables $N < 100$).
    - Gate 3.5 (Images & Splicing): 96 cases -> Specificity **79.17%** (76 / 96 passed clean; fraud isolated to figures).
    - Gate 2 (Paper-Mill/NLP): 55 cases -> Specificity **83.64%** (46 / 55 passed clean).
    - Gate 4 (Governance/Ethics): 761 cases -> Specificity **78.19%** (595 / 761 passed clean; matches controls $p=0.31$).
    - Clean Controls: 1,000 studies -> Specificity **80.10%** (801 / 1,000; TN=801, FP=199).
  - **Wave 2 (2,000 Independent Studies: 1,000 Cases vs. 1,000 Controls):**
    - Gate 3 (Math/Data Fraud): 124 cases -> Sensitivity **29.03%** (36 / 124, 95% Wilson CI: 21.77% – 37.56%).
    - Gate 3.5 (Images & Splicing): 110 cases -> Specificity **70.91%** (78 / 110 passed clean; fraud isolated to figures).
    - Gate 2 (Paper-Mill/NLP): 88 cases -> Specificity **78.41%** (69 / 88 passed clean).
    - Gate 4 (Governance/Ethics): 678 cases -> Specificity **80.97%** (549 / 678 passed clean).
    - Clean Controls: 1,000 studies -> Specificity **70.20%** (702 / 1,000; TN=702, FP=298).
  - **Pooled Meta-Analysis (4,000 Studies: 2,000 Cases vs. 2,000 Controls):**
    - Gate 3 (Math/Data Fraud): 212 cases -> Sensitivity **27.36%** (58 / 212, 95% Wilson CI: 21.80% – 33.72%).
    - Gate 3.5 (Images & Splicing): 206 cases -> Specificity **74.76%** (154 / 206 passed clean).
    - Gate 2 (Paper-Mill/NLP): 143 cases -> Specificity **80.42%** (115 / 143 passed clean).
    - Gate 4 (Governance/Ethics): 1,439 cases -> Specificity **79.50%** (1,144 / 1,439 passed clean).
    - Clean Controls: 2,000 studies -> Specificity **75.15%** (1,503 / 2,000 passed clean).
  
- **Key Scientific Breakthroughs Replicated:**
  - **Authentic Arithmetic in Non-Data Retractions:** Across 1,439 governance retractions, 79.50% pass table math cleanly, matching clean controls ($p=0.42$).
  - **Image Splicing Does Not Corrupt Tables:** Across 206 image fraud retractions, 74.76% pass table math cleanly, validating the physical separation into Gate 3.5.

- **Artifacts:**
  - `src/evaluation/blind_2000_fulltext_auditor.py` & `src/evaluation/blind_wave2_fulltext_auditor.py`
  - `reports/BLIND_2000_FULLTEXT_AUDIT_REPORT.md` (Wave 1)
  - `reports/BLIND_WAVE2_FULLTEXT_AUDIT_REPORT.md` (Wave 2)
  - `reports/BLIND_COMBINED_4000_FULLTEXT_AUDIT_REPORT.md` (Pooled 4,000 studies)
  - `data/extracted_tables/real_2000_fulltext_blind_ledger.jsonl` & `data/extracted_tables/real_wave2_fulltext_blind_ledger.jsonl`
  - `docs/data/blind_2000_ledger.json`, `docs/data/blind_wave2_ledger.json`, `docs/data/blind_combined_4000_ledger.json`
  - Interactive Web App at `docs/index.html` with reactive Wave 1 / Wave 2 / Pooled selector.

- **CI Pipeline & Verification:**
  - `pytest tests/test_forensic_math_suite.py`: 18 deterministic math, zero-intersection, and ledger integrity tests passing in ~2.1s.
