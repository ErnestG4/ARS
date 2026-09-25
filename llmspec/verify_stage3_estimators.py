"""Synthetic known answers for stage3_analyze's estimators. Exit 1 on any failure.
  htsr_mle_v1: lambda ~ Pareto(alpha) (n=2048) -> alpha within 0.3 and boot p >= 0.1 in >= 3/4 draws;
               Wishart eigenvalues (2048 x 8192) -> power-law fit FAILS (p < 0.1) in >= 3/4 draws.
  mp_fit_v1:   Gaussian 2048 x 8192 + k planted spikes (k = 0, 3, 10) -> exactly k upper outliers.
  changepoints: piecewise-linear with one break + noise -> one change point within +-1 index.
--redpath: feed Wishart eigenvalues to the Pareto check; it must FAIL (exit 0 iff it does)."""
import sys
import numpy as np, torch
import stage3_analyze as A

rng = np.random.default_rng(3)
fails = []
def pareto_check(name, sampler, alpha):
    ok = 0
    for i in range(4):
        lam = sampler(i)
        r = A.htsr_mle_v1(np.sqrt(lam), seed=i)
        good = abs(r["alpha_raw"] - alpha) <= 0.3 and r["boot_p"] >= 0.1
        ok += good
        print(f"  {name} draw {i}: alpha {r['alpha_raw']:.3f} D {r['ks_D']:.4f} p {r['boot_p']:.2f} n_tail {r['n_tail']}")
    if ok < 3: fails.append(f"{name}: {ok}/4")
def wishart(i):
    g = torch.Generator(device="cuda").manual_seed(100 + i)
    W = torch.randn((2048, 8192), generator=g, device="cuda", dtype=torch.float64)
    return torch.linalg.eigvalsh(W @ W.T).cpu().numpy()
if "--redpath" in sys.argv:
    pareto_check("wishart-as-pareto", wishart, 2.5)
    print("REDPATH failures:", fails); sys.exit(0 if fails else 1)
for a in (2.0, 3.0):
    pareto_check(f"pareto{a}", lambda i, a=a: (1 - rng.random(2048)) ** (-1 / (a - 1)), a)
nf = 0
for i in range(4):
    r = A.htsr_mle_v1(np.sqrt(wishart(i)), seed=i); nf += r["powerlaw_fit_fails"]
    print(f"  wishart draw {i}: p {r['boot_p']:.2f} fails={r['powerlaw_fit_fails']}")
if nf < 3: fails.append(f"wishart fit-fails only {nf}/4")
# mp_fit_v1 with spikes; tau+ from 40 plain draws
g = torch.Generator(device="cuda").manual_seed(7)
s = 0.02; m, n = 2048, 8192
def sig_of(W): return torch.linalg.eigvalsh(W @ W.T).clamp_min(0).sqrt().flip(0).cpu().numpy()
smax = [sig_of(torch.randn((m, n), generator=g, device="cuda", dtype=torch.float64) * s)[0] / (s * (np.sqrt(m) + np.sqrt(n))) for _ in range(40)]
tau_p = float(np.quantile(smax, 0.99))
for k in (0, 3, 10):
    W = torch.randn((m, n), generator=g, device="cuda", dtype=torch.float64) * s
    if k:
        u = torch.linalg.qr(torch.randn((m, k), generator=g, device="cuda", dtype=torch.float64))[0]
        v = torch.linalg.qr(torch.randn((n, k), generator=g, device="cuda", dtype=torch.float64))[0]
        W = W + (u * (s * np.sqrt(n) * torch.linspace(2.0, 4.0, k, device="cuda", dtype=torch.float64))) @ v.T
    r = A.mp_fit_v1(sig_of(W), m, n, float(W.pow(2).mean().sqrt()), tau_p, 0.99)
    print(f"  spikes {k}: upper outliers {r['n_upper_outliers']} scale/true {r['mp_scale']/s:.4f}")
    if r["n_upper_outliers"] != k: fails.append(f"mp_fit spikes {k} -> {r['n_upper_outliers']}")
# mp_fit_v2 on the same spiked matrices, and the v1 collapse on a heavy-tailed (Student-t nu=2.5) matrix
for k in (0, 3, 10):
    W = torch.randn((m, n), generator=g, device="cuda", dtype=torch.float64) * s
    if k:
        u = torch.linalg.qr(torch.randn((m, k), generator=g, device="cuda", dtype=torch.float64))[0]
        v = torch.linalg.qr(torch.randn((n, k), generator=g, device="cuda", dtype=torch.float64))[0]
        W = W + (u * (s * np.sqrt(n) * torch.linspace(2.0, 4.0, k, device="cuda", dtype=torch.float64))) @ v.T
    r2 = A.mp_fit_v2(sig_of(W), m, n, tau_p, 0.99)
    print(f"  v2 spikes {k}: upper outliers {r2['mp2_n_upper_outliers']} scale/true {r2['mp2_scale']/s:.4f}")
    if r2["mp2_n_upper_outliers"] != k: fails.append(f"mp_fit_v2 spikes {k} -> {r2['mp2_n_upper_outliers']}")
z = torch.randn((m, n), generator=g, device="cuda", dtype=torch.float64)
chi = torch.distributions.Chi2(torch.tensor(2.5, device="cuda", dtype=torch.float64)).sample((m, n))
Wt = z / torch.sqrt(chi / 2.5) * s
st = sig_of(Wt)
r1 = A.mp_fit_v1(st, m, n, float(Wt.pow(2).mean().sqrt()), tau_p, 0.99)
r2 = A.mp_fit_v2(st, m, n, tau_p, 0.99)
print(f"  heavy-tailed t2.5: v1 outliers {r1['n_upper_outliers']} (collapse expected), v2 outliers {r2['mp2_n_upper_outliers']}")
if not r1["n_upper_outliers"] > 0.5 * len(st): fails.append("v1 collapse not reproduced on t2.5 (DEGENERATE flag untested)")
if r2["mp2_n_upper_outliers"] > 0.5 * len(st): fails.append("v2 also collapses on t2.5")
x = np.log10(np.array([1, 2, 4, 8, 16, 32, 64, 128, 256, 512, 1000, 2000, 4000, 8000, 16000, 32000, 64000, 128000], float))
y = np.where(x < 2.5, 1.0 + 0.1 * x, 1.25 - 0.8 * (x - 2.5)) + 0.01 * rng.standard_normal(len(x))
cps, _ = A.changepoints(x, y)
true = int(np.searchsorted(x, 2.5))
print("  changepoints:", cps, "true index", true)
if len(cps) != 1 or abs(cps[0] - true) > 1: fails.append(f"changepoints {cps} vs {true}")
print("FAILURES:", fails or "none"); sys.exit(1 if fails else 0)
