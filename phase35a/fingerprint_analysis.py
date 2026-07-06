"""
phase35a/fingerprint_analysis.py — analysis-only fingerprint
extraction from existing rawtables (Will authorization 2026-05-21,
pre-compact). NO eigensolves; reads stored per-φ W1δ patterns + the
(N,L) growth factors. Completes the AM fingerprint (§6 φ-pattern
shape + §2 growth-law fit) from data already on disk.

OUTPUTS: fingerprint_analysis_results.json + console summary.
"""
from __future__ import annotations
import os, json
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))


def load_patterns():
    """Collect 16-φ normalized patterns from results JSONs with phi data.
    Returns list of dicts: {tag, leg, delta, N, lam, L, phi(list), w(list)}."""
    pats = []
    # sub/sup_phi_resolved_L: per_cell[i]['phi_W1d_per_L']
    for fn, leg in [("sub_phi_resolved_L_results.json", "sub"),
                    ("sup_phi_resolved_L_results.json", "sup")]:
        p = os.path.join(HERE, fn)
        if not os.path.exists(p):
            continue
        r = json.load(open(p))
        for c in r["per_cell"]:
            if "phi_W1d_per_L" not in c:
                continue
            lam = c.get("lam_sub", c.get("lam_sup"))
            grid = c.get("phi_grid")
            for L, w in c["phi_W1d_per_L"].items():
                pats.append({"tag": fn.split("_")[0], "leg": leg,
                             "delta": c["delta"], "N": c["N"], "lam": lam,
                             "L": int(L), "phi": grid, "w": w})
    # test2 / tier2: top-level phi_per_L, fixed cell
    for fn, leg in [("test2_sup_L_extend_results.json", "sup"),
                    ("tier2_sup_L_extend_N50k_results.json", "sup"),
                    ("tier2_sup_L_extend_N100k_results.json", "sup")]:
        p = os.path.join(HERE, fn)
        if not os.path.exists(p):
            continue
        r = json.load(open(p))
        cell = r.get("cell", {})
        for L, w in r.get("phi_per_L", {}).items():
            pats.append({"tag": fn.split("_")[0] + "_" + fn.split("_")[-1].split(".")[0],
                         "leg": leg, "delta": cell.get("delta"),
                         "N": cell.get("N"), "lam": cell.get("lam"),
                         "L": int(L), "phi": None, "w": w})
    return pats


def harmonics(w):
    """rfft harmonic content of the φ-pattern (assumes uniform φ grid,
    one period over [0,0.5)). Returns dominant mode (≥1) and the
    fraction of AC power in mode 1 vs higher modes."""
    a = np.asarray(w, float)
    n = len(a)
    f = np.fft.rfft(a - a.mean())
    amp = np.abs(f)
    ac = amp[1:]                              # drop DC
    if ac.sum() == 0 or len(ac) == 0:
        return {"n": n, "dominant_mode": None, "mode1_frac": None,
                "ac_power": 0.0}
    dom = int(np.argmax(ac)) + 1
    mode1_frac = float(ac[0] / ac.sum())
    return {"n": n, "dominant_mode": dom,
            "mode1_frac": round(mode1_frac, 4),
            "mode_amps_norm": [round(float(x / ac.sum()), 4) for x in ac[:6]]}


def norm_pattern(w):
    a = np.asarray(w, float)
    sp = np.ptp(a)
    return (a - a.mean()) / sp if sp > 0 else a - a.mean()


