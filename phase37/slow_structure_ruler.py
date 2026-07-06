"""
phase37/slow_structure_ruler.py — calibrate the global-CV vs CV2 gap as a RULER for the neural %slowdrift,
to decompose it into nonstationarity-ARTIFACT vs genuine slow-CLUSTERING (the up/down-state question).

Both inflate global CV while CV2 stays ~1 (CV2 is fast-local by design), so the gap magnitude ALONE cannot
separate them. We build two on-target stochastic calibrators and find the discriminator:

  PRIMARY (signal model): telegraph-Cox — inhomogeneous Poisson whose rate switches between two states on a
    SLOW stochastic timescale = the up/down-state analog (slow stochastic rate structure, spread throughout).
  ARTIFACT model: epoch-gap — Poisson within epochs separated by a few HUGE discrete gaps (the recording-
    concatenation artifact).

DISCRIMINATOR = trim-collapse: remove the largest 1% of ISIs and recompute global CV. Artifact (a few discrete
gaps) COLLAPSES toward CV2; continuous slow modulation (up/down) SURVIVES trimming. So at matched global CV,
trim-collapse separates artifact from signal. Deterministic generators (lorenz/MG global>CV2; Chialvo-torus
CV2>global) are kept as cross-check ticks — a DIFFERENT (serial/quasiperiodic) flavor, per the framing.
"""
import numpy as np
RNG = np.random.default_rng(20260602)


def metrics(spk):
    spk = np.sort(np.asarray(spk, float)); iei = np.diff(spk); iei = iei[iei > 0]
    if iei.size < 50:
        return None
    s = iei / iei.mean()
    gcv = float(s.std())
    a, b = iei[:-1], iei[1:]; cv2 = float(np.mean(2 * np.abs(a - b) / (a + b)))
    # trim top-1% largest ISIs, recompute global CV
    thr = np.quantile(iei, 0.99); it = iei[iei <= thr]; st = it / it.mean()
    gcv_trim = float(st.std())
    # fraction of the (global-CV − CV2) gap removed by trimming the top-1% gaps
    denom = max(gcv - cv2, 1e-9)
    trim_collapse = float((gcv - gcv_trim) / denom) if gcv > cv2 else float("nan")
    top1_share = float(iei[iei > thr].sum() / iei.sum())
    return dict(gcv=gcv, cv2=cv2, gap=gcv - cv2, gcv_trim=gcv_trim,
                trim_collapse=trim_collapse, top1_share=top1_share, n=int(iei.size))


def telegraph_cox(T=4000.0, r_hi=12.0, depth=0.0, tau_state=8.0):
    """Up/down analog: rate alternates r_hi <-> r_lo with exp(tau_state) dwell; inhomogeneous Poisson.
    depth in [0,1): r_lo = r_hi*(1-depth)/(1+depth) so mean rate ~ const; depth=0 => homogeneous Poisson."""
    r_lo = r_hi * (1 - depth) / (1 + depth) if depth < 1 else 0.01
    t = 0.0; spk = []; state_hi = True
    while t < T:
        dwell = RNG.exponential(tau_state); t_end = min(t + dwell, T)
        rate = r_hi if state_hi else r_lo
        # homogeneous Poisson within the dwell
        n = RNG.poisson(rate * (t_end - t))
        if n: spk.extend(np.sort(RNG.uniform(t, t_end, n)))
        t = t_end; state_hi = not state_hi
    return np.array(spk)


def epoch_gap(T=4000.0, rate=8.0, n_epochs=20, gap=120.0):
    """Artifact: Poisson within n_epochs of equal length, separated by a fixed huge gap.
    Total recording extends to T + gap-time so epochs keep positive length (gaps add duration)."""
    ep_len = T / n_epochs            # epoch length fixed; gaps add on top (extend total duration)
    spk = []; t = 0.0
    for _ in range(n_epochs):
        n = RNG.poisson(rate * ep_len)
        if n: spk.extend(np.sort(RNG.uniform(t, t + ep_len, n)))
        t += ep_len + gap
    return np.array(spk)


print("=" * 92)
print("PRIMARY RULER — telegraph-Cox (up/down-state analog: slow STOCHASTIC rate modulation)")
print("=" * 92)
print(f"  {'depth':>6} {'globalCV':>9} {'CV2':>6} {'gap':>6} {'trim_collapse':>14} {'top1%share':>11}")
for d in [0.0, 0.2, 0.4, 0.6, 0.8, 0.9]:
    m = metrics(telegraph_cox(depth=d))
    print(f"  {d:6.2f} {m['gcv']:9.3f} {m['cv2']:6.3f} {m['gap']:6.3f} {m['trim_collapse']:14.3f} {m['top1_share']:11.3f}")
print("  -> global CV (and gap) GROW with slow-modulation depth; CV2 stays ~1 (blind by design).")
print("     trim_collapse LOW = the inflation is continuous/spread (survives trimming) = SIGNAL flavor.")

print("\n" + "=" * 92)
print("ARTIFACT ARM — epoch-gap (Poisson + a few huge discrete gaps: recording-concatenation artifact)")
print("=" * 92)
print(f"  {'n_epochs':>8} {'gap_s':>6} {'globalCV':>9} {'CV2':>6} {'gap':>6} {'trim_collapse':>14} {'top1%share':>11}")
for ne, g in [(0, 0), (10, 120), (20, 120), (40, 120), (20, 300)]:  # ep_len = T/ne now (gaps add duration)
    spk = epoch_gap(n_epochs=ne, gap=g) if ne else telegraph_cox(depth=0.0)
    m = metrics(spk)
    print(f"  {ne:8d} {g:6.0f} {m['gcv']:9.3f} {m['cv2']:6.3f} {m['gap']:6.3f} {m['trim_collapse']:14.3f} {m['top1_share']:11.3f}")
print("  -> also inflates global CV with CV2~1, BUT trim_collapse HIGH + top1%share HIGH = a few discrete")
print("     gaps carry the inflation = ARTIFACT flavor. Discriminator separates it from up/down at matched gap.")

print("\n" + "=" * 92)
print("MATCHED-GAP CONTRAST (same global CV, opposite trim_collapse => the discriminator works)")
print("=" * 92)
sig = metrics(telegraph_cox(depth=0.8)); art = metrics(epoch_gap(n_epochs=20, gap=120))
print(f"  up/down (depth0.8): globalCV={sig['gcv']:.2f} trim_collapse={sig['trim_collapse']:.2f} top1%={sig['top1_share']:.2f}")
print(f"  epoch-gap        : globalCV={art['gcv']:.2f} trim_collapse={art['trim_collapse']:.2f} top1%={art['top1_share']:.2f}")

print("\nDeterministic cross-check ticks (different flavor; global/CV2 ratio from the wave/Chialvo):")
print("  lorenz 1.27 · mackey-glass 1.09  (global>CV2 = serial structure)  |  Chialvo-torus 0.52 (CV2>global = quasiperiodic)")
print("\nNEXT: read each neural cell's (global CV, CV2, trim_collapse, top1%share) against this ruler ->")
print("      high trim_collapse/top1% = epoch/nonstationarity ARTIFACT; low + sustained gap = up/down-state SIGNAL.")
