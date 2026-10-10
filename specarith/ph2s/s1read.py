"""PH2S Stage 1 read (PH2S_SEAL_1.0): the shrink arms on F1, and the dry run through the same code.

  python s1read.py read            REFUSED unless seals/PH2S_SEAL_1.0.json exists, pins this code, and every F1 file's md5
                                   matches; F1 files in ../ph2r2/data/platt_fresh/ -> results/read/S1_READ.json
  python s1read.py dryrun          the same evaluation on (i) the seen R zeros vs the Stage 1 baseline mapped to R heights
                                   (expect A, C, D PASS) and (ii) a GUE stand-in at F1 heights, seeds 0–7 vs 8–15
                                   (expect A, C, D FAIL), plus the precision-guard witness -> results/dryrun/S1_DRYRUN.json

Rules (sealed): A — f = (0.5, 0.3), L = 10⁶: a bin shrinks iff d > 3·SE_c and it is resolvable (pre-data and achieved,
precision only); PASS iff ≥ 4 of the 5 core bins shrink (an unresolvable bin counts as not shrinking; F1a is NOT
RESOLVABLE pre-data, so PASS needs all of F1b–F1e). B — the same at L = 2·10⁵: descriptive (unresolvable pre-data in
every bin). C — Δ_u with unit-resampled SE; PASS iff Δ_u > 0 for ≥ 3 of 4 u and mean > 3·SE. D — WLS slope of d on L
over the six F1 bins; PASS iff slope + 2·SE < 0. Pooled one-sided test for A: descriptive.
"""
import hashlib
import json
import math
import os
import sys

import numpy as np

import s1lib as S
import s1preread as SP

SEAL = os.path.join(S.HERE, "seals", "PH2S_SEAL_1.0.json")
FRESH = os.path.join(S.HERE, "..", "ph2r2", "data", "platt_fresh")
CODE = ("s1lib.py", "s1preread.py", "s1read.py")
K_C = 3.0


def zeros_recs(path, name):
    """Disjoint windows of the file (one window each), all members at 10⁶, primary at 2·10⁵ (as s1preread.seen)."""
    g = S.bin_geometry(name)
    W = {L: S.zero_windows(path, L) for L in (S.L_PRIMARY, S.L_SECONDARY)}
    recs = []
    for k in range(max(len(W[L]) for L in W)):
        q = {"1000000": {}, "200000": {}}
        for L in W:
            if k < len(W[L]):
                for u, w in (S.FAMILY if L == S.L_PRIMARY else [S.PRIMARY]):
                    q[str(L)][f"{u}_{w}"] = S.growth(W[L][k], g, u, w, (2, k, L, SP.BIN_IDX[name], SP.MEM_IDX[f"{u}_{w}"]))
        recs.append(dict(window=k, **q))
    return recs


def arms(zrecs, brecs, core, dbins, d_ref, resolvable, zeros_joint):
    vals = lambda recs: {L: {k: [r[str(L)][k] for r in recs if k in r[str(L)]] for k in SP.MEM_IDX}
                         for L in (S.L_PRIMARY, S.L_SECONDARY)}
    zv = {n: vals(zrecs[n]) for n in zrecs}
    bv = {n: vals(brecs[n]) for n in brecs}
    res = SP.evaluate(core, zv, bv, d_ref, resolvable, dbins)
    res["B"]["status"] = "DESCRIPTIVE (unresolvable pre-data in every bin)"
    res["C"] = SP.arm_width_units({n: zrecs[n] for n in core}, {n: brecs[n] for n in core}, core, zeros_joint,
                                  nboot=2000, seed=7, k_se=K_C)
    ds = np.array([res["A"]["bins"][n]["d"] for n in core])
    ses = np.array([res["A"]["bins"][n]["se"] for n in core])
    w = 1 / ses ** 2
    pooled, pse = float(np.sum(w * ds) / np.sum(w)), float(1 / math.sqrt(np.sum(w)))
    res["A_pooled_descriptive"] = dict(d=pooled, se=pse, z=pooled / pse)
    return res


