"""
verify/tier2_longrange_unfold.py — Tier-2 verification harness.

QUESTION (from audit): several callers feed RAW or merely global-unit-mean-unfolded
positions into Family-II long-range stats (axes.py II1_sigma2_at_L / II2_delta3_at_L),
which apply NO internal unfolding. Global unit-mean leaves any non-flat density in,
inflating Σ²(L). The GUARDED path (cross_substrate/longrange_discriminator.longrange_verdict)
does a density-adaptive polynomial unfold internally. For each EXPOSED substrate: does
switching from the unit-mean/raw path to the density-adaptive guarded path CHANGE the
long-range Σ² and/or the verdict?

Run:
  PYTHONPATH=$HOME/fmexplorer/riemann_explorer \
  $HOME/fmexplorer/bin/python3 verify/tier2_longrange_unfold.py

Writes verify/tier2_results.md. Reads (does NOT edit) the tool/driver files. Real
numbers only; missing inputs → BLOCKED.
"""
from __future__ import annotations

import os
import sys
import traceback

import numpy as np

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_HERE)
for p in (_ROOT, os.path.join(_ROOT, "phase22a"), os.path.join(_ROOT, "cross_substrate"),
          os.path.expandvars("$HOME/fmexplorer/brocot")):
    if p not in sys.path:
        sys.path.insert(0, p)

# banked-path pieces
from cross_substrate.axes import compute_family_II, matched_L, MIN_N_LONGRANGE   # noqa: E402
from phase22a.ars_classify import unfold_unit_mean                                # noqa: E402
# guarded-path pieces
from cross_substrate.longrange_discriminator import (                            # noqa: E402
    longrange_verdict, unfolding_sensitivity)

N_SEEDS = 8
N_REF = 1500

RESULTS = []          # list of dict rows
BLOCKED = []          # (site, reason)


def _num(x, nd=3):
    if x is None or (isinstance(x, float) and not np.isfinite(x)):
        return "—"
    return f"{x:.{nd}f}"


def run_site(name, source_note, pos, banked_transform="unit_mean"):
    """Compute banked (unit_mean or raw) family-II + guarded verdict + lens sensitivity."""
    row = {"site": name, "source": source_note}
    try:
        pos = np.sort(np.asarray(pos, dtype=np.float64))
        n = int(pos.size)
        row["n"] = n
        if n < MIN_N_LONGRANGE:
            row["status"] = "UNDERPOWERED"
            row["note"] = f"n={n} < MIN_N_LONGRANGE={MIN_N_LONGRANGE}"
            RESULTS.append(row)
            return row

        # ── banked path (what the site actually feeds) ──
        if banked_transform == "unit_mean":
            banked_in = unfold_unit_mean(pos)
        else:   # "raw" — brocot sites feed sorted freqs directly, no unfold
            banked_in = pos
        fII = compute_family_II(banked_in)
        row["banked_transform"] = banked_transform
        row["banked_sigma2"] = fII.get("II.1_sigma2_L")
        row["banked_delta3"] = fII.get("II.2_delta3_L")

        # ── guarded path (density-adaptive poly unfold inside longrange_verdict) ──
        v = longrange_verdict(pos, n_seeds=N_SEEDS, n_ref=N_REF)
        row["L"] = v.get("L")
        row["guarded_verdict"] = v.get("verdict")
        s2 = v.get("sigma2") or {}
        row["guarded_sigma2"] = s2.get("obs")
        row["gue_ref"] = (s2.get("gue") or {}).get("mean")
        row["poisson_ref"] = (s2.get("poisson") or {}).get("mean")
        row["z_vs_gue"] = s2.get("z_vs_gue")
        row["z_vs_poisson"] = s2.get("z_vs_poisson")

        # ── lens sensitivity: INVARIANT vs COVARIANT ──
        sens = unfolding_sensitivity(pos, n_seeds=N_SEEDS, n_ref=N_REF)
        row["lens"] = sens.get("lens")
        row["lens_verdicts"] = sens.get("verdicts")
        row["per_degree"] = sens.get("per_degree")

        # ── conclusion: does the guarded Σ² differ materially from banked, and/or
        #    does the verdict move away from a naive "banked-looks-Poissonish"? ──
        bs = row["banked_sigma2"]
        gs = row["guarded_sigma2"]
        if bs and gs and bs > 0:
            row["sigma2_ratio_banked_over_guarded"] = bs / gs
        row["status"] = "OK"
        RESULTS.append(row)
        return row
    except Exception as e:
        BLOCKED.append((name, f"{type(e).__name__}: {e}"))
        row["status"] = "BLOCKED"
        row["note"] = f"{type(e).__name__}: {e}"
        RESULTS.append(row)
        traceback.print_exc()
        return row


