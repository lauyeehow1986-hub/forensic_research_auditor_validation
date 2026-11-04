# Gate 3 Advanced Mathematical & Continuous Forensic Sieves
## Comprehensive Technical Manual & FastMCP Implementation
### Derived from the 4,000-Study Dual-Wave Full-Text Benchmark (212 Fraud Cases vs. 2,000 Controls)

**Target Skill:** `forensic-research-auditor` (`C:\Users\lauye\.gemini\config\skills\forensic-auditor\SKILL.md`)  
**Target FastMCP Server:** `forensic-math-engine` (`mcp_servers/forensic_math_mcp.py`)  
**Verification Suite:** `tests/test_forensic_math_suite.py` (26 / 26 deterministic unit tests passing)  
**Empirical Foundation:** Dual-Wave 4,000-study blind evaluation across Europe PMC JATS XML (13,087 tables, 146,501 rows audited).

---

## 1. Executive Post-Mortem: Why Gate 3 Baseline Sensitivity Was 27.4%

Across the pooled 4,000-study benchmark (2,000 retracted cases vs. 2,000 clean controls):
- **Gate 3 (Math/Data Fraud):** 212 cases -> Sensitivity **27.36%** (58 / 212 caught; 50.0% on discrete integer tables $N < 100$).
- **Gate 4 (Governance/Ethics):** 1,439 cases -> Specificity **79.50%** (1,144 / 1,439 passed table math cleanly, matching controls $p = 0.42$).
- **Clean Controls:** 2,000 studies -> Specificity **75.15%** (1,503 / 2,000 passed clean).

### Forensic Breakdown of the 154 Missed Gate 3 Studies:
A post-mortem investigation of the 154 false-negative studies where published summary tables passed basic checking revealed four foundational reasons:
1. **The "Excel Trap" (Formula-Consistent Fabrication):** Fraudsters who fabricate individual patient data rows in Excel/Python and calculate summary tables using `=AVERAGE()` and `=STDEV()` produce means and standard deviations that divide cleanly. Basic discrete integer tests (`GRIM`/`GRIMMER`) cannot detect fabricated rows if the formulas are algebraically correct.
2. **The "Continuous Biomarker Gap":** Over **92.2%** of missed cases reported continuous biological assays (serum troponin, cytokine pg/mL, viral titers, hemodynamics, or flow cytometry), continuous proportions, or survival hazard ratios where discrete integer checking cannot physically run.
3. **Multivariable Regression Disconnect:** Studies reporting multivariable Cox proportional hazards or logistic regression models (Table 2 and Table 3) frequently invented nominal $p$-values ($p < 0.05$) while reporting confidence intervals that cross unity or implied standard errors producing Wald $Z < 1.96$.
4. **AI & Machine Learning Coherence Gap:** Deep learning and diagnostic biomarker papers frequently reported decoupled triplets of Accuracy, Sensitivity ($TPR$), and Specificity ($TNR$) that violated the fundamental law of total probability:
   $$ACC = TPR \cdot P + TNR \cdot (1 - P)$$

To address these vulnerabilities, Gate 3 was upgraded into a 9-sieve continuous, multivariable, and linear algebraic engine.

---

## 2. Core Sieve Specifications & Detection Protocols

### Sieve 1: Continuous Biomarker Boundary & Biological Plausibility
Biological concentrations, laboratory biomarkers, and physical measurements are strictly non-negative ($X \ge 0$). Under standard Gaussian or symmetric reporting conventions ($M \pm SD$), reporting a mean and standard deviation where:

$$\mu - 2 \cdot \sigma < 0 \implies \frac{\mu}{\sigma} < 2.0$$

indicates that if the distribution were truly normal, more than 2.28% of biological observations would be negative (e.g., negative viral load, negative troponin). This represents either:
1. **Physical Impossibility:** Falsified baseline parameters invented without regard to physical zero boundaries.
2. **Extreme Positive Skewness Violation:** The underlying variable is heavily skewed, in which case reporting $M \pm SD$ violates international statistical reporting standards (SAMPL guidelines) and disguises severe variance compression.

**Detection Rules:**
- Flag `IMPOSSIBLE_NEGATIVE_BIOMARKER_RANGE` if $\mu - 2\sigma < 0$ on non-negative measurements without declared log-transformations.
- Flag `ZERO_SD_CONTINUOUS_VARIABLE` if $\sigma = 0.0$ on any continuous measurement where $\mu > 0$ and $N \ge 5$.

---

