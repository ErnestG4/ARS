"""C1 — rail fractions per classified site. COMMITTED GENERATOR.
Run AFTER bounded_census/CLASSIFICATION_SEALED.md was committed; commit order is
the evidence that classification preceded measurement.

Coverage is a LOWER BOUND: key-pattern matching flagged 251 banked keys this
sweep's names would miss. The largest, `rho1` (1,439 values), was checked and
excluded by measurement -- it ranges -0.79..0.59, so it is a correlation
coefficient, not a bounded fit. The other 250 are unchecked.
"""
import json, glob, os
import numpy as np

# Repo-relative, not a hardcoded checkout: with the absolute path a board run
# from a nested worktree regenerated the MAIN checkout's tracked JSONs while
# verify_bounded_census compared the worktree's own copies (2026-09-20).
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TOL = 1e-3
# key-substring -> (bounds, sealed class)
SITES = {
    "brody_q_unbounded": ((-1.0, 4.0), "CONVENTION (wider)"),
    "brody_q":           ((0.0, 1.0),  "CONVENTION"),
    "berry_robnik":      ((0.0, 1.0),  "MATHEMATICAL"),
    "alpha":             ((1e-3, None), "MIXED (lower CONVENTION)"),
    "kappa":             ((1e-4, 100.0), "CONVENTION both ends"),
}


def walk(o, out):
    if isinstance(o, dict):
        for k, v in o.items():
            if isinstance(v, (int, float)) and not isinstance(v, bool):
                kl = k.lower()
                if "unbounded" in kl and "brody" in kl:
                    out.setdefault("brody_q_unbounded", []).append(float(v))
                elif "brody_q" in kl:
                    out.setdefault("brody_q", []).append(float(v))
                elif "berry_robnik" in kl:
                    out.setdefault("berry_robnik", []).append(float(v))
                elif kl == "alpha":
                    out.setdefault("alpha", []).append(float(v))
                elif kl == "kappa":
                    out.setdefault("kappa", []).append(float(v))
            walk(v, out)
    elif isinstance(o, list):
        for v in o:
            walk(v, out)


vals = {}
for f in glob.glob(f"{R}/**/*.json", recursive=True) + glob.glob(f"{R}/**/*.jsonl", recursive=True):
    rel = os.path.relpath(f, R)
    if rel.startswith(".git/") or rel.startswith(".claude/"):   # relative: a worktree's own path contains /.claude/
        continue
    # ring/ is a different arc whose tables reuse the key NAMES this census
    # matches by (`alpha` = a Jacobian's spectral abscissa, `kappa` = an
    # eigenvector condition number -- not the DPP alpha / Thomas kappa the
    # sites are labelled with). 19 of each entered the census on 2026-09-20 and
    # flipped alpha@lo from CLEAR to INSUFFICIENT_N. A key-name census must
    # exclude arcs whose keys it does not own.
    if rel.startswith("ring/"):
        continue
    try:
        t = open(f, errors="replace").read()
    except OSError:
        continue
    if not any(k.split("_")[0] in t for k in SITES):
        continue
    try:
        if f.endswith(".jsonl"):
            for line in t.splitlines():
                if line.strip():
                    try:
                        walk(json.loads(line), vals)
                    except json.JSONDecodeError:
                        pass
        else:
            walk(json.loads(t), vals)
    except json.JSONDecodeError:
        pass

out = {"coverage": "LOWER BOUND — 251 keys unmatched; rho1 checked and excluded "
                   "by measurement (range -0.79..0.59, a correlation coefficient, "
                   "not a bounded fit); 250 unchecked", "sites": {}}
print("  (* = TRUE RAIL: near-bound AND distinct-ratio < 1%. no star = real "
      "measurements that happen to lie near the bound)")
print(f"{'site':22s} {'class':24s} {'n':>7s} {'near lo':>8s} {'near hi':>8s}  sealed prediction")
PRED = {"brody_q": "substantial rail", "brody_q_unbounded": "little/none",
        "berry_robnik": "rare, and real answers", "alpha": "only if non-repulsive data",
        "kappa": "only if non-clustered data"}
for key, (bnds, cls) in SITES.items():
    v = np.array(vals.get(key, []), float)
    if v.size == 0:
        print(f"{key:22s} {cls:24s} {'0':>7s}       -       -   (none banked)")
        continue
    lo, hi = bnds
    # A RAIL IS A PILEUP, NOT A PROXIMITY. Distance alone conflates "pinned at
    # the optimizer's floor" with "genuinely small". The discriminator is the
    # DISTINCT-VALUE RATIO among the near-bound values: an optimizer floor emits
    # ONE number (Brody: 15,174 values near 0, 4 distinct, ratio 0.0003), while a
    # real distribution concentrated near a bound emits as many values as it has
    # samples (Berry-Robnik rho: 7,328 near 0, 7,319 distinct, ratio 0.9988).
    # Found by the sealed prediction for rho FAILING on the distance-only test at
    # 36.1% and then being VINDICATED once the criterion was right.
    def _rail(bound):
        if bound is None:
            return None, None, None
        near = v[np.abs(v - bound) <= TOL]
        if near.size == 0:
            return 0.0, 0, 0.0
        distinct = len({round(float(x), 15) for x in near})
        return float(near.size / v.size), distinct, distinct / near.size
    flo, dlo, rlo = _rail(lo)
    fhi, dhi, rhi = _rail(hi)
    RAIL_RATIO = 0.01
    MIN_N = int(1 / RAIL_RATIO)
    flo_is_rail = bool(flo and rlo is not None and rlo < RAIL_RATIO)
    fhi_is_rail = bool(fhi and rhi is not None and rhi < RAIL_RATIO)

    def _verdict(bound, frac, ratio, is_rail):
        """EVERY site-bound gets an explicit verdict. A site with no verdict is a
        slot someone later fills from memory, so 'the arm cannot fire here' is
        recorded as INSUFFICIENT_N rather than left as an exemption."""
        if bound is None:
            return "NO_BOUND"
        near_n = int(round((frac or 0.0) * v.size))
        if near_n == 0:
            return "CLEAR (nothing near the bound)"
        if near_n < MIN_N:
            return (f"INSUFFICIENT_N (n={near_n} < {MIN_N}) — the discriminator "
                    "cannot fire; SEALED CLASSIFICATION RETAINED as the standing "
                    "call pending more samples")
        return "TRUE_RAIL" if is_rail else "CONCENTRATION (real measurements)"

    verdict_lo = _verdict(lo, flo, rlo, flo_is_rail)
    verdict_hi = _verdict(hi, fhi, rhi, fhi_is_rail)
    out["sites"][key] = dict(n=int(v.size), bounds=list(bnds), sealed_class=cls,
                             near_lo_frac=flo, near_hi_frac=fhi,
                             distinct_ratio_lo=rlo, distinct_ratio_hi=rhi,
                             TRUE_RAIL_lo=flo_is_rail, TRUE_RAIL_hi=fhi_is_rail,
                             verdict_lo=verdict_lo, verdict_hi=verdict_hi,
                             vmin=float(v.min()), vmax=float(v.max()),
                             prediction=PRED[key])
    s_lo = (f"{flo:.1%}{'*' if flo_is_rail else ' '}") if flo is not None else "   -"
    s_hi = (f"{fhi:.1%}{'*' if fhi_is_rail else ' '}") if fhi is not None else "   -"
    print(f"{key:22s} {cls:24s} {v.size:>7,} {s_lo:>8s} {s_hi:>8s}  {PRED[key]}")
json.dump(out, open(f"{R}/bounded_census/rail_fractions.json", "w"), indent=1)
