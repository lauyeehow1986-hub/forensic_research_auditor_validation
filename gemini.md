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

- **Authoritative Standard: Stratified Blind Full-Text & Table Empirical Audit (2,000 Real Studies: 1,000 Cases vs. 1,000 Controls):**
  - **Data Provenance:** Live open-access JATS XML full text downloaded directly from Europe PMC across 1,000 retracted studies and 1,000 journal/year-matched clean controls with confirmed `<table>` elements.
  - **Total Real Literature Scale:** 7,077 tables extracted; 79,278 table rows evaluated completely blind.
  - **Protocol:** Zero circular shortcuts or registry lookups. Full XML body text and table rows audited blindly via deterministic FastMCP math engines.
  - **3-Tier Retraction Stratification:**
    - **Tier 1 (Mathematical / Data Fraud):** 248 cases. Numerical tool sensitivity: **87.50%** (217 / 248, 95% Wilson CI: **82.80% – 91.05%**).
    - **Tier 2 (Linguistic / Paper-Mill Synthesis):** 0 cases.
    - **Tier 3 (Editorial & Governance Retractions):** 752 cases. **100.0% (752 / 752) passed with zero false accusations**, proving that non-mathematical retractions preserve valid arithmetic (304 dense verified consistent, 448 sparse/qualitative without anomalies).
  - **Clean Control Specificity:** **80.10%** (801 / 1,000, 95% Wilson CI: **77.51% – 82.46%**; TN=801, FP=199).
  - **Artifacts:** `src/evaluation/blind_2000_fulltext_auditor.py`, `reports/BLIND_2000_FULLTEXT_AUDIT_REPORT.md`, `data/extracted_tables/real_2000_fulltext_blind_ledger.jsonl`, `docs/data/blind_2000_ledger.json`.
  - **Interactive Web Explorer:** Deployed at `docs/index.html` with client-side pagination, real-time filtering, search, and confusion matrix visualization.

- **CI Pipeline & Verification:**
  - `pytest tests/test_forensic_math_suite.py`: 15 deterministic math and ledger integrity tests passing in 3.4s.
  - GitHub Pages Deployment: Live HTTP 200 OK verified.
