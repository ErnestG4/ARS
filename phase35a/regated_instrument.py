"""
phase35a/regated_instrument.py — RE-GATED SCOPING INSTRUMENT (not 35a execution).

Built to Will's three specs (2026-05-16), after the prior campaign's
Stage-0 gate failed the instrument on known truth:

  SPEC-1 clock metric: drop KS-to-δ AND Kuiper (degenerate vs a point
    mass by construction). Primary = var(s) (exact clock ⇒ var=0 to
    machine precision). Companion = Wasserstein-1-to-δ = E[|s−1|]
    (non-degenerate "distance to clock"). KS-Wigner / KS-Poisson kept
    (non-degenerate vs continuous laws), on the §7.ter.59 floor.
  SPEC-2 clock-recognition: the classifier's clock→BR_artifact is a
    correct DETECTION mislabeled (true clock is a legitimate maximally
    rigid class, not noise). Fix = the missing clock CALIBRATOR: this
    instrument carries an exact-clock reference and derives a
    `clock_rigid` label (W1δ ≤ τ_clock, τ_clock calibrated from the
    exact clock at matched N). The raw quadrant is still recorded
    (horizon), but the decisive label no longer mislabels clock.
  SPEC-3 IDS-leg gate: λ=0 cannot gate the IDS leg (no gaps). Use the
    rational-θ periodic approximant θ=p/q (Fibonacci convergents) —
    a genuine AM operator, spectrum = q bands, IDS plateaus EXACTLY at
    k/q (rational gap-labelling). Gate C confirms unfold_ids_ref places
    the gaps at k/q and the periodic NNS is well-behaved.

HARD RULE: Gates A,B,C must ALL pass before the grid is run/interpreted.
Any gate failure ⇒ STOP, report (instrument still broken), no grid,
no auto-adjudication. §7.ter.55/57.

Still SCOPING, still brief-and-hold; NO 35a execution, NO calibrator
built, NO NNS derived. Trimmed grid for turnaround.
"""
from __future__ import annotations
import os, sys, json, warnings
import numpy as np
from scipy.linalg import eigvalsh_tridiagonal

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(THIS_DIR))
from arithmetic_toolkit import joint_q_profile, joint_quadrant_diagnostic  # side-effect-free

GOLDEN = (np.sqrt(5.0) - 1.0) / 2.0
Q_MAX, MIN_EV = 30, 30


# ── operator (θ arbitrary; θ=0 + λ=0 ⇒ free Laplacian) ────────────────────
def am_eigs(lam, N, phi, theta=GOLDEN):
    n = np.arange(N, dtype=np.float64)
    diag = 2.0 * lam * np.cos(2.0 * np.pi * (theta * n + phi))
    return eigvalsh_tridiagonal(diag, np.ones(N - 1))


# ── unfoldings (inline; no side-effecting import) ─────────────────────────
def unfold_poly(eigs, deg):
    e = np.asarray(eigs, float)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        c = np.polyfit(e, np.arange(1, e.size + 1, dtype=float), deg)
    return np.polyval(c, e)


def unfold_ids_ref(eigs, eigs_ref):
    er = np.sort(np.asarray(eigs_ref, float))
    idx = np.searchsorted(er, np.asarray(eigs, float), side="right")
    return (idx / er.size) * len(eigs)


def unfold_arcsine(eigs, N):
    e = np.clip(np.asarray(eigs, float) / 2.0, -1.0, 1.0)
    return (0.5 + np.arcsin(e) / np.pi) * N


# ── spacings + metrics ────────────────────────────────────────────────────
def spacings(unfolded):
    u = np.sort(unfolded)
    d = np.diff(u)
    d = d[int(0.02 * len(d)):int(0.98 * len(d))]
    m = d.mean()
    return d / m if m > 0 else d


def _cdf_wigner(s):
    g = np.linspace(0, max(s.max(), 6.0), 6001)
    pdf = (32 / np.pi**2) * g * g * np.exp(-4 * g * g / np.pi)
    cdf = np.concatenate([[0], np.cumsum(0.5 * (pdf[:-1] + pdf[1:]) * np.diff(g))])
    return np.interp(s, g, cdf)


