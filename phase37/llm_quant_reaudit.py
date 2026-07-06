"""
phase37/llm_quant_reaudit.py — Set 3a: re-analyze the BANKED Phase-10 LLM fingerprints for the
numerical-quantization shift. Immediate (no model inference). Reads data/phase10_llm_fingerprints.json,
extracts (precision × structure × extractor) → mass03 / ks_Poisson / best, and tests whether coarser
quantization (fp16→int8→int4) systematically shifts the fingerprint. The banked data is single-shot per
cell (no surrogate), so this establishes the TREND; Set 3b (fresh extraction) provides the surrogate floor.
"""
from __future__ import annotations
import os, json
import numpy as np

THIS = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(THIS)
FP = os.path.join(ROOT, "data", "phase10_llm_fingerprints.json")


def main():
    d = json.load(open(FP))
    precs = ["fp16", "int8", "int4"]
    # collect per (structure, extractor): mass03 + ks_p across precisions
    structs = sorted({s for p in d for s in d[p]})
    exts = sorted({e for p in d for s in d[p] for e in d[p][s]})
    print(f"{'structure':14s} {'extractor':22s}  mass03 fp16->int8->int4    ksP fp16->int8->int4   trend")
    mono_up = mono_dn = 0; total = 0
    deltas_mass = []
    for st in structs:
        for ex in exts:
            try:
                ms = [d[p][st][ex]["primary_nns"]["mass03"] for p in precs]
                kp = [d[p][st][ex]["primary_nns"]["ks_p"] for p in precs]
                best = [d[p][st][ex]["primary_nns"]["best"] for p in precs]
            except KeyError:
                continue
            total += 1
            up = ms[0] <= ms[1] <= ms[2]; dn = ms[0] >= ms[1] >= ms[2]
            mono_up += up; mono_dn += dn
            deltas_mass.append(ms[2] - ms[0])
            trend = "↑mono" if up else ("↓mono" if dn else "  -  ")
            flip = "" if len(set(best)) == 1 else f"  best:{'/'.join(best)}"
            print(f"{st:14s} {ex:22s}  {ms[0]:.3f}->{ms[1]:.3f}->{ms[2]:.3f}   "
                  f"{kp[0]:.3f}->{kp[1]:.3f}->{kp[2]:.3f}  {trend}{flip}")
    print(f"\n  cells: {total}  | mass03 ↑monotone fp16→int4: {mono_up}  ↓monotone: {mono_dn}")
    print(f"  mean Δmass03 (int4 − fp16): {np.mean(deltas_mass):+.4f}  "
          f"(median {np.median(deltas_mass):+.4f}, max {max(deltas_mass):+.4f})")
    print("  NOTE: banked = single-shot per cell (no surrogate). Set 3b adds the rate-matched floor.")
    pos = sum(1 for x in deltas_mass if x > 0)
    print(f"  cells with int4 mass03 > fp16: {pos}/{total} "
          f"-> {'leans MORE clustering at coarser precision' if pos > total/2 else 'no consistent direction'}")


if __name__ == "__main__":
    main()
