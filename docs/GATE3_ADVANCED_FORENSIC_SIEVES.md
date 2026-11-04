# Gate 3 Advanced Mathematical & Continuous Forensic Sieves
## Empirical Upgrade Specification (Derived from the 2,000-Study Benchmark)

**Target Skill:** `forensic-research-auditor`  
**Target Server:** `forensic-math-engine` (FastMCP)  
**Origin:** Empirical findings from 2,000 real studies (7,077 tables, 79,278 rows) across Europe PMC and Retraction Watch.

---

## 1. Architectural Purpose & Rationale

The 2,000-study empirical benchmark demonstrated that while discrete integer granularity sieves (**GRIM** and **GRIMMER**) achieve **50.00% sensitivity** on integer tables ($N < 100$), overall table sensitivity on real-world data fraud retractions was **25.00%**. 

This performance envelope was bounded by two empirical realities:
1. **The "Excel Trap" (Formula-Consistent Fabrication):** Fraudsters who fabricate patient rows in spreadsheets and calculate summary tables using `=AVERAGE()` and `=STDEV()` produce mathematically self-consistent means and SDs that pass basic rounding and parity checks.
2. **The "Continuous Biomarker Gap":** **92.6%** of false-negative data retractions reported continuous biological concentrations (viral load, cytokines, enzymes, hemodynamic pressures), percentages, or survival models where discrete integer arithmetic cannot physically run.

This specification defines **5 advanced deterministic sieves** to bridge these gaps, expanding Gate 3 from discrete integer checking into bounded continuous distributions, multi-table conservation, and matrix linear algebra.

---

## 2. Sieve 1: Continuous Biomarker Boundary & Biological Plausibility Sieve

### Mathematical Principle
Biological concentrations, laboratory biomarkers, and physical measurements are strictly non-negative ($X \ge 0$). Under standard Gaussian or symmetric reporting conventions ($M \pm SD$), reporting a mean and standard deviation where:

$$\mu - 2 \cdot \sigma < 0 \implies \frac{\mu}{\sigma} < 2.0$$

indicates that if the distribution were truly normal, more than 2.28% of biological observations would be negative (e.g., negative viral load, negative troponin). This represents either:
1. **Physical Impossibility:** Falsified baseline parameters invented without regard to physical zero boundaries.
2. **Extreme Positive Skewness Violation:** The underlying variable is heavily skewed, in which case reporting $M \pm SD$ violates international statistical reporting standards (SAMPL guidelines) and disguises severe variance compression.

### Detection Rules
1. **Strictly Positive Physical Boundary:** For biomarkers tagged as strictly positive, flag `IMPOSSIBLE_NEGATIVE_BIOMARKER_RANGE` if $\mu - 2\sigma < 0$ and authors do not state log-normal or non-parametric transformations.
2. **Zero Variance on Continuous Measurements:** Flag `ZERO_SD_CONTINUOUS_VARIABLE` if $\sigma = 0.0$ on any continuous measurement where $\mu > 0$ and $N \ge 5$.
3. **Implied SE-for-SD Misreporting (Variance Compression):** Reconstruct implied standard deviation $\sigma_{\text{implied}} = SD \times \sqrt{N}$. If $\sigma_{\text{implied}}$ is $< 25\%$ of established physiological reference ranges, flag `IMPLAUSIBLE_VARIANCE_COMPRESSION_SE_FOR_SD` ($LR = 0.15$).

### Python / FastMCP Implementation
```python
def verify_continuous_biomarker_boundary(
    variable_name: str,
    mean: float,
    sd: float,
    n: int,
    is_strictly_positive: bool = True,
    physiological_min_sd: float = None
) -> dict:
    anomalies = []
    
    # Rule 1: Zero standard deviation on non-zero continuous measurement
    if sd == 0.0 and mean > 0.0:
        anomalies.append(f"ZERO_SD_CONTINUOUS_VARIABLE({variable_name}, M={mean}, N={n})")
        
    # Rule 2: Non-negative biological boundary violation
    if is_strictly_positive and mean > 0.0 and (mean - 2.0 * sd) < 0.0:
        pct_negative = stats.norm.cdf(0.0, loc=mean, scale=sd) * 100.0
        anomalies.append(
            f"SKEWNESS_BOUNDARY_VIOLATION({variable_name}, M={mean}, SD={sd}, "
            f"Implies {pct_negative:.1f}% negative values under normal reporting)"
        )
        
    # Rule 3: SE-for-SD compression
    if physiological_min_sd is not None and sd < (0.25 * physiological_min_sd):
        anomalies.append(
            f"SUSPICIOUS_VARIANCE_COMPRESSION({variable_name}, SD={sd}, RefSD={physiological_min_sd})"
        )
        
    return {
        "variable": variable_name,
        "mean": mean,
        "sd": sd,
        "n": n,
        "anomalies": anomalies,
        "verdict": "FLAGGED" if anomalies else "CONSISTENT"
    }
```

