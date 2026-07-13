"""
cross_substrate/ret1_rf.py — retinal pillar-2: RF-quality (white-noise STA SNR) vs ks_gue, burst-controlled.

ret-1 has no motion stimulus, so this is NOT the motion/direction axis-kind. It is a FEEDFORWARD-circuit test
of pillar-2 on an RF/encoding-quality axis: does a retinal ganglion cell's extrinsic selectivity-quality (how
well-defined its spatial receptive field is) track its universality class (ks_gue), controlling for intrinsic
burst? RF reconstructed from the precomputed binary white-noise (ran1.bin, bit-packed, LSB-first) per the
dataset's Analysis_example.m recipe: m=Nx*Ny bars/frame, STA over a 0.5 s window → (m x n_lag) STRF per cell.
RF-quality = STA peak SNR (peak |STA| / robust baseline std). Joins ks_gue + burst from ret1-cell.jsonl.

Run: --validate (one recording, check STA is structured)  |  --run (all)  |  --analyse
Out: coordinates/ret1-rf.jsonl
"""
from __future__ import annotations

import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(_v, "1")

import argparse
import glob
import json
import sys
from datetime import date

import numpy as np
import scipy.io

_HERE = os.path.dirname(os.path.abspath(__file__))
RET = os.path.expandvars("$HOME/fmexplorer/crcns_cache/ret1/crcns_ret-1")
DATA = os.path.join(RET, "Data")
RAN1 = os.path.join(RET, "ran1.bin")
COORD = os.path.join(_HERE, "coordinates")

_BITS = None


def _ran1_bits():
    global _BITS
    if _BITS is None:
        raw = np.fromfile(RAN1, dtype=np.uint8)
        _BITS = np.unpackbits(raw, bitorder="little")  # MATLAB fread ubit1 = LSB-first
    return _BITS


