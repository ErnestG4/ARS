"""Does brocot's rho(rank, Brody q) = -0.91 survive its own error bars?
COMMITTED GENERATOR of cross_substrate/brocot_within_class.json.

THE EXACT-QUESTION CHECK, run before paying for anything bigger.  The banked
brocot claim is CORRELATIONAL -- "Brody q falls with approximability,
rho(rank, q) = -0.91 across 9 Lagrange classes".  The admissibility bar that
declared those rows underpowered (n >= 2000) comes from the GUE-vs-GOE
DISCRIMINATION gate, which assigns a universality class to a SINGLE row.  A
correlation across classes does not obviously need that gate at all.  So the
question is not "can we reach n=2000" but "what would actually falsify the
correlation", and that turns out to be two things the original never measured:

  (1) WITHIN-CLASS SPREAD.  A Lagrange class is an equivalence class containing
      infinitely many alpha; the banked run used EXACTLY ONE representative per
      class and therefore has no error bar.  If within-class spread is
      comparable to between-class spread, rho is not supported at any n.
      Representatives are generated exactly: prepending continued-fraction
      terms leaves the CF TAIL unchanged, so the Lagrange class is preserved
      by construction (GL2(Z)-equivalence), while the value moves a lot.

  (2) THE X-AXIS.  rho is computed against `rank = np.arange(9)`, the position
      in a hardcoded list, annotated "already ~approximability-ordered".  But
      SIX of the nine classes have IDENTICAL irrationality measure mu = 2.0
      (golden, silver, bronze, metallic4, metallic5, e_minus_2).  Their order
      in the list comes from max CF quotient (1,2,3,4,5,99), a different and
      finer notion than mu.  So the deployed x-axis silently splices two
      orderings and imposes a strict order on six tied points.  We recompute
      rho against each candidate x separately and report all of them.

PREDICTION, COMMITTED BEFORE THE RUN: within-class spread will be NON-TRIVIAL
(the value of alpha changes the sideband lattice even at fixed tail), and rho
against mu alone will be much weaker than -0.91 because six of nine points tie.
The interesting outcome is whether an ordering survives ANY honest x-axis.
"""
import json, os, sys
import numpy as np

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_HERE)
for p in (os.path.expandvars("$HOME/fmexplorer/brocot"), _ROOT):
    if p not in sys.path:
        sys.path.insert(0, p)
from phase3.partial_prediction import predict_partials          # noqa: E402
from cross_substrate.axes import canonical_spacings, I8_brody_q  # noqa: E402
from scipy import stats                                          # noqa: E402

DEPTH, F_CARRIER, N_REPS = 8.0, 220.0, 12
# (name, alpha, mu, max CF quotient) -- verbatim from brocot_approximability.CLASSES
CLASSES = [
    ("golden",     (np.sqrt(5) - 1) / 2,  2.0, 1),
    ("silver",     np.sqrt(2) - 1,        2.0, 2),
    ("bronze",     (np.sqrt(13) - 3) / 2, 2.0, 3),
    ("metallic4",  np.sqrt(5) - 2,        2.0, 4),
    ("metallic5",  (np.sqrt(29) - 5) / 2, 2.0, 5),
    ("e_minus_2",  np.e - 2,              2.0, 99),
    ("ln2",        np.log(2),             3.57, 99),
    ("pi_minus_3", np.pi - 3,             7.10, 99),
    ("liouville",  sum(10.0 ** -e for e in (1, 2, 6, 24, 120, 720)), 1e9, 99),
]


def prepend_cf(alpha, prefix):
    """Number whose CF is [0; prefix..., (alpha's expansion)]. Same TAIL, hence
    the same Lagrange class, by construction rather than by assertion."""
    x = float(alpha)
    for p in reversed(prefix):
        x = 1.0 / (p + x)
    return x


