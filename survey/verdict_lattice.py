"""Survey arc verdict lattice — SHARED MODULE per rulings-as-code (TOOLKIT §9;
the runner imports resolve(); no hand-transcribed if/elif chains anywhere).

Implementation-time lattice completion (pre-seal, filed): the brief's §4 has
no cell for tiles DISAGREEING on the class call.  Added here as
CLASS_INCONSISTENT_ACROSS_TILES — no single-class banking; the split itself
files.  This is the rulings-as-code discipline catching a lattice hole at
authoring time instead of one floor down at run time (comb precedent).

Sealed decision rules (numbers live in prereg_sealed.json; this module reads
them so a seal edit cannot silently diverge from the code):
  tile class call at each sealed L from z = (F-1)/sigma_F:
    SUPER            z >= +Z_CLASS at every sealed L
    POISSON_CONS     |z| <= 3 at every sealed L
    SUB_FLAG         z <= -Z_CLASS at any sealed L   (feeds §0.1 surprise)
    MIXED            anything else
  slice consistency: >= CONSISTENCY_FRAC of accepted tiles share the call.
  within-slice drift: chi2 of the linear log(F-1)-vs-log(L) fit > DRIFT_CHI2
    -> coherent within-slice drift -> BOUNDED_AT_SCALE (drift law filed with
    sign and coefficient).  Inter-slice differences NEVER enter (physics).
"""

VERDICTS = ("CLASS_MEASURED", "CLASS_MEASURED_BOUNDED_AT_SCALE",
            "UNDERPOWERED", "INSTRUMENT_HOLD",
            "CLASS_INCONSISTENT_ACROSS_TILES", "NO_VERDICT_GATES_RED")
FLAGS = ("OBSTRUCTION_BANKED",)


def tile_class(zs, z_class):
    if all(z >= z_class for z in zs):
        return "SUPER"
    if all(abs(z) <= 3.0 for z in zs):
        return "POISSON_CONS"
    if any(z <= -z_class for z in zs):
        return "SUB_FLAG"
    return "MIXED"


def resolve(slice_id, *, gates_green, power_ok, tile_calls, sub_fired,
            hold_cleared, drift_chi2, obstruction_excess, seal):
    """Single address per outcome.  Returns dict(primary, flags, detail)."""
    flags = []
    if obstruction_excess:
        flags.append("OBSTRUCTION_BANKED")
    if not gates_green:
        return dict(slice=slice_id, primary="NO_VERDICT_GATES_RED",
                    flags=flags, detail="mask KAG or FIX-2 gate red in an "
                    "included tile — nothing banks")
    if sub_fired and not hold_cleared:
        return dict(slice=slice_id, primary="INSTRUMENT_HOLD", flags=flags,
                    detail="§0.1 surprise clause fired; sealed audit "
                    "checklist not yet cleared — no banking in this state")
    if not power_ok:
        return dict(slice=slice_id, primary="UNDERPOWERED", flags=flags,
                    detail="sealed power criterion unmet after one-shot "
                    "extension")
    calls = list(tile_calls.values())
    top = max(set(calls), key=calls.count)
    frac = calls.count(top) / len(calls)
    if frac < seal["CONSISTENCY_FRAC"]:
        return dict(slice=slice_id, primary="CLASS_INCONSISTENT_ACROSS_TILES",
                    flags=flags, detail=f"top call {top} at {frac:.2f} < "
                    f"{seal['CONSISTENCY_FRAC']}; split files as the result")
    primary = ("CLASS_MEASURED_BOUNDED_AT_SCALE"
               if drift_chi2 > seal["DRIFT_CHI2"] else "CLASS_MEASURED")
    return dict(slice=slice_id, primary=primary, flags=flags,
                detail=f"class={top} ({frac:.0%} of tiles), "
                f"drift chi2={drift_chi2:.2f} vs {seal['DRIFT_CHI2']}")