---

## 3. Sieve 2: SPRITE Bounded Discrete Distribution Reconstruction

### Mathematical Principle
Developed by Heathers et al. (2018), **SPRITE** (Sample Parameter Reconstruction via Iterative TEchniques) tests whether **any** discrete response distribution constrained by sample size $N$ and bounded range $[X_{\min}, X_{\max}]$ (e.g. Likert scale $1$ to $5$, or clinical symptom score $0$ to $20$) can mathematically produce the reported Mean and Standard Deviation.

Even if an invented mean and SD divide cleanly in basic math, the bounded envelope of discrete items imposes strict kurtosis and variance limits:

$$\sigma_{\max}^2 = (X_{\max} - \mu)(\mu - X_{\min})$$

If $\sigma^2 > \sigma_{\max}^2$, no combination of responses within $[X_{\min}, X_{\max}]$ can produce that standard deviation.

### Detection Rules
1. **Variance Upper Bound:** If $\sigma^2 > (X_{\max} - \mu)(\mu - X_{\min})$, flag `SPRITE_VARIANCE_EXCEEDS_BOUNDS`.
2. **Frequency Non-Negativity:** Iterate integer allocations to test if any valid frequency distribution satisfies:
   $$\sum_{i=X_{\min}}^{X_{\max}} f_i = N, \quad \sum_{i=X_{\min}}^{X_{\max}} i \cdot f_i = \text{round}(\mu \cdot N), \quad \frac{1}{N-1} \sum_{i=X_{\min}}^{X_{\max}} f_i (i - \mu)^2 \approx \sigma^2$$
   If no non-negative integer vector $\{f_i \ge 0\}$ exists, flag `SPRITE_IMPOSSIBLE_BOUNDED_DISTRIBUTION`.
3. **Cross-Arm Homoscedasticity Ratio:** In randomized multi-arm trials, flag `UNNATURAL_ARM_HOMOSCEDASTICITY` if the ratio of standard deviations across independent intervention arms satisfies:
   $$0.995 \le \frac{\sigma_{\text{arm1}}}{\sigma_{\text{arm2}}} \le 1.005 \quad \text{for } N_{\text{total}} \ge 40$$

---

## 4. Sieve 3: Correlation Matrix Positive Semi-Definiteness Sieve

### Mathematical Principle
In observational studies, psychology, and epidemiology, Table 2 and Table 3 report correlation matrices ($r$) or regression models ($\beta$).

