# Project State Ledger (`gemini.md`)
- **Project:** `forensic_research_auditor_benchmark` (2,000-Study Blind Full-Text & Table Forensic Benchmark)
- **Target Model:** Gemini 3.8 High Reasoning (Antigravity IDE)
- **Live Interactive Dashboard:** [https://lauyeehow1986-hub.github.io/forensic_research_auditor_validation/](https://lauyeehow1986-hub.github.io/forensic_research_auditor_validation/)
- **Active MCP Servers:** 
  - `mcp_servers/forensic_math_mcp.py` (`forensic-math-engine`)
  - `mcp_servers/forensic_math_mcp_10k.py` (`forensic-math-engine-10k`)
- **Active Skills:** 
  - `forensic-table-extractor`
  - `benchmark-calibration-evaluator`
  - `high-throughput-10k-orchestrator`

- **Authoritative Standard: 5-Gate Blind Full-Text & Table Empirical Audit (2,000 Real Studies: 1,000 Cases vs. 1,000 Controls):**
  - **Data Provenance:** Live open-access JATS XML full text downloaded directly from Europe PMC across 1,000 retracted studies and 1,000 journal/year-matched clean controls with confirmed `<table>` elements.
  - **Total Real Literature Scale:** 7,077 tables extracted; 79,278 table rows evaluated completely blind.
  - **Protocol:** Zero circular shortcuts or incorporation bias. Studies categorized by objective Retraction Watch / Europe PMC metadata, separating visual image splicing and linguistic synthesis from table arithmetic.
  - **5-Gate Diagnostic Stratification:**
    - **Gate 3 (Numerical & Data Fraud):** 88 cases. Math sensitivity: **25.00%** (22 / 88, 95% Wilson CI: **17.13% – 34.96%**; rises to **50.00%** (10 / 20) on discrete integer tables $N < 100$).
    - **Gate 3.5 (Images & Figure Splicing):** 96 cases. Specificity: **79.17%** (76 / 96 passed clean; fraud isolated to figures/blots, tables valid).
    - **Gate 2 (Paper-Mill & NLP Synthesis):** 55 cases. Specificity: **83.64%** (46 / 55 passed clean; fraud isolated to language/PPS).
    - **Gate 4 (Editorial & Governance):** 761 cases. Specificity: **78.19%** (595 / 761 passed clean; matches controls $p=0.31$, authentic arithmetic preserved).
    - **Gate 1 (Provenance & Registry):** 100% of cases cataloged.
  - **Clean Control Specificity:** **80.10%** (801 / 1,000, 95% Wilson CI: **77.51% – 82.46%**; TN=801, FP=199).
  - **Artifacts:** `src/evaluation/blind_2000_fulltext_auditor.py`, `reports/BLIND_2000_FULLTEXT_AUDIT_REPORT.md`, `data/extracted_tables/real_2000_fulltext_blind_ledger.jsonl`, `docs/data/blind_2000_ledger.json`.
  - **Interactive Web Explorer:** Deployed at `docs/index.html` with client-side pagination, 5-gate filtering, search, and confusion matrix visualization.

- **CI Pipeline & Verification:**
  - `pytest tests/test_forensic_math_suite.py`: 15 deterministic math and ledger integrity tests passing in ~2s.
  - GitHub Pages Deployment: Live HTTP 200 OK verified.
