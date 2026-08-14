"""Pre-step P1: true Ginibre eigenvalue point-process sampler + its own KAG.

The repo previously had NO Ginibre point process: phase34d/circular_sampler.py
uses a Ginibre matrix only as the QR intermediate for CUE (its output is CUE
phases).  This module is new code and carries its own known-answer gate.

Convention (load-bearing, per amended brief G-B1): the matrix is UNSCALED —
entries are standard complex normal (variance 1).  Its eigenvalues then fill a
disk of radius ≈ √N with intensity λ = 1/π, and the infinite-Ginibre pair
correlation is exactly  g(r) = 1 − exp(−r²)  in these units, with NO rescaling
step in between.  (At unit intensity it would be 1 − exp(−π r²).)

Central sub-window (mandatory; TOOLKIT.md §11.1 first customer): all analysis
uses |z| ≤ C_WINDOW·√N.  Disk-edge fluctuations have O(1) width, so C_WINDOW=0.8
leaves a ≥9-unit buffer at N=2048.
"""

import json
import sys
import numpy as np

C_WINDOW = 0.8   # central sub-window fraction of √N


def sample_ginibre(N, seed):
    """Eigenvalues of an N×N matrix of standard complex normals (UNSCALED).
    Returns complex eigenvalues; intensity 1/π inside the disk of radius √N."""
    rng = np.random.default_rng(seed)
    G = (rng.standard_normal((N, N)) + 1j * rng.standard_normal((N, N))) / np.sqrt(2.0)
    return np.linalg.eigvals(G)


def central_points(ev, N):
    """Central sub-window restriction (DIM=2 xy array) + window radius."""
    R = C_WINDOW * np.sqrt(N)
    z = ev[np.abs(ev) <= R]
    return np.column_stack([z.real, z.imag]), R


def kag(N=2048, seeds=(900, 901, 902), tol_intensity=0.05, tol_radius=5.0):
    """Sampler KAG (smoke-grade, sealed in prereg):
      (i)  intensity in the central sub-window within tol_intensity of 1/π;
      (ii) spectral radius within tol_radius of √N  (edge sits at √N + O(1)).
    The distribution-level gate on g(r) is G-B1 in the arc prereg, not here."""
    rows = []
    for s in seeds:
        ev = sample_ginibre(N, s)
        pts, R = central_points(ev, N)
        lam = len(pts) / (np.pi * R**2)
        rows.append(dict(seed=s,
                         lam=float(lam),
                         lam_relerr=float(abs(lam - 1/np.pi) * np.pi),
                         spec_radius=float(np.abs(ev).max()),
                         sqrtN=float(np.sqrt(N))))
    ok_i = all(r["lam_relerr"] <= tol_intensity for r in rows)
    ok_r = all(abs(r["spec_radius"] - r["sqrtN"]) <= tol_radius for r in rows)
    return dict(N=N, C_WINDOW=C_WINDOW, rows=rows,
                intensity_gate=bool(ok_i), radius_gate=bool(ok_r),
                PASS=bool(ok_i and ok_r))


if __name__ == "__main__":
    out = kag()
    with open(sys.path[0] + "/ginibre_kag_measured.json", "w") as f:
        json.dump(out, f, indent=1)
    print(json.dumps({k: out[k] for k in ("N", "intensity_gate", "radius_gate", "PASS")}))
    for r in out["rows"]:
        print(f"  seed {r['seed']}: lam={r['lam']:.4f} (1/pi={1/np.pi:.4f}, "
              f"relerr {r['lam_relerr']:.3f})  |z|max={r['spec_radius']:.1f} vs sqrtN={r['sqrtN']:.1f}")