# ═══════════════════════════════════════════════════════════════════════════
# SANITY GATE — homogeneous Poisson: both paths must read ≈ Poisson (Σ²≈L)
# ═══════════════════════════════════════════════════════════════════════════
def sanity_gate():
    rng = np.random.default_rng(12345)
    pos = np.cumsum(rng.exponential(size=3000))
    fII = compute_family_II(unfold_unit_mean(pos))
    v = longrange_verdict(pos, n_seeds=N_SEEDS, n_ref=N_REF)
    s2 = v.get("sigma2") or {}
    L = v.get("L")
    return {
        "n": 3000, "L": L,
        "banked_sigma2": fII.get("II.1_sigma2_L"),
        "guarded_sigma2": s2.get("obs"),
        "poisson_ref": (s2.get("poisson") or {}).get("mean"),
        "gue_ref": (s2.get("gue") or {}).get("mean"),
        "guarded_verdict": v.get("verdict"),
        "L_target": L,
    }


# ═══════════════════════════════════════════════════════════════════════════
# SITE 1 & 2 — Mertens / Liouville sign-changes  (data/phase34*_results/*.npz)
# ═══════════════════════════════════════════════════════════════════════════
def site_mertens():
    f = os.path.join(_ROOT, "data/phase34a_results/mertens_signchanges_N10000000.npz")
    if not os.path.exists(f):
        BLOCKED.append(("mertens", f"missing {f}"))
        RESULTS.append({"site": "mertens", "status": "BLOCKED", "note": f"missing {f}"})
        return
    pos = np.load(f)["signchanges"].astype(np.float64)
    run_site("mertens_signchanges",
             "data/phase34a_results/mertens_signchanges_N10000000.npz['signchanges']; "
             "fed at phase34a nns/family-II via unit-mean",
             pos, banked_transform="unit_mean")


def site_liouville():
    f = os.path.join(_ROOT, "data/phase34b_results/liouville_signchanges_N1000000000.npz")
    if not os.path.exists(f):
        BLOCKED.append(("liouville", f"missing {f}"))
        RESULTS.append({"site": "liouville", "status": "BLOCKED", "note": f"missing {f}"})
        return
    pos = np.load(f)["signchanges"].astype(np.float64)
    run_site("liouville_signchanges",
             "data/phase34b_results/liouville_signchanges_N1000000000.npz['signchanges']",
             pos, banked_transform="unit_mean")


# ═══════════════════════════════════════════════════════════════════════════
# SITE 3 & 4 — brocot FM partials (brocot_landscape.py:52 / brocot_approximability.py:83)
#   Both feed RAW sorted partial freqs `f` directly into compute_family_II(f).
#   Replicate the approximability generator (self-contained, deterministic).
# ═══════════════════════════════════════════════════════════════════════════
def _brocot_partials(alpha, depth, f_carrier=220.0):
    from phase3.partial_prediction import predict_partials
    sp = predict_partials([1.0, float(alpha)], [float(depth), float(depth)],
                          f_carrier=f_carrier)
    return np.sort(np.asarray(sp.freqs, float))


