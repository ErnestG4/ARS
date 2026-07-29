"""
cross_substrate/brocot_audio_harness.py — audio → partial-extraction → fingerprint, validated.

The brocot LUT-fitting workflow will fit families to recorded SY/ARP targets. Those are AUDIO, so we
need an extractor: audio → partial set → fingerprint. This harness builds it and VALIDATES it against
`predict_partials` on KNOWN configs (recording-independent), so the extractor is trusted before it
touches a real recording.

Pipeline:
  render_fm(config)  — offline parallel-FM synthesis: y(t)=sin(2π f_c t + Σ I_i sin(2π f_c r_i t)).
                       This is exactly the model predict_partials expands via Bessel functions.
  extract_partials(y) — Hann-windowed FFT → FREQUENCY-DOMAIN spectral peak-picking (+ parabolic interp).
                       NB: this is partial extraction in the FREQUENCY domain (the standard sinusoidal
                       analysis), NOT time-domain find_peaks on an autocorrelated trace — that latter is
                       the §7.ter.19 artifact, and we deliberately avoid it. The output is partial
                       FREQUENCIES (then fingerprinted), not a find_peaks spacing sequence.

Validation per config: extracted partial set vs predict_partials (frequency match-rate, amplitude
correlation) AND fingerprint agreement (Brody q / W1δ / I.5 on extracted-freqs vs predicted-freqs).
If both agree, the extractor is trustworthy for the SY/ARP recordings. Run: --validate.
"""
from __future__ import annotations

import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(_v, "1")

import sys

import numpy as np
from scipy.signal import find_peaks

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_HERE)
_BROCOT = os.path.expandvars("$HOME/fmexplorer/brocot")
for p in (_BROCOT, _ROOT):
    if p not in sys.path:
        sys.path.insert(0, p)

from phase3.partial_prediction import predict_partials                # noqa: E402
from cross_substrate.axes import canonical_spacings, FAMILY_I         # noqa: E402

SR = 48000
DUR = 2.0
F_CARRIER = 220.0


def render_fm(ratios, depths, f_carrier=F_CARRIER, sr=SR, dur=DUR):
    """Offline parallel-FM render (the model predict_partials expands)."""
    t = np.arange(int(sr * dur)) / sr
    phase = 2 * np.pi * f_carrier * t
    for r, I in zip(ratios, depths):
        phase = phase + I * np.sin(2 * np.pi * f_carrier * r * t)
    return np.sin(phase)


def extract_partials(y, sr=SR, threshold_db=-50.0, f_min=20.0, f_max=20000.0):
    """Partials from audio via Hann-FFT + frequency-domain peak-picking (parabolic-interpolated).
    Frequency-domain spectral peaks = partials (standard); NOT time-domain find_peaks."""
    w = np.hanning(len(y))
    mag = np.abs(np.fft.rfft(y * w))
    freqs = np.fft.rfftfreq(len(y), 1.0 / sr)
    if mag.max() <= 0:
        return np.zeros(0), np.zeros(0)
    thr = mag.max() * 10.0 ** (threshold_db / 20.0)
    pk, _ = find_peaks(mag, height=thr)
    fpk, apk = [], []
    logm = np.log(mag + 1e-300)
    for k in pk:
        if 1 <= k < len(mag) - 1:                       # parabolic sub-bin refinement
            a, b, c = logm[k - 1], logm[k], logm[k + 1]
            denom = (a - 2 * b + c)
            d = 0.5 * (a - c) / denom if denom != 0 else 0.0
            fpk.append(freqs[k] + d * (freqs[1] - freqs[0]))
            apk.append(mag[k])
        else:
            fpk.append(freqs[k]); apk.append(mag[k])
    fpk, apk = np.array(fpk), np.array(apk)
    keep = (fpk >= f_min) & (fpk <= f_max)
    return fpk[keep], apk[keep]


def _fp(freqs):
    f = np.sort(np.asarray(freqs, float))
    if f.size < 20:
        return None
    s = canonical_spacings(f)
    return {k: (float(FAMILY_I[k](s)) if FAMILY_I[k](s) is not None
                and np.isfinite(FAMILY_I[k](s)) else None)
            # R-179: explicit key list, so the FAMILY_I registry repair does not reach it for
            # free. `I.8_brody_q_unbounded` added alongside the bounded one.
            for k in ("I.5_ks_gue", "I.1_w1_clock", "I.8_brody_q",
                      "I.8_brody_q_unbounded")}


def _match(pred_f, ext_f, tol_hz=3.0):
    """Fraction of predicted partials with an extracted partial within tol."""
    if pred_f.size == 0:
        return 0.0
    ext = np.sort(ext_f)
    hit = 0
    for f in pred_f:
        i = np.searchsorted(ext, f)
        near = min([abs(ext[j] - f) for j in (i - 1, i) if 0 <= j < ext.size] or [1e9])
        if near <= tol_hz:
            hit += 1
    return hit / pred_f.size


CONFIGS = [
    ("harmonic r1 I2",     [1.0], [2.0]),
    ("2-mod r1,r1.5 I3",   [1.0, 1.5], [3.0, 3.0]),
    ("bridge [1,golden] I4", [1.0, (np.sqrt(5) - 1) / 2], [4.0, 4.0]),
    ("bridge [1,golden] I6", [1.0, (np.sqrt(5) - 1) / 2], [6.0, 6.0]),
    ("bridge [1,liouv] I6",  [1.0, sum(10.0 ** -e for e in (1, 2, 6, 24, 120, 720))], [6.0, 6.0]),
]


def validate():
    print(f"AUDIO HARNESS VALIDATION — render→FFT→extract vs predict_partials (sr={SR}, dur={DUR}s)")
    print(f"{'config':24s} {'n_pred':>6s} {'n_ext':>6s} {'match%':>6s} {'q_pred':>6s} {'q_ext':>6s} {'I.5_p':>6s} {'I.5_e':>6s}")
    for name, ratios, depths in CONFIGS:
        sp = predict_partials(ratios, depths, f_carrier=F_CARRIER)
        y = render_fm(ratios, depths)
        ef, ea = extract_partials(y)
        m = _match(np.sort(sp.freqs), ef)
        fp_p = _fp(sp.freqs)
        fp_e = _fp(ef)
        def g(d, k):
            return f"{d[k]:.3f}" if d and d.get(k) is not None else "  -"
        print(f"{name:24s} {sp.freqs.size:>6d} {ef.size:>6d} {m*100:>5.0f}% "
              f"{g(fp_p,'I.8_brody_q'):>6s} {g(fp_e,'I.8_brody_q'):>6s} "
              f"{g(fp_p,'I.5_ks_gue'):>6s} {g(fp_e,'I.5_ks_gue'):>6s}")
    print("\n[gate] high match% + agreeing Brody q / I.5 (pred vs ext) ⇒ extractor validated, "
          "predict_partials tracks real synthesis → trust the harness on SY/ARP recordings.")


def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--validate", action="store_true")
    a = ap.parse_args()
    if a.validate:
        validate()
    else:
        ap.error("need --validate")


if __name__ == "__main__":
    main()
