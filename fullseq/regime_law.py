"""A repaired composition law, derived then tested out-of-sample.
COMMITTED GENERATOR of fullseq/regime_law.json.

The exhaustive run falsified the additive law and handed back a mechanism:
every significantly super-additive ordering places UNFOLD (T2) last or
second-to-last, and their measured Delta is pinned at ~ -3.20 regardless of
what the additive sum predicts.  That is a SATURATION regime, not a
correction term — the sum is not merely too large, it is irrelevant there.

PROPOSED TWO-REGIME LAW (derived POST-HOC from run 1 — this is exploratory,
not a prediction test, and is labelled as such):

    Regime B (UNFOLD in slot 3 or 4):  Delta = FLOOR, a constant
    Regime A (otherwise):              Delta = additive pairwise sum

HONEST STATUS: the regime boundary and the floor value were both read off
the same data that motivated them, so run 1 can only DESCRIBE.  The test
that matters is run 2 — FRESH SEEDS AND A DIFFERENT n — where the law's
parameters are carried over unchanged and asked to predict.  A law fitted on
run 1 and evaluated on run 1 would be the estimand mistake this session has
already made twice in other clothes.
"""

import hashlib
import itertools
import json
import sys

import numpy as np

ROOT = "/home/combust/fmexplorer/criticality_tool"
sys.path.insert(0, f"{ROOT}/fullseq")

SEAL = json.load(open(f"{ROOT}/fullseq/prereg_sealed.json"))
for f, sha in SEAL["code_freeze_blob_shas"].items():
    d = open(f"{ROOT}/fullseq/{f}", "rb").read()
    assert hashlib.sha1(b"blob %d\0" % len(d) + d).hexdigest() == sha, \
        f"FREEZE VIOLATION {f}"

from transitions_1d import (REFERENCE_ORDER, admissible, apply_sequence,   # noqa: E402
                            sigma2)

REF = REFERENCE_ORDER
L_STAT = 20.0
REGIME_B_SLOTS = (3, 4)          # UNFOLD last or second-to-last


def gue_unfolded(n, rng):
    A = (rng.standard_normal((n, n)) + 1j * rng.standard_normal((n, n))) / np.sqrt(2)
    H = (A + A.conj().T) / np.sqrt(2 * n)
    ev = np.sort(np.linalg.eigvalsh(H).real)
    x = np.clip(ev / 2.0, -1, 1)
    return (0.5 + (x * np.sqrt(1 - x * x) + np.arcsin(x)) / np.pi) * n


def measure(n_pts, n_seeds, seed0):
    subs = []
    for sd in range(n_seeds):
        rng = np.random.default_rng(seed0 + sd)
        pts = gue_unfolded(n_pts, rng)
        partner = gue_unfolded(n_pts // 2,
                               np.random.default_rng(seed0 + sd + 5000))
        u = rng.uniform(size=pts.size)
        p_ref, _ = apply_sequence(pts, REF, u, partner)
        subs.append((pts, u, partner, sigma2(p_ref, L_STAT)))
    pair = {}
    for a, b in itertools.combinations(REF, 2):
        o = REF.copy()
        ia, ib = o.index(a), o.index(b)
        o[ia], o[ib] = o[ib], o[ia]
        if not admissible(o):
            continue
        v = [sigma2(apply_sequence(p, o, u, pa)[0], L_STAT) - rv
             for p, u, pa, rv in subs]
        pair[f"{a}{b}"] = float(np.nanmean(v))
    rows = {}
    for o in [list(x) for x in itertools.permutations(REF)
              if admissible(list(x)) and list(x) != REF]:
        d = np.array([sigma2(apply_sequence(p, o, u, pa)[0], L_STAT) - rv
                      for p, u, pa, rv in subs], float)
        d = d[np.isfinite(d)]
        add = 0.0
        for i in range(5):
            for j in range(i + 1, 5):
                if REF.index(o[i]) > REF.index(o[j]):
                    a, b = sorted([o[i], o[j]], key=REF.index)
                    add += pair.get(f"{a}{b}", 0.0)
        rows["".join(o)] = dict(order=o, measured=float(d.mean()),
                                additive=add,
                                sem=float(d.std(ddof=1) / np.sqrt(d.size)),
                                regime=("B" if o.index("T2") in REGIME_B_SLOTS
                                        else "A"))
    return rows


def rmse(rows, predict):
    e = [predict(v) - v["measured"] for v in rows.values()]
    return float(np.sqrt(np.mean(np.square(e))))


def main():
    print("run 1 (n=1600, seeds 0-23) — DERIVE the law", flush=True)
    r1 = measure(1600, 24, 0)
    B1 = [v["measured"] for v in r1.values() if v["regime"] == "B"]
    floor = float(np.mean(B1))
    print(f"  regime B: n={len(B1)} measured mean {floor:.3f} "
          f"sd {np.std(B1, ddof=1):.3f}  (a constant if the sd is small)",
          flush=True)

    def additive(v):
        return v["additive"]

    def regime(v):
        return floor if v["regime"] == "B" else v["additive"]

    r1_stats = dict(rmse_additive=rmse(r1, additive),
                    rmse_regime=rmse(r1, regime),
                    floor=floor, n_B=len(B1),
                    B_sd=float(np.std(B1, ddof=1)))
    print(f"  RMSE additive {r1_stats['rmse_additive']:.3f} -> regime "
          f"{r1_stats['rmse_regime']:.3f} (descriptive only)", flush=True)

    print("run 2 (n=2400, seeds 700-723) — TEST it, parameters carried over",
          flush=True)
    r2 = measure(2400, 24, 700)
    B2 = [v["measured"] for v in r2.values() if v["regime"] == "B"]
    r2_stats = dict(rmse_additive=rmse(r2, additive),
                    rmse_regime_run1_floor=rmse(r2, regime),
                    run2_own_floor=float(np.mean(B2)),
                    run2_B_sd=float(np.std(B2, ddof=1)),
                    floor_carried=floor)
    print(f"  regime B at n=2400: mean {np.mean(B2):.3f} "
          f"sd {np.std(B2, ddof=1):.3f}  (run-1 floor was {floor:.3f})",
          flush=True)
    print(f"  RMSE additive {r2_stats['rmse_additive']:.3f} -> regime with "
          f"RUN-1 floor {r2_stats['rmse_regime_run1_floor']:.3f}", flush=True)

    improves = bool(r2_stats["rmse_regime_run1_floor"]
                    < r2_stats["rmse_additive"])
    floor_transfers = bool(abs(r2_stats["run2_own_floor"] - floor)
                           < 3 * r2_stats["run2_B_sd"])
    out = dict(
        status="regime boundary and floor DERIVED on run 1 (post-hoc, "
               "descriptive); TESTED on run 2 with fresh seeds and a "
               "different n, parameters carried over unchanged",
        regime_B_slots=list(REGIME_B_SLOTS), run1=r1_stats, run2=r2_stats,
        law_improves_out_of_sample=improves,
        floor_transfers_across_n=floor_transfers,
        verdict=("REGIME_LAW_SUPPORTED" if improves and floor_transfers
                 else "REGIME_LAW_NOT_SUPPORTED"),
        rows_run1=r1, rows_run2=r2)
    json.dump(out, open(f"{ROOT}/fullseq/regime_law.json", "w"), indent=1)
    print(f"\nout-of-sample improvement: {improves}; floor transfers across "
          f"n: {floor_transfers}")
    print(f"VERDICT: {out['verdict']}")


if __name__ == "__main__":
    main()