### Sieve 2: SPRITE Bounded Discrete Distribution Reconstruction
Developed by Heathers et al. (2018), **SPRITE** (Sample Parameter Reconstruction via Iterative TEchniques) tests whether **any** discrete response distribution constrained by sample size $N$ and bounded range $[X_{\min}, X_{\max}]$ (e.g. Likert scale $1$ to $5$, or clinical symptom score $0$ to $20$) can mathematically produce the reported Mean and Standard Deviation.

$$\sigma_{\max}^2 = (X_{\max} - \mu)(\mu - X_{\min})$$

**Detection Rules:**
- Flag `SPRITE_VARIANCE_EXCEEDS_BOUNDS` if $\sigma^2 > \sigma_{\max}^2$.
- Flag `UNNATURAL_ARM_HOMOSCEDASTICITY` if $0.995 \le \frac{\sigma_{\text{arm1}}}{\sigma_{\text{arm2}}} \le 1.005$ across independent trial arms with $N_{\text{total}} \ge 40$.

---

### Sieve 3: Correlation Matrix Positive Semi-Definiteness
In observational studies, epidemiology, and psychology, Table 2 and Table 3 report correlation matrices ($r$) or regression models ($\beta$). Any authentic Pearson/Spearman correlation matrix $R$ must be **positive semi-definite** ($R \succeq 0$):
1. All eigenvalues must be non-negative: $\lambda_{\min}(R) \ge 0$.
2. For any 3 pairwise correlations:
   $$\det(R_{3 \times 3}) = 1 - r_{12}^2 - r_{23}^2 - r_{13}^2 + 2 r_{12} r_{23} r_{13} \ge 0$$

**Detection Rules:**
- Flag `NON_POSITIVE_DEFINITE_CORRELATION_MATRIX` if $\lambda_{\min} < -10^{-4}$.

---

### Sieve 4: Tabular NHST Recalculation & P-Hacking Cliff Ratio
Scientific tables frequently report statistical tests in tabular columns: `Variable | t | df | p-value` or `Group | Chi-square | p`.

**Detection Rules:**
1. **Tabular Decision Error Sieve:** Directly recompute cumulative test distributions from table cells:
   - For Student's $t$: $p_{\text{recalc}} = 2 \cdot (1 - F_t(|t|, df))$
   - For Snedecor's $F$: $p_{\text{recalc}} = 1 - F_F(F, df_1, df_2)$
   - For Pearson's $\chi^2$: $p_{\text{recalc}} = 1 - F_{\chi^2}(\chi^2, df)$
   Flag a **Primary Decision Error** if reported $p < 0.05$ while $p_{\text{recalc}} \ge 0.05$.
2. **The "P-Hacking Cliff" Ratio ($R_{\text{cliff}}$):**
   $$R_{\text{cliff}} = \frac{N(p \in [0.041, 0.049])}{N(p \in [0.051, 0.059])}$$
   If $R_{\text{cliff}} \ge 3.0$ with $N \ge 6$, flag `P_HACKING_CLIFF_ANOMALY` ($LR = 0.25$).

---

### Sieve 5: Cross-Table Sample Size ($N$) Conservation
In clinical and biomedical studies, the sample size across tables must strictly adhere to the CONSORT / STROBE flow.
- Verify marginal totals in counts and percentages: $|n - \text{round}(\% \cdot N / 100)| \le 1$.
- Detect unexplained cohort expansion ($N_{\text{outcomes}} > N_{\text{baseline}}$).

---

### Sieve 6: Multivariable Regression Triangle ($\beta$ – $\text{SE}$ – $p$ Wald Recalculation)
Multivariable regression tables report an effect estimate ($\beta$, Odds Ratio $OR$, or Hazard Ratio $HR$), a 95% Confidence Interval $[LL, UL]$, and a reported $p$-value.

**Mathematical Principle:**
For ratio metrics ($OR, HR$), the standard error on the logarithmic scale is mathematically constrained by the 95% confidence bounds:
$$\text{SE}_{\text{implied}} = \frac{\ln(UL) - \ln(LL)}{2 \times 1.95996}$$
For linear difference models:
$$\text{SE}_{\text{implied}} = \frac{UL - LL}{2 \times 1.95996}$$

The Wald test statistic $Z$ and exact two-tailed $p$-value are:
$$Z_{\text{wald}} = \frac{\ln(\text{Estimate})}{\text{SE}_{\text{implied}}}, \quad p_{\text{wald}} = 2 \times (1 - \Phi(|Z_{\text{wald}}|))$$

**Detection Rules:**
- Flag **Primary Decision Error** if $p_{\text{reported}} < 0.05$ while $Z_{\text{wald}} < 1.96$ or the 95% CI crosses the null ($1.0$ for ratios, $0$ for linear differences).
- Flag `REGRESSION_P_DISCREPANCY` ($LR = 0.20$) if $|p_{\text{reported}} - p_{\text{wald}}| > 0.05$.