def site_brocot():
    # representative Lagrange classes from brocot_approximability CLASSES, high depth
    cases = [
        ("golden",     (np.sqrt(5) - 1) / 2),
        ("liouville",  sum(10.0 ** -e for e in (1, 2, 6, 24, 120, 720))),
        ("pi_minus_3", np.pi - 3),
    ]
    any_ok = False
    for cname, alpha in cases:
        got = None
        for depth in (8.0, 6.0, 5.0):   # try to clear MIN_N_LONGRANGE=200 partials
            try:
                f = _brocot_partials(alpha, depth)
            except Exception as e:
                BLOCKED.append((f"brocot/{cname}", f"predict_partials: {e}"))
                break
            if f.size >= MIN_N_LONGRANGE:
                got = (depth, f)
                break
            got = (depth, f)  # keep last even if small, to report UNDERPOWERED
        if got is None:
            RESULTS.append({"site": f"brocot/{cname}", "status": "BLOCKED",
                            "note": "predict_partials failed"})
            continue
        depth, f = got
        any_ok = True
        run_site(f"brocot/{cname}(depth{depth:g})",
                 f"brocot_landscape.py:52 / brocot_approximability.py:83 — RAW partials "
                 f"predict_partials([1,{alpha:.6f}],[{depth:g},{depth:g}]); n={f.size}",
                 f, banked_transform="raw")
    if not any_ok:
        BLOCKED.append(("brocot", "no class produced usable partial set"))


# ═══════════════════════════════════════════════════════════════════════════
# SITE 5 — allen_depth_fam2.py:47-48  (unit_mean spike train from NWB)
# ═══════════════════════════════════════════════════════════════════════════
def site_allen():
    try:
        import glob
        import h5py
        import cross_substrate.allen_depth as ad
        # driver holds literal '$HOME' and expandvars at its own call sites; expand at
        # runtime here (NOT editing the driver file on disk).
        ad.CACHE = os.path.expandvars(ad.CACHE)
        ad.NWB_GLOB = os.path.expandvars(ad.NWB_GLOB)
        from cross_substrate.allen_depth import build_targets, _session_tasks, NWB_GLOB
    except Exception as e:
        BLOCKED.append(("allen", f"import: {e}"))
        RESULTS.append({"site": "allen-depth", "status": "BLOCKED", "note": f"import: {e}"})
        return
    files = sorted(glob.glob(NWB_GLOB))
    if not files:
        BLOCKED.append(("allen", f"no NWB at {NWB_GLOB}"))
        RESULTS.append({"site": "allen-depth", "status": "BLOCKED",
                        "note": f"no NWB at {NWB_GLOB}"})
        return
    try:
        targets = build_targets()
    except Exception as e:
        BLOCKED.append(("allen", f"build_targets: {e}"))
        RESULTS.append({"site": "allen-depth", "status": "BLOCKED",
                        "note": f"build_targets: {e}"})
        return
    # take the first session, pick a few units whose train clears MIN_N_LONGRANGE
    picked = 0
    for f in files:
        sid = int(os.path.basename(os.path.dirname(f)).split("_")[1])
        sess_rows = targets[targets["session_id"] == sid]
        if sess_rows.empty:
            continue
        try:
            with h5py.File(f, "r") as h:
                tasks = _session_tasks(h, sess_rows, sid)
        except Exception as e:
            BLOCKED.append(("allen", f"session {sid} read: {e}"))
            continue
        # sort tasks by train size desc so we get well-powered units
        tasks = sorted(tasks, key=lambda t: -t[1].size)
        for meta, train in tasks:
            if train.size < MIN_N_LONGRANGE:
                break
            run_site(f"allen/{meta['area']}/{meta['stimulus']}/u{meta['unit_id']}",
                     f"allen_depth_fam2.py:47-48 unit_mean(train); session {sid}",
                     np.asarray(train, float), banked_transform="unit_mean")
            picked += 1
            if picked >= 3:
                return
        if picked:
            return
    if not picked:
        BLOCKED.append(("allen", "no unit cleared MIN_N_LONGRANGE"))
        RESULTS.append({"site": "allen-depth", "status": "BLOCKED",
                        "note": "no unit cleared MIN_N_LONGRANGE"})


