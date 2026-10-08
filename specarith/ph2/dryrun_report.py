"""Dry-run report: each synthetic bin's κ̂ (both arms) against the G0d known answer κ* for the same (bin, N), in units of
the G0d SD; verdict labels and red-path statuses; the A6(iii) witness. Reads results/run_synth/*.json and
results/g0d/*.json; writes results/run_synth/DRYRUN.md."""
import json
import os

import preread as R

RS = os.path.join(R.RES, "run_synth")
SYN = {"A": 2, "B": 3, "P1": 3, "P2": 3, "P3": 4, "P4": 4, "P5": 5, "P6": 5}


def main():
    md = ["| bin | N | arm | κ̂ | κ* (G0d) | (κ̂−κ*)/SD | G1 | widened/stat interval | ½-width pred → achieved | h_bin arm | ±20% arm |",
          "|---|---|---|---|---|---|---|---|---|---|---|"]
    red = ["| bin | misprint (mean, κ̂ prim, κ̂ sec) → FAILS as required | RP-mix (power) | RP-shuffle | mean spacing (band) |",
           "|---|---|---|---|---|"]
    for b, N in SYN.items():
        out = json.load(open(os.path.join(RS, f"{b}.json")))
        g = json.load(open(os.path.join(R.RES, "g0d", f"{b}_N{N}.json")))
        for arm in ("prim", "sec"):
            a, ga = out[arm], g[arm]
            sd_k = ga["kappa_sd_rel"] * ga["kappa_star"]
            lo, hi = a["kappa_ci_widened"]
            md.append(f"| {b} | {N} | {arm} | {a['kappa']:.4f} | {ga['kappa_star']:.4f} | {(a['kappa'] - ga['kappa_star']) / sd_k:+.2f} |"
                      f" {a['G1']} | [{lo:.4f}, {hi:.4f}] | {a['halfwidth']['predicted']:.4f} → {a['halfwidth']['achieved']:.4f} |"
                      f" {a['pinned_h_bin']} | {a['pinned_floor']} |")
        m = out["rp_misprint"]
        red.append(f"| {b} | ({m['arm_mean']}, {m['arm_N_prim']}, {m['arm_N_sec']}) → {m['FAILS_as_required']} |"
                   f" {out['rp_mix']['status']} ({out['rp_mix']['power']:.2f}) | {out['rp_shuffle']['status']} |"
                   f" {out['mean_spacing']['value']:.8f} (±{out['mean_spacing']['band']:.1e}) |")
    w = json.load(open(os.path.join(RS, "witness_achieved_P1.json")))
    text = ("# Phase 2 dry run (synthetic CUE_N bins at full size; no zero file opened)\n\n"
            "## Estimates vs G0d known answers\n\n" + "\n".join(md) +
            "\n\n## Red paths\n\n" + "\n".join(red) +
            f"\n\n## A6(iii) witness (P1, first {w['keep']} spacings)\n\n"
            f"{'FIRED' if w['FIRED'] else 'DID NOT FIRE'}: {json.dumps(w['checks'])}\n\n"
            f"half-widths predicted → achieved: PRIMARY {w['halfwidth']['prim']['predicted']:.4f} → "
            f"{w['halfwidth']['prim']['achieved']:.4f}; SECONDARY {w['halfwidth']['sec']['predicted']:.4f} → "
            f"{w['halfwidth']['sec']['achieved']:.4f}\n")
    open(os.path.join(RS, "DRYRUN.md"), "w").write(text)
    print(text)


if __name__ == "__main__":
    main()