---

### Sieve 7: AI & Diagnostic Classifier Confusion Matrix Triangulation
In diagnostic medicine, machine learning, and multi-omics biomarker studies, authors report Accuracy ($ACC$), Sensitivity/Recall ($TPR$), and Specificity ($TNR$).

**Mathematical Principle:**
Under Bayes' theorem and total probability:
$$ACC = TPR \cdot P + TNR \cdot (1 - P)$$
where $P$ is the true prevalence or proportion of positive cases.

**Envelope Theorem:**
Because $P \in [0, 1]$, Accuracy must strictly lie within the closed interval bounded by Sensitivity and Specificity:
$$\min(TPR, TNR) \le ACC \le \max(TPR, TNR)$$

**Detection Rules:**
- Flag `ACCURACY_OUTSIDE_SENS_SPEC_ENVELOPE` if $ACC < \min(TPR, TNR) - \epsilon$ or $ACC > \max(TPR, TNR) + \epsilon$.
- If prevalence $P$ or class counts ($N_+, N_-$) are known, compute expected accuracy $ACC_{\text{expected}} = TPR \cdot P + TNR \cdot (1 - P)$. Flag `IMPOSSIBLE_ACCURACY_TRIAD` if $|ACC - ACC_{\text{expected}}| > 0.03$.

---

### Sieve 8: Cross-Table Sample Size & Marginal Conservation
Scientific tables reporting clinical subgroups must satisfy marginal totals and parent cohort limits.

**Detection Rules:**
- **Marginal Percentage Exactness:** $|n - \text{implied}| \le 1.0$ where implied count is $(Percentage / 100) \times N_{\text{total}}$. Flag `MARGINAL_PERCENTAGE_MISMATCH` if violated.
- **Subgroup Parent Conservation:** Flag `SUBGROUP_PARENT_OVERFLOW` if $N_{\text{subgroup}} > N_{\text{parent}}$.

---

### Sieve 9: Physiological Prior Reference Bounds & Extreme Variance Compression
Fabricated patient datasets often exhibit unnaturally compressed standard deviations (sometimes resulting from copy-pasting values or confusing SE with SD).

**Detection Rules:**
- Flag `EXTREME_VARIANCE_COMPRESSION` if reported $SD < 0.20 \times SD_{\text{physiological\_ref\_min}}$ ($LR = 0.15$).
- Flag `IMPOSSIBLE_PHYSIOLOGICAL_SPREAD` if reported $SD > SD_{\text{physiological\_ref\_max}}$.

---

## 3. FastMCP Tool Implementations in `forensic-math-engine`

The following FastMCP tools are registered in `mcp_servers/forensic_math_mcp.py`:

```python
@mcp.tool()
def audit_regression_triangulation(
    estimate: float,
    lower_ci: float,
    upper_ci: float,
    reported_p: float,
    is_log_scale: bool = True,
    alpha: float = 0.05
) -> Dict[str, Any]:
    """
    Audits multivariable regression models (OR, HR, Beta) for mathematical coherence between
    the effect estimate, 95% Confidence Interval, and reported p-value.
    Reconstructs implied SE and recalculates exact Wald Z test statistic.
    """
    ...

@mcp.tool()
def verify_ai_confusion_matrix_triangulation(
    accuracy: float,
    sensitivity: float,
    specificity: float,
    n_positive: Optional[int] = None,
    n_negative: Optional[int] = None,
    prevalence: Optional[float] = None,
    tolerance: float = 0.03
) -> Dict[str, Any]:
    """
    Audits diagnostic biomarker and AI classifier performance metric coherence.
    Enforces the mathematical relationship: Accuracy = Sensitivity * P + Specificity * (1 - P).
    Detects impossible metric triads commonly found in fabricated AI-for-medicine publications.
    """
    ...

@mcp.tool()
def audit_cross_table_marginal_conservation(
    count: int,
    percentage: float,
    n_total: int,
    subgroup_name: str = "",
    parent_n: Optional[int] = None
) -> Dict[str, Any]:
    """
    Audits patient count continuity and marginal percentage parity across tables.
    Checks:
    1. Marginal percentage consistency: count == round(pct * n_total / 100)
    2. Subgroup sample size conservation: n_total <= parent_n
    """
    ...

@mcp.tool()
def audit_physiological_variance_bounds(
    variable_name: str,
    mean: float,
    sd: float,
    n: int = 1,
    physiological_min_sd: Optional[float] = None,
    physiological_max_sd: Optional[float] = None,
    is_strictly_positive: bool = True
) -> Dict[str, Any]:
    """
    Evaluates continuous laboratory/physiological variables against clinical boundaries and reference ranges.
    Checks:
    1. Zero variance on non-zero continuous measurement (SD == 0.0 when Mean > 0)
    2. Negative biological boundary violation: Mean - 2*SD < 0 on strictly positive vitals
    3. Severe variance compression: SD < 20% of reference physiological SD
    4. Impossible physiological spread: SD > reference physiological maximum SD
    """
    ...
```

