"""Phase 1 RF-engine wiring (D4, P7): the RF engine's `peak_q` wired into the family pipeline, committed BEFORE any family
statistic is computed (closes audit/04 #1 honestly: wiring first, then a sealed null, then the read).

Sealed null (D4): peak_q shows no family dependence beyond the calibrated RMT band; PASS iff every pairwise family
difference stays within its band.

Pipeline (P7, thirty-second round):
  member      peak_q of the member's scaled zeros in (0, 8] (positive side; scaled x = γ log c / 2π), computed by the
              engine as is: arithmetic_toolkit.ramanujan_fourier(x, q_max=200, normalize=True). Members with fewer than
              MIN_ZEROS such zeros are excluded and counted.
  family      the distribution of peak_q over its members (a histogram on q = 2 … 200).
  difference  total-variation distance between two families' distributions.
  band        the same pipeline on random-matrix draws of each family's type, each member's draw truncated to the
              same number of low zeros as the member; per-pair thresholds at a common per-pair quantile chosen so that
              the FAMILY-WISE false-fail rate over the pairs is 5%, calibrated empirically on the draws.
The draw size per member is an input (`n_draw`). P8 (thirty-third round, hybrid): the peak_q bands use a size covering
the full data window (scaled height 8), not the member-matched size, which does not reach it.
P9 (thirty-third round): bands from >= BAND_REPS_MIN repeats; a hold-out of >= HOLDOUT_REPS_MIN fresh repeats must give a
family-wise rate inside HOLDOUT_RANGE (`holdout_check`).

Random-matrix types (Haar, by Gram–Schmidt of Gaussian columns, so left-invariant):
  U(N)       eigenangles θ ∈ (−π, π]; scaled x = θ N / 2π; positive side x > 0.
  USp(2N)    columns in pairs (v, J v̄); eigenangles in conjugate pairs; scaled x = θ N / π on θ ∈ (0, π].
  SO(2N)     Haar O(2N) with a fixed reflection applied when det = −1; scaled x = θ N / π.
  SO(2N+1)   likewise; the forced eigenvalue 1 is dropped (non-central, as P2); scaled x = θ (N + ½) / π.

  python rfwire.py selftest          (small draws only; no zero of any family is read)
"""
import itertools
import os
import sys

import numpy as np

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
sys.path.insert(0, ROOT)
from arithmetic_toolkit import ramanujan_fourier  # noqa: E402

Q_MAX = 200
MIN_ZEROS = 6
X_MAX = 8.0
FWER = 0.05
BAND_REPS_MIN = 1000
HOLDOUT_REPS_MIN = 2000
HOLDOUT_RANGE = (0.035, 0.065)


# ---------------------------------------------------------------- member and family statistics
def member_peak_q(x):
    """peak_q of scaled positive zeros in (0, X_MAX], or None if fewer than MIN_ZEROS."""
    x = np.sort(np.asarray(x, dtype=float))
    x = x[(x > 0) & (x <= X_MAX)]
    if x.size < MIN_ZEROS:
        return None
    return int(ramanujan_fourier(x, q_max=Q_MAX, normalize=True)["peak_q"])


_CT = None


def _ctable(nmax=256):
    """c_q(n)/φ(q) for q = 1…Q_MAX, n = 1…nmax, from the engine's own ramanujan_sum_array and _phi."""
    global _CT
    if _CT is None or _CT.shape[1] < nmax:
        from arithmetic_toolkit import _phi, ramanujan_sum_array
        _CT = np.array([ramanujan_sum_array(q, nmax) / _phi(q) for q in range(1, Q_MAX + 1)])
    return _CT


def fast_peak_q(x):
    """The engine's peak_q by one matrix product (same c_q(n), same normalisation, same argsort ranking). Equality
    with member_peak_q is CHECKED in selftest; the calibration and the read use whichever the seal names."""
    x = np.sort(np.asarray(x, dtype=float))
    x = x[(x > 0) & (x <= X_MAX)]
    if x.size < MIN_ZEROS:
        return None
    iv = np.diff(x)
    iv = iv[iv > 0]
    if iv.size < 5:
        return None
    f = iv / iv.mean()
    a = _ctable(max(256, f.size))[:, :f.size] @ f / f.size
    return int(np.argsort(np.abs(a)[1:])[::-1][0] + 2)


def family_distribution(members, fast=True):
    """members: iterable of scaled-zero arrays → (histogram over q = 2…Q_MAX, n_used, n_excluded)."""
    qs = [(fast_peak_q if fast else member_peak_q)(x) for x in members]
    used = [q for q in qs if q is not None]
    h = np.bincount(np.asarray(used, dtype=int), minlength=Q_MAX + 1)[2:].astype(float)
    return (h / h.sum() if h.sum() else h), len(used), len(qs) - len(used)


