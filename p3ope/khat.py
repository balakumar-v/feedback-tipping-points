import numpy as np

def gpd_fit_zs(x):
    """Zhang & Stephens (2009) empirical-Bayes GPD fit used in PSIS (Vehtari et al.). x: sorted exceedances > 0. Returns (k, sigma)."""
    n = len(x); m = 30 + int(np.sqrt(n))
    prior = 3
    xs = x[int(n / 4 + 0.5) - 1]
    b = 1 / x[-1] + (1 - np.sqrt(m / (np.arange(1, m + 1) - 0.5))) / (prior * xs)
    k = np.log1p(-b[:, None] * x[None, :]).mean(1)
    L = n * (np.log(-b / k) - k - 1)
    w = 1 / np.exp(L - L[:, None]).sum(1)
    keep = w > 10 * np.finfo(float).eps
    b_hat = (b[keep] * w[keep]).sum() / w[keep].sum()
    k_hat = np.log1p(-b_hat * x).mean()
    sigma = -k_hat / b_hat
    k_hat = (n * k_hat + prior * 0.5) / (n + prior)   # shrink toward 0.5 as in PSIS
    return k_hat, sigma

def pareto_khat(w):
    w = np.asarray(w, float); w = w[w > 0]
    n = len(w)
    if n < 50: return np.nan
    M = int(min(0.2 * n, 3 * np.sqrt(n)))
    M = max(M, 10)
    ws = np.sort(w)
    cutoff = ws[-M - 1]
    exc = ws[-M:] - cutoff
    if exc.max() <= 1e-12 * max(cutoff, 1e-12): return 0.0   # no tail
    exc = exc[exc > 0]
    if len(exc) < 5: return 0.0
    k, _ = gpd_fit_zs(np.sort(exc))
    return float(k)

if __name__ == "__main__":
    rng = np.random.default_rng(1)
    for alpha in [4.0, 2.0, 1.5, 1.0, 0.7]:
        ks = [pareto_khat(rng.pareto(alpha, 5000) + 1) for _ in range(20)]
        print(f"Pareto(alpha={alpha}) true k = {1/alpha:.2f} ; estimated k-hat mean {np.mean(ks):.2f}")
    ks = [pareto_khat(np.exp(rng.normal(size=5000))) for _ in range(5)]
    print("lognormal weights k-hat (light-ish tail, expect <0.5):", np.round(np.mean(ks),2))
