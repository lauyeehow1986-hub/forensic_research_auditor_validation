# 01: Mathematical & Statistical Axioms for 10,000 Case vs. 10,000 Control Forensic Validation

## 1. GRIM (Brown & Heathers, 2016)
For integer observations $x_i \in \mathbb{Z}$ across sample size $N$ and scale items $k$, $S = \sum x_i$ must be an integer within $[(\bar{x} - 0.5 \times 10^{-D}) N k, (\bar{x} + 0.5 \times 10^{-D}) N k]$ under at least one of the four rounding rules (`half_to_even`, `half_up`, `half_down`, `truncate`).

## 2. Analytic-GRIMMER (Allard, 2018; Anaya, 2016)
For any integer sum $S$ passing GRIM, $\sum x_i^2 = (N-1)SD^2 + N\bar{x}^2$ must fall within the rounding interval of $SD$ and satisfy the parity identity $\sum x_i^2 \equiv \sum x_i \pmod 2$.

## 3. DEBIT (Heathers & Brown, 2019)
For binary $(0/1)$ outcomes with proportion $p = S/N$, the sample standard deviation is strictly $SD = \sqrt{\frac{N}{N-1} p (1 - p)}$.

## 4. Carlisle Baseline ANOVA & Stouffer Pooling (Carlisle, 2012, 2017)
Across $m$ baseline RCT continuous variables, one-way ANOVA $p$-values are transformed via $z_i = \Phi^{-1}(p_i)$ and pooled into $Z_S = \frac{\sum_{i=1}^m z_i}{\sqrt{m}}$. Right-tail cumulative probability $\Phi(Z_S) > 0.999$ flags hyper-homogeneous baseline variance compression; $\Phi(Z_S) < 0.001$ flags extreme baseline imbalance.

## 5. Wilson 95% Score Confidence Intervals for 10k-vs-10k Diagnostic Proportions
For binomial diagnostic proportions $\hat{p} = k / n$ ($n = 10,000$ Cases or $n = 10,000$ Controls), exact Wilson 95% confidence bounds are:
$$\frac{\hat{p} + \frac{z^2}{2n} \pm z \sqrt{\frac{\hat{p}(1-\hat{p})}{n} + \frac{z^2}{4n^2}}}{1 + \frac{z^2}{n}}, \quad z = 1.95996$$
