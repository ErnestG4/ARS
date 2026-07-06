"""
phase37/set3_discriminator.py — Set 3 substrate-vs-readout-quantization discriminator.

The fp16→int4 clustering shift on surprisal_threshold has TWO possible routes:
  (A) SUBSTRATE: int4 genuinely restructures the model's surprisals.
  (B) READOUT-QUANTIZATION: int4 coarsens the surprisal VALUES → threshold-crossings tie/bunch → false
      clustering — the Phase-36 grid artifact, living on the surprisal axis instead of a time axis.

Two checks (same logic as dt-refinement):
  1. Are int4 surprisals DISCRETIZED (few unique values / high tie fraction / large min-gap between sorted
     uniques) or CONTINUOUS (fp16-like)? Discretized → route B is live.
  2. DITHER test: add tiny noise (<< surprisal scale) to the surprisals before threshold-crossing, recompute
     mass03. If the fp16→int4 clustering shift DIES under dither → it was tie-bunching (route B). If it
     SURVIVES → genuine restructuring (route A, substrate). Caveat: only bites if quantization reaches the
     surprisal values; bnb nf4 is weight-only with high-precision compute → surprisals may stay continuous.
"""
from __future__ import annotations
import os, sys, json
import numpy as np

THIS = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(THIS)
sys.path.insert(0, ROOT)
from llm_cascade import extract_cascade, get_event_times, get_default_texts  # noqa: E402

MODEL = "Qwen/Qwen2.5-3B"
MAX_SEQ_LEN = 4096
OUT = os.path.join(THIS, "set3_discriminator.json")


def mass03_from_events(ev):
    e = np.sort(np.asarray(ev, float)); s = np.diff(e); s = s[s > 0]
    if s.size < 20:
        return None
    s = s / s.mean()
    return float(np.mean(s < 0.3))


def surprisal_discreteness(surp):
    """Is the surprisal series discretized? unique fraction, tie fraction, smallest gap between uniques."""
    s = np.asarray(surp, float)
    u = np.unique(s)
    sg = np.diff(np.sort(u))
    return dict(n=int(s.size), n_unique=int(u.size), unique_frac=float(u.size / s.size),
                tie_frac=float(1 - u.size / s.size),
                min_gap=float(sg.min()) if sg.size else None,
                std=float(s.std()),
                min_gap_over_std=float(sg.min() / s.std()) if sg.size and s.std() > 0 else None)


def main():
    text = get_default_texts()["structured"]   # the condition with the clearest fp16→int4 mass03 shift
    res = {}
    for quant in [None, "int4"]:
        ql = quant or "fp16"
        cascade = extract_cascade(text, model_name=MODEL, quantization=quant, max_seq_len=MAX_SEQ_LEN)
        surp = np.asarray(cascade["surprisal"], float)
        disc = surprisal_discreteness(surp)
        ev = get_event_times(cascade, method="surprisal_threshold", k=1.0)
        m_plain = mass03_from_events(ev)
        # dither: re-threshold on surprisals + tiny noise (1e-4 of std — far below any real structure,
        # but enough to break exact ties). Recompute events on the dithered series.
        rng = np.random.default_rng(0)
        cas_d = dict(cascade); cas_d["surprisal"] = surp + rng.normal(0, 1e-4 * disc["std"], surp.size)
        ev_d = get_event_times(cas_d, method="surprisal_threshold", k=1.0)
        m_dither = mass03_from_events(ev_d)
        res[ql] = dict(discreteness=disc, mass03_plain=m_plain, mass03_dither=m_dither)
        print(f"[{ql}] n={disc['n']} unique_frac={disc['unique_frac']:.4f} tie_frac={disc['tie_frac']:.4f} "
              f"min_gap/std={disc['min_gap_over_std']}", flush=True)
        print(f"      mass03 plain={m_plain:.4f}  dithered={m_dither:.4f}", flush=True)
        try:
            import torch, gc; del cascade, cas_d; gc.collect(); torch.cuda.empty_cache()
        except Exception:
            pass

    shift_plain = res["int4"]["mass03_plain"] - res["fp16"]["mass03_plain"]
    shift_dither = res["int4"]["mass03_dither"] - res["fp16"]["mass03_dither"]
    res["adjudication"] = dict(shift_plain=shift_plain, shift_dither=shift_dither)
    json.dump(res, open(OUT, "w"), indent=1)
    print("\n=== DISCRIMINATOR ===", flush=True)
    print(f"  fp16 surprisals discretized? tie_frac={res['fp16']['discreteness']['tie_frac']:.4f}", flush=True)
    print(f"  int4 surprisals discretized? tie_frac={res['int4']['discreteness']['tie_frac']:.4f}", flush=True)
    print(f"  mass03 shift (int4-fp16): plain={shift_plain:+.4f}  dithered={shift_dither:+.4f}", flush=True)
    if abs(shift_plain) < 1e-6:
        verdict = "no shift on this text"
    elif abs(shift_dither) >= 0.5 * abs(shift_plain):
        verdict = "SHIFT SURVIVES DITHER -> route A (SUBSTRATE: int4 restructures surprisals)"
    else:
        verdict = "SHIFT DIES UNDER DITHER -> route B (READOUT-QUANTIZATION: tie-bunching on surprisal_threshold)"
    print(f"  VERDICT: {verdict}", flush=True)
    res["verdict"] = verdict
    json.dump(res, open(OUT, "w"), indent=1)


if __name__ == "__main__":
    main()
