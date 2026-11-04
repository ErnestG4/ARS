# SPDX-License-Identifier: AGPL-3.0-or-later
"""Label check for RQ1 B2, RQ1-c P1 and RQ1-c P4's ordering (Will, 2026-11-03). Desk arithmetic on committed results;
no data are read. Definitions committed before the ℤ[ω] slices run.

Brief (verbatim): "Label check before any relabel. For each RQ1 and RQ1-c verdict, compute the noise-inflation factor at
which it would flip. Compare it with the slice 90% upper bound on noise (1 ÷ the lower end of model/empirical) at that
verdict's β and field. Upgrade "significance unresolved" to "significant under the slice-validated SE model" only where
flip factor > upper bound. Where it isn't, keep the label and state both numbers. State which β each verdict used. No
change to any verdict itself."

Definitions (declared here, before the ℤ[ω] slice numbers exist):
- **Slice upper bound** u(field, β) = 1 / (lower end of the slices' 90% interval on model/empirical), from
  `results/l13/L13_SLICES.json` (ℤ[√2], ℤ[i]) and `results/l13/L13_SLICES_ZW.json` (ℤ[ω]). The slices were taken at
  RQ1's 10¹⁰ matched N; the verdicts' 10¹¹ / 10¹² cells use the same β but larger N and K. u at the verdict's β is used
  for every X of that verdict, as the brief says (stated as a caveat, not corrected).
- **B2 and P1 (T rules: PASS iff T = Σ_cells D/SE_diff > t, guard D ≥ −2·SE_diff).** If the true noise is f × the model
  at every cell, T in true-SE units is T/f against the same t (t came from null replicates in model units), so the
  verdict flips at **f* = T/t**. The guard can only get easier under inflation. Compared with
  **U = max u over the verdict's fields (both) and β (its cells)**. Upgrade iff f* > U.
  - Also reported (descriptive): T_U = Σ D / SE_U with each cell's SE_diff recomputed as
    hypot(u_√2·R_√2·m, u_i·R_i·m), m = √(2/(cK)) (the per-field form of rq1_read.se_diff), against t.
- **P4 (sign rule: R_√2 > R_ω > R_i at β 0.55 at 10¹⁰, 10¹¹, 10¹²; no SE in the rule).** No noise inflation changes the
  observed R, so the sealed rule itself never flips; under its sealed null (three sets at equal R, exchangeable
  independent noise) the false-PASS rate is ≈ (1/6)³ at any noise scale. That reading is reported but is not the one
  used, because it does not test what the label is about (whether the separations exceed the noise).
  **Declared flip factor for P4:** for each of the six inequalities (two pairs × three X), z = ΔR / hypot(R_a·m, R_b·m)
  (the read report's SE); f*_ineq = z / 1.645 (the inflation at which that inequality is no longer one-sided 5%
  significant); compared with U_ineq = max(u_a, u_b) at β 0.55. **Upgrade iff f*_ineq > U_ineq for all six.**
  Also reported: z / 2 (the seal's 2-SE gating bar), and z_U = ΔR / hypot(u_a·R_a·m, u_b·R_b·m).
- No verdict changes. The output says only "upgrade" or "keep", with both numbers.

TOOLKIT §9.I: safeio.enforce(); the output goes to scratch (OUT_REL under ~/tmp/claude) and is copied into the repo
by a separate cp + git add.

  python rq1_label_check.py OUT_REL
"""
import json, math, os, sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import safeio
safeio.enforce()

HERE = os.path.dirname(os.path.abspath(__file__))
C_SE = 0.6271633049515984


def m(K):
    return math.sqrt(2 / (C_SE * K))


def ubounds():
    u = {}
    s = json.load(open(os.path.join(HERE, "results/l13/L13_SLICES.json")))
    for f in ("zs2", "zi"):
        for b, v in s["fields"][f].items():
            u[(f, float(b))] = 1 / v["model_over_emp_ci90"][0]
    pz = os.path.join(HERE, "results/l13/L13_SLICES_ZW.json")
    if os.path.exists(pz):
        for b, v in json.load(open(pz))["fields"]["zw"].items():
            u[("zw", float(b))] = 1 / v["model_over_emp_ci90"][0]
    return u