def read():
    if not os.path.exists(SEAL):
        raise SystemExit("REFUSED: no PH2S_SEAL_1.0.json — F1 zeros are not decoded before the seal")
    seal = json.load(open(SEAL))
    for f in CODE:
        if hashlib.sha256(open(os.path.join(S.HERE, f), "rb").read()).hexdigest() != seal["code_sha256"][f]:
            raise SystemExit(f"REFUSED: {f} differs from the sealed code")
    zrecs = {}
    for n, (fname, _, _) in S.F1.items():
        p = os.path.join(FRESH, fname)
        if hashlib.md5(open(p, "rb").read()).hexdigest() != seal["f1_md5"][fname]:
            raise SystemExit(f"REFUSED: {p} md5 differs from the pin")
        zrecs[n] = zeros_recs(p, n)
    brecs = {n: SP.load_base(os.path.join(S.HERE, "results", "preread"), n) for n in S.F1}
    res = arms(zrecs, brecs, list(S.CORE), list(S.F1), seal["d_ref"], seal["resolvable"], zeros_joint=False)
    os.makedirs(os.path.join(S.HERE, "results", "read"), exist_ok=True)
    json.dump(dict(zeros=zrecs, arms=res), open(os.path.join(S.HERE, "results", "read", "S1_READ.json"), "w"),
              indent=1, default=float)
    print(json.dumps({a: res[a]["verdict"] for a in "ACD"}), "B:", res["B"]["verdict"], "(descriptive)")


def dryrun():
    pre = json.load(open(os.path.join(S.HERE, "results", "preread", "preread.json")))
    out = {}
    # (i) seen R zeros through the read path (decoded again here; R files are seen)
    Rn = list(S.R)
    zR = {n: zeros_recs(os.path.join(S.HERE, "..", "ph2r2", "data", "platt", S.R[n][0]), n) for n in Rn}
    bR = {n: SP.load_base(os.path.join(S.HERE, "results", "preread"), n) for n in Rn}
    out["seen_R"] = arms(zR, bR, Rn, Rn, pre["d_ref"], {str(L): {} for L in (S.L_PRIMARY, S.L_SECONDARY)}, False)
    out["seen_R"]["expected"] = dict(A="PASS", C="PASS", D="PASS")
    # (ii) GUE stand-in at F1 heights: seeds 0–7 as the zeros, 8–15 as the baseline
    F1n = list(S.F1)
    allb = {n: SP.load_base(os.path.join(S.HERE, "results", "preread"), n) for n in F1n}
    za = {n: [r for r in allb[n] if r["seed"] < 8] for n in F1n}
    bb = {n: [r for r in allb[n] if r["seed"] >= 8] for n in F1n}
    out["gue_standin"] = arms(za, bb, list(S.CORE), F1n, pre["d_ref"], pre["resolvable"], True)
    out["gue_standin"]["expected"] = dict(A="FAIL", C="FAIL", D="FAIL")
    for k in ("seen_R", "gue_standin"):
        out[k]["as_expected"] = {a: out[k][a]["verdict"] == e for a, e in out[k]["expected"].items()}
    out["guard_witness"] = S.bin_shrink(1.0, 0.01, 0.2, math.inf, pre["d_ref"][str(S.L_PRIMARY)])
    out["guard_witness"]["FIRED"] = out["guard_witness"]["NOT_RESOLVABLE_achieved"]
    os.makedirs(os.path.join(S.HERE, "results", "dryrun"), exist_ok=True)
    json.dump(out, open(os.path.join(S.HERE, "results", "dryrun", "S1_DRYRUN.json"), "w"), indent=1, default=float)
    print(json.dumps({k: {a: out[k][a]["verdict"] for a in "ABCD"} for k in ("seen_R", "gue_standin")}),
          "as expected:", {k: out[k]["as_expected"] for k in ("seen_R", "gue_standin")},
          "witness:", out["guard_witness"]["FIRED"])


if __name__ == "__main__":
    {"read": read, "dryrun": dryrun}[sys.argv[1]]()
