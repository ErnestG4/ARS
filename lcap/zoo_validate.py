"""CONDITION 1 (Will's ruling, 2026-08-16): the capped policy must earn its
trust on the calibrator zoo ALONE, with no reference to zeta.
COMMITTED GENERATOR of lcap/zoo_measured.json.  Nonzero exit on failure —
run_lcap.py refuses to evaluate zeta unless this file records PASS.

The validity-window argument is substrate-independent physics; if the capped
rule classifies every zoo member of KNOWN class correctly, the policy stands
on its own.  Members whose expected Sigma^2 class is not independently
established are RUN AND REPORTED but carry no pass/fail weight — including
them as gate members would let an unestablished expectation adjudicate the
policy.
"""

import json
import sys

import numpy as np

ROOT = "/home/combust/fmexplorer/criticality_tool"
for p in (f"{ROOT}/rigidgate", f"{ROOT}/lcap", f"{ROOT}/sessionK"):
    if p not in sys.path:
        sys.path.insert(0, p)
import gate_probe as G                                          # noqa: E402
from proposed_rule import rigid_cell                            # noqa: E402

VAL = json.load(open(f"{ROOT}/lcap/validity_scales.json"))
POL = json.load(open(f"{ROOT}/lcap/policy.json"))
N = 2000
DEG = 6
SEEDS = 24
GATE_L = 50.0            # the deployed AUDIT_L the policy is compared against


def goe_positions(n, rng):
    """GOE (beta=1) eigenvalues, semicircle-unfolded to unit mean spacing."""
    A = rng.standard_normal((n, n))
    H = (A + A.T) / np.sqrt(2.0 * n)
    ev = np.sort(np.linalg.eigvalsh(H))
    x = np.clip(ev / 2.0, -1, 1)
    cdf = 0.5 + (x * np.sqrt(1 - x * x) + np.arcsin(x)) / np.pi
    return cdf * n


def full_verdict(sigma2, gue_band, pois_mean):
    """Proposed rule: the split RIGID branch, then the DEPLOYED Poisson-side
    cells unchanged (this arc changes the rigid branch only)."""
    v, z = rigid_cell(sigma2, gue_band)
    if v is not None:
        return v, z
    if sigma2 > 1.5 * pois_mean:
        return "SUPER_POISSON", z
    if sigma2 >= 0.6 * pois_mean:
        return "POISSON_INDEP", z
    return "INTERMEDIATE", z


def cap_for(tag):
    """L_judge from the derived policy (validity AND discrimination caps)."""
    row = POL["policy"].get(tag)
    if row is None:
        return POL["discrimination_L"], "discrimination cap only"
    return row["L_judge"], f"binding: {'+'.join(row['binding'])}"


# (tag, generator, expected verdict under the capped rule, gate member?)
MEMBERS = [
    ("gue_n2000", lambda r: G.gue_positions(N, r), "RIGID_GUE", True),
    ("goe", lambda r: goe_positions(N, r), None, True),   # expect NOT RIGID_GUE
    ("poisson", lambda r: G.poisson_positions(N, r), "POISSON_INDEP", True),
    ("clock", lambda r: np.arange(N, dtype=float), "HYPER_RIGID", True),
    ("jitter_clock", lambda r: np.sort(np.arange(N) + r.normal(0, 0.1, N)),
     "HYPER_RIGID", True),
    ("wigner_renewal", lambda r: G.DECOYS["renewal"](N, r), "INTERMEDIATE",
     True),
]


def farey_points(n_target=N):
    from farey_stride_calibrator import farey_spacings
    Q = 80
    sp = farey_spacings(Q)
    while sp.size < n_target and Q < 400:
        Q += 20
        sp = farey_spacings(Q)
    sp = sp[:n_target]
    sp = sp / sp.mean()
    return np.cumsum(sp)


def main():
    out = dict(gate_L=GATE_L, deg=DEG, n=N, members={}, reported={})
    fails = []
    for tag, gen, expected, is_gate in MEMBERS:
        L, capnote = cap_for("gue_n2000" if tag == "goe" else tag)
        gue_b, pois_b = G.bands(N, L, SEEDS, DEG)
        vals, verds = [], []
        for k in range(8):
            rng = np.random.default_rng(77_000 + k)
            v = G.sigma2(gen(rng), L, DEG)
            vals.append(v)
            verds.append(full_verdict(v, gue_b["sigma2"],
                                      pois_b["sigma2"]["mean"])[0])
        modal = max(set(verds), key=verds.count)
        z = (float(np.mean(vals)) - gue_b["sigma2"]["mean"]) / \
            gue_b["sigma2"]["sd"]
        ok = ((modal == expected) if expected is not None
              else (modal != "RIGID_GUE"))
        out["members"][tag] = dict(L=L, cap=capnote,
                                   sigma2_mean=float(np.mean(vals)),
                                   z=float(z), verdict=modal,
                                   expected=expected or "NOT RIGID_GUE",
                                   unanimous=bool(len(set(verds)) == 1),
                                   PASS=bool(ok))
        if is_gate and not ok:
            fails.append(f"{tag}: got {modal}, expected "
                         f"{expected or 'NOT RIGID_GUE'}")
        print(f"  {tag:16s} L={L:5.2f} Sigma2={np.mean(vals):8.4f} "
              f"z={z:+7.2f} -> {modal:14s} expected="
              f"{expected or 'NOT RIGID_GUE':14s} {'OK' if ok else 'FAIL'}",
              flush=True)

    # reported-only: expected Sigma^2 class not independently established
    try:
        L, capnote = cap_for("none")
        gue_b, pois_b = G.bands(N, L, SEEDS, DEG)
        v = G.sigma2(farey_points(), L, DEG)
        vv, z = full_verdict(v, gue_b["sigma2"], pois_b["sigma2"]["mean"])
        out["reported"]["farey"] = dict(
            L=L, sigma2=float(v), z=float(z), verdict=vv,
            note="REPORTED ONLY — no independently established Sigma^2 class "
                 "expectation, so this row carries no pass/fail weight")
        print(f"  [reported] farey    L={L:5.2f} Sigma2={v:8.4f} "
              f"z={z:+7.2f} -> {vv}", flush=True)
    except Exception as exc:                                # noqa: BLE001
        out["reported"]["farey"] = dict(error=str(exc))
        print(f"  [reported] farey unavailable: {exc}", flush=True)

    out["PASS"] = bool(not fails)
    out["failures"] = fails
    json.dump(out, open(f"{ROOT}/lcap/zoo_measured.json", "w"), indent=1)
    print(f"ZOO GATE PASS={out['PASS']}"
          + ("" if out["PASS"] else f" — {fails}"), flush=True)
    sys.exit(0 if out["PASS"] else 1)


if __name__ == "__main__":
    main()
