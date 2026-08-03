"""Khinchin Landscape — falsification gates (spec sec 4).

    python3 gates.py phase0     # G0a-G0e (+G0f engine-vs-closed-form)
    python3 gates.py phase1     # the above plus G1, G2
Writes validation/gates_<tag>.json and prints a verdict table.
"""
import json
import math
import os
import sys

import numpy as np
from scipy import stats

import kcore as kc
from compute import CONFIGS, DATA, HERE

ANCHOR_DEPTH = 2048   # closed-form anchors cost nothing; evaluate them at full depth
                      # regardless of the phase's field depth D.


def gauss_kuzmin(k):
    """P(a = k) under the invariant Gauss measure -- the n->inf law."""
    return math.log2(1.0 + 1.0 / (k * (k + 2.0)))


def lebesgue_a1(k):
    """P(a_1 = k) for alpha uniform on (0,1) -- EXACT, and not the same law.

    The sample grid is Lebesgue-uniform, so a_1 obeys 1/(k(k+1)), not Gauss-Kuzmin.
    The two agree only asymptotically in n (Kuzmin/Wirsing, rate ~0.303^n).
    """
    return 1.0 / (k * (k + 1.0))


def chisq_vs_law(sample, law, kmax=15):
    """Binned chi-square of integer sample against P(a=k), bins 1..kmax plus tail."""
    n = len(sample)
    obs = np.array([np.sum(sample == k) for k in range(1, kmax + 1)] +
                   [np.sum(sample > kmax)], dtype=float)
    p = np.array([law(k) for k in range(1, kmax + 1)])
    p = np.append(p, 1.0 - p.sum())
    exp = p * n
    chi2 = float(np.sum((obs - exp) ** 2 / exp))
    dof = len(obs) - 1
    return chi2, dof, float(stats.chi2.sf(chi2, dof))


# --- G0: anchors --------------------------------------------------------------
def gate_G0(B):
    res = {}
    seq = {k: kc.anchor_sequence(k, ANCHOR_DEPTH) for k in kc.ANCHORS}

    K_phi = kc.running_K(seq['phi'])
    res['G0a'] = dict(
        claim='1/phi: K_n == 1 exactly, all n',
        max_abs_dev=float(max(abs(k - 1.0) for k in K_phi)), depth=len(K_phi))
    res['G0a']['pass'] = res['G0a']['max_abs_dev'] == 0.0

    K_s2 = kc.running_K(seq['sqrt2m1'])
    res['G0b'] = dict(
        claim='sqrt2-1: K_n == 2 exactly, all n',
        max_abs_dev=float(max(abs(k - 2.0) for k in K_s2)), depth=len(K_s2))
    res['G0b']['pass'] = res['G0b']['max_abs_dev'] == 0.0

    K_s3 = kc.running_K(seq['sqrt3m1'])
    dev2000 = abs(K_s3[1999] - math.sqrt(2))
    res['G0c'] = dict(
        claim='sqrt3-1: |K_2000 - sqrt2| < 1e-3', K_2000=K_s3[1999],
        target=math.sqrt(2), dev=float(dev2000), tol=1e-3, pass_=None)
    res['G0c']['pass'] = dev2000 < 1e-3

    # e-2: K_{3m} = (2^m m!)^{1/(3m)} in closed form
    K_e = kc.running_K(seq['e_m2'])
    m = 500
    n = 3 * m
    closed = math.exp((m * math.log(2) + math.lgamma(m + 1)) / n)
    rel = abs(K_e[n - 1] - closed) / closed
    res['G0d'] = dict(claim='e-2: K_1500 matches (2^m m!)^{1/3m} at m=500 within 0.5%',
                      K_1500=K_e[n - 1], closed_form=closed, rel_err=float(rel), tol=5e-3)
    res['G0d']['pass'] = rel < 5e-3

    # Liouville-type: precision death, and the depth must match the predicted budget
    lseq = seq['liouville']
    pred = kc.predicted_horizon(lseq, B)
    P, Q = kc.anchor_rational('liouville', B)
    eq, er = kc.cf_quotients(P, Q, ANCHOR_DEPTH, kc.horizon_limit(B))
    res['G0e'] = dict(claim='Liouville-type masks early at the predicted depth',
                      engine_depth=len(eq), predicted_horizon=pred, reason=er,
                      quotients_agree=bool(eq == lseq[:len(eq)]))
    res['G0e']['pass'] = (len(eq) == pred and er == 'precision'
                          and res['G0e']['quotients_agree'])

    # G0f (added): the Euclid engine reproduces every closed form up to its horizon.
    # Without this, G0a-G0d test only the closed forms and never touch the engine.
    g0f = {}
    ok = True
    for key in kc.ANCHORS:
        P, Q = kc.anchor_rational(key, B)
        eq, er = kc.cf_quotients(P, Q, ANCHOR_DEPTH, kc.horizon_limit(B))
        pred = kc.predicted_horizon(seq[key], B)
        match = (eq == seq[key][:len(eq)])
        g0f[key] = dict(engine_depth=len(eq), predicted=pred, reason=er, match=bool(match))
        ok &= bool(match) and (len(eq) == pred or er == 'depth')
    res['G0f'] = dict(claim='engine reproduces all closed forms up to the trust horizon',
                      per_anchor=g0f, pass_=None)
    res['G0f']['pass'] = ok
    return res


