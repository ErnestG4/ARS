"""Thread 1 — Thouless per-step total-bandwidth law.

Empirical law spotted in the depth-4 pi data (FLOQUET_RESOLUTION.md):
  per convergent step, total bandwidth of the period-q approximant thins by
    ratio = tw(depth k-1)/tw(depth k) ≈ lambda   when a_k >= 2  (INDEPENDENT of a_k's size)
          = 1 (exactly)                            when a_k == 1
  with ratio/lambda -> 1 from above as lambda grows (O(1/lambda) correction),
  and depth-1 (single impurity, p=1) obeying lambda*tw -> 4 = |spec(free Laplacian)|.

Sharp test: golden (CF all-1s) would, if "a=1 preserves" held literally, keep total
bandwidth CONSTANT across depth -> contradicts Suto's zero-measure Cantor spectrum for
the Fibonacci Hamiltonian. So measure golden/silver/bronze (CF all-m) directly and see
whether the per-step ratio depends only on a_k or on CF context.
"""
import sys, math, json
sys.path.insert(0, ".")
import numpy as np
from numpy.linalg import eigvalsh
from task1_pi_depth5 import potential, convergents

def floquet_bands_tw(V):
    q = len(V)
    H = np.zeros((q, q)); np.fill_diagonal(H, V)
    idx = np.arange(q - 1); H[idx, idx + 1] = 1; H[idx + 1, idx] = 1
    Hp = H.copy(); Hp[0, q - 1] = 1; Hp[q - 1, 0] = 1
    Ha = H.copy(); Ha[0, q - 1] = -1; Ha[q - 1, 0] = -1
    e = np.sort(np.concatenate([eigvalsh(Hp), eigvalsh(Ha)]))
    tw = sum(e[2 * j + 1] - e[2 * j] for j in range(q))
    return q, tw

def metallic_convergents(m, K):
    cf = [m] * K
    ps, qs = convergents(cf)
    return cf, ps, qs

LAMS = [8.0, 24.0, 32.0]
out = {"lams": LAMS, "targets": {}}

# --- metallic targets: golden(1), silver(2), bronze(3); CF is all-m ---
for name, m, qcap in [("golden", 1, 20000), ("silver", 2, 20000), ("bronze", 3, 20000)]:
    cf, ps, qs = metallic_convergents(m, 30)
    # pick depths with q under qcap and >= 2 (need a real period)
    depths = [k for k in range(len(qs)) if 2 <= qs[k] <= qcap]
    rec = {"cf_head": cf[:6], "q": [qs[k] for k in depths], "a_k": [cf[k] for k in depths]}
    for lam in LAMS:
        tws = []
        for k in depths:
            p, q = ps[k], qs[k]
            if math.gcd(p, q) != 1:
                tws.append(None); continue
            _, tw = floquet_bands_tw(potential(p, q, lam))
            tws.append(tw)
        # per-step ratios
        ratios = []
        for i in range(1, len(tws)):
            if tws[i] and tws[i - 1]:
                ratios.append(tws[i - 1] / tws[i])
            else:
                ratios.append(None)
        rec[f"lam{lam:.0f}_tw"] = tws
        rec[f"lam{lam:.0f}_ratio"] = ratios
        rec[f"lam{lam:.0f}_ratio_over_lam"] = [r / lam if r else None for r in ratios]
    out["targets"][name] = rec

json.dump(out, open("thouless_law.json", "w"), indent=1)

# --- pretty print ---
for name in ("golden", "silver", "bronze"):
    rec = out["targets"][name]
    print(f"\n=== {name}  CF={rec['cf_head']}  q={rec['q'][:8]}... ===")
    print(f"{'q':>7} {'a_k':>4} | " + " ".join(f"lam{int(l):<2} ratio(/lam)" for l in LAMS))
    qs = rec["q"]; aks = rec["a_k"]
    for i in range(len(qs)):
        row = f"{qs[i]:>7} {aks[i]:>4} | "
        for lam in LAMS:
            if i == 0:
                row += f"{'  tw=%.3e' % rec[f'lam{lam:.0f}_tw'][0]:>18} "
            else:
                r = rec[f"lam{lam:.0f}_ratio"][i - 1]
                rl = rec[f"lam{lam:.0f}_ratio_over_lam"][i - 1]
                row += f"{r:8.4f}({rl:6.4f}) " if r else f"{'--':>18} "
        print(row)
print("\nwrote thouless_law.json")
