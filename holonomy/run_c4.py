"""C4 measurement: window -> project vs project -> window (holonomy seal
addendum ADD-6).  COMMITTED GENERATOR of holonomy/c4_measured.json.

Structure mirrors the established pairs: KAG first (non-vacuous null + a red
demo whose non-inertness is proven below), then the dialed law leg against
the committed continuum prediction (predict_c4.py, run and banked BEFORE
this file was written), then the statistic leg with a correctness arm, then
a fixed-substrate point check on the survey KAG randoms, then a
margin-denominated materiality pass — discharged HERE, in the shared
resolver path, per the fail-closed rule (TOOLKIT §9, 2026-08-16).

Tripwire 7 inherited: nothing under survey/ is written; frozen surfaces
only; null_half is never manipulated.

RED-DEMO NON-INERTNESS — first argument WRONG, corrected in-window:
  v1 (as written before running): under MISMATCHED ordering the data occupy
  A_sky while expectations come from A_plane, so cells in A_sky \\ A_plane
  carry data with ~zero expectation and F inflates.  The KAG FIRED RED on
  this and halted the run: the argument named the mechanism but missed one
  of the estimator's own suppressors — cells_F's CELL_FLOOR mask
  (E_c >= 0.2*median) drops exactly the near-zero-expectation cells the
  mechanism creates.  The §9 non-inertness rule worked as designed even
  though the analytic argument was incomplete; recorded rather than quietly
  patched.
  v2 (measured, and the criterion this file uses): the surviving effect is
  carried by the cells that are only PARTIALLY covered, and it scales with
  the symmetric-difference fraction itself — measured dF_mismatch ~ -q
  (t=10: q=0.006, dF=-0.006; t=30: q=0.052, dF=-0.051).  So the red demo
  runs at the TOP of the dial (t=30) where the predicted effect is ~50x the
  seed scatter, and its criterion is statistical detection against that
  scatter, not an arbitrary fixed fraction.

OBSERVABLES, stated explicitly (the first design conflated them):
  * commutator observable  q  = fraction of points whose tile membership
    differs between orderings — the DIRECT, unsuppressed quantity, with the
    committed continuum law in c4_prediction.json;
  * downstream consequence dF(L) under MATCHED ordering — the quantity a
    banked survey row would actually feel.
  There is NO ground truth for the ordering question: both regions are
  legitimate windows and a stationary process is unbiased on either, so C4
  has no correctness leg by construction (per-ordering F-vs-1 numbers are
  reported as diagnostics, never ruled on).  The ruling content is
  therefore MATCHED, not a sequence order — the same shape as OP1.
"""

import hashlib
import json
import sys

import numpy as np

ROOT = "/home/combust/fmexplorer/criticality_tool"
for p in (f"{ROOT}/holonomy", f"{ROOT}/survey"):
    if p not in sys.path:
        sys.path.insert(0, p)

SEAL = json.load(open(f"{ROOT}/holonomy/prereg_sealed.json"))
for f, sha in SEAL["code_freeze_blob_shas"].items():
    d = open(f"{ROOT}/holonomy/{f}", "rb").read()
    assert hashlib.sha1(b"blob %d\0" % len(d) + d).hexdigest() == sha, \
        f"FREEZE VIOLATION {f}"

from tiling import gnomonic                                    # noqa: E402
from estimators import cells_F                                 # noqa: E402
from lattice_h import resolve_pair                             # noqa: E402

PRED = json.load(open(f"{ROOT}/holonomy/c4_prediction.json"))
K = SEAL["k_arc"]
TILES = PRED["tiles"]
SEEDS = 16
N_PTS = 60_000
L_FRAC = [0.02, 0.05]          # cell side as a fraction of tile size
OUT = dict(seal_cited="holonomy/prereg_sealed.json (ADD-6)",
           prediction_cited="holonomy/c4_prediction.json")


def uniform_patch(n, tile, rng, dec0=0.0):
    """Uniform-on-sphere points covering generously beyond both boxes."""
    dra = tile / np.cos(np.radians(dec0))
    ra = rng.uniform(-0.9 * dra, 0.9 * dra, n)
    s0, s1 = (np.sin(np.radians(dec0 - 0.9 * tile)),
              np.sin(np.radians(dec0 + 0.9 * tile)))
    dec = np.degrees(np.arcsin(rng.uniform(s0, s1, n)))
    return ra, dec


def order_A(ra, dec, tile, dec0=0.0):
    """window -> project (deployed tile_points semantics)."""
    dra = tile / np.cos(np.radians(dec0))
    m = (np.abs(ra) <= dra / 2.0) & (np.abs(dec - dec0) <= tile / 2.0)
    x, y = gnomonic(ra[m], dec[m], 0.0, dec0)
    return np.column_stack([x, y])


def order_B(ra, dec, tile, dec0=0.0):
    """project -> window (cut the same nominal box in plane coords)."""
    x, y = gnomonic(ra, dec, 0.0, dec0)
    m = (np.abs(x) <= tile / 2.0) & (np.abs(y) <= tile / 2.0)
    return np.column_stack([x[m], y[m]])