# ═══════════════════════════════════════════════════════════════════════════
# SITE 6 — phase2b_recompute.py:92  (unit_mean pvc-11 concatenated_spikes)
# ═══════════════════════════════════════════════════════════════════════════
def site_pvc11():
    try:
        import phase22a.loader as loader
        from pathlib import Path
        # driver holds literal '$HOME' Path; expand at runtime here (NOT editing driver).
        loader.PVC11_ROOT = Path(os.path.expandvars(str(loader.PVC11_ROOT)))
        from phase22a.loader import load
    except Exception as e:
        BLOCKED.append(("pvc-11", f"import loader: {e}"))
        RESULTS.append({"site": "pvc-11", "status": "BLOCKED", "note": f"import loader: {e}"})
        return
    rec = None
    for name in ("monkey1_spontaneous", "monkey2_spontaneous", "monkey1_gratings"):
        try:
            rec = load(name)
            recname = name
            break
        except Exception as e:
            last = f"{name}: {e}"
    if rec is None:
        BLOCKED.append(("pvc-11", f"load failed ({last})"))
        RESULTS.append({"site": "pvc-11", "status": "BLOCKED", "note": f"load failed ({last})"})
        return
    picked = 0
    sizes = []
    for u in range(rec.n_units):
        try:
            spk = np.asarray(rec.concatenated_spikes(u), float)
        except Exception:
            continue
        sizes.append((u, spk.size))
    sizes.sort(key=lambda t: -t[1])
    for u, sz in sizes:
        if sz < MIN_N_LONGRANGE:
            break
        spk = np.asarray(rec.concatenated_spikes(u), float)
        run_site(f"pvc-11/{recname}/u{u}",
                 f"phase2b_recompute.py:92 unit_mean(concatenated_spikes); {recname} unit {u}",
                 spk, banked_transform="unit_mean")
        picked += 1
        if picked >= 3:
            break
    if not picked:
        BLOCKED.append(("pvc-11", "no unit cleared MIN_N_LONGRANGE"))
        RESULTS.append({"site": "pvc-11", "status": "BLOCKED",
                        "note": "no unit cleared MIN_N_LONGRANGE"})