def tv(h1, h2):
    return 0.5 * float(np.abs(h1 - h2).sum())


def pairwise_tv(hists):
    names = sorted(hists)
    return {(a, b): tv(hists[a], hists[b]) for a, b in itertools.combinations(names, 2)}


# ---------------------------------------------------------------- Haar random matrices
def _gs_unitary(rng, n):
    z = (rng.standard_normal((n, n)) + 1j * rng.standard_normal((n, n))) / np.sqrt(2)
    q, r = np.linalg.qr(z)
    return q * (np.diag(r) / np.abs(np.diag(r)))


def _haar_orthogonal(rng, n):
    q, r = np.linalg.qr(rng.standard_normal((n, n)))
    q = q * np.sign(np.diag(r))
    if np.linalg.det(q) < 0:                       # O⁻ → SO by a fixed reflection (measure-preserving)
        q[:, 0] = -q[:, 0]
    return q


def _haar_symplectic(rng, n):
    """USp(2n) = {S unitary, SᵀJS = J}, J = [[0, I], [−I, 0]]: Gram–Schmidt on Gaussian vectors v_k, each orthogonalised
    against all earlier v's and their partners w = −J v̄; S = [v_1 … v_n | w_1 … w_n]. The law is left-invariant under
    USp(2n), hence Haar."""
    m = 2 * n
    J = np.block([[np.zeros((n, n)), np.eye(n)], [-np.eye(n), np.zeros((n, n))]])
    V, W = [], []
    for _ in range(n):
        v = (rng.standard_normal(m) + 1j * rng.standard_normal(m)) / np.sqrt(2)
        for c in V + W:
            v = v - (c.conj() @ v) * c
        v = v / np.linalg.norm(v)
        V.append(v)
        W.append(-J @ v.conj())
    return np.array(V + W).T


def draw_scaled(rng, kind, n):
    """Positive-side scaled eigenangles (sorted) of one Haar draw of the given type and size parameter n."""
    if kind == "U":
        th = np.angle(np.linalg.eigvals(_gs_unitary(rng, n)))
        x = th * n / (2 * np.pi)
    elif kind == "USp":
        th = np.angle(np.linalg.eigvals(_haar_symplectic(rng, n)))
        x = th[th > 0] * n / np.pi
    elif kind == "SO_even":
        th = np.angle(np.linalg.eigvals(_haar_orthogonal(rng, 2 * n)))
        x = th[th > 0] * n / np.pi
    elif kind == "SO_odd":
        th = np.angle(np.linalg.eigvals(_haar_orthogonal(rng, 2 * n + 1)))
        x = th[th > 1e-9] * (n + 0.5) / np.pi
    else:
        raise ValueError(kind)
    return np.sort(x[x > 0])


# ---------------------------------------------------------------- band calibration (family-wise)
def rmt_family(rng, kind, templates):
    """templates: list of (n_draw, n_low) per member → list of scaled-zero arrays truncated to n_low."""
    return [draw_scaled(rng, kind, nd)[:nl] for nd, nl in templates]


def calibrate_bands(rng, families, reps):
    """families: {name: (kind, templates)}. Returns per-pair thresholds with family-wise false-fail = FWER, the
    per-pair quantile level, and the replicate TV table."""
    names = sorted(families)
    pairs = list(itertools.combinations(names, 2))
    table = np.zeros((reps, len(pairs)))
    for r in range(reps):
        hists = {k: family_distribution(rmt_family(rng, *families[k]))[0] for k in names}
        d = pairwise_tv(hists)
        table[r] = [d[p] for p in pairs]
    # common per-pair upper-tail level a; thresholds are order statistics (method "higher"), exceedance is strict,
    # so FWER(a) is a monotone step function of a and the bisection lands on the largest a with FWER(a) ≤ 5%
    lo, hi = 0.0, FWER
    for _ in range(60):
        a = 0.5 * (lo + hi)
        thr = np.quantile(table, 1 - a, axis=0, method="higher")
        if np.mean((table > thr).any(axis=1)) > FWER:
            hi = a
        else:
            lo = a
    thr = np.quantile(table, 1 - lo, axis=0, method="higher")
    return dict(pairs=pairs, thresholds=thr, per_pair_level=lo,
                fwer_achieved=float(np.mean((table > thr).any(axis=1))), table=table)


def fwer_on(table, thresholds):
    return float(np.mean((table > thresholds).any(axis=1)))


