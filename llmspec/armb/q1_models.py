"""Q1 anchor models (ARMB_PREREG_B1B.md Q1; sealed with it). Data-free: predictions for arm X's turning point given
A0's turning point t0, under three anchors, using the SEALED LR function (B1a §1: GPT-NeoX v1.0 AnnealingLR incl. the
/E cosine quirk; optimizer update k uses lr(k-1)).
  STEP     P = t0
  WARMUP   P = t0 + (W_X - W_0)
  LR_INT   P = smallest t with Lambda_X(t) >= Lambda_0(t0), Lambda(t) = sum_{k=1..t} lr(k-1)  (cumulative LR applied
           by the end of step t)
Also d P_LRint / d t0 = lr_0(t0-1) / lr_X(P-1), used to propagate A0's localisation error into the prediction.
`python q1_models.py` prints the prediction table and the minimum inter-model gap per arm over t0 in [800, 3500].
"""
import math
import numpy as np

LR0, MINLR, E = 1e-3, 1e-4, 143000
W0 = 1430
ARMS = {"A1": 2860, "A2": 715}


def lr(n, W):
    num = min(n, E - W)
    if W > 0 and n <= W:
        return LR0 * num / W
    num -= W
    return max(LR0 / 2.0 * (math.cos(math.pi * num / E) + 1), MINLR)


def cum(W, T):
    """Lambda(t) for t = 0..T: cumulative LR applied by the end of step t (update k uses lr(k-1))."""
    a = np.zeros(T + 1)
    for k in range(1, T + 1):
        a[k] = a[k - 1] + lr(k - 1, W)
    return a


_C0 = cum(W0, 12000)
_CX = {X: cum(W, 12000) for X, W in ARMS.items()}


def predict(t0, X):
    WX = ARMS[X]
    p_step = t0
    p_warm = t0 + (WX - W0)
    p_lr = int(np.searchsorted(_CX[X], _C0[t0]))
    dP = lr(t0 - 1, W0) / max(lr(p_lr - 1, WX), 1e-30)
    return {"STEP": p_step, "WARMUP": p_warm, "LR_INT": p_lr, "dLRINT_dt0": dP}


def min_gap(t0, X):
    p = predict(t0, X); v = sorted([p["STEP"], p["WARMUP"], p["LR_INT"]])
    return min(v[1] - v[0], v[2] - v[1])


if __name__ == "__main__":
    for t0 in (800, 1000, 1500, 2000, 2500, 3000, 3500):
        row = {X: predict(t0, X) for X in ARMS}
        print(t0, {X: (r["STEP"], r["WARMUP"], r["LR_INT"], round(r["dLRINT_dt0"], 2), min_gap(t0, X)) for X, r in row.items()})
