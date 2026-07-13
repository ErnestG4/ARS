"""
approximability/panel_D_records.py — Panel D: the record / exceedance process on CF partial quotients.

The natural Λ-home: order statistics on the quotients a_n DIRECTLY — no unfolding, no smoothness gate, no FIX-2 path.
Tool-risk ≈ 0 (the panel after the one where the Farey gate got retuned).

THEORY / PRE-REGISTRATION (written before reading π):
  Borel–Bernstein: for a.e. α, a_n ≥ φ(n) infinitely often ⟺ Σ 1/φ(n) = ∞.
  Record process = running maxima of (a_n). Three controls, maximally different record CLOCKS:
    • metallic [ā]: exactly 1 record (a_1=a; never exceeded). Record count R(N)=1 ∀N.  [HARD ZERO GROWTH]
    • e = [2;1,2,1,1,4,1,1,6,…]: the 2,4,6,8,… spine ⇒ a new record every ~3rd quotient ⇒ R(N) ~ N/3 LINEAR.
      Euler's closed form makes R_e(N) EXACT (computed here from e's own CF, not modeled).
    • π (if Gauss–Kuzmin-typical): R(N) ~ H_N = Σ 1/n ≈ ln N + γ (iid record law; CF quotients weakly dependent).
  Borel–Bernstein exceedance a_n ≥ n (φ=n, Σ1/n=∞ ⇒ i.o. for a.e. α):
    • π (typical): count grows ~ (ln N)/ln2 → i.o.   • metallic: saturates at a (finite).   • e: saturates small (finite).
  ⇒ π is the LONE a.e.-typical sequence on the BB axis; metallic & e are both measure-zero exceptions (opposite reasons).

READ-ONLY. Run: PYTHONPATH=$HOME/fmexplorer/riemann_explorer $HOME/fmexplorer/bin/python3 \
                  approximability/panel_D_records.py
"""
import os, sys, json
_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _ROOT)
import numpy as np
import mpmath as mp

mp.mp.dps = 1800
OUT = os.path.dirname(os.path.abspath(__file__))
GAMMA = 0.5772156649015329
N = 600


def cf_digits(x, n):
    a = []; y = mp.mpf(x)
    for _ in range(n):
        ai = int(mp.floor(y)); a.append(ai); f = y - ai
        if f == 0: break
        y = 1.0 / f
    return a


def records(quotients):
    """Running-maxima record process: return (record_times, record_values, record_count_curve)."""
    rt, rv, curve = [], [], []
    m = 0; cnt = 0
    for n, a in enumerate(quotients, 1):
        if a > m:
            m = a; cnt += 1; rt.append(n); rv.append(a)
        curve.append(cnt)
    return rt, rv, np.array(curve)


def bb_exceed(quotients, phi):
    """Cumulative count of a_n ≥ φ(n) (Borel–Bernstein exceedances)."""
    c = 0; out = []
    for n, a in enumerate(quotients, 1):
        if a >= phi(n): c += 1
        out.append(c)
    return np.array(out)


def gk_random(n, seed=1):
    rng = np.random.default_rng(seed)
    ks = np.arange(1, 200000); cdf = 1.0 - np.log2(1.0 + 1.0 / (ks + 1))
    return [int(ks[np.searchsorted(cdf, u)]) for u in rng.random(n)]


