"""
r077_blockboot_mechanism.py — WHY is the n_eff/n diagnostic biased on real data but not synthetic?

THE GAP TO EXPLAIN (R-170). A jointly-permuted control on the REAL (G,Y,L) triples -- serial order
destroyed, so truth = 1.000 by construction -- returns 0.51..1.16 depending on stratum. Fully
synthetic i.i.d. data with MATCHED n_conv, event rate, block length and success probability returns
0.92..1.18. Same resampler, same shapes, different answer. Three candidate mechanisms were already
eliminated (block length, event-conditioning, small success counts), so the cause is something in
the real data's structure that SURVIVES a joint permutation.

Only three things survive a joint permutation of triples:
  (a) the MARGINAL of each of G, Y, L,
  (b) the JOINT dependence among G, Y, L within a single index,
  (c) the array LENGTH.
Serial correlation, orbit ordering and block structure are all destroyed. So the mechanism must be
one of those three, and this file measures which by rebuilding the synthetic case one property at a
time until it reproduces the real-shuffled value.

LADDER, each rung adding ONE property of the real data:
  L0  i.i.d. binary G, i.i.d. Bernoulli event marker            (the ARM-3 synthetic)
  L1  + the real EVENT-RATE and success probability, exactly
  L2  + the real L MARGINAL (resample real L values i.i.d.)     -> tests (a) via the event process
  L3  + the real (G,L) JOINT (resample real index-pairs i.i.d.) -> tests (b)
  L4  the real jointly-permuted array itself                    (the ARM-1 control)
The rung at which the value drops to the real-shuffled number IS the mechanism.

Run:  $HOME/fmexplorer/bin/python3 arsrh/cubic/r077_blockboot_mechanism.py
Writes: arsrh/cubic/r077_blockboot_mechanism_measured.json
"""
from __future__ import annotations

import json
import math
import os
import sys

import numpy as np

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(os.path.dirname(_HERE))
for _p in (_HERE, _ROOT):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import mpmath as mp                                                      # noqa: E402
from gate0e_precision import collect_cyclic, gl2z_orbit_reps, cf_of_mpf  # noqa: E402
from r077_control import orbit, A_EV                                     # noqa: E402

SEED = 20260730
N_BOOT = 600
N_REP = 25
B = 50
p_ = lambda *a: print(*a, flush=True)


def stratum_arrays(t):
    reps = gl2z_orbit_reps(collect_cyclic(box=14, per=8)[t])
    G, Y, L = [], [], []
    for (A, Bc, C, M) in reps:
        r = sorted(mp.re(x) for x in mp.polyroots([1, A, Bc, C], maxsteps=600, extraprec=1200))
        g_, y_, l_, _ = orbit(cf_of_mpf(r[0]), M)
        G.append(g_); Y.append(y_); L.append(l_)
    return np.concatenate(G), np.concatenate(Y), np.concatenate(L)


def neff(G, Y, L, g, rng, n_boot=N_BOOT, block=B, report=False):
    """r077d.py's shape, with every intermediate exposed."""
    w = 1.0 + Y
    ev = L >= A_EV
    n = int(ev.sum())
    pred = float((w * (G == g)).sum() / w.sum())
    se_iid = math.sqrt(max(pred * (1 - pred), 1e-12) / n)
    nb = len(G) // block
    boot, nev = [], []
    for _ in range(n_boot):
        st = rng.integers(0, len(G) - block, size=nb)
        idx = (st[:, None] + np.arange(block)[None, :]).ravel()
        e2 = L[idx] >= A_EV
        if e2.sum() > 10:
            boot.append(float((G[idx][e2] == g).mean()))
            nev.append(int(e2.sum()))
    se_blk = float(np.std(boot, ddof=1))
    out = {"n_events": n, "pred": pred, "se_iid": se_iid, "se_blk": se_blk,
           "boot_mean": float(np.mean(boot)), "neff_over_n": (se_iid / se_blk) ** 2,
           "replicate_n_events_mean": float(np.mean(nev)),
           "replicate_n_events_sd": float(np.std(nev, ddof=1))}
    if report:
        return out
    return out["neff_over_n"]