def metrics(d):
    """SPEC-1: var(s) primary, W1δ=E|s−1| companion (both non-degenerate
    for clock). KS vs Wigner/Poisson on the §7.ter.59 floor (KS·√n/0.8687).
    NO KS-to-δ, NO Kuiper."""
    s = np.sort(d)
    n = s.size
    floor = 0.8687 / np.sqrt(max(n, 1))
    F = np.arange(1, n + 1) / n
    ks_w = float(np.max(np.abs(F - _cdf_wigner(s))))
    ks_p = float(np.max(np.abs(F - (1.0 - np.exp(-s)))))
    return {
        "var_s":  round(float(np.var(d)), 6),
        "W1d":    round(float(np.mean(np.abs(d - 1.0))), 6),
        "ksW_fl": round(ks_w / floor, 2),
        "ksP_fl": round(ks_p / floor, 2),
        "n": n, "floor": round(floor, 5),
    }


def quadrant(unfolded):
    ev = np.sort(unfolded)
    j = joint_q_profile(ev, q_max=Q_MAX, min_events_per_q=MIN_EV)
    qd = joint_quadrant_diagnostic(j)
    vc = qd['quadrant'].value_counts(normalize=True)
    return max(vc.index, key=lambda k: vc[k]), {k: round(float(v), 3) for k, v in vc.items()}


def fib(kmin, kmax):
    F = [1, 1]
    while len(F) <= kmax:
        F.append(F[-1] + F[-2])
    return [F[k] for k in range(kmin, kmax + 1)]


# ── GATES ─────────────────────────────────────────────────────────────────
def gate_A_clock(rec):
    """Exact clock (λ=0, arcsine truth-unfold). Defines τ_clock.
    PASS ⇔ var≈0 & W1δ≈0 (numerical floor) and clock is far from
    Wigner/Poisson by W1δ."""
    print("\n── GATE A — exact clock (λ=0, arcsine) : var≈0, W1δ≈0 expected")
    w1s = []
    for N in (377, 2584, 6765):
        d = spacings(unfold_arcsine(am_eigs(0.0, N, 0.0, theta=0.0), N))
        m = metrics(d)
        w1s.append(m["W1d"])
        rec.append({"gate": "A", "N": N, **m})
        print(f"   N={N:5d} var={m['var_s']:.2e} W1δ={m['W1d']:.2e} "
              f"ksW_fl={m['ksW_fl']} ksP_fl={m['ksP_fl']}")
    tau = max(w1s) * 50.0 + 1e-6                       # clock-class threshold
    ok = max(w1s) < 1e-3
    print(f"   τ_clock := {tau:.2e}  (50× max exact-clock W1δ)   "
          f"GATE A {'PASS' if ok else 'FAIL'}")
    return ok, tau


def gate_B_poisson(rec, tau):
    """Synthetic Poisson (exp spacings, mean 1). var≈1, W1δ≈0.736,
    KS-Poisson on floor, NOT clock_rigid, classifier BL."""
    print("\n── GATE B — synthetic Poisson : var≈1, W1δ≈0.74, ksP_fl small, BL")
    rng = np.random.default_rng(0)
    oks = []
    for n in (3000, 6000):
        s = rng.exponential(1.0, n)
        pts = np.cumsum(s)
        d = spacings(pts)
        m = metrics(d)
        q, _ = quadrant(pts)
        clk = m["W1d"] <= tau
        ok = (0.7 < m["var_s"] < 1.4) and (m["ksP_fl"] < 4.0) and (not clk)
        oks.append(ok)
        rec.append({"gate": "B", "n": n, **m, "quad": q, "clock_rigid": clk})
        print(f"   n={n:5d} var={m['var_s']:.3f} W1δ={m['W1d']:.3f} "
              f"ksP_fl={m['ksP_fl']} ksW_fl={m['ksW_fl']} quad={q} "
              f"clock_rigid={clk}")
    ok = all(oks)
    print(f"   GATE B {'PASS' if ok else 'FAIL'}")
    return ok


