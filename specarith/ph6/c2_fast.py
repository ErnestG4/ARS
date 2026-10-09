"""C2 (Berry–Keating 2011) — compiled phase function for the level build. Same mathematics as c2_bk11.py (the scipy
DOP853 reference): backward integration of the solution decaying at +∞, Φ(E) = arg(η χ′(0)/χ(0)); levels at
Φ(E) = α (mod 2π), α = 0, η = 1/2π. Integrator: adaptive Dormand–Prince 5(4) on the complex 2-vector (χ, χ′), compiled
with numba; validated against c2_bk11.phase at several E before use (c2_fast.validate)."""
import cmath
import math

import numpy as np
from numba import njit

ETA = 1 / (2 * math.pi)

# Dormand–Prince 5(4) tableau
C2, C3, C4, C5 = 1 / 5, 3 / 10, 4 / 5, 8 / 9
A21 = 1 / 5
A31, A32 = 3 / 40, 9 / 40
A41, A42, A43 = 44 / 45, -56 / 15, 32 / 9
A51, A52, A53, A54 = 19372 / 6561, -25360 / 2187, 64448 / 6561, -212 / 729
A61, A62, A63, A64, A65 = 9017 / 3168, -355 / 33, 46732 / 5247, 49 / 176, -5103 / 18656
B1, B3, B4, B5, B6 = 35 / 384, 500 / 1113, 125 / 192, -2187 / 6784, 11 / 84
E1, E3, E4, E5, E6, E7 = 71 / 57600, -71 / 16695, 71 / 1920, -17253 / 339200, 22 / 525, -1 / 40


@njit(cache=True)
def _q(x, E, eta):
    d = (1.0 + x * x) ** 2
    h = 1.0 - E * E * x * x / (4.0 * d)
    g = E * (1.0 - x * x) / (2.0 * d)
    return complex(h / (eta * eta), g / eta)


@njit(cache=True)
def _integrate(E, eta, xmax, y0, y1, rtol, atol):
    x = xmax
    h = -1e-3
    u, v = y0, y1
    nsteps = 0
    while x > 0.0:
        if x + h < 0.0:
            h = -x
        k1u, k1v = v, _q(x, E, eta) * u
        u2, v2 = u + h * A21 * k1u, v + h * A21 * k1v
        k2u, k2v = v2, _q(x + C2 * h, E, eta) * u2
        u3, v3 = u + h * (A31 * k1u + A32 * k2u), v + h * (A31 * k1v + A32 * k2v)
        k3u, k3v = v3, _q(x + C3 * h, E, eta) * u3
        u4 = u + h * (A41 * k1u + A42 * k2u + A43 * k3u)
        v4 = v + h * (A41 * k1v + A42 * k2v + A43 * k3v)
        k4u, k4v = v4, _q(x + C4 * h, E, eta) * u4
        u5 = u + h * (A51 * k1u + A52 * k2u + A53 * k3u + A54 * k4u)
        v5 = v + h * (A51 * k1v + A52 * k2v + A53 * k3v + A54 * k4v)
        k5u, k5v = v5, _q(x + C5 * h, E, eta) * u5
        u6 = u + h * (A61 * k1u + A62 * k2u + A63 * k3u + A64 * k4u + A65 * k5u)
        v6 = v + h * (A61 * k1v + A62 * k2v + A63 * k3v + A64 * k4v + A65 * k5v)
        k6u, k6v = v6, _q(x + h, E, eta) * u6
        un = u + h * (B1 * k1u + B3 * k3u + B4 * k4u + B5 * k5u + B6 * k6u)
        vn = v + h * (B1 * k1v + B3 * k3v + B4 * k4v + B5 * k5v + B6 * k6v)
        k7u, k7v = vn, _q(x + h, E, eta) * un
        eu = h * (E1 * k1u + E3 * k3u + E4 * k4u + E5 * k5u + E6 * k6u + E7 * k7u)
        ev = h * (E1 * k1v + E3 * k3v + E4 * k4v + E5 * k5v + E6 * k6v + E7 * k7v)
        su = atol + rtol * max(abs(u), abs(un))
        sv = atol + rtol * max(abs(v), abs(vn))
        err = math.sqrt(0.5 * ((abs(eu) / su) ** 2 + (abs(ev) / sv) ** 2))
        if err <= 1.0:
            x += h
            u, v = un, vn
            nsteps += 1
            # rescale to keep magnitudes bounded (the log-derivative is scale-free)
            m = abs(u)
            if m > 1e100 or m < 1e-100:
                u, v = u / m, v / m
        fac = 0.9 * err ** (-0.2) if err > 0 else 5.0
        h *= min(5.0, max(0.2, fac))
    return u, v, nsteps


def _xmax(E, eta, margin_action=40.0):
    xt = 0.0 if E <= 4 else (E / 2 + math.sqrt(E * E / 4 - 4)) / 2
    x, acc, dx = max(xt, 1.0), 0.0, 0.05
    while acc < margin_action:
        d = (1 + x * x) ** 2
        qq = complex((1 - E * E * x * x / (4 * d)) / eta ** 2, E * (1 - x * x) / (2 * d) / eta)
        acc += cmath.sqrt(qq).real * dx
        x += dx
    return x


def phase(E, eta=ETA, rtol=1e-11, atol=1e-30):
    xmax = _xmax(E, eta)
    d = (1 + xmax * xmax) ** 2
    s = cmath.sqrt(complex((1 - E * E * xmax * xmax / (4 * d)) / eta ** 2, E * (1 - xmax * xmax) / (2 * d) / eta))
    if s.real < 0:
        s = -s
    u, v, n = _integrate(E, eta, xmax, 1.0 + 0j, -s, rtol, atol)
    a = v / u
    return cmath.phase(a * eta), abs(a * eta), n


def validate(Es=(0.0, 1.0, 20.0, 50.0, 200.0, 800.0)):
    import c2_bk11 as ref
    out = []
    for E in Es:
        pf, mf, n = phase(E)
        pr, mr, info = ref.phase(E)
        d = abs(cmath.exp(1j * pf) - cmath.exp(1j * pr))
        out.append((E, pf, pr, d, mf, n))
        print(f"E={E}: fast {pf:.12f} (|ηa|={mf:.12f}, {n} steps)  scipy-DOP853 {pr:.12f}  |Δ|={d:.1e}", flush=True)
    return out


if __name__ == "__main__":
    validate()