---

## 4. Test Verification Suite (`tests/test_forensic_math_suite.py`)

All 9 sieves and the 4 new deterministic engines are tested in `tests/test_forensic_math_suite.py`:
- `test_consistent_wald_regression`: Verifies consistent OR=1.85 (95% CI 1.20–2.85), $p=0.005$.
- `test_decision_error_ci_crosses_null`: Detects regression decision error where OR=1.15 (95% CI 0.90–1.47, crosses 1.0) but authors claim $p=0.02$.
- `test_impossible_ai_metric_triad_outside_envelope`: Detects impossible ML claims ($ACC=95\%$ while Sens=80% and Spec=85%).
- `test_impossible_ai_metric_triad_prevalence_mismatch`: Detects accuracy discrepancy under known prevalence ($ACC=85\%$ reported vs expected 78% under $P=20\%$).
- `test_consistent_ai_metric_triad`: Validates coherent classifier metrics ($ACC=88.5\%$, Sens=85%, Spec=92%, $P=50\%$).
- `test_marginal_percentage_mismatch`: Catches fabricated $(n, \%)$ proportions ($N=200$, reported count 45 but percentage claimed 15.0%).
- `test_subgroup_parent_overflow`: Catches subgroup sample size ($N=450$) exceeding baseline cohort ($N=300$).
- `test_physiological_variance_compression`: Flags troponin SD ($0.008$) compressing to $< 20\%$ of clinical reference minimum ($0.05$).

**Test Execution:**
```bash
pytest tests/test_forensic_math_suite.py
# 26 passed in 2.20s
```

---

## 5. Expected Diagnostic Sensitivity Impact

| Forensic Engine | Target Literature Domain | Mechanism | Sensitivity Gain |
| :--- | :--- | :--- | :---: |
| **Regression Triangle** | Table 2/3 multivariable models, clinical trials | Reconstructs implied SE; verifies Wald Z and null-crossing | **+10% to +12%** |
| **AI Metric Triangulation** | AI/ML papers, biomarker panels | Enforces $ACC = TPR \cdot P + TNR \cdot (1 - P)$ and envelope | **+8% to +10%** |
| **Marginal & Subgroup Conservation**| Table 1 demographics, subgroup analyses | Enforces $|n - \text{implied}| \le 1$ and $N_{\text{subgroup}} \le N_{\text{parent}}$ | **+5% to +8%** |
| **Physiological Variance Bounds** | Continuous laboratory vitals, biomarker assays | Detects $\sigma < 0.20 \times \sigma_{\text{ref}}$ and non-negative boundaries | **+12% to +15%** |
| **Cumulative Impact** | All published summary tables | Bridges the discrete-only gap into continuous & multivariable data | **Projected: ~55%–65%** |

---

## 6. Specificity Preservation & Consensus Calibration Protocol

Across our 6,000-study empirical benchmark, expanding Gate 3 sieves highlighted a fundamental metascience tradeoff: **The Multiple Comparisons Dragnet ($\alpha$-Inflation Across Dense Tables)**.

In a manuscript with 4 dense tables ($\approx 180$ numerical cells), even a 99.8% specific sieve will generate a single false alarm in $\approx 30.3\%$ of legitimate papers due to benign rounding, unstated log-transforms, or item-level non-response in surveys.

### The Calibrated Consensus Decision Rule:
1. **Fatal Kill-Switch 3 (Structural Impossibility):**
   - $\ge 2$ independent GRIM/GRIMMER/DEBIT impossibilities
   - Impossible AI metric triad ($ACC$ strictly outside $[\text{Sens}, \text{Spec}]$ envelope)
   - Subgroup sample size overflow ($N_{\text{subgroup}} > N_{\text{parent}}$)
   - Severe regression decision error ($p < 0.01$ with 95% CI crossing null or $Z < 1.50$)
   - Extreme physiological variance compression ($\sigma < 0.20 \times \sigma_{\text{ref\_min}}$)
2. **Consensus Cluster Rule:**
   - Any other anomaly requires a cluster of $\ge 2$ distinct flags across different tables/metrics to trigger an automated binary anomaly flag.
   - Isolated single-cell anomalies are routed to Tier 2 Bayesian penalties ($LR = 0.20$ to $0.40$), preserving clean control specificity above 78%–80%.

