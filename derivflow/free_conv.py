#!/usr/bin/env python3
"""derivflow free-convolution evaluator — Belinschi–Bercovici subordination (TRACK0_SCOPE §4 v1.2).

Route (Will's design, pinned in scope): NOT the R-transform power series. The subordinator solves
    omega(z) = z/kappa + (1 - 1/kappa) * F_mu(omega(z)),      F = 1/G,  kappa = 1/(1-s) >= 1,
a Denjoy–Wolff contraction on the upper half-plane, so convergence is certified — the contraction
residual is logged per call, not assumed. Then G_{mu^boxplus kappa}(z) = G_mu(omega(z)) and the
density comes by Stieltjes inversion rho(x) = -(1/pi) Im G(x + i*eps), with an eps-doubling
stability check so bandwidth sensitivity cannot masquerade as density mismatch.

Flow-time reference: mu_s = D_{1-s}(mu^boxplus 1/(1-s)) — dilation by (1-s); exact on the
Hermite/semicircle family (radius sqrt(2n) -> sqrt(2n)*sqrt(1-s) = sqrt(2m)).

KNOWN-ANSWER GATES (this file's __main__; the evaluator gates nothing until both are green):
  S — semicircle: sc(sigma)^boxplus kappa = sc(sigma*sqrt(kappa)) exactly, every kappa (smooth input).
  B — symmetric Bernoulli (1/2)(d_{-1}+d_{+1}): free binomial, closed form derived via R-transform:
      G_kappa(z) = [-z(kappa-2) + kappa*sqrt(z^2 - 4(kappa-1))] / (2(z^2 - kappa^2)),
      a.c. density kappa*sqrt(4(kappa-1)-x^2) / (2*pi*(kappa^2-x^2)) on |x| < 2*sqrt(kappa-1),
      atoms at +-kappa of mass (1 - kappa/2) for kappa < 2 (atom of mass a survives iff
      a > 1 - 1/kappa = s; here a = 1/2 -> dissolves exactly at s = 1/2, i.e. kappa = 2, where
      the law is the arcsine law 1/(pi*sqrt(4-x^2)) — Bernoulli boxplus Bernoulli).
"""
import json
import numpy as np

# ---- declared constants (do not tune after seeing gate results) ----
SUB_TOL = 1e-13        # contraction residual target (absolute, in z-units of the problem)
SUB_MAX_ITER = 20000
EPS_GATE = 1e-6        # Stieltjes eps for closed-form gates (analytic G_mu, no atomic graininess)
SC_KAPPAS = [1.5, 2.0, 4.0, 8.0, 16.0]
BERN_KAPPAS = [1.2, 1.5, 1.9, 2.0, 3.0, 5.0]
DENS_TOL = 1e-4        # gate: max |rho_eval - rho_closed| on the interior grid (|x| <= 0.95 edge)
MASS_TOL = 1e-4        # gate: |trapz(rho_eval) - trapz(rho_closed)| on the SAME grid
EPS_DOUBLE_TOL = 1e-4  # gate: max |rho(eps) - rho(2 eps)| on the interior grid
ATOM_EPS = 1e-8        # pole-mass probe: a_est = eps * |Im G(atom + i*eps)|
ATOM_TOL = 1e-3
N_GRID = 400


def _sqrt_uhp(z, a):
    """sqrt(z^2 - a^2), branch analytic off [-a, a], ~ z at infinity."""
    return np.sqrt(z - a) * np.sqrt(z + a)


def F_semicircle(sigma):
    """F = 1/G for sc(sigma) (variance sigma^2, support [-2 sigma, 2 sigma])."""
    return lambda w: 0.5 * (w + _sqrt_uhp(w, 2.0 * sigma))


def F_bernoulli(w):
    """F = 1/G for (1/2)(d_{-1} + d_{+1}); G(w) = w/(w^2-1)."""
    return (w * w - 1.0) / w


def F_empirical(roots):
    r = np.asarray(roots, dtype=float)
    return lambda w: 1.0 / np.mean(1.0 / (w[:, None] - r[None, :]), axis=1)


def free_power_G(F_mu, z, kappa):
    """G_{mu^boxplus kappa}(z) for Im z > 0, with certified contraction residual."""
    z = np.asarray(z, dtype=complex)
    omega = z.copy()
    res = np.inf
    for it in range(SUB_MAX_ITER):
        omega_new = z / kappa + (1.0 - 1.0 / kappa) * F_mu(omega)
        res = float(np.max(np.abs(omega_new - omega)))
        omega = omega_new
        if res < SUB_TOL:
            break
    return 1.0 / F_mu(omega), res, it + 1


def density(F_mu, x, kappa, eps):
    G, res, iters = free_power_G(F_mu, x + 1j * eps, kappa)
    return -np.imag(G) / np.pi, res, iters


def flow_density(F_mu_seed, x, s, eps):
    """Density of mu_s = D_{1-s}(mu_seed^boxplus 1/(1-s)) at points x (Im-shift eps in seed units)."""
    c = 1.0 - s
    rho, res, iters = density(F_mu_seed, np.asarray(x) / c, 1.0 / c, eps)
    return rho / c, res, iters


