"""
cross_substrate/phase2b_arith.py — Phase 2b extension: matched object-(a)
recompute for the arithmetic substrates + Maass Γ₀(N).

Regenerates each banked cell's EXACT point process via the originating phase's
own generator (deterministic / cached — see implementation_notes), unfolds it
the same way the phase did, then computes matched Family I/II and merges into
coordinates/{substrate}.jsonl. Validates faithfulness by matching the
regenerated event count against the banked n_events.

Substrates: maass-gamma0, mertens, liouville, L-zeros,
            gaussian-primes, eisenstein-primes.

Generators (read-only reuse):
  maass:      phase34e/maass_loader.{load_eigenvalues_at_level, unfold_gamma0}
  mertens:    phase34a/mertens_events.load_or_compute
  liouville:  phase34b/liouville_events.load_or_compute
  L-zeros:    phase34c/{zeros_loaders, unfolding}
  primes:     phase34d/{gaussian_primes, eisenstein_primes}

Brody/BR banked only if fitter_validation all_pass (§7.ter.57).
"""
from __future__ import annotations

import json
import os
import sys
from datetime import date
from pathlib import Path

import numpy as np

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_HERE)
for _d in ("", "phase34a", "phase34b", "phase34c", "phase34d", "phase34e"):
    p = os.path.join(_ROOT, _d) if _d else _ROOT
    if p not in sys.path:
        sys.path.insert(0, p)

from cross_substrate.axes import compute_family_I, compute_family_II  # noqa: E402

COORD_DIR = os.path.join(_HERE, "coordinates")
TODAY = date.today().isoformat()


def _fitter_gate():
    p = os.path.join(_HERE, "fitter_validation.json")
    return bool(json.load(open(p)).get("all_pass")) if os.path.exists(p) else False


def _matched_axes(positions, gate):
    fI = compute_family_I(positions)
    fII = compute_family_II(positions)
    if not gate:
        fI["I.8_brody_q"] = None
        fI["I.9_berry_robnik_rho"] = None
    return {**fI, **fII}


# ── per-substrate position regenerators (cell_id → positions) ────────────────
def positions_maass():
    import maass_loader as ml
    out = {}
    for lvl in (91, 95, 85, 77, 93, 87):
        r = ml.load_eigenvalues_at_level(lvl)
        out[f"level_{lvl}"] = ml.unfold_gamma0(np.asarray(r, float), lvl)
    return out, "unfold_gamma0 on Γ₀(N) Maass spectral params (matched to AM NNS leg)"


def positions_mertens():
    import mertens_events as me
    cache = Path(_ROOT) / "data/phase34a_results/mertens_signchanges_N10000000.npz"
    sc = np.asarray(me.load_or_compute(10**7, cache_path=cache)["signchanges"], float)
    return ({
        "full": sc,
        "dense_1_to_4e6": sc[sc < 4e6],
        "tail_5e6_to_1e7": sc[(sc >= 5e6) & (sc < 1e7)],
    }, "raw Mertens sign-change integer positions (no pre-unfold; renorm in spacings)")


def positions_liouville():
    import liouville_events as le
    cache = Path(_ROOT) / "data/phase34b_results/liouville_signchanges_N1000000000.npz"
    sc = np.asarray(le.load_or_compute(10**9, cache_path=cache)["signchanges"], float)
    lo, hi = 906150257, 906488081
    cluster = sc[(sc >= lo) & (sc <= hi)]
    gaps = np.diff(cluster)
    boundary = (int(np.argmax(gaps)) + 1
                if gaps.size and gaps.max() > 1000 else len(cluster))
    return ({
        "full_133": sc,
        "cluster_132": cluster,
        "sub_low": cluster[:boundary],
        "sub_high": cluster[boundary:],
    }, "raw Liouville sign-change integer positions (no pre-unfold; renorm in spacings)")


def positions_lzeros():
    import zeros_loaders as zl
    import unfolding as uf
    z = zl.load_zeta_zeros("odlyzko_zeros6.txt")
    d = zl.load_dirichlet()
    e = zl.load_ec_curves()

    def pool(objs, substrate):
        return uf.pool_unfolded(
            [(o["conductor"], np.asarray(o["zeros"], float)) for o in objs],
            substrate=substrate)

    real = zl.dirichlet_by_character_type(d, is_real=True)
    comp = zl.dirichlet_by_character_type(d, is_real=False)
    ec_plus = zl.ec_by_root_number(e, +1)
    ec_minus = zl.ec_by_root_number(e, -1)
    ec_plus_pos = pool(ec_plus, "ec")
    ec_minus_pos = pool(ec_minus, "ec")
    return ({
        "zeta-low-height-bulk": uf.zeta_unfold(np.asarray(z[:10_000], float)),
        "zeta-mid-height-1e5-to-2e5": uf.zeta_unfold(np.asarray(z[100_000:200_000], float)),
        "dirichlet-real-Sp": pool(real, "dirichlet"),
        "dirichlet-complex-U": pool(comp, "dirichlet"),
        "ec-root-plus-SO-even": ec_plus_pos,
        "ec-root-minus-SO-odd": ec_minus_pos,
        # _qmax20 variants differ only in the q-banded leg; object-(a) identical
        "ec-root-plus-SO-even_qmax20": ec_plus_pos,
        "ec-root-minus-SO-odd_qmax20": ec_minus_pos,
    }, "phase34c unfolding (zeta_unfold / pool_unfolded per conductor) — matched NNS leg")


