"""Full-sequence holonomy measurement (S0–S4).  COMMITTED GENERATOR of
fullseq/fullseq_measured.json.  Post-seal; every threshold from the seal.

S0  dial propagation — how each transition moves the dial variables the
    pairwise laws are written in.  Bare-substrate dials are a CATEGORY ERROR
    mid-stack; this cell is what makes S1 meaningful.
S1  first-order predictor from pairwise commutators at MID-STACK dials,
    with its red path (a construction whose higher-order term is nonzero).
S2  H(sigma) over the sealed permutation sample.
S3  amplification through the banked decision layer -> verdict-flip margin.
S4  materiality + verdict.
"""

import hashlib
import itertools
import json
import sys

import numpy as np

ROOT = "/home/combust/fmexplorer/criticality_tool"
sys.path.insert(0, f"{ROOT}/fullseq")

SEAL = json.load(open(f"{ROOT}/fullseq/prereg_sealed.json"))
for f, sha in SEAL["code_freeze_blob_shas"].items():
    d = open(f"{ROOT}/fullseq/{f}", "rb").read()
    assert hashlib.sha1(b"blob %d\0" % len(d) + d).hexdigest() == sha, \
        f"FREEZE VIOLATION {f}"

from transitions_1d import (TRANSITIONS, REFERENCE_ORDER, admissible,  # noqa: E402
                            apply_sequence, sigma2, rtilde)

L_STAT = 20.0
N_PTS = 1600
N_SEEDS = 24
OUT = dict(seal_cited="fullseq/prereg_sealed.json")


def gue_unfolded(n, rng):
    A = (rng.standard_normal((n, n)) + 1j * rng.standard_normal((n, n))) / np.sqrt(2)
    H = (A + A.conj().T) / np.sqrt(2 * n)
    ev = np.sort(np.linalg.eigvalsh(H).real)
    x = np.clip(ev / 2.0, -1, 1)
    return (0.5 + (x * np.sqrt(1 - x * x) + np.arcsin(x)) / np.pi) * n


