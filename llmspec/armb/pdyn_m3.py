"""M3 -- EDGE / outlier dynamics of the top-K singular triplets across checkpoints.

Input per checkpoint: sig (>= K, descending), U (d_out, >= K), V (d_in, >= K): top-K singular values and left/right
vectors (the bank's U32/V32 give K <= 32; this phase uses K = 16). Everything below uses |overlaps| only, so the
sign gauge of (u_j, v_j) -- joint or independent flips -- cannot change any metric (calibrator C5; verify (d) checks
bit-identity).

Per consecutive pair of checkpoints (a -> b):
  OVERLAP      O_ij = (|<u_i(a), u_j(b)>| + |<v_i(a), v_j(b)>|) / 2   (i, j in top-K; mean of the two sides, declared)
  MATCHING     Hungarian (scipy linear_sum_assignment) maximising sum_i O_{i, perm(i)}; the matched overlap O_i is
               the match quality; swaps = number of i with perm(i) != i (index-order changes).
  SIGN FIX     the matched (u, v) at b are flipped so that <u_i(a), u_perm(i)(b)> >= 0 (and v likewise) -- returned
               for trajectory plots only; no metric depends on it.
  GAP RULE     Davis-Kahan: sin(theta) <= ||dW||_2 / gap. ||dW|| is not available from the bank, so the per-step
               spectral change delta_ab = max_j |sig_j(b) - sig_j(a)| over the top-K (a Weyl lower bound on
               ||dW||_2; declared proxy) stands in: level i's match is ACCEPTED only if its local gap
               g_i = min(sig_{i-1} - sig_i, sig_i - sig_{i+1}) exceeds gap_mult * delta_ab at BOTH a and b
               (for i = K-1 the lower gap uses sig_K when the input carries > K levels, else only the upper gap),
               AND the matched overlap O_i >= overlap_min. Otherwise the match is FLAGGED ambiguous.
  AVOIDED CROSSINGS  for each adjacent pair (i, i+1) the gap series g(t) = sig_i(t) - sig_{i+1}(t); an event is an
               interior local minimum of g with g_min < event_frac * median_t g (declared); the minimum is refined
               by fitting g^2 (EXACTLY quadratic in t for a two-level system) through the three points around it:
               t_min = vertex, g_min = sqrt(vertex value) (clipped at the observed minimum if the parabola dips
               below 0). MIXING ANGLE theta = arccos |<u_i(t_{k-1}), u_i(t_{k+1})>| (and the V-side analogue): the
               rotation of the level-i vector across the event (90 deg = complete adiabatic swap of the two diabatic
               states; small = diabatic passage). An event is AMBIGUOUS if either step k-1 -> k or k -> k+1 was
               flagged for level i or i+1; the ambiguous fraction is reported, and the event times are exported as
               a point process (sorted array), all events and unambiguous events separately.
Outputs: analyse() -> dict (per-step arrays + events); CLI reads an npz with sig (T, >=K), U (T, d_out, >=K),
V (T, d_in, >=K), times (T,).
"""
import sys, json
from pathlib import Path
import numpy as np
from scipy.optimize import linear_sum_assignment

PARAMS = dict(K=16, gap_mult=2.0, overlap_min=0.5, event_frac=0.5)
EST = "pdyn_m3-v1"


def overlap(Ua, Va, Ub, Vb):
    return 0.5 * (np.abs(Ua.T @ Ub) + np.abs(Va.T @ Vb))


def match(Ua, Va, Ub, Vb):
    O = overlap(Ua, Va, Ub, Vb)
    r, c = linear_sum_assignment(-O)
    perm = np.empty(len(r), int); perm[r] = c
    return perm, O[r, c], O


def local_gaps(sig, K):
    """g_i = min(upper gap, lower gap) for i < K; uses sig[K] for the last lower gap when available."""
    s = np.asarray(sig, float)
    g = np.full(K, np.inf)
    for i in range(K):
        up = s[i - 1] - s[i] if i > 0 else np.inf
        lo = s[i] - s[i + 1] if i + 1 < len(s) else np.inf
        g[i] = min(up, lo)
    return g


def step(sig_a, Ua, Va, sig_b, Ub, Vb, K, gap_mult, overlap_min):
    Ua, Va, Ub, Vb = Ua[:, :K], Va[:, :K], Ub[:, :K], Vb[:, :K]
    perm, q, O = match(Ua, Va, Ub, Vb)
    delta = float(np.max(np.abs(np.asarray(sig_b[:K]) - np.asarray(sig_a[:K]))))
    ga, gb = local_gaps(sig_a, K), local_gaps(sig_b, K)
    gap_ok = (ga > gap_mult * delta) & (gb[perm] > gap_mult * delta)
    accepted = gap_ok & (q >= overlap_min)
    # sign fix (display only): flip matched columns of b so the signed overlaps are non-negative
    su = np.sign(np.einsum("ij,ij->j", Ua, Ub[:, perm])); su[su == 0] = 1
    sv = np.sign(np.einsum("ij,ij->j", Va, Vb[:, perm])); sv[sv == 0] = 1
    return dict(perm=perm, quality=q, delta=delta, gap_a=ga, gap_b=gb, gap_ok=gap_ok, accepted=accepted,
                swaps=int((perm != np.arange(K)).sum()), sign_u=su, sign_v=sv)