def q_of(alpha):
    sp = predict_partials([1.0, float(alpha)], [DEPTH, DEPTH], f_carrier=F_CARRIER)
    if sp.freqs.size < 20:
        return None, int(sp.freqs.size)
    return I8_brody_q(canonical_spacings(np.sort(sp.freqs))), int(sp.freqs.size)


def main():
    rng = np.random.default_rng(20260819)
    out = {"depth": DEPTH, "n_reps": N_REPS, "prediction": (
        "within-class spread NON-TRIVIAL; rho vs mu much weaker than -0.91 "
        "because six of nine classes tie at mu=2.0"), "classes": {}}
    print(f"{'class':12s} {'mu':>6s} {'q(banked rep)':>14s} {'q mean+-sd (12 reps)':>24s} {'n range':>12s}")
    for name, alpha, mu, maxq in CLASSES:
        q0, n0 = q_of(alpha)
        qs, ns = [], []
        for _ in range(N_REPS):
            pref = [int(v) for v in rng.integers(1, 6, size=int(rng.integers(1, 4)))]
            q, n = q_of(prepend_cf(alpha, pref))
            if q is not None:
                qs.append(q); ns.append(n)
        qs = np.asarray(qs, float)
        out["classes"][name] = dict(mu=mu, max_cf_quotient=maxq,
                                    q_banked_representative=q0, n_banked=n0,
                                    q_reps=qs.tolist(), n_reps_partials=ns,
                                    q_mean=float(qs.mean()), q_sd=float(qs.std(ddof=1)))
        print(f"{name:12s} {('inf' if mu>1e8 else f'{mu:.2f}'):>6s} {q0:>14.3f} "
              f"{qs.mean():>13.3f} +- {qs.std(ddof=1):<8.3f} {min(ns):>5d}-{max(ns):<5d}", flush=True)

    names = [c[0] for c in CLASSES]
    q_banked = np.array([out["classes"][n]["q_banked_representative"] for n in names])
    q_mean = np.array([out["classes"][n]["q_mean"] for n in names])
    sds = np.array([out["classes"][n]["q_sd"] for n in names])
    within = float(np.sqrt(np.mean(sds ** 2)))
    between = float(np.std(q_mean, ddof=1))
    xs = {"assumed_rank_0_to_8": np.arange(len(names), dtype=float),
          "irrationality_measure_mu": np.array([out["classes"][n]["mu"] for n in names]),
          "max_cf_quotient": np.array([out["classes"][n]["max_cf_quotient"] for n in names], float)}
    out["spread"] = dict(within_class_rms_sd=within, between_class_sd=between,
                         ratio_within_over_between=within / between)
    out["rho"] = {}
    print(f"\nwithin-class RMS sd = {within:.4f}   between-class sd = {between:.4f}"
          f"   ratio = {within/between:.2f}")
    print("\nrho(x, Brody q) -- deployed uses the FIRST row only:")
    for xn, xv in xs.items():
        r_b = float(stats.spearmanr(xv, q_banked)[0])
        r_m = float(stats.spearmanr(xv, q_mean)[0])
        # class-level CI: resample each class's q from its own representatives
        boots = []
        for _ in range(2000):
            qb = [rng.choice(out["classes"][n]["q_reps"]) for n in names]
            boots.append(stats.spearmanr(xv, qb)[0])
        lo, hi = np.percentile(boots, [2.5, 97.5])
        n_tied = int(len(xv) - len(set(xv.tolist())))
        out["rho"][xn] = dict(rho_banked_rep=r_b, rho_class_mean=r_m,
                              ci95=[float(lo), float(hi)], n_tied_points=n_tied)
        print(f"  {xn:26s} banked-rep {r_b:+.3f}   class-mean {r_m:+.3f}   "
              f"95% CI [{lo:+.3f}, {hi:+.3f}]   ties={n_tied}")
    json.dump(out, open(f"{_HERE}/brocot_within_class.json", "w"), indent=1)


if __name__ == "__main__":
    main()
