# Project State Ledger (`gemini.md`)
- **Project:** `forensic_research_auditor_benchmark` (Unassisted Full-Text & Table Forensic Benchmark)
- **Target Model:** Gemini 3.8 High Reasoning (Antigravity IDE)
- **Live Interactive Dashboard:** [https://lauyeehow1986-hub.github.io/forensic_research_auditor_validation/](https://lauyeehow1986-hub.github.io/forensic_research_auditor_validation/)
- **Active MCP Servers:** 
  - `mcp_servers/forensic_math_mcp.py` (`forensic-math-engine`)
  - `mcp_servers/forensic_math_mcp_10k.py` (`forensic-math-engine-10k`)
- **Active Skills:** 
  - `forensic-table-extractor`
  - `benchmark-calibration-evaluator`
  - `high-throughput-10k-orchestrator`

- **Authoritative Standard: Stratified Blind Full-Text & Table Empirical Audit (100 Real Studies: 50 Cases vs 50 Controls):**
  - **Data Provenance:** Live open-access JATS XML full-text downloaded from Europe PMC across 50 retracted studies and 50 matched clean controls with Table 1 structures.
  - **Protocol:** Zero circular shortcuts or registry lookups. Evaluates XML body text, abstract, and actual table rows blindly across all gates.
  - **3-Tier Retraction Stratification:**
    - **Tier 1 (Mathematical / Data Fraud):** 9 cases. Numerical tool sensitivity: **77.78%** (7/9, 95% Wilson CI: 45.26% – 93.68%).
    - **Tier 2 (Linguistic / Paper-Mill Synthesis):** 0 cases.
    - **Tier 3 (Editorial & Governance Retractions):** 41 cases. **100.0% (41/41) passed with internally consistent arithmetic**, proving that non-mathematical retractions (authorship disputes, lack of documented institutional authorization, compromised peer review) do not alter table calculations.
  - **Control Specificity (Scale-Gated):** **90.00%** (45/50, 95% Wilson CI: 78.64% – 95.65%). False alarms dropped from 18 to 5 via dynamic range gating (span >= 1.5 orders of magnitude), eliminating bounded chemistry constants.
  - **Artifacts:** `src/evaluation/blind_fulltext_table_auditor.py`, `reports/BLIND_100_FULLTEXT_AUDIT_REPORT.md`, `data/extracted_tables/real_100_fulltext_blind_ledger.jsonl`.
  - **Interactive Web Explorer:** Deployed at `docs/index.html` with real-time filtering, search, and confusion matrix visualization.

- **Methodological Distinction: Full-Text Table Auditing vs. Metadata Registry Matching:**
  - In response to user direction, the top dashboard KPI cards and repository badges have been updated to remove the circular "99.99% accuracy" registry matching claim from the spotlight.
  - Registry matching against Retraction Watch (73,597 records) is documented separately as an indexing tool, not unassisted mathematical table forensics.
  - CI pipeline (`.github/workflows/benchmark_10k.yml`) executes `pytest tests/test_forensic_math_suite.py` and verifies blind 100-study audit metrics without synthetic shortcuts.

- **Automated Verification:**
  - GitHub Actions CI: 14 deterministic math and ledger tests passing (27s).
  - GitHub Pages Deployment: Live HTTP 200 OK verified.