Any authentic Pearson/Spearman correlation matrix $R$ must be **positive semi-definite** ($R \succeq 0$):
1. All eigenvalues must be non-negative: $\lambda_{\min}(R) \ge 0$.
2. Every principal minor must be non-negative (Sylvester's Criterion). For any 3 pairwise correlations:

$$\det(R_{3 \times 3}) = 1 - r_{12}^2 - r_{23}^2 - r_{13}^2 + 2 r_{12} r_{23} r_{13} \ge 0$$

When researchers invent correlation tables without generating multivariate data, they frequently pick pairwise coefficients that violate transitivity or yield negative eigenvalues ($\lambda_{\min} < 0$).

### Python / FastMCP Implementation
```python
def verify_correlation_matrix_definiteness(labels: list, matrix: list) -> dict:
    R = np.array(matrix, dtype=float)
    p = R.shape[0]
    
    # Check diagonal
    if not np.allclose(np.diag(R), 1.0):
        return {"verdict": "INVALID_DIAGONAL", "details": "Diagonal elements must equal 1.0"}
        
    # Check symmetry
    if not np.allclose(R, R.T, atol=1e-3):
        return {"verdict": "ASYMMETRIC_MATRIX", "details": "Correlation matrix must be symmetric"}
        
    # Eigenvalue decomposition
    eigenvalues = np.linalg.eigvalsh(R)
    min_eigenval = float(np.min(eigenvalues))
    
    if min_eigenval < -1e-4:
        return {
            "verdict": "NON_POSITIVE_DEFINITE",
            "min_eigenvalue": round(min_eigenval, 5),
            "eigenvalues": [round(float(e), 5) for e in eigenvalues],
            "flag": f"CORRELATION_MATRIX_IMPOSSIBLE(min_lambda={min_eigenval:.5f})"
        }
        
    return {
        "verdict": "CONSISTENT_POSITIVE_DEFINITE",
        "min_eigenvalue": round(min_eigenval, 5)
    }
```

---

## 5. Sieve 4: Tabular NHST Recalculation & P-Hacking Cliff Sieve

### Mathematical Principle
While inline text tools (`statcheck`) scan sentences, scientific tables frequently report statistical tests in tabular columns: `Variable | t | df | p-value` or `Group | Chi-square | p`.

### Detection Rules
1. **Tabular Decision Error Sieve:**
   Directly recompute cumulative test distributions from table cells:
   - For Student's $t$: $p_{\text{recalc}} = 2 \cdot (1 - F_t(|t|, df))$
   - For Snedecor's $F$: $p_{\text{recalc}} = 1 - F_F(F, df_1, df_2)$
   - For Pearson's $\chi^2$: $p_{\text{recalc}} = 1 - F_{\chi^2}(\chi^2, df)$
   Flag a **Tabular Decision Error** if reported $p < 0.05$ while $p_{\text{recalc}} \ge 0.05$.

2. **The "P-Hacking Cliff" Ratio ($R_{\text{cliff}}$):**
   Count all reported $p$-values across tables and text. Compare the frequency of $p$-values in the suspicious zone immediately below significance vs. immediately above:

$$R_{\text{cliff}} = \frac{N(p \in [0.041, 0.049])}{N(p \in [0.051, 0.059])}$$

Under true null or true effect distributions, $p$-value density is smooth and monotonically non-increasing across the threshold $0.05$. If $R_{\text{cliff}} \ge 3.0$ with $N \ge 6$, flag `P_HACKING_CLIFF_ANOMALY` ($LR = 0.25$).

---

## 6. Sieve 5: Cross-Table Sample Size ($N$) Conservation Sieve

### Mathematical Principle
In clinical and biomedical studies, the sample size across tables must strictly adhere to the CONSORT / STROBE flow. In fraudulent manuscripts, patient counts frequently shift between Table 1 (demographics), Table 2 (efficacy), and Table 3 (subgroups).

### Detection Rules
1. **Marginal Total Inconsistency:** In categorical summary tables reporting counts and percentages $(n, \%)$:

$$\left| n - \text{round}\left( \frac{\% \cdot N}{100} \right) \right| = 0$$

If $|n - \text{implied}| \ge 2$, flag `MARGINAL_PERCENTAGE_MISMATCH`.
2. **Cross-Table $N$ Inflation:** Flag `SAMPLE_SIZE_EXPANSION_ACROSS_TABLES` if Table 2 reports total evaluated patients $N_{\text{outcomes}} > N_{\text{baseline}}$ without explicit documentation of newly enrolled cohorts.

---

## 7. FastMCP Registration Blueprint (`forensic-math-engine`)

```python
# New FastMCP tool definitions to register in mcp_servers/forensic_math_mcp.py:

@mcp.tool()
def audit_continuous_biomarker_bounds(variable: str, mean: float, sd: float, n: int, is_strictly_positive: bool = True) -> dict:
    """Evaluates non-negative boundary constraints (M - 2*SD < 0) and zero variance."""
    ...

@mcp.tool()
def verify_sprite_distribution(mean: float, sd: float, n: int, min_val: int, max_val: int) -> dict:
    """Reconstructs discrete integer frequency distributions within bounded scales."""
    ...

@mcp.tool()
def audit_correlation_matrix(matrix: list, variable_names: list = None) -> dict:
    """Verifies that correlation matrix is positive semi-definite (all eigenvalues >= 0)."""
    ...

@mcp.tool()
def audit_tabular_nhst_cell(test_type: str, stat_val: float, df1: float, df2: float, reported_p: float) -> dict:
    """Recalculates exact p-values for table cell test statistics (t, F, chi2)."""
    ...
```

---

## 8. Expected Impact on Gate 3 Diagnostic Sensitivity

| New Sieve Module | Target Vulnerability | Prior Limitation | Projected Detection Gain |
| :--- | :--- | :--- | :---: |
| **Sieve 1: Biomarker Envelope** | Continuous lab assays ($N > 100$) | GRIM inapplicable on continuous data | **+15% to +20%** |
| **Sieve 2: SPRITE Reconstruction** | Formula-derived Excel spreadsheets | GRIM passed valid formula averages | **+10% to +15%** |
| **Sieve 3: Correlation Definiteness**| Multivariate regression tables | Untested correlation transitivity | **+5% to +10%** |
| **Sieve 4: Tabular NHST & P-Cliff** | Tabular test statistic columns | Statcheck only mined inline prose | **+10% to +15%** |
| **Sieve 5: Cross-Table $N$** | Patient attrition across tables | Isolated table extraction | **+5% to +10%** |

*This upgrade elevates Gate 3 from a discrete-only rounding validator into a complete, mathematically grounded continuous and multivariate forensic verification engine.*
