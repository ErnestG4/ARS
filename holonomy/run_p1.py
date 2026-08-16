"""P1 measurement: unfold->window vs window->unfold.  COMMITTED GENERATOR of
holonomy/p1_measured.json.  Runs only after the seal; every threshold from
prereg_sealed.json; verdicts via lattice_h.resolve_pair only.

Synthetic law leg: trended GUE, sealed dial ladder, Delta Sigma^2 per seed
vs the sealed continuum prediction (family-wise z).  Correctness leg: bias
vs the TRUTH-unfolded window (R4).  <r~> control: family-wise detection
halt.  NNS-KS secondary under the expectation-target form.  Bandwidth
jitter: sealed deg set, reported envelope on the mean Delta (both roles).

Zeta leg (deterministic point-check): the LIVE path semantics — RvM smooth
count + per-set renormalisation (census C1/C2) — under both orders;
sensitivity envelope from the sealed unfolding-variant jitter.
"""

import json
import sys

import numpy as np
from scipy.stats import norm

ROOT = "/home/combust/fmexplorer/criticality_tool"
sys.path.insert(0, f"{ROOT}/holonomy")

from transitions import (gen_trended_set, p1_apply, sigma2_at, rtilde,   # noqa: E402
                         nns_ks_gue, unfold_poly, central_ranks)

SEAL = json.load(open(f"{ROOT}/holonomy/prereg_sealed.json"))
import hashlib                                                            # noqa: E402
for f, sha in SEAL["code_freeze_blob_shas"].items():
    d = open(f"{ROOT}/holonomy/{f}", "rb").read()
    cur = hashlib.sha1(b"blob %d\0" % len(d) + d).hexdigest()
    assert cur == sha, f"FREEZE VIOLATION {f} — dated addendum required"

P1 = SEAL["p1"]
K = SEAL["k_arc"]
PRED = json.load(open(f"{ROOT}/holonomy/p1_prediction.json"))


def z_fam(n_cells):
    """Sealed family-wise rule: Bonferroni on the two-sided k-sigma alpha."""
    alpha = 2.0 * norm.sf(K)
    return float(norm.isf(alpha / (2.0 * n_cells)))


def synth_leg(deg, seeds):
    rows = {}
    for dial in P1["dials"]:
        ell = P1["n_W"] / dial
        dd = {f: [] for f in P1["L_fracs"]}
        bias = {f: {"A": [], "B": []} for f in P1["L_fracs"]}
        drt, dks = [], []
        for s in seeds:
            st = gen_trended_set(seed=s, N=2048, n_keep=P1["n_full"],
                                 a=P1["a"], ell=ell)
            A = p1_apply(st["x"], "unfold_then_window", deg, P1["n_W"])
            B = p1_apply(st["x"], "window_then_unfold", deg, P1["n_W"])
            T = st["u_true"][central_ranks(P1["n_full"], P1["n_W"])]
            Ls = [f * P1["n_W"] for f in P1["L_fracs"]]
            sA, sB, sT = sigma2_at(A, Ls), sigma2_at(B, Ls), sigma2_at(T, Ls)
            for f, a, b, t in zip(P1["L_fracs"], sA, sB, sT):
                dd[f].append(a - b)
                bias[f]["A"].append(abs(a - t))
                bias[f]["B"].append(abs(b - t))
            drt.append(rtilde(A) - rtilde(B))
            dks.append(abs(nns_ks_gue(A) - nns_ks_gue(T))
                       - abs(nns_ks_gue(B) - nns_ks_gue(T)))
        row = {}
        for f in P1["L_fracs"]:
            d = np.array(dd[f])
            row[f"L{f * P1['n_W']:.1f}"] = dict(
                mean=float(d.mean()), sem=float(d.std(ddof=1) / np.sqrt(len(d))),
                bias_A=float(np.mean(bias[f]["A"])),
                bias_B=float(np.mean(bias[f]["B"])),
                bias_A_sem=float(np.std(bias[f]["A"], ddof=1) / np.sqrt(len(seeds))),
                bias_B_sem=float(np.std(bias[f]["B"], ddof=1) / np.sqrt(len(seeds))))
        c = np.array(drt)
        k2 = np.array(dks)
        rows[f"dial{dial}"] = dict(
            cells=row,
            control_rtilde=dict(mean=float(c.mean()),
                                sem=float(c.std(ddof=1) / np.sqrt(len(c)))),
            ks_secondary=dict(mean=float(k2.mean()),
                              sem=float(k2.std(ddof=1) / np.sqrt(len(k2)))))
    return rows


