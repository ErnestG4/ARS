"""Khinchin Landscape — Phase 1b sibling fields (spec sec 5b).

Derives, from the master quotient array alone (no recompute):
  log2K   log2 K_n(alpha)                      -- the landscape itself
  S1      running-min shadow of K from n0      -- DOWNWARD-BIASED liminf estimate
  S2      rho_n = #{k<=n : a_k >= 2}/n         -- the banked W ~ 4/lambda^{#{a>=2}} rate
and evaluates gate G3.

    python3 derive.py phase1
"""
import json
import math
import os
import sys

import numpy as np

import kcore as kc
from compute import CONFIGS, DATA, HERE

N0_LIST = (16, 64)      # burn-ins for the running-min shadow; render uses 64
COLBLK = 4096


def _open(name, D, N):
    return np.lib.format.open_memmap(os.path.join(DATA, 'derived', name),
                                     mode='w+', dtype=np.float16, shape=(D, N))


def derive(tag):
    cfg = CONFIGS[tag]
    arr = np.load(os.path.join(DATA, f'quotients_{tag}.npy'), mmap_mode='r')
    D, N = arr.shape
    os.makedirs(os.path.join(DATA, 'derived'), exist_ok=True)
    outK = _open(f'log2K_{tag}.npy', D, N)
    outS2 = _open(f'S2_rate_{tag}.npy', D, N)
    outS1 = {n0: _open(f'S1_shadow_n{n0}_{tag}.npy', D, N) for n0 in N0_LIST}
    depths = np.arange(1, D + 1, dtype=np.float32)[:, None]

    med_rate, med_K, med_S1 = [], [], {n0: [] for n0 in N0_LIST}
    for c0 in range(0, N, COLBLK):
        c1 = min(c0 + COLBLK, N)
        blk = np.asarray(arr[:, c0:c1], dtype=np.float32)
        valid = np.isfinite(blk)
        filled = np.where(valid, blk, 0.0)

        log2K = np.cumsum(filled, axis=0) / depths
        # a_k >= 2  <=>  log2 a_k >= 1, and log2 1 = 0, log2 2 = 1 are exact in f16
        rate = np.cumsum((filled >= 1.0) & valid, axis=0, dtype=np.float32) / depths
        log2K[~valid] = np.nan
        rate[~valid] = np.nan
        outK[:, c0:c1] = log2K.astype(np.float16)
        outS2[:, c0:c1] = rate.astype(np.float16)
        for n0 in N0_LIST:
            sh = np.full_like(log2K, np.nan)
            sh[n0 - 1:] = np.fmin.accumulate(log2K[n0 - 1:], axis=0)
            outS1[n0][:, c0:c1] = sh.astype(np.float16)
            med_S1[n0].append(sh[-1])
        med_rate.append(rate[-1])
        med_K.append(log2K[-1])
    for m in (outK, outS2, *outS1.values()):
        m.flush()

    med_rate = np.concatenate(med_rate)
    med_K = np.concatenate(med_K)
    res = {'tag': tag, 'depth': D, 'n_columns': N}

    # --- G3 -------------------------------------------------------------------
    anch = np.load(os.path.join(DATA, f'anchors_{tag}.npz'))
    def anchor_rate(key):
        col = anch[key]
        v = np.isfinite(col)
        return float(np.cumsum((col >= 1.0) & v)[v.sum() - 1] / v.sum())
    phi_rate, s2_rate = anchor_rate('phi'), anchor_rate('sqrt2m1')
    gen_med = float(np.nanmedian(med_rate))
    res['G3'] = dict(
        claim='a>=2 rate field: phi==0, sqrt2-1==1, generic median within 1% of 1-log2(4/3)',
        phi_rate=phi_rate, sqrt2m1_rate=s2_rate, generic_median_rate=gen_med,
        gauss_kuzmin_rate=kc.GK_RATE_A_GE_2,
        rel_err=abs(gen_med - kc.GK_RATE_A_GE_2) / kc.GK_RATE_A_GE_2)
    res['G3']['pass'] = (phi_rate == 0.0 and s2_rate == 1.0
                         and res['G3']['rel_err'] < 0.01)

    # --- S1 burn-in sensitivity (mandatory honesty report, spec sec 5b) --------
    res['S1_sensitivity'] = {
        str(n0): dict(median_shadow_K=float(2 ** np.nanmedian(np.concatenate(med_S1[n0]))),
                      mean_shadow_K=float(2 ** np.nanmean(np.concatenate(med_S1[n0]))))
        for n0 in N0_LIST}
    res['S1_caption'] = 'running-min shadow of K (n0 = 64)'
    res['S1_bias_note'] = ('DOWNWARD-BIASED estimate of liminf K: the running min from n0 '
                           'converges to the tail-inf, which is <= liminf, and transient '
                           'dips between n0 and the asymptotic regime bias it low. '
                           'Never caption this "liminf K".')
    res['median_K_final'] = float(2 ** np.nanmedian(med_K))

    # disagreement set for R6: K near K0 but the shadow sits low
    K_fin, S1_fin = med_K, np.concatenate(med_S1[64])
    near = np.abs(2 ** K_fin - kc.KHINCHIN_K0) / kc.KHINCHIN_K0 < 0.05
    lowsh = (2 ** S1_fin) < 0.75 * kc.KHINCHIN_K0
    res['disagreement_fraction'] = float((near & lowsh).mean())
    np.save(os.path.join(DATA, 'derived', f'disagree_{tag}.npy'), (near & lowsh))

    json.dump(res, open(os.path.join(HERE, 'validation', f'derived_{tag}.json'), 'w'),
              indent=2, default=str)
    print(json.dumps(res, indent=2, default=str))
    return res


if __name__ == '__main__':
    derive(sys.argv[1] if len(sys.argv) > 1 else 'phase1')