def holdout_check(rng, families, bands, reps=HOLDOUT_REPS_MIN):
    """P9: the family-wise false-fail rate of `bands` on fresh replicates. Raises (fails closed) if the bands came from
    fewer than BAND_REPS_MIN repeats or the hold-out is smaller than HOLDOUT_REPS_MIN; returns (rate, ok)."""
    if bands["table"].shape[0] < BAND_REPS_MIN:
        raise ValueError(f"bands from {bands['table'].shape[0]} repeats < BAND_REPS_MIN = {BAND_REPS_MIN}")
    if reps < HOLDOUT_REPS_MIN:
        raise ValueError(f"hold-out of {reps} repeats < HOLDOUT_REPS_MIN = {HOLDOUT_REPS_MIN}")
    rate = fwer_on(calibrate_bands(rng, families, reps)["table"], bands["thresholds"])
    return rate, HOLDOUT_RANGE[0] <= rate <= HOLDOUT_RANGE[1]


def verdict(observed, bands):
    """observed: {(a, b): TV}. PASS iff every pair is within its band."""
    out = {p: (observed[p], float(t), observed[p] <= t) for p, t in zip(bands["pairs"], bands["thresholds"])}
    return ("PASS" if all(v[2] for v in out.values()) else "FAIL"), out


# ---------------------------------------------------------------- self-test (no family data)
def selftest():
    rng = np.random.default_rng(1)
    # Haar checks: unitarity, symplecticity, orthogonality with det +1
    U = _gs_unitary(rng, 6)
    S = _haar_symplectic(rng, 4)
    J = np.block([[np.zeros((4, 4)), np.eye(4)], [-np.eye(4), np.zeros((4, 4))]])
    O = _haar_orthogonal(rng, 9)
    assert np.allclose(U.conj().T @ U, np.eye(6))
    assert np.allclose(S.conj().T @ S, np.eye(8)) and np.allclose(S.T @ J @ S, J)
    assert np.allclose(O.T @ O, np.eye(9)) and np.isclose(np.linalg.det(O), 1)
    # one-level density sanity: USp repels from 0, SO(even) attracts (mean lowest scaled angle, N = 8, 4000 draws)
    m = {k: np.mean([draw_scaled(rng, k, 8)[0] for _ in range(4000)]) for k in ("USp", "SO_even", "U")}
    print("mean lowest scaled angle, N = 8:", {k: round(v, 3) for k, v in m.items()})
    assert m["SO_even"] < m["U"] < m["USp"]
    # fast path = engine, member by member, on draws of every type and on members with 6 … 12 zeros
    mism, n = 0, 0
    for k in ("U", "USp", "SO_even", "SO_odd"):
        for _ in range(1500):
            x = draw_scaled(rng, k, 16 if k == "U" else 8)[: rng.integers(6, 13)]
            mism += fast_peak_q(x) != member_peak_q(x)
            n += 1
    print(f"fast path vs engine: {mism} mismatches in {n} members")
    assert mism == 0
    # band calibration on a toy family set: identical types must PASS against their own bands at about the FWER rate
    fam = {k: ("U", [(16, 7)] * 60) for k in ("A", "B", "C", "D")}
    bands = calibrate_bands(rng, fam, 200)
    fresh = calibrate_bands(rng, fam, 400)["table"]                 # replicates the bands were not set on
    print("toy bands (200 reps): per-pair level %.4f, family-wise %.3f in-sample, %.3f on 400 fresh reps"
          % (bands["per_pair_level"], bands["fwer_achieved"], fwer_on(fresh, bands["thresholds"])))
    obs = pairwise_tv({k: family_distribution(rmt_family(rng, *fam[k]))[0] for k in fam})
    print("toy verdict (same type everywhere):", verdict(obs, bands)[0])
    # red path: a family whose spacings are a rigid picket fence must leave the band
    fam_red = dict(fam)
    picket = [np.arange(1, 8) * 1.0 + 0.05 for _ in range(60)]
    obs_red = pairwise_tv({**{k: family_distribution(rmt_family(rng, *fam[k]))[0] for k in "ABC"},
                           "D": family_distribution(picket)[0]})
    print("red path (picket-fence family D):", verdict(obs_red, bands)[0])
    # P9 guard fails closed on under-sized bands (the 200-rep toy bands above must be refused)
    try:
        holdout_check(rng, fam, bands)
        raise AssertionError("holdout_check accepted 200-repeat bands")
    except ValueError as e:
        print("holdout_check refuses toy bands:", e)
    print("selftest done")


if __name__ == "__main__":
    if sys.argv[1:] == ["selftest"]:
        selftest()