def F_of(xy_d, xy_r, L, ext):
    out = cells_F(xy_d, np.ones(len(xy_d)), xy_r, np.ones(len(xy_r)), L, ext)
    return None if out is None else out["F"]


def extent_of(xy, tile):
    h = tile / 2.0
    return (-h, h, -h, h)


# ── KAG ─────────────────────────────────────────────────────────────────────
print("C4 KAG", flush=True)
T_RED = 30.0                       # dial top: predicted effect ~50x scatter
L = 0.05 * T_RED
d_match, d_mis = [], []
for s in range(8):
    ra, dec = uniform_patch(N_PTS, T_RED, np.random.default_rng(880_000 + s))
    raR, decR = uniform_patch(6 * N_PTS, T_RED,
                              np.random.default_rng(880_500 + s))
    A_d, A_r = order_A(ra, dec, T_RED), order_A(raR, decR, T_RED)
    B_r = order_B(raR, decR, T_RED)
    d_match.append(F_of(A_d, A_r, L, extent_of(None, T_RED)))
    d_mis.append(F_of(A_d, B_r, L, extent_of(None, T_RED)))
d_match, d_mis = np.array(d_match), np.array(d_mis)
diff = d_mis - d_match
sem = float(diff.std(ddof=1) / np.sqrt(len(diff)))
red_z = float(diff.mean() / sem) if sem > 0 else np.inf
# null: identical ordering both sides, two runs -> exact reproduction
ra, dec = uniform_patch(N_PTS, 10.0, np.random.default_rng(880_000))
raR, decR = uniform_patch(6 * N_PTS, 10.0, np.random.default_rng(880_001))
f1 = F_of(order_A(ra, dec, 10.0), order_A(raR, decR, 10.0), 0.5,
          extent_of(None, 10.0))
f2 = F_of(order_A(ra, dec, 10.0), order_A(raR, decR, 10.0), 0.5,
          extent_of(None, 10.0))
null_rel = abs(f1 - f2) / max(abs(f1), 1e-12)
red_fired = bool(abs(red_z) >= K)
OUT["kag"] = dict(null_rel=float(null_rel), red_tile=T_RED,
                  F_matched=float(d_match.mean()),
                  F_mismatched=float(d_mis.mean()),
                  red_diff=float(diff.mean()), red_sem=sem, red_z=red_z,
                  q_pred_at_red=PRED["prediction"][f"tile{T_RED:g}"]["q_pred"],
                  red_fired=red_fired,
                  PASS=bool(null_rel <= 1e-12 and red_fired))
print(f"  null rel {null_rel:.2e}; red demo (t={T_RED:g}): "
      f"dF={diff.mean():+.4f}+-{sem:.4f} (z={red_z:+.1f}) vs predicted "
      f"magnitude ~q={OUT['kag']['q_pred_at_red']:.4f} -> "
      f"fired={red_fired}", flush=True)
assert OUT["kag"]["PASS"], "C4 KAG red — fix before measuring (D1 clause)"

# ── law leg: membership fraction vs the committed continuum prediction ───────
print("C4 law leg (membership fraction q)", flush=True)
law = {}
for t in TILES:
    qs = []
    for s in range(SEEDS):
        r = np.random.default_rng(881_000 + s)
        ra, dec = uniform_patch(N_PTS, t, r)
        A, B = order_A(ra, dec, t), order_B(ra, dec, t)
        sa = set(map(tuple, np.round(A, 12)))
        sb = set(map(tuple, np.round(B, 12)))
        n_ref = max(len(sa), 1)
        qs.append(len(sa ^ sb) / n_ref)
    q = np.array(qs)
    pred = PRED["prediction"][f"tile{t:g}"]["q_pred"]
    sem = float(q.std(ddof=1) / np.sqrt(len(q)))
    law[f"tile{t:g}"] = dict(q_measured=float(q.mean()), sem=sem,
                             q_pred=pred, z=float((q.mean() - pred) / sem))
    print(f"  TILE={t:g}: q={q.mean():.5f}+-{sem:.5f} pred={pred:.5f} "
          f"z={law[f'tile{t:g}']['z']:+.2f}", flush=True)
zmax = max(abs(v["z"]) for v in law.values())
OUT["law"] = dict(rows=law, max_abs_z=float(zmax),
                  law_agrees=bool(zmax <= K))