def main(out):
    u = ubounds()
    res = dict(label="Label check (Will, 2026-11-03): flip factor against the slice 90% noise upper bound",
               upper_bounds={f"{f} {b}": v for (f, b), v in sorted(u.items())}, verdicts={})
    # B2
    r1 = json.load(open(os.path.join(HERE, "results/read/read1.json")))
    t, T = r1["rule"]["t"], r1["B2_T"]
    cells = [(X, b) for X, b in r1["rule"]["cells"]]
    rows = {}
    for X, b in cells:
        rr = {r["beta"]: r for r in r1["rows"][str(X)]["rows"]}[b]
        rows[(X, b)] = rr
    betas = sorted({b for _, b in cells})
    U = max(u[(f, b)] for f in ("zs2", "zi") for b in betas)
    TU = sum((rows[c]["R_zs2"] - rows[c]["R_zi"]) /
             math.hypot(u[("zs2", c[1])] * rows[c]["R_zs2"] * m(rows[c]["K"]),
                        u[("zi", c[1])] * rows[c]["R_zi"] * m(rows[c]["K"])) for c in cells)
    res["verdicts"]["RQ1 B2"] = dict(cells=[[X, b, rows[(X, b)]["K"]] for X, b in cells], betas=betas, T=T, t=t,
                                     flip_factor=T / t, U=U, T_at_U=TU, T_at_U_over_t=TU / t,
                                     outcome="upgrade" if T / t > U else "keep")
    # P1
    rc = json.load(open(os.path.join(HERE, "results/rq1c_read_void/read1.json")))
    p1 = rc["P1"]
    betas = sorted(float(b) for b in p1["cells"])
    U = max(u[(f, b)] for f in ("zs2", "zi") for b in betas)
    res["verdicts"]["RQ1-c P1"] = dict(X=10 ** 12, betas=betas, K=rc.get("K_1e12"), T=p1["T"], t=p1["t"],
                                       flip_factor=p1["T"] / p1["t"], U=U,
                                       outcome="upgrade" if p1["T"] / p1["t"] > U else "keep",
                                       note="T_at_U not recomputed: the 10^12 cells' per-field R are in the read's R "
                                            "table; SE_diff scales by at most U, so T_at_U >= T/U")
    res["verdicts"]["RQ1-c P1"]["T_over_U_over_t"] = p1["T"] / U / p1["t"]
    # P4
    ineq = []
    for X, c in rc["P4"]["cells"].items():
        c = c["0.55"]
        K = c["K"]
        for a, bb in (("zs2", "zw"), ("zw", "zi")):
            Ra, Rb = c[f"R_{a}"], c[f"R_{bb}"]
            z = (Ra - Rb) / math.hypot(Ra * m(K), Rb * m(K))
            d = dict(X=X, pair=f"{a}-{bb}", K=K, z=z, flip_factor=z / 1.645, flip_factor_2SE=z / 2)
            if (a, 0.55) in u and (bb, 0.55) in u:
                d["U"] = max(u[(a, 0.55)], u[(bb, 0.55)])
                d["z_at_U"] = (Ra - Rb) / math.hypot(u[(a, 0.55)] * Ra * m(K), u[(bb, 0.55)] * Rb * m(K))
                d["exceeds"] = d["flip_factor"] > d["U"]
            ineq.append(d)
    done = all("U" in d for d in ineq)
    res["verdicts"]["RQ1-c P4 ordering"] = dict(
        beta=0.55, inequalities=ineq, flip_factor=min(d["flip_factor"] for d in ineq),
        outcome=("upgrade" if all(d["exceeds"] for d in ineq) else "keep") if done else "pending (zw slices)",
        sign_rule_note="the sealed rule has no SE; under its equal-R null with exchangeable independent noise the "
                       "false-PASS rate is about (1/6)^3 at any noise scale (not the declared reading)")
    print("written", safeio.write_json(safeio.scratch(out), res, overwrite=True))
    for k, v in res["verdicts"].items():
        print(k, "flip %.3f" % v["flip_factor"], "U %s" % (("%.3f" % v["U"]) if "U" in v else "-"), v["outcome"])


if __name__ == "__main__":
    main(sys.argv[1])
