"""RIGID_GUE arc KAG (brief §4) — the legal debugging window.
COMMITTED GENERATOR of rigidgate/kag_measured.json.

Witnesses, each two-sided (TOOLKIT §9: a one-sided witness certifies
nothing):
  A. the deployed classifier CAN say yes: real GUE -> RIGID rate ~1;
  B. it CAN say no: Poisson -> RIGID rate ~0;
  C. the PROPOSED HYPER_RIGID arm CAN fire (a clock must trip it) and CAN
     stay silent (real GUE must not trip it) — the arm's specificity cost is
     measured here, before it is proposed;
  D. marginal-exactness of the adversarial family verified as an IDENTITY,
     not a statistic: the antithetic construction and the renewal decoy from
     the same seed have bit-identical sorted spacing multisets, so their NNS
     is identical by permutation invariance.

IN-WINDOW DESIGN CHANGE (recorded, pilot-informed-seal): a Sigma^2 GROWTH
arm was specified in brief §2 and FAILED witness C as originally written
(GUE pass 0.42, flat-process pass 0.75 — underpowered at a 2x L lever,
where the GUE log-increment ~0.07 sits under single-realization noise
~0.13).  Its Delta_3 replacement is well powered but rejects the banked
zeta row for a physically real reason (see proposed_rule.py).  The growth
arm was therefore withdrawn as a GATE and retained as a reported
diagnostic; the proposed fix became the HYPER_RIGID cell split.  Both
rejected designs are banked in this file's `rejected_designs` block so the
choice is auditable.
"""

import json
import sys

import numpy as np

ROOT = "/home/combust/fmexplorer/criticality_tool"
sys.path.insert(0, f"{ROOT}/rigidgate")

import gate_probe as G                                          # noqa: E402
from proposed_rule import rigid_cell                            # noqa: E402

CONFIGS = {"C-brocot": (343, 6.86), "C-add5": (1200, 20.0),
           "C-zeta": (2000, 40.0)}
N_SEEDS_BAND = 24
DEG = 6
RES = {}


def main():
    print("A/B. deployed-classifier two-sided witness", flush=True)
    for name, (n, L) in CONFIGS.items():
        gue_b, _ = G.bands(n, L, N_SEEDS_BAND, DEG)
        b = G.gue_boundary(gue_b)
        g = G.gue_sample(n, L, 16, 41_000, DEG)
        p = np.array([G.sigma2(G.poisson_positions(
            n, np.random.default_rng(42_000 + k)), L, DEG) for k in range(16)])
        RES.setdefault("witness", {})[name] = dict(
            boundary=float(b),
            gue_rigid_rate=float(np.mean(g <= b)),
            poisson_rigid_rate=float(np.mean(p <= b)),
            gue_mean=float(g.mean()), poisson_mean=float(p.mean()))
        print(f"  {name}: GUE rigid-rate {np.mean(g <= b):.2f} "
              f"Poisson rigid-rate {np.mean(p <= b):.2f}", flush=True)

    print("C. proposed HYPER_RIGID arm, two-sided", flush=True)
    hyper = {}
    for name, (n, L) in CONFIGS.items():
        gue_b, _ = G.bands(n, L, N_SEEDS_BAND, DEG)
        band = gue_b["sigma2"]
        clock = np.arange(n, dtype=float)
        v_clock, z_clock = rigid_cell(G.sigma2(clock, L, DEG), band)
        g = G.gue_sample(n, L, 16, 41_000, DEG)
        gue_hyper_rate = float(np.mean(
            [rigid_cell(v, band)[0] == "HYPER_RIGID" for v in g]))
        hyper[name] = dict(clock_verdict=v_clock, clock_z=float(z_clock),
                           gue_false_hyper_rate=gue_hyper_rate)
        print(f"  {name}: clock -> {v_clock} (z={z_clock:+.2f}); "
              f"real-GUE false-HYPER rate {gue_hyper_rate:.2f}", flush=True)
    RES["hyper_arm"] = hyper

    print("D. marginal-exactness IDENTITY check", flush=True)
    ident = []
    for k in range(6):
        s_ren = G.wigner_spacings(1200, np.random.default_rng(44_000 + k))
        for f in (0.0, 0.3, 1.0):
            a = G.antithetic_order(s_ren.copy())
            kk = int(round(f * a.size))
            rng2 = np.random.default_rng(44_000 + k)
            if kk > 1:
                idx = rng2.choice(a.size, size=kk, replace=False)
                a[idx] = rng2.permutation(a[idx])
            ident.append(bool(np.array_equal(np.sort(a), np.sort(s_ren))))
    RES["marginal_exact_identity"] = dict(all_identical=bool(all(ident)),
                                          n_checks=len(ident))
    print(f"  multiset identity: {all(ident)} over {len(ident)} checks",
          flush=True)

    RES["rejected_designs"] = {
        "sigma2_growth_arm": dict(
            why="failed witness C as specified in brief §2",
            gue_pass_rate=0.42, flat_pass_rate=0.75,
            diagnosis="2x L lever: GUE log-increment ~0.07 under "
                      "single-realization noise ~0.13 — underpowered by "
                      "construction"),
        "delta3_growth_arm": dict(
            why="well powered (12:1) but rejects the banked zeta row",
            zeta_growth_z=-9.50,
            diagnosis="zeta_first_2000 Sigma^2 is nearly flat in L "
                      "(0.30->0.39 over L=2->40 vs GUE 0.40->0.74); "
                      "lens absorbs 0.0% at n=2000 and the deviation is "
                      "lens-invariant, so the flatness is real (Berry "
                      "saturation, ln(T/2pi)=5.99) — a growth arm cannot "
                      "separate low-height zeta from a clock"),
    }

    w = RES["witness"]
    RES["PASS"] = bool(
        all(v["gue_rigid_rate"] >= 0.9 for v in w.values())
        and all(v["poisson_rigid_rate"] <= 0.05 for v in w.values())
        and all(v["clock_verdict"] == "HYPER_RIGID" for v in hyper.values())
        and all(v["gue_false_hyper_rate"] <= 0.05 for v in hyper.values())
        and RES["marginal_exact_identity"]["all_identical"])
    json.dump(RES, open(f"{ROOT}/rigidgate/kag_measured.json", "w"), indent=1)
    print(f"KAG PASS={RES['PASS']}", flush=True)
    sys.exit(0 if RES["PASS"] else 1)


if __name__ == "__main__":
    main()
