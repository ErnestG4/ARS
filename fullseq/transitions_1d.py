"""Full-sequence holonomy — the five registered 1-D transitions.

Sequence length 5 (sealed). Each is a real transition in the repo's 1-D
dialect, and each takes and returns (points, meta) so they compose in any
order the type constraints allow.

  T1 WINDOW    select a central fraction of the point set
  T2 UNFOLD    degree-d polynomial fit to the counting staircase
  T3 THIN      stochastic decimation, PRE-DRAWN u per point (§0 of the
               holonomy pilot brief: randomness is drawn once, before any
               ordering runs, and consumed by whichever position the
               transition occupies — otherwise the two orderings consume the
               RNG stream against different inputs and the difference
               measures stream drift, not order)
  T4 RESCALE   renormalise spacings to unit mean — the hidden transition the
               census found inside compute_nns (finding C1)
  T5 POOL      superpose a second independent segment (the operation the
               pooled-arithmetic rows perform, and the one known to
               Poissonise long-range structure)

Type constraint (sealed): T1 must precede T5 — pooling before windowing
would window the pooled set, which is a different pipeline, not a reordering
of this one. All other orders are admissible.
"""

import numpy as np


def t1_window(pts, meta, frac=0.6):
    p = np.sort(np.asarray(pts, float))
    n = p.size
    lo = int(n * (1 - frac) / 2)
    hi = lo + int(n * frac)
    keep = np.zeros(n, bool)
    keep[lo:hi] = True
    m = dict(meta)
    m["u"] = meta["u"][keep] if meta.get("u") is not None else None
    m["applied"] = meta["applied"] + ["T1"]
    return p[keep], m


def t2_unfold(pts, meta, deg=6):
    p = np.sort(np.asarray(pts, float))
    if p.size < deg + 2:
        return p, {**meta, "applied": meta["applied"] + ["T2"]}
    y = np.arange(1, p.size + 1, dtype=float)
    x = (p - p[0]) / (p[-1] - p[0] + 1e-12)
    out = np.polyval(np.polyfit(x, y, deg), x)
    return np.sort(out), {**meta, "applied": meta["applied"] + ["T2"]}


def t3_thin(pts, meta, keep_prob=0.7):
    p = np.sort(np.asarray(pts, float))
    u = meta.get("u")
    if u is None or len(u) != p.size:
        u = np.random.default_rng(0).uniform(size=p.size)
    keep = u < keep_prob
    m = dict(meta)
    m["u"] = u[keep]
    m["applied"] = meta["applied"] + ["T3"]
    return p[keep], m


def t4_rescale(pts, meta):
    p = np.sort(np.asarray(pts, float))
    if p.size < 3:
        return p, {**meta, "applied": meta["applied"] + ["T4"]}
    s = np.diff(p)
    mu = s.mean()
    if mu <= 0:
        return p, {**meta, "applied": meta["applied"] + ["T4"]}
    out = np.concatenate([[0.0], np.cumsum(s / mu)])
    return out, {**meta, "applied": meta["applied"] + ["T4"]}


def t5_pool(pts, meta):
    """Superpose an independent second segment of the same generator, at the
    current state's density and span."""
    p = np.sort(np.asarray(pts, float))
    if p.size < 5:
        return p, {**meta, "applied": meta["applied"] + ["T5"]}
    other = meta["pool_partner"]
    o = np.sort(np.asarray(other, float))
    span = p[-1] - p[0]
    if o.size > 1 and (o[-1] - o[0]) > 0:
        o = p[0] + (o - o[0]) * span / (o[-1] - o[0])
    out = np.sort(np.concatenate([p, o]))
    m = dict(meta)
    m["u"] = None                       # pooled set has no per-point draw
    m["applied"] = meta["applied"] + ["T5"]
    return out, m


TRANSITIONS = {"T1": t1_window, "T2": t2_unfold, "T3": t3_thin,
               "T4": t4_rescale, "T5": t5_pool}
REFERENCE_ORDER = ["T1", "T2", "T3", "T4", "T5"]


def admissible(order):
    """Sealed type constraint: T1 before T5."""
    return order.index("T1") < order.index("T5")


def apply_sequence(pts, order, u, pool_partner, **kw):
    meta = dict(u=np.asarray(u, float), pool_partner=pool_partner,
                applied=[])
    p = np.asarray(pts, float)
    for t in order:
        p, meta = TRANSITIONS[t](p, meta, **kw.get(t, {}))
    return p, meta


# ── statistics read at the end of the stack ─────────────────────────────────

def sigma2(events, L):
    e = np.sort(np.asarray(events, float))
    if e.size < 20:
        return np.nan
    step = max(0.1 * L, 1.0)
    pos = np.arange(e[0], e[-1] - L, step)
    if pos.size < 5:
        return np.nan
    c = (np.searchsorted(e, pos + L, "left")
         - np.searchsorted(e, pos, "left")).astype(float)
    return float(c.var(ddof=1))


def rtilde(events):
    s = np.diff(np.sort(np.asarray(events, float)))
    s = s[s > 0]
    if s.size < 3:
        return np.nan
    r = s[1:] / s[:-1]
    return float(np.mean(np.minimum(r, 1.0 / r)))
