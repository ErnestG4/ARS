"""
cross_substrate/dynamical_breadth.py — Job 3: more chaotic systems for the Family-V landscape.

Adds Rössler / Chua / Duffing (3-D flows) + Hénon (2-D map) as bifurcation-sweep trajectories, each
placed by Family V: λ₁ via tangent-space Benettin (correct sign+magnitude, the validated tool for
known-equation substrates) + D₂ via Grassberger-Procaccia, plus event-NNS (Family I) on clean
dynamical events (median-upcrossing transitions — NOT find_peaks). Extends the chaos-ordered
dynamical region of the landscape beyond Lorenz/Mackey-Glass/logistic.

Out: coordinates/dynamical-breadth.jsonl. Run: --probe | --sweep [--workers 10].
"""
from __future__ import annotations

import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(_v, "1")

import argparse
import json
import sys
from concurrent.futures import ProcessPoolExecutor
from datetime import date

import numpy as np

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_HERE)
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from cross_substrate.axes import compute_family_I, compute_family_II, V2_correlation_dim  # noqa: E402

COORD = os.path.join(_HERE, "coordinates")


# ── generic integrators + tangent-space Benettin ────────────────────────────
def _rk4(f, s, dt):
    k1 = f(s); k2 = f(s + .5 * dt * k1); k3 = f(s + .5 * dt * k2); k4 = f(s + dt * k3)
    return s + dt / 6 * (k1 + 2 * k2 + 2 * k3 + k4)


def traj_flow(f, s0, n, dt=0.01, discard=20_000):
    s = np.array(s0, float)
    for _ in range(discard):
        s = _rk4(f, s, dt)
    out = np.empty((n, len(s)))
    for i in range(n):
        s = _rk4(f, s, dt); out[i] = s
    return out


def benettin_flow(f, J, s0, dt=0.01, n_steps=120_000, discard=20_000):
    s = np.array(s0, float); d = np.zeros_like(s); d[0] = 1e-8; d0 = np.linalg.norm(d)
    for _ in range(discard):
        s = _rk4(f, s, dt)
    lsum = 0.0
    for _ in range(n_steps):
        def fd(s, d):
            return f(s), J(s) @ d
        a1, b1 = fd(s, d); a2, b2 = fd(s + .5 * dt * a1, d + .5 * dt * b1)
        a3, b3 = fd(s + .5 * dt * a2, d + .5 * dt * b2); a4, b4 = fd(s + dt * a3, d + dt * b3)
        s = s + dt / 6 * (a1 + 2 * a2 + 2 * a3 + a4)
        d = d + dt / 6 * (b1 + 2 * b2 + 2 * b3 + b4)
        nd = np.linalg.norm(d); lsum += np.log(nd / d0); d = d * (d0 / nd)
    return lsum / (n_steps * dt)


def _crossing_events(x, dt=0.01):
    """Median-upcrossing times — a clean dynamical point process (NOT find_peaks)."""
    m = np.median(x)
    up = (x[1:] >= m) & (x[:-1] < m)
    return np.where(up)[0].astype(float) * dt


# ── systems: f(s), J(s), s0, param-sweep ────────────────────────────────────
def rossler(c, a=0.2, b=0.2):
    f = lambda s: np.array([-s[1] - s[2], s[0] + a * s[1], b + s[2] * (s[0] - c)])
    J = lambda s: np.array([[0., -1., -1.], [1., a, 0.], [s[2], 0., s[0] - c]])
    return f, J, [1.0, 1.0, 1.0]


def chua(alpha, beta=28.0, m0=-1.143, m1=-0.714):
    def g(x):
        return m1 * x + 0.5 * (m0 - m1) * (abs(x + 1) - abs(x - 1))
    def gp(x):
        return m0 if abs(x) < 1 else m1
    f = lambda s: np.array([alpha * (s[1] - s[0] - g(s[0])), s[0] - s[1] + s[2], -beta * s[1]])
    J = lambda s: np.array([[alpha * (-1 - gp(s[0])), alpha, 0.], [1., -1., 1.], [0., -beta, 0.]])
    return f, J, [0.1, 0.0, 0.0]


def duffing(gamma, delta=0.3, omega=1.2):
    # ẍ + δẋ − x + x³ = γ cos(ωt); autonomous via phase coord φ̇=ω. s=(x,v,φ)
    f = lambda s: np.array([s[1], -delta * s[1] + s[0] - s[0] ** 3 + gamma * np.cos(s[2]), omega])
    J = lambda s: np.array([[0., 1., 0.], [1 - 3 * s[0] ** 2, -delta, -gamma * np.sin(s[2])], [0., 0., 0.]])
    return f, J, [0.1, 0.0, 0.0]


SWEEPS = {
    "rossler": ("c", [4.0, 6.0, 8.5, 12.0, 18.0], rossler),
    "chua":    ("alpha", [8.5, 10.0, 13.0, 15.6], chua),
    "duffing": ("gamma", [0.2, 0.3, 0.37, 0.5], duffing),
}