# --- G1/G2: field-level -------------------------------------------------------
def gate_G1_G2(tag, cfg):
    arr = np.load(os.path.join(DATA, f'quotients_{tag}.npy'), mmap_mode='r')
    horizon = np.load(os.path.join(DATA, f'horizon_{tag}.npy'))
    D, N = arr.shape
    res = {}

    # Sobol subsample of columns (>= 10,000 per spec)
    n_sob = 1 << 14
    eng = stats.qmc.Sobol(d=1, scramble=True, seed=20260803)
    idx = np.unique((eng.random(n_sob).ravel() * N).astype(int))
    idx = idx[idx < N]
    sub = np.asarray(arr[:, idx], dtype=np.float32)

    deepest = int(horizon[idx].min())
    log2K = np.cumsum(np.nan_to_num(sub, nan=0.0), axis=0) / np.arange(1, D + 1)[:, None]
    med = float(2.0 ** np.median(log2K[deepest - 1]))
    res['G1a'] = dict(claim='median K at deepest common unmasked depth within 2% of K0',
                      depth=deepest, median_K=med, K0=kc.KHINCHIN_K0,
                      rel_err=abs(med - kc.KHINCHIN_K0) / kc.KHINCHIN_K0,
                      n_columns=int(len(idx)))
    res['G1a']['pass'] = res['G1a']['rel_err'] < 0.02

    a1 = np.rint(2.0 ** sub[0]).astype(np.int64)
    c_leb, d_leb, p_leb = chisq_vs_law(a1, lebesgue_a1)
    c_gk1, d_gk1, p_gk1 = chisq_vs_law(a1, gauss_kuzmin)
    res['G1b'] = dict(
        claim='a_1 across columns matches its EXACT law for a Lebesgue-uniform grid, 1/(k(k+1))',
        chi2=c_leb, dof=d_leb, p=p_leb, n=int(len(a1)),
        note=('spec sec 4 G1 asks for a_1 vs Gauss-Kuzmin; that is the wrong law for a '
              'uniform grid. Gauss-Kuzmin p for the same a_1 sample = %.3g' % p_gk1),
        p_if_tested_against_gauss_kuzmin=p_gk1)
    res['G1b']['pass'] = p_leb > 0.01

    # the intended asymptotic check, at a depth where the transfer operator has converged
    n_deep = 64
    a_deep = np.rint(2.0 ** sub[n_deep - 1]).astype(np.int64)
    c_gk, d_gk, p_gk = chisq_vs_law(a_deep, gauss_kuzmin)
    res['G1c'] = dict(claim=f'a_{n_deep} across columns matches Gauss-Kuzmin log2(1+1/(k(k+2)))',
                      chi2=c_gk, dof=d_gk, p=p_gk, n=int(len(a_deep)), depth=n_deep)
    res['G1c']['pass'] = p_gk > 0.01

    # G2: honesty -- nothing rendered past a column's horizon
    finite = np.isfinite(np.asarray(arr[:, idx], dtype=np.float32))
    beyond = int(sum(int(finite[horizon[i]:, j].sum()) for j, i in enumerate(idx)))
    masked_by_row = 1.0 - (horizon[None, :] > np.arange(D)[:, None]).mean(axis=1)
    res['G2'] = dict(claim='zero finite values past any column horizon',
                     finite_values_past_horizon=beyond,
                     masked_fraction_overall=float(masked_by_row.mean()),
                     masked_fraction_final_row=float(masked_by_row[-1]),
                     horizon_min=int(horizon.min()), horizon_median=int(np.median(horizon)),
                     horizon_max=int(horizon.max()))
    res['G2']['pass'] = beyond == 0
    np.save(os.path.join(HERE, 'validation', f'masked_by_row_{tag}.npy'), masked_by_row)
    return res


def main(tag):
    cfg = CONFIGS[tag]
    res = {'tag': tag, 'config': cfg}
    res.update(gate_G0(cfg['B']))
    if os.path.exists(os.path.join(DATA, f'quotients_{tag}.npy')):
        res.update(gate_G1_G2(tag, cfg))
    os.makedirs(os.path.join(HERE, 'validation'), exist_ok=True)
    json.dump(res, open(os.path.join(HERE, 'validation', f'gates_{tag}.json'), 'w'),
              indent=2, default=str)
    print(f'\n=== GATES [{tag}]  N={cfg["N"]} D={cfg["D"]} B={cfg["B"]} ===')
    for k in sorted(x for x in res if x.startswith('G')):
        v = res[k]
        print(f'  {k}  {"PASS" if v["pass"] else "FAIL"}  {v["claim"]}')
        for f, val in v.items():
            if f in ('claim', 'pass', 'pass_', 'per_anchor'):
                continue
            print(f'        {f} = {val}')
        if 'per_anchor' in v:
            for a, d in v['per_anchor'].items():
                print(f'        {a:11s} {d}')
    return res


if __name__ == '__main__':
    main(sys.argv[1] if len(sys.argv) > 1 else 'phase0')
