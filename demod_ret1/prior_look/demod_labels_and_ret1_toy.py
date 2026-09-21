"""
demod_labels_and_ret1_toy.py -- two checks on DEMODULATION_FINDINGS.md

PART A. Do INTRINSIC/EXTRINSIC labels track MECHANISM or TIMESCALE?
  The two calibrators span one confound each: a slow Cox (should read
  EXTRINSIC) and a memoryless constant-rate gamma (should read INTRINSIC).
  Added here: a FAST Cox (stimulus-locked 6.25 Hz modulation, the pvc-11
  grating TF; pure rate modulation, zero intrinsic structure) and a SLOW
  INTRINSIC process (constant input, intrinsic up/down cycle, ~5 s on / ~10 s off).
  Statistic: mass03 (fraction of unit-mean ISIs < 0.3), reported raw and
  demodulated, with a demodulated-Poisson reference -- no ratio.
  Demodulator: rate estimated from the train itself, Gaussian kernel SD W
  (a stand-in; the repo's estimator may differ in kernel and edge handling).

PART B. Can a textbook FIRING-EVENTS model reproduce ret-1's printed
  signature (CV^2 2.14, Sigma^2 slope 0.44-0.78, R2(0.1) ~2.5, clusters per
  threshold 1.01/1.24/1.78/2.72 at 5/10/20/50 ms)? Events arrive
  quasi-regularly; each carries a few spikes with low count variance;
  intra-event intervals start after a 5 ms refractory floor. Then the ISI
  shuffle: F_inf = CV^2 (1 + 2 sum rho_k), so shuffling removes the
  serial-correlation factor and the long-range slope should jump toward CV^2.
Run: python3 demod_labels_and_ret1_toy.py     (numpy + scipy only)

Provenance: written by Will, handed over 2026-09-21 (pasted; not a sealed
generator, not a board row). Output banked alongside as
demod_labels_and_ret1_toy.out.txt from the run recorded in the commit.
"""
import numpy as np

DT = 0.001
RATE = 7.0          # Hz; the Part 4 Poisson-collapse rows are consistent with ~7 Hz
T_REC = 600.0


def rescale_by(t, lam):
    L = np.concatenate([[0.0], np.cumsum(lam) * DT])
    return np.interp(t, np.arange(len(L)) * DT, L)


def from_rate(rng, lam, k=1.0):
    """gamma(k) renewal in operational time, exact time change on the grid"""
    L = np.concatenate([[0.0], np.cumsum(lam) * DT])
    n = int(L[-1] * 1.3 + 100)
    tau = np.cumsum(rng.gamma(k, 1.0 / k, size=n))
    tau = tau[tau < L[-1]]
    return np.interp(tau, L, np.arange(len(L)) * DT)


def smooth_fft(x, sig):
    pad = int(min(4 * sig, len(x) - 1))
    xp = np.concatenate([x[pad:0:-1], x, x[-2:-pad - 2:-1]])
    f = np.fft.rfftfreq(len(xp))
    return np.fft.irfft(np.fft.rfft(xp) * np.exp(-0.5 * (2 * np.pi * f * sig) ** 2), n=len(xp))[pad:pad + len(x)]


def demod(t, W, T=T_REC):
    hist = np.bincount((t / DT).astype(int), minlength=int(T / DT) + 1).astype(float) / DT
    lam = np.maximum(smooth_fft(hist, W / DT), 0.02 * len(t) / T)
    return rescale_by(t, lam)


def mass03(t):
    s = np.diff(t)
    return np.mean(s / s.mean() < 0.3)


# ---------------------------------------------------------------- PART A
def part_a(rng):
    n = int(T_REC / DT)
    tt = np.arange(n) * DT
    trains = {}
    trains["poisson (reference)"] = from_rate(rng, np.full(n, RATE))
    # slow Cox: 2 s stimulus / 1 s blank, trial rates lognormal (tuning + gain)
    lam = np.empty(n)
    pos = 0
    while pos < n:
        lam[pos:pos + 2000] = rng.lognormal(0, 1.0)
        lam[pos + 2000:pos + 3000] = 0.3
        pos += 3000
    trains["slow Cox (EXTRINSIC)"] = from_rate(rng, lam / lam.mean() * RATE)
    # fast Cox: fully modulated 6.25 Hz, constant envelope -- pure rate modulation
    trains["fast Cox 6.25 Hz (EXTRINSIC)"] = from_rate(rng, RATE * (1 + np.cos(2 * np.pi * 6.25 * tt)))
    # constant-rate gamma CV=2 (the repo's intrinsic calibrator)
    trains["gamma CV=2 (INTRINSIC)"] = from_rate(rng, np.full(n, RATE), k=0.25)
    # slow intrinsic: constant input, intrinsic up/down cycle (active ~5 s, silent ~10 s)
    phases, pos, active = np.empty(n), 0, True
    while pos < n:
        d = int((rng.gamma(4, 1.25) if active else rng.gamma(4, 2.5)) / DT) + 1
        phases[pos:pos + d] = 3.0 if active else 0.05
        pos, active = pos + d, not active
    trains["slow intrinsic cycle (INTRINSIC)"] = from_rate(rng, phases / phases.mean() * RATE)

    Ws = (0.05, 0.2, 1.0, 5.0, 100.0)
    print("PART A  mass03 raw -> demodulated at W (Poisson raw = 0.259)")
    print(f"{'train':34s} {'raw':>6s} " + " ".join(f"{'W=' + format(w, 'g'):>7s}" for w in Ws))
    for name, t in trains.items():
        vals = [mass03(demod(t, W)) for W in Ws]
        print(f"{name:34s} {mass03(t):6.3f} " + " ".join(f"{v:7.3f}" for v in vals))