# ---- closed forms for the gates ----
def rho_sc(x, sigma):
    v = 4.0 * sigma * sigma - x * x
    return np.where(v > 0, np.sqrt(np.maximum(v, 0.0)) / (2.0 * np.pi * sigma * sigma), 0.0)


def rho_bern_closed(x, kappa):
    v = 4.0 * (kappa - 1.0) - x * x
    return np.where(v > 0, kappa * np.sqrt(np.maximum(v, 0.0)) /
                    (2.0 * np.pi * (kappa * kappa - x * x)), 0.0)


def run_gates():
    report = {"constants": {k: v for k, v in [("SUB_TOL", SUB_TOL), ("EPS_GATE", EPS_GATE),
              ("DENS_TOL", DENS_TOL), ("MASS_TOL", MASS_TOL), ("EPS_DOUBLE_TOL", EPS_DOUBLE_TOL),
              ("ATOM_EPS", ATOM_EPS), ("ATOM_TOL", ATOM_TOL), ("N_GRID", N_GRID)]},
              "semicircle": [], "bernoulli": [], "atoms": [], "verdict": "PASS"}

    def fail(msg):
        report["verdict"] = "FAIL"
        report.setdefault("failures", []).append(msg)

    F_sc = F_semicircle(1.0)
    for kappa in SC_KAPPAS:
        edge = 2.0 * np.sqrt(kappa)
        x = np.linspace(-0.95 * edge, 0.95 * edge, N_GRID)
        rho1, res, iters = density(F_sc, x, kappa, EPS_GATE)
        rho2, _, _ = density(F_sc, x, kappa, 2.0 * EPS_GATE)
        ref = rho_sc(x, np.sqrt(kappa))
        dev = float(np.max(np.abs(rho1 - ref)))
        mdev = float(abs(np.trapezoid(rho1, x) - np.trapezoid(ref, x)))
        edev = float(np.max(np.abs(rho1 - rho2)))
        report["semicircle"].append({"kappa": kappa, "max_dens_dev": dev, "mass_dev": mdev,
                                     "eps_double_dev": edev, "sub_residual": res, "iters": iters})
        if dev > DENS_TOL: fail(f"sc kappa={kappa} dens dev {dev:.3g}")
        if mdev > MASS_TOL: fail(f"sc kappa={kappa} mass dev {mdev:.3g}")
        if edev > EPS_DOUBLE_TOL: fail(f"sc kappa={kappa} eps-doubling {edev:.3g}")

    for kappa in BERN_KAPPAS:
        edge = 2.0 * np.sqrt(kappa - 1.0)
        x = np.linspace(-0.95 * edge, 0.95 * edge, N_GRID)
        rho1, res, iters = density(F_bernoulli, x, kappa, EPS_GATE)
        rho2, _, _ = density(F_bernoulli, x, kappa, 2.0 * EPS_GATE)
        ref = rho_bern_closed(x, kappa)
        dev = float(np.max(np.abs(rho1 - ref)))
        mdev = float(abs(np.trapezoid(rho1, x) - np.trapezoid(ref, x)))
        edev = float(np.max(np.abs(rho1 - rho2)))
        report["bernoulli"].append({"kappa": kappa, "max_dens_dev": dev, "mass_dev": mdev,
                                    "eps_double_dev": edev, "sub_residual": res, "iters": iters})
        if dev > DENS_TOL: fail(f"bern kappa={kappa} dens dev {dev:.3g}")
        if mdev > MASS_TOL: fail(f"bern kappa={kappa} mass dev {mdev:.3g}")
        if edev > EPS_DOUBLE_TOL: fail(f"bern kappa={kappa} eps-doubling {edev:.3g}")

    # atom-threshold checks: mass predicted to the digit at kappa=1.5 (0.25), absent at kappa=3.
    for kappa, want in [(1.5, 0.25), (3.0, 0.0)]:
        G, res, _ = free_power_G(F_bernoulli, np.array([kappa + 1j * ATOM_EPS]), kappa)
        a_est = float(ATOM_EPS * abs(np.imag(G[0])))
        report["atoms"].append({"kappa": kappa, "atom_mass_est": a_est, "predicted": want,
                                "sub_residual": res})
        if abs(a_est - want) > ATOM_TOL:
            fail(f"atom kappa={kappa}: est {a_est:.5f} vs predicted {want}")

    with open("derivflow/freeconv_gates.json", "w") as f:
        json.dump(report, f, indent=1)
    print(f"VERDICT: {report['verdict']}")
    for name in ("semicircle", "bernoulli"):
        w = report[name]
        print(f"{name}: worst dens dev {max(r['max_dens_dev'] for r in w):.3g}, "
              f"worst mass dev {max(r['mass_dev'] for r in w):.3g}, "
              f"worst eps-double {max(r['eps_double_dev'] for r in w):.3g}, "
              f"worst sub residual {max(r['sub_residual'] for r in w):.3g}, "
              f"max iters {max(r['iters'] for r in w)}")
    for a in report["atoms"]:
        print(f"atom kappa={a['kappa']}: mass est {a['atom_mass_est']:.6f} (predicted {a['predicted']})")
    if report["verdict"] != "PASS":
        for m in report.get("failures", []):
            print("  FAIL:", m)
    return report["verdict"]


if __name__ == "__main__":
    import sys
    sys.exit(0 if run_gates() == "PASS" else 1)
