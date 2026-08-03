"""Khinchin Landscape — Phase 0/1 field computation (spec sec 3).

Writes the MASTER artifact: data/quotients_<tag>.npy, a (D, N) float16 memmap of
log2(a_n), NaN past each column's trust horizon, plus a per-column horizon index.
Everything downstream (K, S1, S2) derives from this one array -- no second pass.

    python3 compute.py phase0     # N=4096  D=512  B=2048   (preview)
    python3 compute.py phase1     # N=65536 D=2048 B=8192   (production)
"""
import json
import multiprocessing as mp
import os
import sys
import time

import numpy as np

import kcore as kc

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, 'data')

CONFIGS = {
    'phase0': dict(N=4096,  D=512,  B=2048, chunk=512,  offset=kc.DEFAULT_OFFSET),
    'phase1': dict(N=65536, D=2048, B=8192, chunk=1024, offset=kc.DEFAULT_OFFSET),
}

REASON_CODE = {'depth': 0, 'precision': 1, 'terminated': 2}

_W = {}


def _init(tag, cfg):
    _W['cfg'] = cfg
    _W['tag'] = tag
    _W['xi'], _W['Q'] = kc.grid_numerators(cfg['N'], cfg['B'], cfg['offset'])
    _W['limit'] = kc.horizon_limit(cfg['B'])
    _W['arr'] = np.lib.format.open_memmap(
        os.path.join(DATA, f'quotients_{tag}.npy'), mode='r+')


def _do_chunk(bounds):
    i0, i1 = bounds
    cfg, xi, Q, limit = _W['cfg'], _W['xi'], _W['Q'], _W['limit']
    D, B = cfg['D'], cfg['B']
    block = np.full((D, i1 - i0), np.nan, dtype=np.float16)
    horizons = np.zeros(i1 - i0, dtype=np.uint16)
    reasons = np.zeros(i1 - i0, dtype=np.uint8)
    for j, i in enumerate(range(i0, i1)):
        quots, reason = kc.cf_quotients((i << B) + xi, Q, D, limit)
        if quots:
            block[:len(quots), j] = np.array([kc.ilog2(a) for a in quots],
                                             dtype=np.float32).astype(np.float16)
        horizons[j] = len(quots)
        reasons[j] = REASON_CODE[reason]
    _W['arr'][:, i0:i1] = block
    _W['arr'].flush()
    return i0, i1, horizons, reasons


def run(tag, workers=None):
    cfg = CONFIGS[tag]
    N, D, B = cfg['N'], cfg['D'], cfg['B']
    os.makedirs(DATA, exist_ok=True)
    master = os.path.join(DATA, f'quotients_{tag}.npy')
    ckpt_path = os.path.join(DATA, f'checkpoint_{tag}.json')

    if not os.path.exists(master):
        arr = np.lib.format.open_memmap(master, mode='w+', dtype=np.float16, shape=(D, N))
        arr[:] = np.nan
        arr.flush()
        del arr
    ckpt = {'done': [], 'horizons': {}, 'reasons': {}}
    if os.path.exists(ckpt_path):
        ckpt = json.load(open(ckpt_path))

    chunks = [(i, min(i + cfg['chunk'], N)) for i in range(0, N, cfg['chunk'])]
    todo = [c for c in chunks if f'{c[0]}' not in ckpt['horizons']]
    workers = workers or max(1, min(22, os.cpu_count() - 2))
    print(f'[{tag}] N={N} D={D} B={B}  {len(todo)}/{len(chunks)} chunks to do, {workers} workers')

    t0 = time.time()
    if todo:
        with mp.Pool(workers, initializer=_init, initargs=(tag, cfg)) as pool:
            for k, (i0, i1, hor, rea) in enumerate(pool.imap_unordered(_do_chunk, todo), 1):
                ckpt['horizons'][str(i0)] = hor.tolist()
                ckpt['reasons'][str(i0)] = rea.tolist()
                if k % 8 == 0 or k == len(todo):
                    json.dump(ckpt, open(ckpt_path, 'w'))
                    el = time.time() - t0
                    print(f'  {k}/{len(todo)} chunks  {el:.0f}s  eta {el/k*(len(todo)-k):.0f}s', flush=True)
        json.dump(ckpt, open(ckpt_path, 'w'))

    horizon = np.zeros(N, dtype=np.uint16)
    reason = np.zeros(N, dtype=np.uint8)
    for i0, hor in ckpt['horizons'].items():
        horizon[int(i0):int(i0) + len(hor)] = hor
    for i0, rea in ckpt['reasons'].items():
        reason[int(i0):int(i0) + len(rea)] = rea
    np.save(os.path.join(DATA, f'horizon_{tag}.npy'), horizon)
    np.save(os.path.join(DATA, f'reason_{tag}.npy'), reason)

    # anchors: closed-form (float32 -- Liouville log2 a overflows float16 by design)
    anch = {}
    for key in kc.ANCHORS:
        seq = kc.anchor_sequence(key, D)
        col = np.full(D, np.nan, dtype=np.float32)
        col[:len(seq)] = [kc.ilog2(a) for a in seq]
        anch[key] = col
        P, Q = kc.anchor_rational(key, B)
        eq, er = kc.cf_quotients(P, Q, D, kc.horizon_limit(B))
        anch[key + '__engine_depth'] = np.array([len(eq)])
        anch[key + '__engine_match'] = np.array([int(eq == seq[:len(eq)])])
        anch[key + '__pred_horizon'] = np.array([kc.predicted_horizon(seq, B)])
    np.savez(os.path.join(DATA, f'anchors_{tag}.npz'), **anch)

    json.dump(dict(cfg, tag=tag, guard_bits=kc.GUARD_BITS,
                   horizon_rule='q_n^2 <= 2^(B-guard)',
                   note='grid offset is pi-3, not the spec 1/phi; see grid_audit.py'),
              open(os.path.join(DATA, f'meta_{tag}.json'), 'w'), indent=2)

    dt = time.time() - t0
    print(f'[{tag}] done in {dt:.1f}s -> {master}')
    print(f'  horizon: min={horizon.min()} med={int(np.median(horizon))} max={horizon.max()}')
    print(f'  stopped by: depth={(reason==0).sum()} precision={(reason==1).sum()} terminated={(reason==2).sum()}')
    return master


if __name__ == '__main__':
    run(sys.argv[1] if len(sys.argv) > 1 else 'phase0')