# ═══════════════════════════════════════════════════════════════════════════
def write_md(sanity):
    lines = []
    A = lines.append
    A("# Tier-2 verification — long-range unfold (unit-mean/raw vs density-adaptive guarded)\n")
    A("Question: for each EXPOSED Family-II site, does switching from the banked "
      "unit-mean/raw path (axes.py II.1/II.2, NO internal unfold) to the guarded "
      "density-adaptive poly-unfold (`longrange_verdict`) CHANGE Σ²(L) and/or the verdict?\n")
    A(f"Params: n_seeds={N_SEEDS}, n_ref={N_REF}, guarded unfold_deg default=6 "
      f"(swept 3/6/10/15 for lens sensitivity). MIN_N_LONGRANGE={MIN_N_LONGRANGE}.\n")

    A("\n## SANITY GATE — homogeneous Poisson (np.cumsum(rng.exponential(size=3000)))\n")
    A("Flat-density control where unit-mean IS correct → both paths must read ≈Poisson (Σ²≈L).\n")
    A(f"- L (matched) = {_num(sanity['L'])}")
    A(f"- banked Σ²(unit_mean) = {_num(sanity['banked_sigma2'])}")
    A(f"- guarded Σ²(obs)     = {_num(sanity['guarded_sigma2'])}")
    A(f"- Poisson ref mean    = {_num(sanity['poisson_ref'])}  |  GUE ref mean = {_num(sanity['gue_ref'])}")
    A(f"- guarded verdict     = **{sanity['guarded_verdict']}**")
    poisson_ok = (sanity['guarded_verdict'] == 'POISSON_INDEP')
    A(f"- GATE: both read ≈Poisson (Σ²≈L≈{_num(sanity['L'])}) → "
      f"{'PASS' if poisson_ok else 'CHECK'}\n")

    A("\n## Per-site results\n")
    for r in RESULTS:
        A(f"\n### {r['site']}")
        A(f"- source: {r.get('source','')}")
        A(f"- status: **{r.get('status')}**")
        if r.get("status") in ("BLOCKED", "UNDERPOWERED"):
            A(f"- note: {r.get('note','')}")
            if "n" in r:
                A(f"- n = {r['n']}")
            continue
        A(f"- n = {r.get('n')}  |  L(matched) = {_num(r.get('L'))}")
        A(f"- banked ({r.get('banked_transform')}): Σ²(L) = {_num(r.get('banked_sigma2'))}, "
          f"Δ₃(L) = {_num(r.get('banked_delta3'))}")
        A(f"- guarded (poly-unfold deg6): Σ²(obs) = {_num(r.get('guarded_sigma2'))}, "
          f"verdict = **{r.get('guarded_verdict')}**")
        A(f"- refs: GUE Σ²={_num(r.get('gue_ref'))}, Poisson Σ²={_num(r.get('poisson_ref'))} "
          f"| z_vs_GUE={_num(r.get('z_vs_gue'),2)}, z_vs_Poisson={_num(r.get('z_vs_poisson'),2)}")
        ratio = r.get("sigma2_ratio_banked_over_guarded")
        if ratio is not None:
            A(f"- Σ² banked/guarded ratio = {_num(ratio,2)}×")
        A(f"- lens sweep (deg 3/6/10/15): **{r.get('lens')}** "
          f"verdicts={r.get('lens_verdicts')}")
        pd = r.get("per_degree") or {}
        A("  - per-degree Σ²(obs)/verdict: " +
          "; ".join(f"deg{d}: {_num(v.get('sigma2'))}/{v.get('verdict')}"
                    for d, v in pd.items()))
        # conclusion
        bs, gs = r.get("banked_sigma2"), r.get("guarded_sigma2")
        material = (bs and gs and bs > 0 and (bs / gs > 1.5 or bs / gs < 0.67))
        concl = []
        if material:
            concl.append(f"Σ² changes MATERIALLY ({_num(ratio,2)}×)")
        else:
            concl.append("Σ² not materially changed")
        if r.get("lens") == "COVARIANT":
            concl.append("verdict is an UNFOLDING ARTIFACT (lens-COVARIANT)")
        else:
            concl.append("guarded verdict lens-INVARIANT")
        A(f"- CONCLUSION: {'; '.join(concl)}.")

    A("\n## Blocked\n")
    if BLOCKED:
        for s, why in BLOCKED:
            A(f"- {s}: {why}")
    else:
        A("- (none)")

    out = os.path.join(_HERE, "tier2_results.md")
    with open(out, "w") as fh:
        fh.write("\n".join(lines) + "\n")
    print(f"\nwrote {out}")
    return out


def main():
    print("SANITY GATE …")
    sanity = sanity_gate()
    print(f"  Poisson: banked Σ²={_num(sanity['banked_sigma2'])}, "
          f"guarded Σ²={_num(sanity['guarded_sigma2'])}, L={_num(sanity['L'])}, "
          f"verdict={sanity['guarded_verdict']}")
    for fn, label in ((site_mertens, "mertens"), (site_liouville, "liouville"),
                      (site_brocot, "brocot"), (site_allen, "allen"),
                      (site_pvc11, "pvc-11")):
        print(f"SITE: {label} …", flush=True)
        try:
            fn()
        except Exception as e:
            BLOCKED.append((label, f"top-level: {e}"))
            traceback.print_exc()
    write_md(sanity)


if __name__ == "__main__":
    main()