def main():
    rng = np.random.default_rng(SEED)
    p_("=" * 92)
    p_("R-077 — the MECHANISM of the n_eff/n bias. Truth is 1.000 on EVERY row below.")
    p_("=" * 92)

    res = {}
    for t in (13, 5, 29):
        G, Y, L = stratum_arrays(t)
        n_conv = len(G)
        ev = L >= A_EV
        ev_rate = float(ev.mean())
        p_g = float((G == t).mean())
        pairs = np.stack([(G == t).astype(float), (L >= A_EV).astype(float)], axis=1)

        rows = {}
        # L0 / L1 -- iid G, iid event marker, matched rate and p
        v = []
        for _ in range(N_REP):
            Gs = np.where(rng.random(n_conv) < p_g, float(t), 1.0)
            Ls = np.where(rng.random(n_conv) < ev_rate, 99.0, 0.0)
            v.append(neff(Gs, np.zeros(n_conv), Ls, t, rng))
        rows["L1_iid_matched"] = float(np.median(v))

        # L2 -- real L MARGINAL, resampled iid (keeps the lambda distribution, kills the joint)
        v = []
        for _ in range(N_REP):
            Gs = np.where(rng.random(n_conv) < p_g, float(t), 1.0)
            Ls = rng.choice(L, size=n_conv, replace=True)
            v.append(neff(Gs, np.zeros(n_conv), Ls, t, rng))
        rows["L2_real_L_marginal"] = float(np.median(v))

        # L3 -- real (G,L) JOINT, resampled iid by index (keeps within-index dependence)
        v = []
        for _ in range(N_REP):
            k = rng.integers(0, n_conv, size=n_conv)
            v.append(neff(G[k], Y[k], L[k], t, rng))
        rows["L3_real_joint_iid"] = float(np.median(v))

        # L4 -- the real array, jointly PERMUTED (the ARM-1 control)
        v, det = [], None
        for i in range(N_REP):
            perm = rng.permutation(n_conv)
            r = neff(G[perm], Y[perm], L[perm], t, rng, report=(i == 0))
            if i == 0:
                det = r
                v.append(r["neff_over_n"])
            else:
                v.append(r)
        rows["L4_real_permuted"] = float(np.median(v))

        res[str(t)] = {"n_conv": n_conv, "event_rate": ev_rate, "p_g": p_g,
                       "ladder": rows, "L4_detail": det}
        p_(f"\n|t|={t}   n_conv={n_conv}  event_rate={ev_rate:.4f}  P(g={t})={p_g:.4f}")
        for k, val in rows.items():
            p_(f"    {k:<24s} n_eff/n = {val:.3f}")
        p_(f"    [L4 intermediates] se_iid={det['se_iid']:.5f}  se_blk={det['se_blk']:.5f}  "
           f"boot_mean={det['boot_mean']:.4f}  pred={det['pred']:.4f}")
        p_(f"    [L4 replicate events] mean={det['replicate_n_events_mean']:.1f} "
           f"sd={det['replicate_n_events_sd']:.1f}   (original n_events={det['n_events']})")

    p_("\n" + "=" * 92)
    p_("READING: the rung where the value DROPS to L4 is the mechanism.")
    p_("  L1->L2 drop  => the real LAMBDA MARGINAL (the event process is not Bernoulli-like)")
    p_("  L2->L3 drop  => the within-index (G,L) JOINT dependence")
    p_("  L3->L4 flat  => confirms nothing beyond the joint marginal is involved")
    p_("=" * 92)

    dest = os.path.join(_HERE, "r077_blockboot_mechanism_measured.json")
    with open(dest, "w") as f:
        json.dump(res, f, indent=2)
    p_(f"-> wrote {dest}")


if __name__ == "__main__":
    main()