def gate_C_ids(rec):
    """SPEC-3: rational-θ=p/q. Two sub-tests, decoupled (Will's
    adjudication 2026-05-16):

      ok_absorb (CAMPAIGN-CRITICAL, gates the grid): does unfold_ids_ref
        correctly ABSORB gaps on the known periodic operator — i.e.
        IDS-unfolded periodic NNS collapses to clock-rigid (var≈0,
        W1δ≈0), so genuine structure separates from the deg-11
        gap-mass artifact. This is the only property the campaign uses
        the IDS leg for, verified on known truth.

      ok_plateau (INSURANCE, NON-BLOCKING): gap-labelling — every OPEN
        gap's IDS value lies on the (1/q)ℤ lattice. Corrected locator:
        relative-threshold detection (van-Hove-robust: true AM gaps are
        thousands× median spacing, edge thinning only a few×), and we
        check OPEN gaps only against the lattice (gap-labelling does NOT
        require all q−1 gaps open — the prior locator forced the full
        ladder and spuriously failed). Recorded for the record; does
        NOT gate the grid."""
    print("\n── GATE C — rational-θ=p/q   (ok_absorb gates grid; ok_plateau = insurance)")
    absorbs, plats = [], []
    for p, q in ((8, 13), (13, 21)):
        th = p / q
        Nref = q * 600                                       # divisible ⇒ IDS@gap_j = j/q exactly
        ref = np.sort(am_eigs(0.6, Nref, 0.0, theta=th))
        ds = np.diff(ref)
        med = float(np.median(ds))
        cand = np.where(ds > 8.0 * med)[0]                   # OPEN gaps (relative, van-Hove-robust)
        kq = np.arange(1, q) / q
        if cand.size:
            ids_vals = (cand + 1) / Nref
            devs = [float(np.min(np.abs(v - kq))) for v in ids_vals]
            maxdev = max(devs)
        else:
            maxdev = 1.0
        tol = 5.0 / Nref + 0.003
        ok_plat = (cand.size >= 1) and (maxdev < tol)
        # campaign-critical: gap absorption on known truth
        Ncell = q * 120
        d = spacings(unfold_ids_ref(am_eigs(0.6, Ncell, 0.0, theta=th), ref))
        mc = metrics(d)
        ok_abs = (mc["var_s"] < 0.05) and (mc["W1d"] < 0.10)
        absorbs.append(ok_abs)
        plats.append(ok_plat)
        rec.append({"gate": "C", "theta": f"{p}/{q}", "n_open_gaps": int(cand.size),
                    "plateau_maxdev": round(maxdev, 6), "plateau_tol": round(tol, 6),
                    "ok_plateau": ok_plat, "ids_unfold_var": mc["var_s"],
                    "ids_unfold_W1d": mc["W1d"], "ok_absorb": ok_abs})
        print(f"   θ={p}/{q}: ABSORB var={mc['var_s']:.4f} W1δ={mc['W1d']:.4f} "
              f"→ {'PASS' if ok_abs else 'FAIL'}   | "
              f"PLATEAU {cand.size} open gaps, max|dev−k/q|={maxdev:.5f} "
              f"(tol {tol:.5f}) → {'PASS' if ok_plat else 'FAIL'}")
    ok_absorb = all(absorbs)
    ok_plateau = all(plats)
    print(f"   GATE C: ok_absorb (gates grid) = {'PASS' if ok_absorb else 'FAIL'} ; "
          f"ok_plateau (insurance) = {'PASS' if ok_plateau else 'FAIL'}")
    return ok_absorb, ok_plateau


def derived_label(m, tau):
    """SPEC-2: clock is a first-class label now (not BR_artifact-noise)."""
    if m["W1d"] <= tau:
        return "clock_rigid"
    return "wigner" if m["ksW_fl"] <= m["ksP_fl"] else "poisson"