def crossing_events(sig, U, V, times, flagged, K, event_frac):
    """sig (T, >=K); U, V lists of (d, >=K); flagged (T-1, K) bool per step/level. Returns events list + arrays."""
    T = len(times); ev = []
    S = np.asarray(sig, float)[:, :K]
    for i in range(K - 1):
        g = S[:, i] - S[:, i + 1]
        med = np.median(g)
        for k in range(1, T - 1):
            if g[k] < g[k - 1] and g[k] <= g[k + 1] and g[k] < event_frac * med:
                tt = times[k - 1:k + 2]; yy = g[k - 1:k + 2] ** 2
                A = np.vstack([tt ** 2, tt, np.ones(3)]).T
                a2, a1, a0 = np.linalg.solve(A, yy)
                if a2 > 0:
                    t_min = -a1 / (2 * a2); v = a0 - a1 ** 2 / (4 * a2)
                    g_min = float(np.sqrt(v)) if v > 0 else 0.0
                    if not (tt[0] <= t_min <= tt[2]): t_min, g_min = float(times[k]), float(g[k])
                else:
                    t_min, g_min = float(times[k]), float(g[k])
                cu = abs(float(U[k - 1][:, i] @ U[k + 1][:, i])); cv = abs(float(V[k - 1][:, i] @ V[k + 1][:, i]))
                th_u = float(np.degrees(np.arccos(min(1.0, cu)))); th_v = float(np.degrees(np.arccos(min(1.0, cv))))
                amb = bool(flagged[k - 1, i] | flagged[k - 1, i + 1] | flagged[k, i] | flagged[k, i + 1])
                ev.append(dict(pair=i, k=k, t_min=float(t_min), g_min=float(g_min), g_obs=float(g[k]),
                               theta_u=th_u, theta_v=th_v, ambiguous=amb))
    times_all = np.sort([e["t_min"] for e in ev]); times_ok = np.sort([e["t_min"] for e in ev if not e["ambiguous"]])
    return ev, times_all, times_ok


def analyse(sig, U, V, times, **kw):
    p = dict(PARAMS); p.update(kw)
    K = p["K"]; T = len(times)
    steps = [step(sig[t], U[t], V[t], sig[t + 1], U[t + 1], V[t + 1], K, p["gap_mult"], p["overlap_min"]) for t in range(T - 1)]
    quality = np.array([s["quality"] for s in steps]); accepted = np.array([s["accepted"] for s in steps])
    gap_ok = np.array([s["gap_ok"] for s in steps]); swaps = np.array([s["swaps"] for s in steps])
    delta = np.array([s["delta"] for s in steps]); perms = np.array([s["perm"] for s in steps])
    flagged = ~accepted
    ev, t_all, t_ok = crossing_events(sig, U, V, np.asarray(times, float), flagged, K, p["event_frac"])
    return dict(est=EST, params=p, T=T, K=K, quality=quality, accepted=accepted, gap_ok=gap_ok, swaps=swaps, delta=delta,
                perms=perms, ambiguous_frac=float(flagged.mean()), mean_quality=float(quality.mean()),
                total_swaps=int(swaps.sum()), events=ev, event_times=t_all, event_times_unambiguous=t_ok,
                n_events=len(ev), n_events_ambiguous=int(sum(e["ambiguous"] for e in ev)),
                event_ambiguous_frac=(float(np.mean([e["ambiguous"] for e in ev])) if ev else float("nan")))


def metric_arrays(res):
    """Every array-valued metric, for bit-identity comparisons (C5)."""
    return dict(quality=res["quality"], accepted=res["accepted"], gap_ok=res["gap_ok"], swaps=res["swaps"],
                delta=res["delta"], perms=res["perms"], event_times=res["event_times"],
                events=np.array([(e["pair"], e["k"], e["t_min"], e["g_min"], e["theta_u"], e["theta_v"], e["ambiguous"]) for e in res["events"]], float))


def summary_lines(res):
    return [f"M3 K={res['K']} T={res['T']}: ambiguous(step,level) frac={res['ambiguous_frac']:.3f} mean quality={res['mean_quality']:.3f} "
            f"swaps={res['total_swaps']} events={res['n_events']} (ambiguous {res['n_events_ambiguous']})"]


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("inp"); ap.add_argument("out")
    ap.add_argument("--K", type=int, default=PARAMS["K"]); ap.add_argument("--gap-mult", type=float, default=PARAMS["gap_mult"])
    ap.add_argument("--overlap-min", type=float, default=PARAMS["overlap_min"]); ap.add_argument("--event-frac", type=float, default=PARAMS["event_frac"])
    a = ap.parse_args()
    z = np.load(a.inp)
    res = analyse(z["sig"], list(z["U"]), list(z["V"]), z["times"], K=a.K, gap_mult=a.gap_mult, overlap_min=a.overlap_min, event_frac=a.event_frac)
    out = Path(a.out)
    np.savez_compressed(out.with_suffix(".npz"), **metric_arrays(res))
    json.dump({k: v for k, v in res.items() if not isinstance(v, np.ndarray)}, open(out.with_suffix(".json"), "w"), indent=1, default=float)
    print("\n".join(summary_lines(res)))