def main():
    pats = load_patterns()
    print("=" * 84)
    print(f"FINGERPRINT ANALYSIS — {len(pats)} φ-patterns loaded (16-φ where present)")
    print("=" * 84)

    # ── §6a: harmonic content per pattern ────────────────────────────
    rows = []
    for p in pats:
        if not p["w"] or len(p["w"]) != 16:
            continue
        h = harmonics(p["w"])
        rows.append({**{k: p[k] for k in ("tag", "leg", "delta", "N", "lam", "L")},
                     **h})
    print(f"\n[§6a] HARMONIC CONTENT (16-φ patterns, n={len(rows)}):")
    for r in rows:
        print(f"  {r['leg']} δ={r['delta']} N={r['N']} L={r['L']:>9}: "
              f"dom_mode={r['dominant_mode']} mode1_frac={r['mode1_frac']} "
              f"amps={r.get('mode_amps_norm')}")
    dom_modes = [r["dominant_mode"] for r in rows if r["dominant_mode"]]
    m1 = [r["mode1_frac"] for r in rows if r["mode1_frac"] is not None]
    print(f"  → dominant-mode distribution: "
          f"{dict((m, dom_modes.count(m)) for m in sorted(set(dom_modes)))}")
    print(f"  → mode1_frac range [{min(m1):.3f}, {max(m1):.3f}] "
          f"mean {np.mean(m1):.3f}")

    # ── §6b: L-evolution of pattern SHAPE (does it reorganize with L?) ─
    print(f"\n[§6b] φ-PATTERN SHAPE vs L (normalized-pattern correlation across L "
          f"per cell):")
    by_cell = {}
    for p in pats:
        if not p["w"] or len(p["w"]) != 16:
            continue
        key = (p["leg"], p["delta"], p["N"])
        by_cell.setdefault(key, {})[p["L"]] = norm_pattern(p["w"])
    l_evo = []
    for key, byL in by_cell.items():
        Ls = sorted(byL)
        if len(Ls) < 2:
            continue
        # correlation of smallest-L pattern vs largest-L pattern
        c = float(np.corrcoef(byL[Ls[0]], byL[Ls[-1]])[0, 1])
        l_evo.append({"cell": key, "L_lo": Ls[0], "L_hi": Ls[-1],
                      "shape_corr_lo_hi": round(c, 4)})
        print(f"  {key[0]} δ={key[1]} N={key[2]}: corr(L={Ls[0]}, L={Ls[-1]}) "
              f"= {c:.4f}  (1=shape preserved, <1=reorganizes)")

    # ── §6c: sub vs sup phase at matched N=70k, L=1e5 ────────────────
    print(f"\n[§6c] SUB vs SUP φ-pattern phase (matched N=70k, L=1e5):")
    sub70 = next((p for p in pats if p["leg"] == "sub" and p["N"] == 70000
                  and p["delta"] == 0.5 and p["L"] == 100000 and p["w"]
                  and len(p["w"]) == 16), None)
    sup70 = next((p for p in pats if p["leg"] == "sup" and p["N"] == 70000
                  and p["delta"] == 0.5 and p["L"] == 100000 and p["w"]
                  and len(p["w"]) == 16), None)
    subsup = None
    if sub70 and sup70:
        c = float(np.corrcoef(norm_pattern(sub70["w"]),
                              norm_pattern(sup70["w"]))[0, 1])
        subsup = round(c, 4)
        print(f"  corr(sub λ=0.5, sup λ=1.5) = {c:.4f} "
              f"(+1 in-phase, −1 anti-phase, 0 unrelated)")
    else:
        print("  (matched cells not both available)")

    # ── §6d: cross-N sup pattern similarity (same shape across N?) ───
    print(f"\n[§6d] CROSS-N sup φ-pattern similarity (δ=0.5, λ=1.5, "
          f"common L if any):")
    sup_by_NL = {}
    for p in pats:
        if (p["leg"] == "sup" and p["delta"] == 0.5 and p["w"]
                and len(p["w"]) == 16 and p["N"]):
            sup_by_NL.setdefault(p["L"], {})[p["N"]] = norm_pattern(p["w"])
    crossN = []
    for L, byN in sorted(sup_by_NL.items()):
        Ns = sorted(byN)
        if len(Ns) < 2:
            continue
        for i in range(len(Ns)):
            for j in range(i + 1, len(Ns)):
                c = float(np.corrcoef(byN[Ns[i]], byN[Ns[j]])[0, 1])
                crossN.append({"L": L, "N1": Ns[i], "N2": Ns[j],
                               "corr": round(c, 4)})
                print(f"  L={L}: corr(N={Ns[i]}, N={Ns[j]}) = {c:.4f}")
    if not crossN:
        print("  (no common-L cross-N pairs at 16-φ)")

    # ── §2: growth-factor law fit ────────────────────────────────────
    print(f"\n[§2] GROWTH-FACTOR LAW (sup δ=0.5, λ=1.5; substrate/L=1e5 spread):")
    gN = np.array([50000, 70000, 100000], float)
    gF = np.array([0.93, 4.99, 118.5], float)
    # power law: log g = p log N + c
    pp = np.polyfit(np.log(gN), np.log(gF), 1)
    # exponential: log g = b N + c
    pe = np.polyfit(gN, np.log(gF), 1)
    # residuals
    pl_pred = np.exp(np.polyval(pp, np.log(gN)))
    ex_pred = np.exp(np.polyval(pe, gN))
    pl_res = float(np.sqrt(np.mean((np.log(gF) - np.log(pl_pred)) ** 2)))
    ex_res = float(np.sqrt(np.mean((np.log(gF) - np.log(ex_pred)) ** 2)))
    print(f"  data: N={list(gN.astype(int))} growth={list(gF)}")
    print(f"  power-law  g ∝ N^{pp[0]:.2f}  (log-log slope; RMSE_log={pl_res:.4f})")
    print(f"  exponential g ∝ exp({pe[0]:.2e}·N)  (RMSE_log={ex_res:.4f})")
    # log-log slope is non-constant (accelerating) — note it
    s1 = (np.log(gF[1]) - np.log(gF[0])) / (np.log(gN[1]) - np.log(gN[0]))
    s2 = (np.log(gF[2]) - np.log(gF[1])) / (np.log(gN[2]) - np.log(gN[1]))
    print(f"  log-log local slope: {s1:.2f} (50k→70k) → {s2:.2f} (70k→100k) "
          f"— ACCELERATING ⇒ faster than power law; ~exponential-or-steeper in N")
    print(f"  CAVEAT: 3 points only; extrapolation beyond N=100k unreliable; "
          f"fit is a fingerprint-feature summary, not a predictor.")

    rec = {"analysis": "AM fingerprint extraction (φ-pattern + growth-law), "
                       "analysis-only from existing rawtables",
           "n_patterns_16phi": len(rows),
           "harmonic_content": rows,
           "dominant_mode_distribution":
               {str(m): dom_modes.count(m) for m in sorted(set(dom_modes))},
           "mode1_frac_summary": {"min": round(min(m1), 4), "max": round(max(m1), 4),
                                   "mean": round(float(np.mean(m1)), 4)},
           "L_evolution_shape_corr": l_evo,
           "sub_sup_phase_corr_N70k_L1e5": subsup,
           "cross_N_sup_pattern_corr": crossN,
           "growth_law": {"N": list(gN.astype(int)), "growth": list(gF),
                          "power_law_exponent": round(float(pp[0]), 3),
                          "power_law_RMSE_log": round(pl_res, 4),
                          "exp_rate_per_N": float(pe[0]),
                          "exp_RMSE_log": round(ex_res, 4),
                          "loglog_local_slopes": [round(float(s1), 3),
                                                   round(float(s2), 3)],
                          "verdict": "log-log slope accelerates (4.9→9.0); "
                                     "faster than power-law; ~exponential or "
                                     "steeper in N; 3-point fit, no extrapolation"}}
    def _jsafe(o):
        if isinstance(o, np.integer): return int(o)
        if isinstance(o, np.floating): return float(o)
        if isinstance(o, (np.ndarray, tuple)): return list(o)
        return str(o)
    json.dump(rec, open(os.path.join(HERE, "fingerprint_analysis_results.json"),
                        "w"), indent=1, default=_jsafe)
    print(f"\n  saved fingerprint_analysis_results.json")
    print("=" * 84)


if __name__ == "__main__":
    main()