def positions_primes(which):
    if which == "gaussian-primes":
        import gaussian_primes as g
        gen, unf, sub = g.gaussian_prime_angles, g.hecke_unfold_gaussian, "gaussian"
    else:
        import eisenstein_primes as g
        gen, unf, sub = g.eisenstein_prime_angles, g.hecke_unfold_eisenstein, "eisenstein"
    return gen, unf, sub


# ── merge driver ─────────────────────────────────────────────────────────────
def _read(substrate):
    path = os.path.join(COORD_DIR, f"{substrate}.jsonl")
    return path, [json.loads(l) for l in open(path)]


def _write(path, recs):
    with open(path, "w") as f:
        for r in recs:
            f.write(json.dumps(r) + "\n")


def _merge(substrate, pos_by_cell, leg_note, gate):
    path, recs = _read(substrate)
    matched_n = 0
    rows = []
    for r in recs:
        cid = r["cell_id"]
        pos = pos_by_cell.get(cid)
        banked_n = (r.get("extraction_audit", {}).get("n_events_used")
                    or r.get("extraction_audit", {}).get("n_events"))
        if pos is None:
            rows.append((cid, "NO_REGEN", None, banked_n))
            continue
        pos = np.asarray(pos, float)
        ax = _matched_axes(pos, gate)
        r["axes_computed"].update(ax)
        r["applicable_axes_not_yet_computed"] = [
            a for a in r["applicable_axes_not_yet_computed"] if a not in ax]
        r["extraction_audit"]["object_a_recompute"] = {
            "leg": leg_note, "matched_to_AM": True, "fitter_gate_pass": gate,
            "n_events_regen": int(pos.size), "n_events_banked": banked_n,
            "date": TODAY}
        matched_n += 1
        rows.append((cid, "ok", int(pos.size), banked_n))
    _write(path, recs)
    return matched_n, rows


def main():
    gate = _fitter_gate()
    print("=" * 74)
    print(f"PHASE 2b (arithmetic + Maass) — fitter gate pass: {gate}")
    print("=" * 74)

    jobs = {
        "maass-gamma0": positions_maass,
        "mertens": positions_mertens,
        "liouville": positions_liouville,
    }
    total = 0

    def _report(substrate, n, rows):
        print(f"\n[{substrate}] {n} cells recomputed")
        for cid, st, nre, nbk in rows:
            tag = "" if (nre and nbk and abs(nre - nbk) <= max(2, 0.02 * nbk)) else "  <-- count mismatch"
            print(f"   {cid:32s} {st:8s} regen_n={nre} banked_n={nbk}{tag}")

    for substrate, fn in jobs.items():
        try:
            pos_by_cell, leg = fn()
        except Exception as ex:
            print(f"\n[{substrate}] GENERATOR FAILED: {type(ex).__name__}: {ex}")
            continue
        n, rows = _merge(substrate, pos_by_cell, leg, gate)
        total += n
        _report(substrate, n, rows)

    # L-zeros: regenerate the pooled positions ONCE, merge into the per-class split
    # files (ζ / Dirichlet / EC — see lzeros_split.py). _merge only touches cells
    # present in each file, so the same dict feeds all three.
    try:
        pos_lz, leg_lz = positions_lzeros()
    except Exception as ex:
        print(f"\n[L-zeros] GENERATOR FAILED: {type(ex).__name__}: {ex}")
    else:
        for substrate in ("L-zeros-zeta", "L-zeros-dirichlet", "L-zeros-ec"):
            if not os.path.exists(os.path.join(COORD_DIR, f"{substrate}.jsonl")):
                continue
            n, rows = _merge(substrate, pos_lz, leg_lz, gate)
            total += n
            _report(substrate, n, rows)

    # primes: parse X from cell_id, generate per cell
    for substrate in ("gaussian-primes", "eisenstein-primes"):
        path, recs = _read(substrate)
        gen, unf, sub = positions_primes(substrate)
        n = 0
        rows = []
        for r in recs:
            cid = r["cell_id"]
            try:
                xtok = cid.split("_X")[1]
                X = int(float(xtok.replace("e", "e")))
            except Exception:
                rows.append((cid, "BAD_X", None, None))
                continue
            angles = gen(X)
            pos = np.asarray(unf(angles), float)
            ax = _matched_axes(pos, gate)
            r["axes_computed"].update(ax)
            r["applicable_axes_not_yet_computed"] = [
                a for a in r["applicable_axes_not_yet_computed"] if a not in ax]
            banked_n = r["extraction_audit"].get("n_events_used")
            r["extraction_audit"]["object_a_recompute"] = {
                "leg": f"phase34d hecke_unfold_{sub} on prime angles X={X}",
                "matched_to_AM": True, "fitter_gate_pass": gate,
                "n_events_regen": int(pos.size), "n_events_banked": banked_n,
                "date": TODAY}
            n += 1
            rows.append((cid, "ok", int(pos.size), banked_n))
        _write(path, recs)
        total += n
        print(f"\n[{substrate}] {n} cells recomputed")
        for cid, st, nre, nbk in rows:
            print(f"   {cid:32s} {st:8s} regen_n={nre} banked_n={nbk}")

    print(f"\nTOTAL arithmetic+Maass cells recomputed: {total}")


if __name__ == "__main__":
    main()