# ── statistic leg (downstream consequence under MATCHED ordering) ──────────
# No correctness ruling: both regions are legitimate windows (see header).
# The per-ordering F-vs-1 numbers below are DIAGNOSTICS ONLY — they also
# carry the estimator's own fixed-N/finite-randoms offset, which is common
# to both orderings and cancels in the difference that C4 measures.
print("C4 statistic leg (matched ordering)", flush=True)
stat = {}
for t in TILES:
    dF, biasA, biasB = [], [], []
    for s in range(SEEDS):
        r = np.random.default_rng(882_000 + s)
        ra, dec = uniform_patch(N_PTS, t, r)
        raR, decR = uniform_patch(6 * N_PTS, t,
                                  np.random.default_rng(883_000 + s))
        Lc = L_FRAC[1] * t
        fa = F_of(order_A(ra, dec, t), order_A(raR, decR, t), Lc,
                  extent_of(None, t))
        fb = F_of(order_B(ra, dec, t), order_B(raR, decR, t), Lc,
                  extent_of(None, t))
        if fa is None or fb is None:
            continue
        dF.append(fa - fb)
        biasA.append(abs(fa - 1.0))
        biasB.append(abs(fb - 1.0))
    d = np.array(dF)
    sem = float(d.std(ddof=1) / np.sqrt(len(d)))
    stat[f"tile{t:g}"] = dict(mean=float(d.mean()), sem=sem,
                              z=float(d.mean() / sem) if sem > 0 else 0.0,
                              bias_A=float(np.mean(biasA)),
                              bias_B=float(np.mean(biasB)),
                              bias_sep_sem=float(np.hypot(
                                  np.std(biasA, ddof=1),
                                  np.std(biasB, ddof=1)) / np.sqrt(len(biasA))))
    print(f"  TILE={t:g}: dF={d.mean():+.5f}+-{sem:.5f} "
          f"(z={stat[f'tile{t:g}']['z']:+.2f}) biasA={np.mean(biasA):.4f} "
          f"biasB={np.mean(biasB):.4f}", flush=True)
OUT["statistic"] = stat
zs = max(abs(v["z"]) for v in stat.values())
OUT["statistic_clean"] = bool(zs <= K)

# ── fixed-substrate point check: survey KAG randoms at the deployed 10 deg ──
print("C4 point check on survey kag_half (read-only)", flush=True)
try:
    from p3_common import load_all
    scal, kag, nulls, tiles = load_all()
    del nulls
    t0 = tiles[len(tiles) // 2]
    ra, dec = kag["ra"], kag["dec"]
    dra = 10.0 / np.cos(np.radians(t0["dec0"]))
    sel = (np.abs(ra - t0["ra0"]) <= 0.9 * dra) & \
          (np.abs(dec - t0["dec0"]) <= 9.0)
    rr, dd = ra[sel], dec[sel]
    half = len(rr) // 2
    A_d = order_A(rr[:half] - t0["ra0"], dd[:half], 10.0, 0.0)
    A_r = order_A(rr[half:] - t0["ra0"], dd[half:], 10.0, 0.0)
    B_d = order_B(rr[:half] - t0["ra0"], dd[:half], 10.0, 0.0)
    B_r = order_B(rr[half:] - t0["ra0"], dd[half:], 10.0, 0.0)
    Lc = 0.5
    fa = F_of(A_d, A_r, Lc, extent_of(None, 10.0))
    fb = F_of(B_d, B_r, Lc, extent_of(None, 10.0))
    q_real = abs(len(A_d) - len(B_d)) / max(len(A_d), 1)
    OUT["point_check"] = dict(tile=(t0["ra0"], t0["dec0"]), n=int(len(rr)),
                              F_A=float(fa), F_B=float(fb),
                              dF=float(fa - fb), q_real=float(q_real))
    print(f"  tile ({t0['ra0']:.0f},{t0['dec0']:.0f}): F_A={fa:.4f} "
          f"F_B={fb:.4f} dF={fa - fb:+.5f} q={q_real:.5f}", flush=True)
except Exception as exc:                                   # noqa: BLE001
    OUT["point_check"] = dict(error=str(exc))
    print(f"  point check unavailable: {exc}", flush=True)

# ── materiality (fail-closed: discharged here, not optional) ────────────────
d3 = json.load(open(f"{ROOT}/survey/d3_measured.json"))
z_class = json.load(open(f"{ROOT}/survey/prereg_sealed.json"))["lattice"]["Z_CLASS"]
margins, sigs = [], []
for srow in d3["slices"].values():
    for tt in srow["tiles"].values():
        for fr in tt["F"]:
            margins.append((fr["F"] - 1.0) / fr["sigma"] - z_class)
            sigs.append(fr["sigma"])
worst_dF = max(abs(v["mean"]) + K * v["sem"] for v in stat.values())
mat_clean = bool(worst_dF / float(np.median(sigs)) < min(margins))
OUT["materiality"] = dict(worst_dF_bound=float(worst_dF),
                          med_sigma_F=float(np.median(sigs)),
                          margin_min_sigma=float(min(margins)),
                          clean=mat_clean)

verdict = resolve_pair(kind="dialed", both_orders_live=False,
                       materiality_clean=mat_clean,
                       fp_all_within_tol=False,
                       law_agrees=OUT["law"]["law_agrees"], powered=True)
OUT["verdict"] = verdict
json.dump(OUT, open(f"{ROOT}/holonomy/c4_measured.json", "w"), indent=1)
print(f"C4: {verdict['primary']} (measurement={verdict['measurement']}, "
      f"flags={verdict['flags']}) | law max|z|={zmax:.2f} | statistic "
      f"max|z|={zs:.2f} | materiality clean={mat_clean}", flush=True)