# ── grid (only if all gates pass) ─────────────────────────────────────────
def grid(rec, tau):
    print("\n" + "=" * 78)
    print("GRID (gates passed) — trimmed; var(s)/W1δ + clock_rigid + KS-floor;")
    print("decisive = is the derived label UNFOLDING-INVARIANT (deg11/ids/deg3)?")
    print("=" * 78)
    sup = [1.05, 1.25, 2.00]
    sub = [0.10, 0.50, 0.95]
    Ns = [377, 2584, 6765]
    NREF = 24000
    for tag, lams in (("SUPERCRITICAL λ→1⁺", sup), ("SUBCRITICAL small-λ", sub)):
        print(f"\n{tag}")
        print(f"{'λ':>5}{'N':>6} | {'unfold':>6} {'label':>11} "
              f"{'var(s)':>9} {'W1δ':>7} {'ksW/ksP_fl':>12} {'quad':>11} | INV?")
        for lam in lams:
            ref = np.concatenate([am_eigs(lam, NREF, p) for p in (0.0, 0.33)])
            for N in Ns:
                labs = {}
                rows = []
                for nm in ("deg11", "ids", "deg3"):
                    eig = am_eigs(lam, N, 0.0)
                    uf = (unfold_poly(eig, 11) if nm == "deg11" else
                          unfold_poly(eig, 3) if nm == "deg3" else
                          unfold_ids_ref(eig, ref))
                    d = spacings(uf)
                    m = metrics(d)
                    lab = derived_label(m, tau)
                    q, occ = quadrant(uf) if N == 2584 else ("—", {})
                    labs[nm] = lab
                    rec.append({"lam": lam, "N": N, "unfold": nm, "label": lab,
                                **m, "quad": q, "occ": occ})
                    rows.append(f"{lam:>5.2f}{N:>6} | {nm:>6} {lab:>11} "
                                f"{m['var_s']:>9.3f} {m['W1d']:>7.3f} "
                                f"{m['ksW_fl']:>5.1f}/{m['ksP_fl']:>5.1f} {q:>11}")
                inv = "YES" if len(set(labs.values())) == 1 else f"NO {labs}"
                for i, r in enumerate(rows):
                    print(r + (f" | {inv}" if i == len(rows) - 1 else ""))


def run():
    rec = []
    print("=" * 78)
    print("RE-GATED SCOPING INSTRUMENT — gates A,B,C must ALL pass before grid")
    print("=" * 78)
    okA, tau = gate_A_clock(rec)
    okB = gate_B_poisson(rec, tau)
    okC_absorb, okC_plateau = gate_C_ids(rec)
    out = os.path.join(THIS_DIR, "regated_instrument_results.json")
    # Grid gated on A, B, and the CAMPAIGN-CRITICAL Gate-C sub-test
    # (gap absorption). ok_plateau is recorded insurance, NON-BLOCKING
    # (Will's adjudication 2026-05-16).
    if okA and okB and okC_absorb:
        print(f"\n*** GRID-CRITICAL GATES PASS (A={okA} B={okB} "
              f"C_absorb={okC_absorb}); C_plateau={okC_plateau} "
              f"[insurance, non-blocking] — proceeding to grid ***")
        grid(rec, tau)
        verdict = ("GATES_PASS_GRID_RUN_PLATEAU_CERTIFIED" if okC_plateau
                   else "GATES_PASS_GRID_RUN_PLATEAU_UNCERTIFIED")
    else:
        print(f"\n*** GRID-CRITICAL GATE FAILURE (A={okA} B={okB} "
              f"C_absorb={okC_absorb}) — INSTRUMENT STILL BROKEN; "
              f"grid NOT run, NOT interpreted ***")
        verdict = "GATE_FAILURE_NO_GRID"
    with open(out, "w") as f:
        json.dump({"verdict": verdict, "tau_clock": tau,
                   "okC_plateau": okC_plateau, "records": rec}, f, indent=1)
    print(f"\nrecord (horizon) → {out}\nNO auto-adjudication. Read gates first.")


if __name__ == "__main__":
    run()
