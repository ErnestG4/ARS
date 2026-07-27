"""
class_collapse_sweep.py — how many banked class assignments came off a saturated axis?

THE DEFECT (R-140/R-144). `cross_substrate/axes.py:I8_brody_q` fits Brody q on bounds=(0.0, 1.0).
Verified: clustered pins to 0.0000, and GOE *and* GUE BOTH pin to 0.9999 (true +1.0032, +1.5325).
One-ended saturation hides MAGNITUDE. Two-ended saturation hides IDENTITY — it substitutes a bound
for a class label. The repair existed on 2026-07-12 and was propagated 2026-07-27.

  ⚠ ALSO SWEPT: `ARS.rep_med` — the same fingerprint store carries the CLIPPED repulsion integral,
  which saturates to exactly 0 for any clustered substrate (R-093/R-094). Both defects live in the
  same banked coordinates, so both are counted here.

OUTCOME MAP, DECLARED BEFORE THE RESULTS PRINT (the SATURATION_SWEEP_PRECOMMIT discipline):
  A  many banked values at the bounds  -> those coordinates carry a BOUND, not a measurement, and
     any class call resting on them is unsupported. Report the count, not a softened version.
  B  few or none at the bounds         -> the axis was recorded but rarely decisive. REPORT AT EQUAL
     PROMINENCE. A sweep that only speaks when it finds something is a publication-bias engine.
  C  values present but no class call rests on them -> the exposure is bookkeeping, not inference.
     This is a REAL outcome and the most likely one; say so plainly rather than manufacturing alarm.

WHAT THIS SWEEP CANNOT DO: recover the true q for a saturated entry. Once q is pinned at a bound the
information is gone, exactly as with 100% I_rep saturation — only recomputation from the spacings
recovers it. Saturated entries are UNRECOVERABLE, not null.
"""
from __future__ import annotations
import glob, json, os, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from commensurable import saturation, Incommensurable   # noqa: E402

BRODY_BOUNDS = (0.0, 1.0)
TOL = 1e-3
p_ = lambda *a: print(*a, flush=True)


def load():
    rows = []
    for f in sorted(glob.glob("cross_substrate/coordinates/*.jsonl")):
        for line in open(f):
            line = line.strip()
            if not line:
                continue
            try:
                d = json.loads(line)
            except Exception:
                continue
            ax = d.get("axes_computed") or {}
            rows.append({"file": os.path.basename(f), "substrate": d.get("substrate"),
                         "cell": d.get("cell_id"), "axes": ax})
    return rows


if __name__ == "__main__":
    p_(__doc__.split("OUTCOME MAP")[0].strip()[:0] or "")
    p_("=== CLASS-COLLAPSE SWEEP ===")
    p_("outcome map declared in the module docstring, before any result. A/B/C all reportable.\n")

    rows = load()
    p_(f"  fingerprint store: {len(rows)} entries across "
       f"{len(set(r['file'] for r in rows))} coordinate files")

    for AXIS, bounds, label in (("I.8_brody_q", BRODY_BOUNDS, "Brody q  (two-ended: hides IDENTITY)"),
                                ("ARS.rep_med", (0.0, None), "clipped I_rep (one-ended: hides MAGNITUDE)")):
        vals = [(r, r["axes"][AXIS]) for r in rows
                if isinstance(r["axes"].get(AXIS), (int, float))]
        p_(f"\n  ── {AXIS} — {label}")
        if not vals:
            p_("     no banked values.")
            continue
        lo, hi = bounds
        at_lo = [r for r, v in vals if abs(v - lo) <= TOL]
        at_hi = [r for r, v in vals if hi is not None and abs(v - hi) <= TOL]
        p_(f"     banked values: {len(vals)}  across {len(set(r['substrate'] for r, _ in vals))} substrates")
        p_(f"     pinned at lower bound {lo}: {len(at_lo)}  ({100*len(at_lo)/len(vals):.1f}%)")
        if hi is not None:
            p_(f"     pinned at upper bound {hi}: {len(at_hi)}  ({100*len(at_hi)/len(vals):.1f}%)")
        tot = len(at_lo) + len(at_hi)
        p_(f"     TOTAL AT A BOUND: {tot}/{len(vals)} = {100*tot/len(vals):.1f}%  "
           f"-> these carry a BOUND, not a measurement")
        # which substrates
        subs = {}
        for r in at_lo + at_hi:
            subs[r["substrate"]] = subs.get(r["substrate"], 0) + 1
        if subs:
            p_("     saturated substrates: " +
               ", ".join(f"{k} ({v})" for k, v in sorted(subs.items(), key=lambda kv: -kv[1])[:8]))
        # the guard, actually called -- this is a real call site, not a demo
        try:
            saturation([v for _, v in vals], at=lo, field_type="continuous")
        except Incommensurable as e:
            p_(f"     [guard] {str(e)[:80]}")

    p_("\n  ── does any banked CLASS CALL rest on these axes?")
    labelled = [r for r in rows if any(
        isinstance(v, str) and v.upper() in ("GOE", "GUE", "POISSON", "GSE")
        for v in (r["axes"] or {}).values())]
    p_(f"     entries carrying an explicit GOE/GUE/Poisson/GSE label in axes_computed: {len(labelled)}")
    p_("     (a label stored ALONGSIDE a saturated q is bookkeeping; a label DERIVED from one is"
       " an unsupported inference. The store records values, not derivations, so this sweep can")
    p_("      count exposure but cannot by itself prove any specific call was made from it.)")