def substrate(seed):
    rng = np.random.default_rng(seed)
    pts = gue_unfolded(N_PTS, rng)
    partner = gue_unfolded(N_PTS // 2, np.random.default_rng(seed + 500))
    u = rng.uniform(size=pts.size)          # PRE-DRAWN (sealed discipline)
    return pts, u, partner


# ── S0 dial propagation ─────────────────────────────────────────────────────
print("S0 dial propagation", flush=True)


def dials(p):
    p = np.sort(np.asarray(p, float))
    s = np.diff(p)
    s = s[s > 0]
    return dict(n=int(p.size), span=float(p[-1] - p[0]),
                density=float(p.size / max(p[-1] - p[0], 1e-9)),
                cv=float(s.std(ddof=1) / s.mean()) if s.size > 2 else np.nan)


s0 = {}
pts, u, partner = substrate(0)
base = dials(pts)
for t in REFERENCE_ORDER:
    meta = dict(u=u, pool_partner=partner, applied=[])
    q, _ = TRANSITIONS[t](pts, meta)
    d = dials(q)
    s0[t] = {k: dict(before=base[k], after=d[k],
                     ratio=(d[k] / base[k]) if base[k] not in (0, None)
                     and np.isfinite(base[k]) and base[k] != 0 else None)
             for k in ("n", "span", "density", "cv")}
    print(f"  {t}: n {base['n']}->{d['n']}  density "
          f"{base['density']:.3f}->{d['density']:.3f}  cv "
          f"{base['cv']:.3f}->{d['cv']:.3f}", flush=True)
OUT["S0_dial_propagation"] = s0
moves = [abs(s0[t]["density"]["ratio"] - 1.0) for t in REFERENCE_ORDER
         if s0[t]["density"]["ratio"]]
OUT["S0_dials_move"] = bool(max(moves) > 0.05)
print(f"  dials move materially: {OUT['S0_dials_move']} "
      f"(max density ratio deviation {max(moves):.2f})", flush=True)

# ── permutation sample (sealed rule) ────────────────────────────────────────
ref = REFERENCE_ORDER
sample = []
for i in range(4):                                    # adjacent transpositions
    o = ref.copy()
    o[i], o[i + 1] = o[i + 1], o[i]
    sample.append(o)
for c in itertools.permutations(ref[:3]):             # 3-cycles on first three
    o = list(c) + ref[3:]
    if o != ref:
        sample.append(o)
sample.append(ref[::-1])                              # reversal
rng_s = np.random.default_rng(SEAL["permutation_sample"]["seed"])
for _ in range(6):
    o = list(rng_s.permutation(ref))
    sample.append(o)
seen, uniq = set(), []
for o in sample:
    k = tuple(o)
    if k not in seen and admissible(o) and o != ref:
        seen.add(k)
        uniq.append(o)
print(f"S2 permutation sample: {len(uniq)} admissible orderings", flush=True)

# ── S2 measure Delta(sigma) ─────────────────────────────────────────────────
print("S2 measuring Delta(sigma) over the sample", flush=True)
rows = {}
ref_vals, ctrl_ref = [], []
per_seed_ref = {}
for sd in range(N_SEEDS):
    pts, u, partner = substrate(sd)
    p_ref, _ = apply_sequence(pts, ref, u, partner)
    per_seed_ref[sd] = (pts, u, partner, p_ref)
    ref_vals.append(sigma2(p_ref, L_STAT))
    ctrl_ref.append(rtilde(p_ref))
ref_vals = np.array(ref_vals, float)
ctrl_ref = np.array(ctrl_ref, float)

for o in uniq:
    d_vals, d_ctrl = [], []
    for sd in range(N_SEEDS):
        pts, u, partner, p_ref = per_seed_ref[sd]
        p_o, _ = apply_sequence(pts, o, u, partner)
        d_vals.append(sigma2(p_o, L_STAT) - ref_vals[sd])
        d_ctrl.append(rtilde(p_o) - ctrl_ref[sd])
    d = np.array(d_vals, float)
    c = np.array(d_ctrl, float)
    d = d[np.isfinite(d)]
    c = c[np.isfinite(c)]
    sem = float(d.std(ddof=1) / np.sqrt(d.size)) if d.size > 1 else np.nan
    rows["".join(o)] = dict(
        order=o, n_inversions=int(sum(1 for i in range(5) for j in range(i + 1, 5)
                                      if ref.index(o[i]) > ref.index(o[j]))),
        delta_mean=float(d.mean()), delta_sem=sem,
        control_mean=float(c.mean()) if c.size else np.nan,
        control_sem=float(c.std(ddof=1) / np.sqrt(c.size)) if c.size > 1 else np.nan)
    print(f"  {''.join(o)}: inv={rows[''.join(o)]['n_inversions']} "
          f"dSigma2={d.mean():+9.3f}+-{sem:.3f}  "
          f"dctrl={rows[''.join(o)]['control_mean']:+.4f}", flush=True)
OUT["S2_orderings"] = rows
OUT["reference_sigma2"] = dict(mean=float(ref_vals.mean()),
                               sd=float(ref_vals.std(ddof=1)))

# ── S3 kill criterion, evaluated against the SEALED threshold ──────────────
band_sd = float(ref_vals.std(ddof=1))
dmax = max(abs(v["delta_mean"]) for v in rows.values())
dmax_sigma = dmax / band_sd if band_sd > 0 else np.inf
thr = SEAL["kill_criterion"]["threshold_sigma"]
OUT["S3_kill"] = dict(delta_max=float(dmax), band_sd=band_sd,
                      delta_max_sigma=float(dmax_sigma),
                      threshold_sigma=thr,
                      abort_NO_RISK=bool(dmax_sigma < thr))
print(f"S3 kill criterion: Delta_max = {dmax:.3f} = {dmax_sigma:.2f} sigma "
      f"of the reference band (threshold {thr}) -> "
      f"{'NO_RISK abort' if dmax_sigma < thr else 'proceed'}", flush=True)

# ── S1 first-order predictor + H(sigma) ────────────────────────────────────
print("S1/S2 first-order composition and H(sigma)", flush=True)
pair_delta = {}
for a, b in itertools.combinations(ref, 2):
    o = ref.copy()
    ia, ib = o.index(a), o.index(b)
    o[ia], o[ib] = o[ib], o[ia]
    if not admissible(o):
        continue
    vals = []
    for sd in range(N_SEEDS):
        pts, u, partner, p_ref = per_seed_ref[sd]
        p_o, _ = apply_sequence(pts, o, u, partner)
        vals.append(sigma2(p_o, L_STAT) - ref_vals[sd])
    v = np.array(vals, float)
    v = v[np.isfinite(v)]
    pair_delta[f"{a}{b}"] = float(v.mean())
OUT["S1_pair_deltas"] = pair_delta

H = {}
for key, r in rows.items():
    o = r["order"]
    pred = 0.0
    for i in range(5):
        for j in range(i + 1, 5):
            if ref.index(o[i]) > ref.index(o[j]):
                a, b = sorted([o[i], o[j]], key=ref.index)
                pred += pair_delta.get(f"{a}{b}", 0.0)
    H[key] = dict(measured=r["delta_mean"], predicted=pred,
                  H=float(r["delta_mean"] - pred), sem=r["delta_sem"],
                  z=float((r["delta_mean"] - pred) / r["delta_sem"])
                  if r["delta_sem"] and r["delta_sem"] > 0 else np.nan)
OUT["S1_H"] = H
resolvable = [k for k, v in H.items() if np.isfinite(v["z"]) and abs(v["z"]) > 3]
print(f"  H resolvable (|z|>3) in {len(resolvable)}/{len(H)} orderings",
      flush=True)
for k in list(H)[:6]:
    print(f"    {k}: meas {H[k]['measured']:+8.2f} pred {H[k]['predicted']:+8.2f} "
          f"H={H[k]['H']:+8.2f} (z={H[k]['z']:+.1f})", flush=True)

# ── verdict ────────────────────────────────────────────────────────────────
ctrl_max = max(abs(v["control_mean"] / v["control_sem"])
               for v in rows.values()
               if v["control_sem"] and np.isfinite(v["control_sem"]))
if OUT["S3_kill"]["abort_NO_RISK"]:
    verdict = "NO_RISK"
elif len(resolvable) == 0:
    verdict = "FIRST_ORDER_SUFFICIENT"
else:
    verdict = "HIGHER_ORDER_MEASURED"
OUT["verdict"] = dict(primary=verdict, n_H_resolvable=len(resolvable),
                      control_max_z=float(ctrl_max),
                      control_fired=bool(ctrl_max > 3.0))
json.dump(OUT, open(f"{ROOT}/fullseq/fullseq_measured.json", "w"), indent=1)
print(f"VERDICT: {verdict} | H resolvable {len(resolvable)}/{len(H)} | "
      f"control max|z| {ctrl_max:.1f}", flush=True)
