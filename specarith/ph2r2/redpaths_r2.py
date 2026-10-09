"""R₂ pre-read: red-path reachability (PH2R2_SEAL 1.0 §4), pre-data, for the primary test function chosen in G0b.
Reachable ⇔ the red path moves μ̂ (under the theory's truth μ = 1) by more than 1.96·SD(μ̂) of the bin; required to fail
only where that power is ≥ 0.80 (as PH2 A8).

  RP-density   prediction with the misprinted density log(E/2πe) (L_t → L_t − 1 in RMT and in the arithmetic terms'
               (t/2π)^{−ir} factor): μ̂_wrong = (S_true − RMT_wrong)/LOT_wrong with S_true = RMT + LOT (theory, μ = 1)
  RP-sign      the LOT term with its sign flipped: μ̂ → −μ̂, i.e. reads −1 under μ = 1
  RP-shuffle   i.i.d. resampled spacings (sequence rebuilt) on CUE surrogates: change of S_f per level, scaled to the bin,
               in units of SD(S_f) — a specificity witness that S_f reads pair correlations beyond the nearest neighbour
               (for small-separation test functions it may legitimately be weak; reported as computed)

  python redpaths_r2.py G0B_DIR OUT
"""
import json
import math
import os
import sys

import numpy as np

import g0b as G
import r2prep as P


def wrong_density_parts(K, wr, edges, u, w, delta):
    """RMT_f, LOT_f with L_t → L_t − 1 (density log(t/2πe)/2π) in every L-dependent term."""
    f = P.f_raw(K.r, u, w, delta)
    fw = f * wr
    xt, wt = np.polynomial.legendre.leggauss(6)
    rmt = lot = 0.0

    def parts(t):
        L = math.log(t / (2 * math.pi)) - 1
        r = K.r
        Rm = (L * L - 2 / r ** 2 + 2 * np.cos(r * L) / r ** 2) / (4 * math.pi ** 2)
        g = K.d1 + np.exp(-1j * r * L) * K.zz * K.A - K.B
        Rt = (L * L + 2 * np.real(g)) / (4 * math.pi ** 2)
        return Rm, Rt - Rm

    for a, b in zip(edges[:-1], edges[1:]):
        tt = 0.5 * (b - a) * (xt + 1) + a
        ww = 0.5 * (b - a) * wt
        for t_, w_ in zip(tt, ww):
            Rm, Lo = parts(t_)
            rmt += 2 * w_ * np.sum(Rm * fw)
            lot += 2 * w_ * np.sum(Lo * fw)
        for te in (a, b):
            Rm, Lo = parts(te)
            rmt -= np.sum(Rm * fw * K.r)
            lot -= np.sum(Lo * fw * K.r)
    return rmt, lot


def shuffle_shift(name, u, w, nblocks=400, seed=7):
    """Per-level change of S_f when the spacings of CUE_250 surrogate blocks are i.i.d. resampled (within each block)."""
    g = P.geometry(name)
    rng = np.random.default_rng(seed)
    d_orig, d_shuf = [], []
    x0 = float(P.nbar(g["t0"]))
    for b in range(nblocks):
        xb = x0 + b * G.BLOCK
        x = G.cue_block(rng)
        s = np.diff(x)
        xs = x[0] + np.concatenate([[0.0], np.cumsum(rng.choice(s, len(s), replace=True))])
        t = G.nbar_inv(xb + x, g["tc"])
        ts = G.nbar_inv(xb + xs, g["tc"])
        d_orig.append(G.contributions(t, u, w, g["delta"]).sum())
        d_shuf.append(G.contributions(ts, u, w, g["delta"]).sum())
    d = np.array(d_shuf) - np.array(d_orig)
    n_levels = nblocks * G.BLOCK
    return float(d.sum() / n_levels), float(d.std(ddof=1) * math.sqrt(nblocks) / n_levels)


def main(g0b_dir, out):
    S = json.load(open(os.path.join(g0b_dir, "g0b_summary.json")))
    key = S["primary_choice"]["primary"]
    u, w = (float(x) for x in key.split("_"))
    res = dict(primary=key)
    for name in P.BINS:
        g = P.geometry(name)
        K = G.CachedKernel(G.kernel_path(g0b_dir, name))
        wr = np.load(G.kernel_path(g0b_dir, name))["wr"]
        edges = [g["t0"], g["t1"]]
        rmt, lot = G.predict_tiling(K, wr, edges, u, w, g["delta"])
        sd = S[name][key]["sd_mu"]
        sd_used = max(sd, max(S[name][key]["boot_sd_over_sd"].values()) * sd)
        rmt_w, lot_w = wrong_density_parts(K, wr, edges, u, w, g["delta"])
        mu_w = ((rmt + lot) - rmt_w) / lot_w
        per_level, per_level_se = shuffle_shift(name, u, w)
        dS = per_level * g["n_zeros"]
        Phi = lambda z: 0.5 * math.erfc(-z / math.sqrt(2))
        rec = dict(sd_mu=sd, sd_used=sd_used,
                   rp_density=dict(mu_read=mu_w, shift=mu_w - 1, power=Phi(abs(mu_w - 1) / sd_used - 1.959964)),
                   rp_sign=dict(mu_read=-1.0, shift=-2.0, power=Phi(2 / sd_used - 1.959964)),
                   rp_shuffle=dict(dS_per_level=per_level, dS_bin=dS, dmu_bin=dS / lot,
                                   power=Phi(abs(dS / lot) / sd_used - 1.959964)))
        for k in ("rp_density", "rp_sign", "rp_shuffle"):
            rec[k]["required"] = bool(rec[k]["power"] >= 0.80)
        res[name] = rec
        print(name, json.dumps({k: (round(v["power"], 3) if isinstance(v, dict) else v) for k, v in rec.items()}),
              flush=True)
    os.makedirs(out, exist_ok=True)
    json.dump(res, open(os.path.join(out, "redpaths.json"), "w"), indent=1)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