# ---------------------------------------------------------------- PART B
def events_train(rng, T, ev_rate, k_e, n_extra_p, n_extra_max, gap_mean):
    ev = np.cumsum(rng.gamma(k_e, 1.0 / (k_e * ev_rate), size=int(T * ev_rate * 1.3) + 10))
    ev = ev[ev < T]
    spikes = []
    for e in ev:
        m = 1 + rng.binomial(n_extra_max, n_extra_p)
        gaps = 0.005 + rng.gamma(2.0, (gap_mean - 0.005) / 2.0, size=m - 1)
        spikes.append(e + np.concatenate([[0.0], np.cumsum(gaps)]))
    t = np.sort(np.concatenate(spikes))
    return t[t < T]


def cv2(t):
    s = np.diff(t)
    return s.var() / s.mean() ** 2


def sigma2_slope(t, Ls=np.arange(4, 13), n_win=20000, rng=None):
    u = t / np.diff(t).mean()           # unit-mean time
    out = []
    for L in Ls:
        starts = rng.uniform(u[0], u[-1] - L, size=n_win)
        c = np.searchsorted(u, starts + L) - np.searchsorted(u, starts)
        out.append(c.var())
    return np.polyfit(Ls, out, 1)[0]


def r2_at(t, r=0.1, half=0.025):
    u = t / np.diff(t).mean()
    cnt = 0
    for j in range(1, 60):
        d = u[j:] - u[:-j]
        cnt += np.count_nonzero((d >= r - half) & (d < r + half))
    return cnt / (len(u) * 2 * half)


def clusters_per(t, thr):
    return len(t) / (1 + np.count_nonzero(np.diff(t) >= thr))


def part_b(rng):
    print("\nPART B  firing-events toy vs ret-1's printed numbers")
    print("  ret-1 (from the file): CV^2 2.14 | slope 0.44-0.78 | R2(0.1) ~2.5 | "
          "clusters/burst 1.01 / 1.24 / 1.78 / 2.72 at 5 / 10 / 20 / 50 ms")
    T = 6000.0
    for label, kw in [("events k_e=8, ~3 spikes", dict(ev_rate=RATE / 3.0, k_e=8, n_extra_p=0.5, n_extra_max=4, gap_mean=0.022)),
                      ("events k_e=3, ~3 spikes", dict(ev_rate=RATE / 3.0, k_e=3, n_extra_p=0.5, n_extra_max=4, gap_mean=0.022)),
                      ("events k_e=8, ~2 spikes", dict(ev_rate=RATE / 2.0, k_e=8, n_extra_p=0.5, n_extra_max=2, gap_mean=0.022))]:
        t = events_train(rng, T, **kw)
        s = np.diff(t)
        sh = np.concatenate([[t[0]], t[0] + np.cumsum(rng.permutation(s))])
        rho = [np.corrcoef(s[:-k], s[k:])[0, 1] for k in range(1, 30)]
        print(f"  {label:26s} rate {len(t) / T:4.1f} Hz | CV^2 {cv2(t):4.2f} | slope {sigma2_slope(t, rng=rng):4.2f}"
              f" -> shuffled {sigma2_slope(sh, rng=rng):4.2f} | CV^2(1+2*sum rho) {cv2(t) * (1 + 2 * sum(rho)):4.2f}"
              f" | R2(0.1) {r2_at(t):4.2f} | clusters/burst "
              + " / ".join(f"{clusters_per(t, th):4.2f}" for th in (0.005, 0.010, 0.020, 0.050)))
    p = rng.exponential(1 / RATE, size=int(T * RATE))
    tp = np.cumsum(p)
    print(f"  {'Poisson, same rate':26s} rate {RATE:4.1f} Hz | CV^2 {cv2(tp):4.2f} | slope {sigma2_slope(tp, rng=rng):4.2f}"
          f" | R2(0.1) {r2_at(tp):4.2f} | clusters/burst "
          + " / ".join(f"{clusters_per(tp, th):4.2f}" for th in (0.005, 0.010, 0.020, 0.050)))
    print("  Reading ret-1's own column: fraction of ISIs below threshold = 1 - 1/(clusters/burst) = "
          + " / ".join(f"{1 - 1 / x:.0%}" for x in (1.01, 1.24, 1.78, 2.72)) + " at 5 / 10 / 20 / 50 ms")


if __name__ == "__main__":
    rng = np.random.default_rng(11)
    part_a(rng)
    part_b(rng)
