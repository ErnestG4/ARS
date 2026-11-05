# SPDX-License-Identifier: AGPL-3.0-or-later
"""FN1-h2 read: POST-HOC descriptive summaries (written after the verdict was viewed; they decide nothing and change
no sealed label). Arithmetic on the sealed record results/h2/read/READ1.json and the pinned simulation
results/h2/FN1H2_SIM.json only; no data is read.

1. Where the primary s sits relative to the four sealed-simulation medians (conductor / L-value × runs in X / runs in
   N, curved truth at σ_μ 0.0213), in units of each scenario's robust SD(ŝ).
2. The h = 2 primary nine's mean offset from the h = 1 line in R units (s·b) at each β, and the same against the
   matched-N h = 1 references (sealed at β 0.55 only; β 0.45 / 0.40 here are post hoc).
3. The χ′ control (D′ = 5): mean measured ΔR against (★)'s committed "runs in X" and "runs in N" values, per β; how
   many of the nine fields lie nearer each; and with −163 left out.
4. The controls: Pearson r of each control constant with C over the primary nine, and of s_j with C, to see whether a
   control correlation could be the C-curvature of §5 in another form.
TOOLKIT §9.I: safeio.enforce(); output to scratch.
    python fn1h2_read_posthoc.py OUT_REL
"""
import json, math, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", ".."))
import safeio
safeio.enforce()

FN1 = os.path.join(HERE, "..")
PRIMARY = ["-35", "-40", "-51", "-52", "-88", "-91", "-115", "-123", "-148"]
H1 = {"-7": (-7, 2), "-8": (-8, 2), "-11": (-11, 2), "zi": (-4, 4), "-19": (-19, 2), "zw": (-3, 6), "-43": (-43, 2),
      "-67": (-67, 2), "-163": (-163, 2)}
BETAS = ["0.55", "0.45", "0.4"]


def ols(xs, ys):
    n = len(xs); mx = sum(xs) / n; my = sum(ys) / n
    b = sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / sum((x - mx) ** 2 for x in xs)
    return my - b * mx, b


def pearson(x, y):
    n = len(x); mx = sum(x) / n; my = sum(y) / n
    sxy = sum((a - mx) * (b - my) for a, b in zip(x, y))
    return sxy / math.sqrt(sum((a - mx) ** 2 for a in x) * sum((b - my) ** 2 for b in y))


def main(out):
    d = safeio.read_json(os.path.join(FN1, "results", "h2", "read", "READ1.json"))
    sim = safeio.read_json(os.path.join(FN1, "results", "h2", "FN1H2_SIM.json"))["scenarios"]
    ctl = safeio.read_json(os.path.join(FN1, "lead", "FN1H2_CONTROLS.json"))["h2"]
    res = dict(label="FN1-h2 read: POST-HOC descriptive summaries (no verdict)")
    s = d["primary"]["s"]
    corners = {}
    for key, name in (("conductor, runs in X", "curved truth, sigma_mu 0.0213: conductor"),
                      ("L-value, runs in X", "curved truth, sigma_mu 0.0213: L-value"),
                      ("conductor, runs in N", "curved truth, runs in N, sigma_mu 0.0213: conductor"),
                      ("L-value, runs in N", "curved truth, runs in N, sigma_mu 0.0213: L-value")):
        sc = sim[name]
        corners[key] = dict(median_s=sc["median_s"], sd=sc["sd_s_robust"],
                            z=(s - sc["median_s"]) / sc["sd_s_robust"])
    res["primary_s"] = s
    res["s_vs_sealed_sim_medians"] = corners

    C2 = {k: d["h2"][k]["C"] for k in d["h2"]}
    C1 = {f: math.log(abs(D_) * (w / 2) ** 2) for f, (D_, w) in H1.items()}
    off = {}
    for b in BETAS:
        a0, b0 = d["tests"][b]["line"]
        am, bm = ols([C1[f] for f in H1], [d["matched_N"]["refs"][f]["R"][b] for f in H1])
        o_full = sum(d["h2"][k]["R"][b] - a0 - b0 * C2[k] for k in PRIMARY) / 9
        o_mN = sum(d["h2"][k]["R"][b] - am - bm * C2[k] for k in PRIMARY) / 9
        off[b] = dict(line_full=[a0, b0], offset_R_full=o_full, s_full=o_full / b0, line_matchedN=[am, bm],
                      offset_R_matchedN=o_mN, s_matchedN=o_mN / bm,
                      mean_R_h1_full=sum(d["h1_refs"][f]["R"][b] for f in H1) / 9,
                      mean_R_h1_matchedN=sum(d["matched_N"]["refs"][f]["R"][b] for f in H1) / 9,
                      mean_R_h2_primary=sum(d["h2"][k]["R"][b] for k in PRIMARY) / 9)
    res["offsets"] = off

    chi = {}
    for b in BETAS:
        rows = {f: (v["dR"][b], v["pred_dR_runs_in_X"][b], v["pred_dR_runs_in_N"][b]) for f, v in d["chi5_control"].items()}
        def summ(keys):
            m = [rows[f][0] for f in keys]; px = [rows[f][1] for f in keys]; pn = [rows[f][2] for f in keys]
            return dict(n=len(keys), mean_measured=sum(m) / len(m), mean_pred_X=sum(px) / len(px),
                        mean_pred_N=sum(pn) / len(pn),
                        nearer_X=sum(abs(rows[f][0] - rows[f][1]) < abs(rows[f][0] - rows[f][2]) for f in keys),
                        above_both=sum(rows[f][0] > max(rows[f][1], rows[f][2]) for f in keys),
                        below_both=sum(rows[f][0] < min(rows[f][1], rows[f][2]) for f in keys))
        chi[b] = dict(all9=summ(list(rows)), without_m163=summ([f for f in rows if f != "-163"]))
    res["chi5_control_summary"] = chi

    sj = d["tests"]["0.55"]["s_j"]
    cP = [C2[k] for k in PRIMARY]
    res["controls_vs_C_primary9"] = dict(
        r_sj_C=pearson([sj[k] for k in PRIMARY], cP),
        r_LpL1_C=pearson([ctl[k]["LpL1"] for k in PRIMARY], cP),
        r_chen_C=pearson([ctl[k]["chen_Lterm"] for k in PRIMARY], cP))
    p = safeio.write_json(safeio.scratch(out), res, overwrite=True)
    print(json.dumps(res, indent=1))
    print("written", p)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1]))
