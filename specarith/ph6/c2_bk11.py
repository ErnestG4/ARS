"""C2: Berry–Keating 2011, H = (x + 1/x)(p + 1/p) (J. Phys. A 44 (2011) 285203), levels by phase tracking.

ODE (BK11 eqs. 2.8–2.9): χ″ = (h(x)/η² + i g(x)/η) χ,  h = 1 − E²x²/(4(1+x²)²),  g = E(1 − x²)/(2(1+x²)²).
Eigencondition (eq. 2.22 with eq. 3.3): the solution decaying as x → ∞ satisfies χ′(0)/χ(0) = e^{iα}/η. For real E the
decaying solution's log-derivative at 0 lies on the circle |a| = 1/η (BK11 p. 5), so the condition is
    Φ(E) ≡ arg(η χ′(0)/χ(0)) = α (mod 2π),   declared α = 0, η = 1/2π, E = t/2π (eq. 5.3).
The decaying solution is integrated BACKWARD from x_max (beyond the outer turning point, WKB start), which is the
stable direction. Known answer: E = 0 ⇒ χ = e^{−x/η} exactly ⇒ η χ′(0)/χ(0) = −1 (eq. 3.4).
"""
import cmath
import math

import numpy as np
from scipy.integrate import solve_ivp

ETA = 1 / (2 * math.pi)


def q(x, E, eta=ETA):
    d = (1 + x * x) ** 2
    h = 1 - E * E * x * x / (4 * d)
    g = E * (1 - x * x) / (2 * d)
    return h / eta ** 2 + 1j * g / eta


def outer_turning_point(E):
    """Largest x with h(x) = 0: E x / (2(1 + x²)) = 1  ⇒  x² − (E/2) x + 1 = 0."""
    if E <= 4:
        return 0.0
    return (E / 2 + math.sqrt(E * E / 4 - 4)) / 2


def log_derivative_at_0(E, eta=ETA, margin_action=40.0, rtol=1e-12, atol=1e-14):
    """a(E) = χ′(0)/χ(0) for the solution decaying at +∞."""
    xt = outer_turning_point(E)
    # extend beyond the turning point until ∫ Re√q dx ≥ margin_action (subdominant contamination ≤ e^{−2·margin})
    x, acc, dx = max(xt, 1.0), 0.0, 0.05
    while acc < margin_action:
        acc += cmath.sqrt(q(x, E, eta)).real * dx
        x += dx
    xmax = x
    s = cmath.sqrt(q(xmax, E, eta))
    if s.real < 0:
        s = -s
    y0 = np.array([1.0 + 0j, -s])                       # χ = 1, χ′ = −√q χ (WKB decaying branch)

    def rhs(xx, y):
        return np.array([y[1], q(xx, E, eta) * y[0]])

    sol = solve_ivp(rhs, (xmax, 0.0), y0, method="DOP853", rtol=rtol, atol=atol)
    chi, dchi = sol.y[0, -1], sol.y[1, -1]
    return dchi / chi, dict(xmax=xmax, nfev=int(sol.nfev))


def phase(E, **kw):
    a, info = log_derivative_at_0(E, **kw)
    return cmath.phase(a * ETA), abs(a * ETA), info


if __name__ == "__main__":
    import sys
    a, info = log_derivative_at_0(0.0)
    print("E=0 known answer: eta*a =", a * ETA, "(must be -1)", info)
    for E in [float(v) for v in sys.argv[1:]] or [1.0, 5.0, 20.0, 50.0]:
        ph, mod, info = phase(E)
        print(f"E={E}: arg(eta a)={ph:.12f}  |eta a|={mod:.12f} (must be 1)  {info}")