def strf_for_recording(f, w=0.5):
    """Return (strf [Ncell, m, n_lag], stim meta, spike-counts-per-frame). Block = longest white-noise."""
    m_ = scipy.io.loadmat(f, squeeze_me=True, struct_as_record=False)
    stim = np.atleast_1d(m_["stimulus"]); ncell = int(getattr(m_["datainfo"], "Ncell"))
    nstim = len(stim)
    sp = np.asarray(m_["spikes"], dtype=object)
    if sp.ndim == 1:
        sp = sp.reshape(ncell, nstim) if nstim == 1 else sp.reshape(nstim, ncell).T
    elif sp.shape[0] != ncell and sp.shape[1] == ncell:
        sp = sp.T
    durs = [float(s.frame) * int(s.Nframes) for s in stim]
    blk = int(np.argmax(durs)); s = stim[blk]
    Nx = int(s.param.x // s.param.dx); Ny = int(s.param.y // s.param.dy); m = Nx * Ny
    frame = float(s.frame); Nframes = int(s.Nframes); onset = float(s.onset)
    n = int(round(w / frame))
    N = Nframes - 1
    bits = _ran1_bits()[: m * N]
    stimseq = (2.0 * bits.reshape(N, m) - 1.0)                       # frame x space, ±1
    edges = np.arange(Nframes) * frame + onset                       # Nframes edges
    C = np.zeros((N, ncell))
    for j in range(ncell):
        spk = np.atleast_1d(sp[j, blk]).astype(float)
        cnt = np.histogram(spk, bins=edges)[0].astype(float)         # length N
        cnt[:n - 1] = 0.0
        tot = cnt.sum()
        C[:, j] = cnt / tot if tot > 0 else cnt
    # STA: rf[lag, space, cell] = sum_frame stimseq[frame-lag, space] * C[frame, cell]
    strf = np.zeros((n, m, ncell))
    for lag in range(n):
        # frames where frame-lag >=0
        strf[lag] = stimseq[: N - lag].T @ C[lag:]                   # (m x cell)
    return np.transpose(strf, (2, 1, 0)), dict(m=m, n=n, Nx=Nx, Ny=Ny, frame=frame), C


def rf_quality(strf_cell):
    """STA peak SNR: peak |STA| / robust std of STA away from the peak (MAD-based). strf_cell: m x n_lag."""
    a = strf_cell
    peak = float(np.max(np.abs(a)))
    # baseline noise: MAD over the earliest (most acausal-ish) third of lags, all space
    nlag = a.shape[1]
    base = a[:, : max(2, nlag // 3)]
    sd = 1.4826 * np.median(np.abs(base - np.median(base)))
    snr = peak / sd if sd > 0 else np.nan
    # peak lag/space
    pi = np.unravel_index(np.argmax(np.abs(a)), a.shape)
    return {"rf_snr": float(snr), "rf_peak": peak, "peak_space": int(pi[0]), "peak_lag": int(pi[1])}


def validate():
    f = os.path.join(DATA, "20080516_R1.mat")
    strf, meta, C = strf_for_recording(f)
    print(f"validate 20080516_R1: m={meta['m']} bars, n={meta['n']} lags, {strf.shape[0]} cells")
    for j in range(min(strf.shape[0], 5)):
        q = rf_quality(strf[j])
        print(f"  cell {j}: rf_snr={q['rf_snr']:.1f}  peak={q['rf_peak']:.4f} at space={q['peak_space']} lag={q['peak_lag']}")
    # a structured RF should have snr >> a temporally-flat control (shuffle lags)
    j = int(np.argmax([rf_quality(strf[k])["rf_snr"] for k in range(strf.shape[0])]))
    print(f"  best cell {j} rf_snr={rf_quality(strf[j])['rf_snr']:.1f} (structured RF => high SNR; noise => ~few)")
    print("  -> if best-cell SNR is many-fold above ~3, STA reconstruction + bit order are correct.")


def run():
    files = sorted(glob.glob(os.path.join(DATA, "*.mat")))
    out = open(os.path.join(COORD, "ret1-rf.jsonl"), "w")
    n = 0
    print(f"ret-1 RF-quality (STA SNR) — {len(files)} recordings")
    for f in files:
        rid = os.path.basename(f).replace(".mat", "")
        strf, meta, C = strf_for_recording(f)
        for j in range(strf.shape[0]):
            q = rf_quality(strf[j])
            out.write(json.dumps({"substrate": "ret1-rf", "recording": rid, "cell": j,
                                  **q, "m": meta["m"], "n_lag": meta["n"],
                                  "source_artifact": "generated (ret-1 white-noise STA RF-quality)",
                                  "computed_date": date.today().isoformat()}) + "\n")
            n += 1
        out.flush()
        print(f"  {rid:14s} {strf.shape[0]:>3d} cells  median rf_snr="
              f"{np.median([rf_quality(strf[k])['rf_snr'] for k in range(strf.shape[0])]):.1f}", flush=True)
    out.close()
    print(f"→ {n} RF-quality records. --analyse next.")


def analyse():
    from scipy import stats
    rf = {(r["recording"], r["cell"]): r for r in (json.loads(l) for l in open(os.path.join(COORD, "ret1-rf.jsonl")) if l.strip())}
    cell = {(r["recording"], r["cell"]): r for r in (json.loads(l) for l in open(os.path.join(COORD, "ret1-cell.jsonl")) if l.strip())}
    rows = []
    for k, rfr in rf.items():
        c = cell.get(k)
        if c is None:
            continue
        snr = rfr["rf_snr"]; ks = c["axes_computed"].get("I.5q_ks_gue_med"); bf = (c.get("burst") or {}).get("burst_frac")
        if None not in (snr, ks, bf) and all(np.isfinite(x) for x in (snr, ks, bf)):
            rows.append((snr, bf, ks))
    a = np.array(rows)
    print(f"ret-1 PILLAR-2 (RF-quality STA-SNR ↔ ks_gue), feedforward circuit, n={len(a)}\n")
    snr, bf, ks = a[:, 0], a[:, 1], a[:, 2]
    r_raw, p_raw = stats.spearmanr(snr, ks)
    r_sb, _ = stats.spearmanr(snr, bf)
    r_bk, _ = stats.spearmanr(bf, ks)
    # partial controlling for burst
    rx = stats.rankdata(snr); ry = stats.rankdata(ks); rz = stats.rankdata(bf)
    bx = rx - np.polyval(np.polyfit(rz, rx, 1), rz); by = ry - np.polyval(np.polyfit(rz, ry, 1), rz)
    r_part, p_part = stats.pearsonr(bx, by)
    print(f"  RF-quality ↔ ks_gue   RAW      : ρ={r_raw:+.3f} p={p_raw:.1e}")
    print(f"  RF-quality ↔ burst              : ρ={r_sb:+.3f}")
    print(f"  burst ↔ ks_gue                  : ρ={r_bk:+.3f}")
    print(f"  RF-quality ↔ ks_gue  PARTIAL|burst: ρ={r_part:+.3f} p={p_part:.1e}  retained={100*r_part/r_raw:.0f}%" if r_raw else "")
    print(f"\n  NB: lower ks_gue = more GUE-like. Sign of RAW ρ tells whether better-RF cells are more/less GUE.")
    print(f"  median rf_snr={np.median(snr):.1f}; cells with rf_snr>5 (well-defined RF): {(snr>5).sum()}/{len(snr)}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--validate", action="store_true"); ap.add_argument("--run", action="store_true")
    ap.add_argument("--analyse", action="store_true")
    a = ap.parse_args()
    if a.validate:
        validate()
    elif a.run:
        run()
    elif a.analyse:
        analyse()
    else:
        ap.error("need --validate | --run | --analyse")


if __name__ == "__main__":
    main()
