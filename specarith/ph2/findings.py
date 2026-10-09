"""Phase 2 findings tables and figure (seal §8) from results/run/*.json under seals/PH2_SEAL_2.1.json.
Writes results/run/FINDINGS_TABLES.md and results/run/kappa_vs_height.png. Sealed verdicts and descriptive outputs are
kept in separate columns; nothing descriptive is scored."""
import json
import math
import os

import preread as R

RUN = os.path.join(R.RES, "run")
SEAL = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "seals", "PH2_SEAL_2.1.json")))
BINS = [b[0] for b in R.BINS]
FLAGS = {"A": "PRIMARY least informative: truncation bias ≈ allowance by construction (N_eff 2.16–2.42, allowance 0.160)"}


def fmt_ci(ci):
    lo, hi = ci
    return f"[{lo:.4f}, {'∞' if not math.isfinite(hi) else f'{hi:.4f}'}]"


def main():
    rows, verdict, red, desc = [], [], [], []
    verdict += ["| bin | N_eff | n | arm | κ̂ = N̂/N_eff | interval (PRIMARY widened) | ½-width pred → achieved | G1 | N=∞ excluded |"
                " h_bin arm | ±20% arm | note |", "|---|---|---|---|---|---|---|---|---|---|---|---|"]
    red += ["| bin | mean spacing (band) | RP-misprint (mean, κ̂ prim, κ̂ sec) → fails as required | RP-mix | RP-shuffle | RP-Λ |",
            "|---|---|---|---|---|---|"]
    desc += ["| bin | PRIMARY with sum allowance (A3) | window 1.8: κ̂ prim / sec | window 2.2: κ̂ prim / sec (flags) |",
             "|---|---|---|---|"]
    for b in BINS:
        o = json.load(open(os.path.join(RUN, f"{b}.json")))
        rows.append(o)
        for arm in ("prim", "sec"):
            a = o[arm]
            note = (FLAGS.get(b, "") if arm == "prim" else "the sharp test (statistical CI only)")
            verdict.append(f"| {b} | {o['N_eff_median']:.3f} | {o['n']:,} | {'PRIMARY' if arm == 'prim' else 'SECONDARY'} |"
                           f" {a['kappa']:.4f} | {fmt_ci(a['kappa_ci_widened'])} |"
                           f" {a['halfwidth']['predicted']:.4f} → {a['halfwidth']['achieved']:.4f} | **{a['G1']}** |"
                           f" {a['power_excludes_inf']} | {a['pinned_h_bin']} | {a['pinned_floor']} | {note} |")
        m = o["rp_misprint"]
        red.append(f"| {b} | {o['mean_spacing']['value']:.8f} (±{o['mean_spacing']['band']:.1e}) {'ok' if o['mean_spacing']['ok'] else 'OUT'} |"
                   f" ({m['arm_mean']}, {m['arm_N_prim']}, {m['arm_N_sec']}) → {m['FAILS_as_required']} |"
                   f" {o['rp_mix']['status']} (power {o['rp_mix']['power']:.2f}) | {o['rp_shuffle']['status']} | {o['rp_lambda']} |")
        ds = o["descriptive_prim_sum_allowance"]
        w = o["descriptive_window_sensitivity"]
        desc.append(f"| {b} | {ds['G1']} {fmt_ci(ds['kappa_ci_widened'])} |"
                    f" {w['1.8']['prim']['kappa']:.4f} / {w['1.8']['sec']['kappa']:.4f} |"
                    f" {w['2.2']['prim']['kappa']:.4f} / {w['2.2']['sec']['kappa']:.4f}"
                    f" ({w['2.2']['prim']['flag']}, {w['2.2']['sec']['flag']}) |")
    text = ("# Phase 2 results tables (under PH2_SEAL_2.1)\n\n## Sealed verdicts per bin\n\n" + "\n".join(verdict) +
            "\n\n## Red paths\n\n" + "\n".join(red) + "\n\n## Descriptive (never scored)\n\n" + "\n".join(desc) + "\n")
    open(os.path.join(RUN, "FINDINGS_TABLES.md"), "w").write(text)
    print(text)
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        fig, ax = plt.subplots(figsize=(8, 4.5))
        for arm, col, dx in (("prim", "C0", -0.15), ("sec", "C3", 0.15)):
            for o in rows:
                L = o["N_eff_median"] * R.NEFF_DEN
                a = o[arm]
                lo, hi = a["kappa_ci_widened"]
                hi_plot = min(hi, 2.0) if math.isfinite(hi) else 2.0
                ax.errorbar(L + dx, a["kappa"], yerr=[[a["kappa"] - lo], [max(hi_plot - a["kappa"], 0)]], fmt="o", ms=4,
                            color=col, alpha=0.4 if a["unresolved"] else 1.0,
                            label=("PRIMARY (widened)" if arm == "prim" else "SECONDARY (statistical)") if o is rows[0] else None)
        ax.axhline(1.0, color="k", lw=0.8)
        ax.axvspan(24.5, 44.6, color="0.9", label="no public data (24.5–44.6)")
        ax.set_xlabel("log(E/2π)")
        ax.set_ylabel("κ̂ = N̂ / N_eff")
        ax.set_ylim(0.4, 2.0)
        ax.legend(fontsize=8)
        ax.set_title("Phase 2: ζ spacings vs CUE(N_eff) per height (faded = NOT RESOLVABLE)")
        fig.tight_layout()
        fig.savefig(os.path.join(RUN, "kappa_vs_height.png"), dpi=140)
    except Exception as e:     # the tables are the record; the figure is a convenience
        print("figure not written:", e)


if __name__ == "__main__":
    main()
