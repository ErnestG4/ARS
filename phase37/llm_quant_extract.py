"""
phase37/llm_quant_extract.py — Set 3b: fresh Qwen2.5-3B extraction across fp16/int8/int4 (4090).

The Phase-36 capstone parallel: numerical quantization (precision) as a quantization knob, asked the same
way temporal-grid quantization was. Does coarser numerical precision (fp16→int8→int4) systematically shift
the ARS fingerprint toward MORE structure (clustering: mass03↑/CV↑, or rigidity)? Preliminary in the banked
fingerprints: surprisal_threshold structured mass03 0.294→0.308→0.354.

Adds over the banked single-shot Phase-10 run: (1) the two-axis lens (CV + mass03 = sign-carrier) on the
event spacings; (2) a rate/length-matched Poisson SURROGATE floor (10 seeds) per condition, so the
fp16→int4 shift can be judged against noise; (3) quantization is the ONLY varied knob (text + extractor +
seq_len held fixed). NOT pooled across texts (each text is its own sequence — no pooled-temporal confound).
"""
from __future__ import annotations
import os, sys, json, time, gc
import numpy as np

THIS = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(THIS)
sys.path.insert(0, ROOT)
from llm_cascade import extract_cascade, get_event_times, get_default_texts  # noqa: E402
from arithmetic_toolkit import full_analysis  # noqa: E402

QUANTS = [None, "int8", "int4"]          # fp16 (None) → int8 → int4
MODEL = "Qwen/Qwen2.5-3B"
MAX_SEQ_LEN = 4096                        # more tokens than the banked run (2048) → more events per sequence
EXTRACTORS = [("surprisal_threshold", dict(k=1.0)),
              ("surprisal_cumulative", dict(prom=0.3)),
              ("residual_norm_peaks", dict(prom=0.3))]
OUT = os.path.join(THIS, "set3b_llm_quant.jsonl")
N_SUR = 10


def two_axis(events):
    """Two-axis readout on an event-time sequence: CV + mass03 (clustering, sign-carrier) +
    ks_poisson/ks_gue (shape). Unit-mean spacings, continuous-time (no grid)."""
    e = np.sort(np.asarray(events, float)); s = np.diff(e); s = s[s > 0]
    if s.size < 20:
        return None
    s = s / s.mean()
    ss = np.sort(s); emp = np.arange(1, ss.size + 1) / ss.size
    ksP = float(np.max(np.abs(emp - (1 - np.exp(-ss)))))
    ksG = float(np.max(np.abs(emp - (1 - np.exp(-np.pi * ss ** 2 / 4)))))
    return dict(n=int(s.size), cv=float(s.std()), mass03=float(np.mean(s < 0.3)),
                ks_poisson=ksP, ks_gue=ksG)


def surrogate_floor(n_events, dur, seed0=0):
    """Rate/length-matched uniform-Poisson floor for CV + mass03 (mean±std over seeds)."""
    cvs, masses = [], []
    for k in range(N_SUR):
        rng = np.random.default_rng(90000 + seed0 + k)
        e = np.sort(rng.uniform(0, dur, n_events)); s = np.diff(e); s = s[s > 0]
        if s.size < 20:
            continue
        s = s / s.mean(); cvs.append(float(s.std())); masses.append(float(np.mean(s < 0.3)))
    if not cvs:
        return None
    return dict(cv_mean=float(np.mean(cvs)), cv_std=float(np.std(cvs)),
                mass_mean=float(np.mean(masses)), mass_std=float(np.std(masses)))


def main():
    texts = get_default_texts()
    rows = []
    fh = open(OUT, "w")
    for quant in QUANTS:
        qlabel = quant if quant else "fp16"
        print("=" * 70, flush=True); print(f"  {MODEL}  QUANT={qlabel}", flush=True)
        for stim, text in texts.items():
            t0 = time.time()
            try:
                cascade = extract_cascade(text, model_name=MODEL, quantization=quant,
                                          max_seq_len=MAX_SEQ_LEN)
            except Exception as e:
                print(f"  [{stim}] extract_cascade FAILED: {e}", flush=True)
                rec = dict(quant=qlabel, stim=stim, error=str(e))
                fh.write(json.dumps(rec) + "\n"); fh.flush(); rows.append(rec); continue
            print(f"  [{stim}] n_tok={cascade['seq_len']} "
                  f"meanS={np.mean(cascade['surprisal']):.3f} ⏱{time.time()-t0:.1f}s", flush=True)
            for method, kw in EXTRACTORS:
                ev = get_event_times(cascade, method=method, **kw)
                ta = two_axis(ev)
                if ta is None:
                    rec = dict(quant=qlabel, stim=stim, extractor=method,
                               error="insufficient", n=int(ev.size))
                    fh.write(json.dumps(rec) + "\n"); fh.flush(); rows.append(rec); continue
                dur = float(np.ptp(np.sort(ev)))
                sur = surrogate_floor(ta["n"], dur)
                rec = dict(quant=qlabel, stim=stim, extractor=method, **ta, surrogate=sur,
                           cv_z=((ta["cv"] - sur["cv_mean"]) / max(sur["cv_std"], 1e-9)) if sur else None,
                           mass_z=((ta["mass03"] - sur["mass_mean"]) / max(sur["mass_std"], 1e-9)) if sur else None)
                fh.write(json.dumps(rec) + "\n"); fh.flush(); rows.append(rec)
                print(f"      [{method:<22}] n={ta['n']:>4} CV={ta['cv']:.3f} mass03={ta['mass03']:.3f} "
                      f"ksP={ta['ks_poisson']:.3f} (cv_z={rec['cv_z']:+.1f} mass_z={rec['mass_z']:+.1f})", flush=True)
            del cascade; gc.collect()
            try:
                import torch; torch.cuda.empty_cache()
            except Exception:
                pass
    fh.close()

    # quantization-shift adjudication: per (stim, extractor) is mass03/CV monotone fp16→int8→int4?
    print("\n=== QUANTIZATION SHIFT (fp16 → int8 → int4), per stim×extractor ===", flush=True)
    import collections
    by = collections.defaultdict(dict)
    for r in rows:
        if "mass03" in r:
            by[(r["stim"], r["extractor"])][r["quant"]] = r
    for key, d in sorted(by.items()):
        if all(q in d for q in ("fp16", "int8", "int4")):
            ms = [d[q]["mass03"] for q in ("fp16", "int8", "int4")]
            cvs = [d[q]["cv"] for q in ("fp16", "int8", "int4")]
            mono = "↑MONOTONE" if ms[0] <= ms[1] <= ms[2] else ("↓MONOTONE" if ms[0] >= ms[1] >= ms[2] else "non-mono")
            print(f"  {key[0]:12s} {key[1]:22s} mass03 {ms[0]:.3f}->{ms[1]:.3f}->{ms[2]:.3f} ({mono}) "
                  f"CV {cvs[0]:.3f}->{cvs[1]:.3f}->{cvs[2]:.3f}", flush=True)
    print(f"\nWrote {OUT} ({len(rows)} rows)", flush=True)


if __name__ == "__main__":
    main()