def henon_traj(a, b=0.3, n=80_000, discard=2000):
    x, y = 0.1, 0.1
    out = np.empty((n, 2))
    for _ in range(discard):
        x, y = 1 - a * x * x + y, b * x
    for i in range(n):
        x, y = 1 - a * x * x + y, b * x; out[i] = [x, y]
    return out


def henon_lyapunov(a, b=0.3, n=80_000, discard=2000):
    x, y = 0.1, 0.1
    for _ in range(discard):
        x, y = 1 - a * x * x + y, b * x
    d = np.array([1e-8, 0.0]); d0 = np.linalg.norm(d); lsum = 0.0
    for _ in range(n):
        d = np.array([[-2 * a * x, 1.0], [b, 0.0]]) @ d
        nd = np.linalg.norm(d); lsum += np.log(nd / d0); d = d * (d0 / nd)
        x, y = 1 - a * x * x + y, b * x
    return lsum / n


def _f(v):
    return None if v is None or not (isinstance(v, (int, float)) and np.isfinite(v)) else float(v)


def _task(arg):
    system, pname, pval = arg
    if system == "henon":
        tr = henon_traj(pval)
        lam = henon_lyapunov(pval)
        x = tr[:, 0]
        m = np.median(x)
        ev = np.where((x[1:] >= m) & (x[:-1] < m))[0].astype(float)
        d2 = V2_correlation_dim(x, emb_dim=3)
    else:
        _, vals, mk = SWEEPS[system]
        f, J, s0 = mk(pval)
        tr = traj_flow(f, s0, 80_000, dt=0.01)
        lam = benettin_flow(f, J, s0, dt=0.01)
        x = tr[:, 0]
        ev = _crossing_events(x, dt=0.01)
        d2 = V2_correlation_dim(x)
    fI = compute_family_I(ev) if ev.size >= 20 else {}
    fII = compute_family_II(ev) if ev.size >= 200 else {}
    axes = {**{k: _f(v) for k, v in fI.items()}, **{k: _f(v) for k, v in fII.items()},
            "V.1_lyapunov": _f(lam), "V.2_correlation_dim": _f(d2)}
    return (system, pname, pval, int(ev.size), axes)


def sweep(workers):
    tasks = [(s, SWEEPS[s][0], v) for s in SWEEPS for v in SWEEPS[s][1]]
    tasks += [("henon", "a", v) for v in (0.9, 1.06, 1.2, 1.4)]
    print(f"DYNAMICAL BREADTH (Job 3) — {len(tasks)} cells: Rössler/Chua/Duffing/Hénon × param-sweeps")
    print(f"{'system':9s} {'param':>7s} {'n_ev':>5s} {'λ₁':>7s} {'D₂':>6s} {'W1δ':>6s} {'Brody q':>8s}")
    with ProcessPoolExecutor(max_workers=workers) as ex:
        res = list(ex.map(_task, tasks))
    recs = []
    for system, pname, pval, nev, axes in res:
        recs.append({"substrate": system, "cell_id": f"{system}_{pname}{pval:g}",
                     "axes_computed": axes,
                     "non_applicable_axes": ["III.1_p2"],
                     "extraction_method": ("RK4 flow + Benettin λ + GP D₂; events=median-upcrossings"
                                           if system != "henon" else
                                           "Hénon map + tangent λ + GP D₂; events=x-median-upcrossings"),
                     "extraction_audit": {pname: pval, "n_events": nev},
                     "source_artifact": "generated (deterministic integration)",
                     "computed_date": date.today().isoformat()})
        def g(k):
            v = axes.get(k)
            return f"{v:.3f}" if isinstance(v, float) else "  -"
        print(f"{system:9s} {pval:>7g} {nev:>5d} {g('V.1_lyapunov'):>7s} {g('V.2_correlation_dim'):>6s} "
              f"{g('I.1_w1_clock'):>6s} {g('I.8_brody_q'):>8s}")
    with open(os.path.join(COORD, "dynamical-breadth.jsonl"), "w") as fh:
        for r in recs:
            fh.write(json.dumps(r) + "\n")
    print(f"\n→ {len(recs)} cells banked. Chaos-ordered trajectories (λ₁ crosses 0 into chaos; D₂ rises). "
          "Extends the Family-V dynamical landscape. Flag, don't interpret.")


def probe(workers):
    print("PROBE — known chaos values: Rössler c=5.7 λ≈0.07/D₂≈2.0; Hénon a=1.4 λ≈0.42/D₂≈1.26")
    for arg in [("rossler", "c", 5.7), ("henon", "a", 1.4), ("chua", "alpha", 15.6), ("duffing", "gamma", 0.37)]:
        s, p, v, nev, ax = _task(arg)
        print(f"  {s:9s} {p}={v:g}: λ₁={_f(ax['V.1_lyapunov'])} D₂={_f(ax['V.2_correlation_dim'])} n_ev={nev}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--probe", action="store_true")
    ap.add_argument("--sweep", action="store_true")
    ap.add_argument("--workers", type=int, default=10)
    a = ap.parse_args()
    if a.probe:
        probe(a.workers)
    elif a.sweep:
        sweep(a.workers)
    else:
        ap.error("need --probe or --sweep")


if __name__ == "__main__":
    main()