if __name__ == "__main__":
    print("=" * 84)
    print(f"PANEL D — record / exceedance process on CF quotients (N={N}, no unfold, no gate, no FIX-2)")
    print("=" * 84)

    pid = cf_digits(mp.pi, N); ed = cf_digits(mp.e, N); gk = gk_random(N)
    print(f"  [depth] π resolved to {len(pid)} quotients, e to {len(ed)} (mpmath dps={mp.mp.dps}).")
    Q = {"golden": [1]*N, "silver": [2]*N, "bronze": [3]*N, "e": ed, "pi": pid, "GK-random": gk}

    # ---- PRE-REGISTER (before reading π's verdict) ----
    depths = [10, 30, 100, 300, min(N, len(pid))]
    print(f"\n[pre-register] record-count clock R(N):  metallic=1 ∀N ; e≈N/3 (linear) ; π≈H_N≈ln N+γ (a.e.)")
    HN = np.cumsum(1.0 / np.arange(1, N + 1))              # harmonic = iid record expectation
    Re = records(ed)[2]
    print(f"  {'N':>5s} {'R_metallic':>10s} {'R_e(exact)':>10s} {'H_N(π pred)':>11s}")
    for d in depths:
        print(f"  {d:>5d} {1:>10d} {Re[d-1]:>10d} {HN[d-1]:>11.2f}")

    # ---- observed records ----
    print(f"\n[records] observed record COUNT at depth N={min(N,len(pid))}:")
    recs = {}
    for name, q in Q.items():
        rt, rv, curve = records(q)
        recs[name] = {"count": int(curve[-1]), "times": rt[:8], "values": rv[:8], "curve": curve}
        print(f"   {name:10s}  count={curve[-1]:>3d}   first records (pos:val)= "
              + " ".join(f"{t}:{v}" for t, v in list(zip(rt, rv))[:6]))

    # π vs the three pre-registered clocks
    d = min(N, len(pid)) - 1
    rpi = recs["pi"]["curve"][d]; rmet = 1; ree = recs["e"]["curve"][d]; hpred = HN[d]
    print(f"\n   at N={d+1}:  π records={rpi} (H_N pred≈{hpred:.1f}) | metallic=1 | e={ree} (≈N/3={(d+1)//3})")
    # which clock does π match? (log vs linear vs flat)
    ratio_to_H = rpi / hpred; ratio_to_e = rpi / max(ree, 1)
    print(f"   π/H_N={ratio_to_H:.2f}  π/e={ratio_to_e:.3f}  → "
          f"{'π ~ logarithmic (a.e./GK clock) ✓, NOT e-linear, NOT metallic-flat' if 0.5<ratio_to_H<2.0 and ratio_to_e<0.3 else 'see ratios'}")

    # ---- Borel–Bernstein exceedance a_n ≥ n ----
    print(f"\n[Borel–Bernstein] cumulative count of a_n ≥ n  (Σ1/n=∞ ⇒ i.o. for a.e. α):")
    bb_pred_pi = np.cumsum(1.0 / (np.arange(1, N + 1) * np.log(2)))   # Σ 1/(n ln2)
    print(f"  {'target':10s} {'BB count(a_n≥n)':>15s}   interpretation")
    bb = {}
    for name, q in Q.items():
        c = bb_exceed(q, lambda n: n)
        bb[name] = int(c[-1])
        if name.startswith(("golden", "silver", "bronze")):
            interp = f"saturates ≤ a (finite; metallic is measure-zero, NOT a.e.-typical)"
        elif name == "e":
            interp = "saturates small (finite; e's spine 2k@pos~3k ⇒ 2k≥3k never — measure-zero)"
        elif name in ("pi", "GK-random"):
            interp = f"grows (a.e.-typical; pred≈(lnN)/ln2≈{bb_pred_pi[d]:.1f})"
        else:
            interp = ""
        print(f"  {name:10s} {c[-1]:>15d}   {interp}")

    # verdict
    pi_typical = (0.4 < ratio_to_H < 2.5) and bb["pi"] >= 3 and bb["golden"] <= 3
    print(f"\n  VERDICT (Panel D): metallic=hard-zero record clock; e=linear (deterministic spine); "
          f"π={'LOGARITHMIC + BB-i.o. ⇒ a.e./Gauss–Kuzmin-typical' if pi_typical else 'see ratios'}.")
    print(f"  → On the RECORD/Λ axis, π groups with neither metallic nor e — it reads as the GENERIC a.e. number, "
          f"while metallic & e are the two (opposite) measure-zero exceptions. [conditional on π GK-typical, unproven]")

    with open(os.path.join(OUT, "panel_D_records.json"), "w") as fh:
        json.dump({"N": N, "n_pi": len(pid), "n_e": len(ed),
                   "record_counts": {k: recs[k]["count"] for k in recs},
                   "record_first": {k: list(zip(recs[k]["times"], recs[k]["values"])) for k in recs},
                   "H_N_at_depth": float(hpred), "bb_exceed_an_ge_n": bb,
                   "bb_pred_pi": float(bb_pred_pi[d]), "pi_typical": bool(pi_typical)}, fh, indent=2, default=str)
    print("\n  wrote approximability/panel_D_records.json — DONE.")