def zeta_leg():
    zeros = np.load(f"{ROOT}/zeros_2000.npy")
    n_W = 1000

    def rvm(z):
        return (z / (2 * np.pi)) * np.log(np.maximum(z / (2 * np.pi * np.e),
                                                     1.0)) + 7.0 / 8.0

    def renorm(u):
        s = np.diff(np.sort(u))
        return np.sort(u) / s.mean()

    def order_A(z):          # unfold(+renorm) on FULL, then window
        u = renorm(rvm(z))
        return u[central_ranks(len(u), n_W)]

    def order_B(z):          # window first, then unfold(+renorm) per window
        zw = np.sort(z)[central_ranks(len(z), n_W)]
        return renorm(rvm(zw))

    Ls = [f * n_W for f in P1["L_fracs"]]
    dA, dB = sigma2_at(order_A(zeros), Ls), sigma2_at(order_B(zeros), Ls)
    delta = {f"L{L:.1f}": float(a - b) for L, a, b in zip(Ls, dA, dB)}
    # sensitivity envelope: sealed unfolding-variant jitter (poly degs)
    env = {}
    for deg in SEAL["zeta_env_degs"]:
        def poly_u(z):
            return np.sort(unfold_poly(np.sort(z), deg))
        a = sigma2_at(renorm(poly_u(zeros))[central_ranks(len(zeros), n_W)], Ls)
        zw = np.sort(zeros)[central_ranks(len(zeros), n_W)]
        b = sigma2_at(renorm(unfold_poly(zw, deg)), Ls)
        env[f"deg{deg}"] = {f"L{L:.1f}": float(x - y)
                            for L, x, y in zip(Ls, a, b)}
    spread = {k: float(np.ptp([delta[k]] + [env[d][k] for d in env]))
              for k in delta}
    ok = all(abs(delta[k]) <= SEAL["zeta_env_mult"] * spread[k]
             + SEAL["zeta_env_floor"] for k in delta)
    # materiality inputs: the live consumer is NNS classification (census
    # C1/C2 downstream rows) — bank all three class KS per ordering so the
    # resolver can compare |delta KS| to the class-gap margin
    from universality import compute_nns
    ks = {}
    for tag, ev in (("A", order_A(zeros)), ("B", order_B(zeros))):
        r = compute_nns(ev)
        ks[tag] = dict(poisson=float(r.ks_poisson), goe=float(r.ks_goe),
                       gue=float(r.ks_gue), best=r.best_fit)
    return dict(delta_sigma2=delta, jitter=env, spread=spread,
                envelope_ok=bool(ok), nns_ks=ks)


def main():
    import time
    t0 = time.time()
    seeds = list(range(SEAL["p1_seeds"]))
    out = dict(seal_cited="holonomy/prereg_sealed.json")
    out["synth"] = synth_leg(P1["deg"], seeds)
    out["bandwidth_envelope"] = {
        f"deg{d}": synth_leg(d, seeds[:SEAL["p1_env_seeds"]])
        for d in P1["jitter_degs"]}
    # law agreement (family-wise) vs sealed continuum prediction
    zf = z_fam(len(P1["dials"]) * len(P1["L_fracs"]))
    zs, worst = [], None
    for dial in P1["dials"]:
        for f in P1["L_fracs"]:
            cell = out["synth"][f"dial{dial}"]["cells"][f"L{f * P1['n_W']:.1f}"]
            pred = PRED["prediction"][f"dial{dial}"][f"L{f * P1['n_W']:.1f}"]["delta_pred"]
            z = (cell["mean"] - pred) / cell["sem"]
            zs.append(abs(z))
            if worst is None or abs(z) > worst[0]:
                worst = (abs(z), dial, f, cell["mean"], pred)
    law_agrees = bool(max(zs) <= zf)
    # control halt check (family-wise over dials)
    zc = [abs(out["synth"][f"dial{d}"]["control_rtilde"]["mean"])
          / out["synth"][f"dial{d}"]["control_rtilde"]["sem"]
          for d in P1["dials"]]
    control_ok = bool(max(zc) <= z_fam(len(P1["dials"])))
    out["law"] = dict(z_fam=zf, max_abs_z=float(max(zs)),
                      worst_cell=dict(z=worst[0], dial=worst[1], frac=worst[2],
                                      measured=worst[3], predicted=worst[4]),
                      law_agrees=law_agrees)
    out["control"] = dict(max_abs_z=float(max(zc)), ok=control_ok)
    out["zeta"] = zeta_leg()
    # correctness ruling input: which ordering less biased where separated
    out["ruling_input"] = dict(
        note="per-cell bias_A vs bias_B; sealed prediction says B (window-"
             "then-unfold) tracks the trend better at mid-dial",)
    out["elapsed_sec"] = float(time.time() - t0)
    json.dump(out, open(f"{ROOT}/holonomy/p1_measured.json", "w"), indent=1)
    print(f"P1: law_agrees={law_agrees} (max|z|={max(zs):.2f} vs "
          f"z_fam={zf:.2f}) control_ok={control_ok} "
          f"zeta_envelope_ok={out['zeta']['envelope_ok']}")
    if not control_ok:
        print("P1 CONTROL FIRED — instrument defect; HALT (tripwire 4)")
        sys.exit(2)


if __name__ == "__main__":
    main()
