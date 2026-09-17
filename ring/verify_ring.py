"""Board row for ring/ — Stage 0 port + Stage 1 measure 1. Nonzero exit on any failure.

What green means here (AUDIT.md caveat, verbatim): the checkers pass, not that
the instrument measures what we claim. Specifically this row certifies:
  R0  the package imports with torch BLOCKED (guard is real, not a comment)
  R1  every declared detector constructs (negative set + confusable named);
      declared-only detectors are NOT certified and cannot be read as passed
  R2  the banked Stage 1 table exists, its instrument is sealed, and the eps=0
      row is at the floor: |lam1| < 1e-12, drift < 1e-9
  R3  the dial does what it must: lam1 strictly decreases with eps at T=2000
      once above the floor; the eps=0.1 row is CONVERGED and collapsed
  R4  STANDING INVARIANT, every row: two independent reads of the marginal
      mode (Jacobian lam1; dynamic relaxation rate) must agree wherever both
      are valid (converged fixed point), and every disagreement must be
      accounted for by non-convergence. It is the cheapest artifact detector
      in the arc: it caught the threshold-linear Jacobian (reads apart by
      ~1e12 at the floor) and the on-grid starts (the obvious initial
      condition that could not see pinning). A live witness is required: at
      least one converged row above the floor, so the invariant CAN fail.
  R5  the T-dependence is banked, not hidden: n_distinct differs between the
      two T rows at the same eps — a collapse threshold is not a substrate
      property until T is stated
  R6  the built detector is two-sided-correct on the banked rows and certifies;
      the nearest confusable is silent by a stated margin, not by luck. The
      tallies (2/2, 3/3) carry Clopper-Pearson intervals via boundary_rate and
      are printed as UNINFORMATIVE where they are — the margin on lam1 is the
      number doing the work, and the summary leads with it (#19: a tally is
      not a verdict).
  R7  plan hygiene: no 'verify ID' tags, no Zone.Identifier stray, v5 header
  R8  the eps*T CONTOUR (stage1_contour_measured.json), against the tolerances
      the generator declared BEFORE it ran: rows at the same product P agree
      across splits in the linear regime (drift) and the collapse regime
      (n_distinct); the fit drift = c*P has small residual. The declared check
      FAILS at P=200 -- the eps=1 split deforms the bump and collapses to one
      attractor -- and this row asserts that failure stays visible: it is the
      contour's domain boundary (perturbative pinning, bump undeformed), not a
      tolerance to loosen.
  R4b the found delta defect stays found: at eps=0.01/T=20000 the delta=0.05
      read is < 0.8 of lam1 while the delta=0.005 read agrees. A refactor that
      silently restores the old constant turns this row red.
  R9  MEASURE 2 (stage1_ph_measured.json, generator v2): the sealed predictions
      P1-P5 (RING_BRIEF.md, a975089 + pilot amendment) are SCORED, not
      re-fitted: each is recorded PASS / FAIL / INAPPLICABLE exactly as
      declared, and the row pins the scored outcome so a regression or a
      quiet re-scoring turns it red. The detector
      ph_topology_consistent_with_continuous_attractor is certified on its
      declared sets (A fires; D, A-jittered-above-tau_c, A-scrambled silent),
      with CP intervals printed. Three findings are pinned as findings:
      (i) subsetting q flips the verdict ONLY at the confusable E;
      (ii) the ISI scramble is under-powered on single-visit clouds (C keeps a
      loop in >= 1 seed) -- the surrogate's confound scope, recorded in the
      spec as a blind spot; (iii) tau_c(B) is one rung above tau_c(A)
      [SUPERSEDED by R10/S4: not replicated on the fine ladder; the pin on
      the coarse table stays so the record shows what was read].
  R10 COVERAGE TEST (stage1_coverage_measured.json): F1-F6b scored as sealed
      (RING_BRIEF.md c478fa0 + S2). Pins: tau_c on the fine ladder for every
      arm; omega*tau_c constant across a 4x speed range (F2); tau_c
      independent of rotations (F3) and of bump width (F4: H_cov PASS,
      H_motion FAIL); the scramble's power is visits-per-unit (F5); E2's
      jitter-grown loop is CONSTRUCTED (b1 >> base) -- order-to-topology
      conversion, not SNR; r12 degenerates (b2 -> 0) on smoothed clouds and
      is declared unusable there.
  R11 STAGE 2 (stage2_nonnormal_measured.json, generator v3): theorem rails on
      a linear circulant (Henrici < 1e-10, gap < 1e-10, G_max = 1, K = 1) --
      red rail = instrument defect; every read row is at a converged fixed
      point (or a co-moving traveling wave with zero-mode residual < 1e-2);
      instrument-limited rows are banked and NOT read. Sealed hypotheses
      (RING_BRIEF.md aacad2f) scored: H_plan (asymmetry creates non-normality,
      first order, large) vs H_gain (gain profile sets it; asymmetry second
      order, small); H_struct/H_comparable/H_inv on matched-norm random vs
      circulant; H_pin vs H_plan on G_max(eps). Pins the headline: the
      SYMMETRIC attractor's linearisation is non-normal (H0 ~ 2.09, gap ~ 0.18,
      G0 = kappa0 = K0 ~ 1.36) and nothing in the sweep moves Henrici by > 0.2%
      on a read row.
  R12 STAGE 3a (stage3_lift_measured.json): path-lift arms L1-L4 scored as
      sealed (RING_BRIEF.md 620e975 + pre-seal amendment). READABLE means
      DREiMac's standard-range class existed; the nonstandard-range fallback
      is a demonstration that a fallback launders a null (it emits counts,
      and they are wrong) and is never read as a value. Pins: |n| exact on
      every readable A row; the smallest readable rho per bin (a censored
      edge, rail class (i)); IND reads identically to A (the kinematic
      ceiling); the per-step continuity statistic is defeated on C_perm; L4's
      transverse-relaxation ratio is ~1 (instrument, per the rate-level probe
      recorded in the brief).
  R13 STAGE 3b (stage3b_recurrence_measured.json): L4b sealed-to-fail scored;
      I1 along-manifold kick -- the continuous attractor RETAINS the phase
      offset (3/3), IND_u RESTORES it (3/3); the driven pinned ring did not
      restore (retention 0.88 vs sealed < 0.1) because drive >> pinning, so
      that negative is re-posed trapped (I1b). T1 traversal statistic: R
      separates C_perm (> 3) from A/IND (1.00); C_ord reads 2.06 (a stepwise
      traversal fails the < 1.5 clause: R - 1 ~ noise-TV/net) -- pinned as the
      statistic's known false-negative channel. The traversal detector is
      certified on its DECLARED sets with that caveat printed.
  R13b I1b (stage3c_trapped_measured.json): the TRAPPED discrete attractor
      restores (eps=0.1, gamma=0: retention 0.02) and the sliding one retains
      (gamma=0.02: 0.72); depinning crossing pinned as an INTERVAL (0.01,
      0.02] (B-sup); monotonicity in gamma FAILED (well-dependent restoring
      rate) and eps=0.03 is INAPPLICABLE at T_obs=300 -- both recorded, not
      re-scoped.
  R13c I1c (stage3d_trapped_long_measured.json): eps=0.03 at T_obs=3000 --
      the retention crossing straddles Stage 4b's tongue edge (0.001 trapped,
      0.003 sliding); R(0) = 0.37 fails the < 0.1 clause (this well's
      restoring rate is 3.3e-4, 10x below the Stage 1 median); retention > 1
      above threshold is recorded: the statistic is bounded only for trapped
      systems.
  R16 attractor_by_along_manifold_memory (intervention class) certified on
      the banked I1 (stage3b) and I1b (stage3c) rows: positive ring eps=0
      fires 3/3; negatives IND_u (3/3) and trapped pinned ring silent.
      Separate from the observational ladder by design.
  R17 STAGE 3e MSD (stage3e_msd_measured.json): the passive dual of the kick.
      Sealed clauses scored per row; the three systems separate IN KIND
      (continuum slope ~1, trapped saturating, IND_u flat) in every row, but
      the trapped clauses sealed against the LINEAR lambda1 fail by a common
      factor ~0.3 -- the anharmonic-well ratio the delta sweep measured at
      0.1 rad. The observational implies rung is NOT certified at sealed
      precision; nor is "unreachable observationally" banked, because the
      zero mode's integration of endogenous noise IS a passive signature.
  R13d T2/T3 (stage3f_traversal2_measured.json, stage3g_traversal3_measured.json):
      T2 failed as sealed (uncentered MAD under drift; M polluted by noise
      steps). T3 (centered MAD; M on jump steps only): the monotone clause M
      separates C_perm (<0.6) from A/IND (0.78-0.95) from C_ord (>0.99), and
      J separates smooth (<50) from stepwise (>100); the sealed NUMERIC
      thresholds fail (A/IND J <= 10: 1/6; C_ord J in [10,40]: 0/3 because
      the kernel SUPPORT is 4 sigma = 8 bins, not 2). Pinned as the ordering;
      thresholds are handed to a negative-set calibration, not a fourth seal.
  R14 STAGE 4 (stage4_circlemap_measured.json): theorem rails -- Denjoy
      convergence for K<1, exact 0/1 tongue boundary K/2pi within one grid
      step, Farey coverage at K=0 within 25%, multistability = 0 for K<=1,
      hysteresis discrepancy D(K) <= one grid step for K<1 (the dead region);
      sealed M2 monotonicity scored; the K=1 staircase test is recorded
      INAPPLICABLE AS POSED because rigid rotation (K=0) passes it too
      (rival rule on the arc's own sealed test).
  R14b M2b/M2c (stage4c_staircase_measured.json, stage4d_staircase_random_
      measured.json): the staircase test re-posed at tol 1e-5 separates K=1
      from K=0 by > 0.3 on both grids; on the RATIONAL grid j/1001 the K=0
      coverage is exactly the 29 grid points that are Farey fractions
      (B-grid rail, pinned); with random Omega the K=0 coverage matches the
      Lebesgue/Farey estimate within 30% and the sealed test PASSES.
  R15 STAGE 4b (stage4b_ringtongue_measured.json): the pinned ring's 0/1
      tongue with gamma* PREDICTED from the measured maximal pinning velocity
      at gamma=0 and tested against the I1b interval (0.01, 0.02] and the
      fine-grid rho(gamma); eps=0 rail rho = 1; eps-scaling of gamma*.
"""
import os
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")

import json
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
sys.path.insert(0, REPO)
PY = sys.executable
fails = []


def chk(c, m):
    if not c:
        fails.append(m)


# R0 — torch guard is real
r = subprocess.run([PY, "-c",
                    "import sys; sys.modules['torch']=None; "
                    "import ring, ring.ringnet, ring.detectors; "
                    "assert ring.HAVE_TORCH is False; print('guard ok')"],
                   cwd=REPO, capture_output=True, text=True)
chk(r.returncode == 0 and "guard ok" in r.stdout,
    f"R0 torch guard: package failed to import with torch blocked: {r.stderr[-300:]}")

# R1 — detectors construct; declared-only are not certified
from ring import detectors as D                                      # noqa: E402
from detector_spec import DetectorNotCertified                       # noqa: E402
for name, mk in {**D.BUILT, **D.DECLARED_ONLY}.items():
    try:
        s = mk()
        chk(s.name == name, f"R1 {name}: spec name mismatch {s.name}")
    except Exception as e:                                           # noqa: BLE001
        chk(False, f"R1 {name}: spec failed to construct: {e}")
for name, mk in D.DECLARED_ONLY.items():
    try:
        mk().certify()
        chk(False, f"R1 {name}: DECLARED-ONLY detector certified with no "
                   "recorded outcomes — that is the laundering this row exists to stop")
    except DetectorNotCertified:
        pass

# R2 — banked table, sealed instrument, floor
path = os.path.join(HERE, "stage1_marginal_measured.json")
chk(os.path.exists(path), "R2 stage1_marginal_measured.json missing — run stage1_marginal.py")
if not os.path.exists(path):
    print("\n".join(fails)); sys.exit(1)
M = json.load(open(path))
inst = M["instrument"]
chk(inst["n_tested"] == 3 and inst["n_declared"] >= 8,
    f"R2 instrument seal shape changed: {inst['n_tested']} tested / {inst['n_declared']} declared")
rows = [x for x in M["rows"] if x["control"] == "bump"]
ctrl = [x for x in M["rows"] if x["control"] != "bump"]
T_long = max(x["T"] for x in rows)
T_short = min(x["T"] for x in rows)
chk(T_long > T_short, "R2 only one T banked")


def row(T, eps):
    m = [x for x in rows if x["T"] == T and abs(x["eps"] - eps) < 1e-12]
    return m[0] if m else None


for T in (T_short, T_long):
    z = row(T, 0.0)
    chk(z is not None, f"R2 eps=0 row missing at T={T}")
    if z:
        chk(abs(z["lam1_median"]) < 1e-12, f"R2 floor: |lam1| at eps=0,T={T} = {z['lam1_median']:.2e}")
        chk(z["drift_median"] < 1e-9, f"R2 floor: drift at eps=0,T={T} = {z['drift_median']:.2e}")
        chk(z["resid_max"] < 1e-10, f"R2 floor: eps=0 not a fixed point, resid {z['resid_max']:.1e}")
        chk(z["bump_amp_median"] > D.AMP_MIN, f"R2 no bump at eps=0,T={T}")
        chk(z["lam2_median"] < -0.3, f"R2 transverse mode not stable: lam2={z['lam2_median']:.3f}")

# R3 — dial monotone above floor; last row converged and collapsed
long_rows = sorted([x for x in rows if x["T"] == T_long], key=lambda x: x["eps"])
lam = [x["lam1_median"] for x in long_rows if x["eps"] > 0]
chk(all(b < a for a, b in zip(lam, lam[1:])),
    f"R3 lam1 not strictly decreasing with eps at T={T_long}: {['%.2e' % v for v in lam]}")
last = long_rows[-1]
chk(last["resid_max"] < 1e-8, f"R3 eps={last['eps']} row not converged: resid {last['resid_max']:.1e}")
chk(last["n_distinct"] <= last["B"] // 2,
    f"R3 no collapse at eps={last['eps']}: n_distinct={last['n_distinct']} of B={last['B']}")
chk(last["lam1_median"] < -1e-3, f"R3 pinned row lam1 too close to zero: {last['lam1_median']:.2e}")

# R8 input (loaded here because R4 runs over both tables)
cpath = os.path.join(HERE, "stage1_contour_measured.json")
chk(os.path.exists(cpath), "R8 stage1_contour_measured.json missing — run stage1_contour.py")
C = json.load(open(cpath)) if os.path.exists(cpath) else dict(rows=[], tolerances={}, fit={})
crows = C["rows"]

# R4 — STANDING INVARIANT on every bump row OF BOTH TABLES: spectral vs dynamic read
CONVERGED = 1e-8      # resid_max below this: a fixed point, both reads valid
AGREE = 0.2           # relative tolerance where both are valid and above floor
# The FLOOR of each read is MEASURED on the eps=0 rows, not assumed: the
# dynamic read's floor scales ~1/delta (resampling error on the bump shape
# enters the log-ratio), so it is ~6e-6 at delta=0.005 where it was ~1e-7 at
# 0.05. A declared CEILING keeps "measured floor" from becoming "whatever it is".
FLOOR_CEILING = 1e-4
_z = [row(T_short, 0.0), row(T_long, 0.0)]
FLOOR_SPEC = 3 * max(abs(z["lam1_median"]) for z in _z if z)
FLOOR_DYN = 3 * max(abs(z["relax_rate_median"]) for z in _z if z)
chk(FLOOR_DYN < FLOOR_CEILING, f"R4 dynamic-read floor {FLOOR_DYN/3:.1e} exceeds the "
                               f"declared ceiling {FLOOR_CEILING:.0e}; the read is too noisy to use")
r4 = []
for x in rows + crows:
    chk(x.get("relax_delta", 0.05) <= 0.005,
        f"R4 T={x['T']} eps={x['eps']}: banked dynamic read taken at delta="
        f"{x.get('relax_delta')} — must be the smallest of the sweep")
    lam1, relax, resid = -x["lam1_median"], x["relax_rate_median"], x["resid_max"]
    conv = resid < CONVERGED
    floor = abs(lam1) < max(FLOOR_SPEC, 1e-12) and abs(relax) < FLOOR_DYN
    if conv and floor:
        state, ok = "CONVERGED_FLOOR", True
    elif conv:
        rel = abs(relax - lam1) / max(abs(lam1), 1e-300)
        state, ok = f"CONVERGED rel_err={rel:.2f}", rel < AGREE
    else:
        # not a fixed point: the dynamic read includes ongoing drift, so the
        # reads MAY disagree -- but that disagreement must be ATTRIBUTED, here
        state, ok = f"NOT_CONVERGED resid={resid:.1e} (reads not compared)", True
    r4.append((x["T"], x["eps"], state))
    chk(ok, f"R4 T={x['T']} eps={x['eps']}: spectral {lam1:+.2e} vs dynamic "
            f"{relax:+.2e} at a converged fixed point — {state}")
live = [t for t in r4 if t[2].startswith("CONVERGED rel_err")]
chk(len(live) >= 3, f"R4 has {len(live)} converged row(s) above the floor — "
                    "fewer than 3 live witnesses is a check that has not been exercised")

# R4b — the delta defect stays found
w20k = [x for x in crows if x.get("kind") == "long" and x["T"] == 20000.0]
chk(bool(w20k), "R4b eps=0.01/T=20000 witness row missing")
if w20k:
    x = w20k[0]
    lam1 = -x["lam1_median"]
    bad = x["relax_by_delta"].get("0.05", float("nan")) / lam1
    good = x["relax_by_delta"].get("0.005", float("nan")) / lam1
    chk(bad < 0.8, f"R4b delta=0.05 read now agrees with lam1 (ratio {bad:.2f}) — "
                   "the anharmonic-pinning defect this row pins has vanished; re-examine")
    chk(abs(good - 1) < AGREE, f"R4b delta=0.005 read disagrees with lam1 (ratio {good:.2f})")

# R5 — T-dependence banked and visible
diffs = [(e, row(T_short, e)["n_distinct"], row(T_long, e)["n_distinct"])
         for e in [x["eps"] for x in long_rows] if row(T_short, e) and row(T_long, e)]
chk(any(a != b for _, a, b in diffs),
    f"R5 n_distinct identical at every eps across T={T_short},{T_long}: {diffs} — "
    "either the sweep is too short to show collapse or T stopped mattering; both need saying")

# R6 — built detector two-sided-correct, confusable silent by margin
spec = D.marginal_mode_spec()


def fires(x):
    return (x["bump_amp_median"] > D.AMP_MIN and x["lam1_median"] > -D.LAM1_TOL
            and x["resid_max"] < 1e-8)


spec.record("intact_eps0_T200", fires(row(T_short, 0.0)))
spec.record("intact_eps0_T2000", fires(row(T_long, 0.0)))
w = row(T_long, 1e-4)
spec.record("weak_pin_eps1e-4_T2000", fires(w) if w else True)
spec.record("pinned_eps0.1_T2000", fires(last))
nb = [x for x in ctrl if x["T"] == T_long]
spec.record("no_bump_J1=1.0_T2000", fires(nb[0]) if nb else True)
try:
    rates = spec.certify()
except DetectorNotCertified as e:
    chk(False, f"R6 {e}")
    rates = spec.rates()
# tallies carry intervals, one convention (boundary_rate), and are labelled
from boundary_rate import classify as _br                            # noqa: E402
_tp, _np_ = map(int, rates["sensitivity"].split("/"))
_tn, _nn = map(int, rates["specificity"].split("/"))
sens_ci, spec_ci = _br(_tp, _np_), _br(_tn, _nn)
if w:
    margin = abs(w["lam1_median"]) / D.LAM1_TOL
    chk(margin > 10, f"R6 nearest confusable silent by only {margin:.1f}x — threshold is luck")
    # NOTE (honest): the weak-pin row has resid ~1e-5 (still drifting) so the
    # amplitude+lam1 read is at a non-fixed-point; the detector's convergence
    # gate keeps it silent for THAT reason too. Both reasons are recorded.
    w_silent_by_lam1 = w["lam1_median"] <= -D.LAM1_TOL
    chk(w_silent_by_lam1, "R6 confusable is silent only via the convergence gate, "
                          "not via lam1 — the spectral threshold is not doing work")

# R8 — the eps*T contour against pre-declared tolerances
TOLC = C["tolerances"]
byP = {}
for x in crows:
    if x.get("kind") == "split":
        byP.setdefault(x["product"], []).append(x)
amp0 = row(T_long, 0.0)["bump_amp_median"]
r8 = {}
for Pv, xs in sorted(byP.items()):
    chk(len(xs) == 3, f"R8 P={Pv}: expected 3 splits, got {len(xs)}")
    drifts = [x["drift_median"] for x in xs]
    nd = [x["n_distinct"] for x in xs]
    deformed = [x for x in xs if x["bump_amp_median"] < 0.99 * amp0]
    if Pv <= TOLC["LINEAR_P_MAX"]:
        spread = (max(drifts) - min(drifts)) / max(drifts)
        ok = spread <= TOLC["DRIFT_AGREE"]
        r8[Pv] = f"linear drift spread {spread:.3f} {'OK' if ok else 'FAIL'}"
        chk(ok, f"R8 P={Pv}: drift disagrees across splits by {spread:.2f} (>"
                f"{TOLC['DRIFT_AGREE']}) — contour claim fails in the linear regime")
    else:
        spread = max(nd) - min(nd)
        ok = spread <= TOLC["NDIST_AGREE"]
        r8[Pv] = f"n_distinct {nd} spread {spread} {'OK' if ok else 'FAIL'}" + \
                 (f" [bump deformed at eps={deformed[0]['eps']:g}, amp {deformed[0]['bump_amp_median']:.3f}]"
                  if deformed else "")
        if not deformed:
            chk(ok, f"R8 P={Pv}: n_distinct {nd} disagrees across splits with the bump "
                    "undeformed — the contour claim fails inside its stated domain")
        else:
            # the declared check FAILS here and that failure is the finding
            chk(not ok, f"R8 P={Pv}: splits agree ({nd}) even with a deformed bump "
                        f"(eps={deformed[0]['eps']:g}) — the domain boundary this row "
                        "pins has moved; re-examine before re-scoping")
fit = C["fit"]
chk(fit["max_rel_resid"] <= TOLC["FIT_RESID"],
    f"R8 fit residual {fit['max_rel_resid']:.3f} > {TOLC['FIT_RESID']}")
chk(0.01 < fit["c"] < 0.1, f"R8 fitted c={fit['c']:.3e} outside the range the two-point "
                            "estimate gave (≈0.03); re-examine the fit rows")

# R9 — measure 2
ppath = os.path.join(HERE, "stage1_ph_measured.json")
chk(os.path.exists(ppath), "R9 stage1_ph_measured.json missing — run stage1_ph.py")
PH = json.load(open(ppath)) if os.path.exists(ppath) else None
r9 = {}
if PH:
    chk(PH["instrument"]["model"] == "ring_ph_v2",
        f"R9 table is {PH['instrument']['model']}, not v2 (v1 had the anchored scramble + clipped jitter)")
    R_MIN = [q["value"] for q in PH["instrument"]["params"] if q["name"] == "R_MIN"][0]
    prow = PH["rows"]
    import statistics as _st

    def r12(cloud, arm="base", q=0.5, tau=None):
        v = [x["r12"] for x in prow if x["cloud"] == cloud and x["arm"] == arm and x["q"] == q
             and (tau is None or x["tau_j"] == tau)]
        return _st.median(v) if v else float("nan")

    taus = sorted({x["tau_j"] for x in prow if x["arm"] == "jitter"})

    def tau_c(cloud):
        """declared rule: first rung whose median r12 < R_MIN, given a detected base"""
        if r12(cloud) < R_MIN:
            return None                       # INAPPLICABLE: nothing to destroy
        for t in taus:
            if r12(cloud, "jitter", 0.5, t) < R_MIN:
                return t
        return float("inf")                   # censored at the top rung

    tcA, tcB, tcE = tau_c("A"), tau_c("B"), tau_c("E:400")
    # P1: tau_c(A) ~ 30 tau within a factor 3
    r9["P1"] = ("PASS" if tcA is not None and 10 <= tcA <= 90 else "FAIL") + f" (tau_c(A)={tcA})"
    # P2: same rung as A => traversal; >= 100 rung and != A => drift-sensitive
    if tcA is None or tcB is None:
        r9["P2"] = "INAPPLICABLE"
    elif tcB == tcA:
        r9["P2"] = f"COINCIDENCE: tau_c(B)=tau_c(A)={tcA} -> PH reads the traversal"
    else:
        r9["P2"] = (f"DIVERGENCE: tau_c(B)={tcB} vs tau_c(A)={tcA} -> PH sensitive to "
                    f"pinning-modulated motion (ladder resolution x3.16, gap = "
                    f"{len([t for t in taus if min(tcA, tcB) <= t < max(tcA, tcB)])} rung)")
    # P3: tau_c(E2) >= 100 rung
    r9["P3"] = ("INAPPLICABLE (E2 base below R_MIN; loop appears only under jitter 10-300)"
                if tcE is None else ("PASS" if tcE >= 100 else "FAIL") + f" (tau_c(E2)={tcE})")
    # P4: scramble kills A, B, E2; on C it was predicted a no-op
    scr = {c: r12(c, "scramble") for c in ("A", "B", "C", "E:400")}
    r9["P4"] = ("PASS" if all(scr[c] < R_MIN for c in ("A", "B", "E:400")) else "FAIL") + \
               f" on A/B/E2 {dict((k, round(v, 2)) for k, v in scr.items() if k != 'C')}; " + \
               f"C: predicted no-op, read {scr['C']:.2f} (base {r12('C'):.1f}) -> FAIL as predicted, " \
               "and the residual loop is the surrogate's blind spot (single-visit units are " \
               "ISI-shuffle invariant)"
    # P5: D ~ 1; E1 < E2; E2 >= R_MIN
    r9["P5"] = (f"D={r12('D'):.2f} {'PASS' if r12('D') < R_MIN else 'FAIL'}; "
                f"E1<E2: {r12('E:100'):.2f}<{r12('E:400'):.2f} {'PASS' if r12('E:100') < r12('E:400') else 'FAIL'}; "
                f"E2>=R_MIN: {'PASS' if r12('E:400') >= R_MIN else 'FAIL'}")
    # pins: scored outcomes must not drift silently
    chk(tcA == 100.0, f"R9 pin: tau_c(A) moved from 100 to {tcA}")
    chk(tcB == 300.0, f"R9 pin: tau_c(B) moved from 300 to {tcB}")
    chk(tcE is None, "R9 pin: E2 base now detected — the SNR finding changed")
    chk(scr["C"] >= R_MIN or any(x["r12"] >= R_MIN for x in prow if x["cloud"] == "C" and x["arm"] == "scramble"),
        "R9 pin: C-scramble residual loop vanished in every seed — the surrogate blind spot has moved")
    # finding (i): q flips the verdict only at E
    for c in ("A", "B", "C"):
        chk(all(r12(c, "base", q) > R_MIN for q in (1.0, 0.5, 0.25)), f"R9 {c} not q-invariant")
    chk(r12("E:100", "base", 1.0) > R_MIN > r12("E:100", "base", 0.5),
        "R9 pin: E1's q-dependence (fires at q=1.0, silent at q=0.5) changed")
    # detector certification on the DECLARED sets
    spec2 = D.ph_consistent_with_continuous_attractor_spec()
    spec2.record("intact_ring_cloud", r12("A") > R_MIN)
    spec2.record("pinned_ring_cloud_converged", r12("D") > R_MIN)
    spec2.record("jittered_cloud_above_tau_c", r12("A", "jitter", 0.5, tcA if tcA else 100.0) > R_MIN)
    spec2.record("within_cell_scrambled_cloud", r12("A", "scramble") > R_MIN)
    try:
        rates2 = spec2.certify()
    except DetectorNotCertified as e:
        chk(False, f"R9 {e}"); rates2 = spec2.rates()
    _tp2, _np2 = map(int, rates2["sensitivity"].split("/")); _tn2, _nn2 = map(int, rates2["specificity"].split("/"))
    sens2, specc2 = _br(_tp2, _np2), _br(_tn2, _nn2)
    r9["detector"] = (f"sens {rates2['sensitivity']} CP95 {sens2['honest_claim']} [{sens2['treatment']}]; "
                      f"spec {rates2['specificity']} CP95 {specc2['honest_claim']} [{specc2['treatment']}]; "
                      f"margin: A r12={r12('A'):.0f} vs R_MIN={R_MIN:g} ({r12('A')/R_MIN:.0f}x), D r12={r12('D'):.2f}")

# R10 — coverage test
vpath = os.path.join(HERE, "stage1_coverage_measured.json")
chk(os.path.exists(vpath), "R10 stage1_coverage_measured.json missing — run stage1_coverage.py")
CV = json.load(open(vpath)) if os.path.exists(vpath) else None
r10 = {}
if CV:
    VR, FINE = CV["rows"], CV["fine"]
    RM = 3.0

    def vsel(**kw):
        return [x for x in VR if all(x.get(k) == v for k, v in kw.items())]

    def vmed(rows, key="r12"):
        return float(_st.median([x[key] for x in rows])) if rows else float("nan")

    def vtau(**kw):
        """declared rule on the fine ladder: first rung with median r12 < R_MIN"""
        if vmed(vsel(kind="base", **kw)) < RM:
            return None
        for t in FINE:
            if vmed(vsel(kind="jitter", tau_j=t, **kw)) < RM:
                return t
        return float("inf")

    tA, tB = vtau(arm="F1", cloud="A"), vtau(arm="F1", cloud="B")
    r10["F1"] = (f"tau_c(A)={tA} {'PASS' if 70 <= tA <= 140 else 'FAIL'} [70,140]; "
                 f"D*=omega*tau_c(A)={0.02 * tA:.2f} rad; tau_c(B)/tau_c(A)={tB / tA:.2f} "
                 f"{'PASS' if 1.2 <= tB / tA <= 1.7 else 'FAIL'} [1.2,1.7] "
                 f"(residence-density account); P2 divergence "
                 f"{'REPLICATED' if tB > tA else 'NOT REPLICATED'}")
    chk(tA == 140.0 and tB == 140.0, f"R10 pin: F1 tau_c moved (A={tA}, B={tB})")
    tg = {g: vtau(arm="F2", gamma=g) for g in (0.01, 0.02, 0.04)}
    Dstar = 0.02 * tA
    ok2 = all(abs(g * tg[g] - Dstar) / Dstar <= 0.30 for g in tg)
    r10["F2"] = ("PASS" if ok2 else "FAIL") + " omega*tau_c = " + \
                ", ".join(f"{g * tg[g]:.2f}" for g in tg) + f" rad (D*={Dstar:.2f} +-30%)"
    chk(tg == {0.01: 300.0, 0.02: 140.0, 0.04: 70.0}, f"R10 pin: F2 tau_c moved {tg}")
    tr = {r: vtau(arm="F3", rot=r) for r in (1, 3, 10)}
    ok3 = max(tr.values()) / min(tr.values()) <= 1.4
    r10["F3"] = ("PASS" if ok3 else "FAIL") + f" tau_c by rotations {tr}"
    tw = {j0: vtau(arm="F4", J0=j0) for j0 in (-2.0, -6.0, -0.5)}
    W = CV["widths"]
    span = max(W.values()) / min(W.values())
    if span < 1.5:
        r10["F4"] = f"INAPPLICABLE width span {span:.2f}"
    else:
        ok_cov = max(tw.values()) / min(tw.values()) <= 1.4
        r10["F4"] = (f"H_cov {'PASS' if ok_cov else 'FAIL'} / H_motion "
                     f"{'FAIL' if ok_cov else 'OPEN'}: tau_c by (J0) {tw}, widths "
                     f"{ {k: round(v, 2) for k, v in W.items()} } (span {span:.2f}x)")
        chk(ok_cov, "R10 pin: tau_c now depends on bump width — the coverage claim moved")
    c1 = [x["r12"] for x in vsel(arm="F5", cloud="C1", kind="scramble")]
    c3 = [x["r12"] for x in vsel(arm="F5", cloud="C3", kind="scramble")]
    ok5 = any(v >= RM for v in c1) and _st.median(c3) < RM
    r10["F5"] = ("PASS" if ok5 else "FAIL") + f" C1 scrambled {[round(v, 2) for v in c1]}, C3 scrambled {[round(v, 2) for v in c3]}"
    chk(ok5, "R10 pin: the scramble's visits-per-unit power statement changed")
    # F6: construction boundary on E2 (r12 rule), A censored; degeneracy documented
    sig = [0.5, 1.0, 2.0, 5.0, 10.0, 20.0, 50.0, 100.0]
    e2 = {sg: vmed(vsel(arm="F6", cloud="E2", sigma=sg)) for sg in sig}
    e2b2 = {sg: vmed(vsel(arm="F6", cloud="E2", sigma=sg), "b2") for sg in sig}
    valid = [sg for sg in sig if e2b2[sg] > 0.05]
    cross = [sg for sg in valid if e2[sg] >= RM]
    a_r12 = {sg: vmed(vsel(arm="F6", cloud="A", sigma=sg)) for sg in sig}
    a_b1 = {sg: vmed(vsel(arm="F6", cloud="A", sigma=sg), "b1") for sg in sig}
    r10["F6"] = (f"E2 crosses R_MIN at sigma={cross} (predicted lower edge in [5,50]: "
                 f"{'PASS' if cross and 5 <= min(cross) <= 50 else 'FAIL'}; r12 valid only for sigma<=10, "
                 f"b2->0 beyond); A never below R_MIN on r12 (censored at 100: FAIL as declared), "
                 f"but A's b1 falls {a_b1[0.5]:.0f}->{a_b1[100.0]:.0f} — r12 is scale-free and blind to it")
    chk(cross == [2.0, 5.0], f"R10 pin: E2 construction regime moved ({cross})")
    degenerate = sum(1 for x in VR if x["kind"] == "matched" and x["b2"] < 0.05)
    n_matched = sum(1 for x in VR if x["kind"] == "matched")
    chk(degenerate >= n_matched // 2, "R10: matched rows no longer degenerate on r12 — re-examine the statistic note")
    # F6b on b1 (r12 INAPPLICABLE): E2 jitter b1 >> base b1 => CONSTRUCTED
    e2base = vmed(vsel(arm="F6b", cloud="E2", kind="base"), "b1")
    e2jit = {t: vmed(vsel(arm="F6b", cloud="E2", kind="jitter", tau_j=t), "b1") for t in FINE}
    e2mat = {t: vmed(vsel(arm="F6b", cloud="E2", kind="matched", tau_j=t), "b1") for t in FINE}
    grow = min(e2jit[t] / max(e2base, 1e-9) for t in FINE)
    r10["F6b"] = (f"r12 INAPPLICABLE (degenerate); on b1: E2 base {e2base:.1f}, jittered "
                  f"{min(e2jit.values()):.0f}-{max(e2jit.values()):.0f} at every rung (>= {grow:.0f}x base) "
                  f"— CONSTRUCTED, not lifted; smoothing-matched {min(e2mat.values()):.0f}-{max(e2mat.values()):.0f}: "
                  f"jitter constructs more than smoothing (wrap bridges the 4->1 segment boundary). "
                  f"'constructed = smoothing' FAIL. A at tau_c: jit/matched b1 = "
                  f"{vmed(vsel(arm='F1', cloud='A', kind='jitter', tau_j=100.0), 'b1') / vmed(vsel(arm='F1', cloud='A', kind='matched', tau_j=100.0), 'b1'):.2f} "
                  f"(<0.5 predicted: FAIL — destruction is mostly displacement, shared with smoothing)")
    chk(grow > 20, f"R10 pin: E2's jitter-grown loop no longer >>20x base (min {grow:.1f}x)")

# R11 — Stage 2
npath = os.path.join(HERE, "stage2_nonnormal_measured.json")
chk(os.path.exists(npath), "R11 stage2_nonnormal_measured.json missing — run stage2_nonnormal.py")
NN = json.load(open(npath)) if os.path.exists(npath) else None
r11 = {}
if NN:
    chk(NN["instrument"]["model"] == "ring_nonnormal_v3",
        f"R11 table is {NN['instrument']['model']}, not v3 (v1/v2 had red rails)")
    NR = NN["rows"]
    rails = [x for x in NR if x["arm"] == "rail"]
    chk(len(rails) == 5, "R11 expected 5 rail rows")
    for x in rails:
        chk(x["henrici"] < 1e-10, f"R11 rail gamma={x['gamma']}: Henrici {x['henrici']:.1e} (normal matrix)")
        chk(abs(x["gap"]) < 1e-10, f"R11 rail gamma={x['gamma']}: numerical-spectral gap {x['gap']:.1e}")
        chk(abs(x["gmax"] - 1) < 1e-9, f"R11 rail gamma={x['gamma']}: G_max {x['gmax']:.6f} != 1")
        chk(abs(x["kreiss"] - 1) < 1e-3, f"R11 rail gamma={x['gamma']}: Kreiss {x['kreiss']:.4f} != 1")
    s0 = [x for x in NR if x["arm"] == "S0"][0]
    H0, G0 = s0["henrici"], s0["gmax"]
    chk(s0["rail_ok"], "R11 S0 not at a fixed point")
    chk(1.9 < H0 < 2.3 and 0.15 < s0["gap"] < 0.21 and 1.3 < G0 < 1.42,
        f"R11 pin: S0 baseline moved (H0={H0:.3f}, gap={s0['gap']:.3f}, G0={G0:.3f})")
    chk(abs(s0["kappa"] - G0) < 1e-3 and abs(s0["kreiss"] - G0) < 1e-2,
        "R11 S0: on the marginal row G_max must equal kappa(0) and the Kreiss constant")
    for x in NR:
        if x["arm"] != "rail":
            chk((x["gap"] > 1e-6) == (x["gmax"] > 1 + 1e-6),
                f"R11 {x['arm']} g={x['gamma']} e={x['eps']}: gap>0 <=> G_max>1 violated")
            chk(x["kreiss"] <= x["gmax"] * (1 + 0.02) or not x.get("rail_ok", True),
                f"R11 {x['arm']} g={x['gamma']} e={x['eps']}: Kreiss {x['kreiss']:.3f} > G_max {x['gmax']:.3f}")
    # S-gamma: read rows only
    sg = [x for x in NR if x["arm"] == "Sgamma"]
    sg_read = [x for x in sg if x["rail_ok"]]
    sg_lim = [x["gamma"] for x in sg if not x["rail_ok"]]
    maxrel = max(abs(x["henrici_rel"]) for x in sg_read)
    hplan_min = 0.5 * max(x["gamma"] for x in sg_read) / 0.32     # first order, >= 50% at 0.32
    r11["Sgamma"] = (f"read gamma={[x['gamma'] for x in sg_read]}, instrument-limited {sg_lim}; "
                     f"max |dHenrici/H0| = {maxrel:.2e} vs H_plan's >= {hplan_min:.2f} -> H_plan FALSIFIED; "
                     f"H_gain magnitude (<10%) PASS; exponent {NN['fits']['exp_henrici_gamma']:.2f} "
                     f"(sealed 2 +- 0.3: {'PASS' if abs(NN['fits']['exp_henrici_gamma'] - 2) <= 0.3 else 'FAIL'}) "
                     f"but {NN['fits']['n_resolved_gamma']}/{len(sg_read)} points individually resolved "
                     f"above 3x their error bound -> exponent PROVISIONAL; G_max {[round(x['gmax'], 4) for x in sg_read]}")
    chk(maxrel < 0.02, "R11 pin: circulant asymmetry now moves Henrici by > 2% on a read row")
    chk(sg_lim == [0.32], f"R11 pin: instrument-limited gamma rows changed: {sg_lim}")
    # S-alpha
    sa = [x for x in NR if x["arm"] == "Salpha"]
    sa_read = [x for x in sa if x["rail_ok"]]
    sa_lim = [x["gamma"] for x in sa if not x["rail_ok"]]
    ratios = NN["fits"]["ratio_rand_over_circ_matched"]
    big = max(sa_read, key=lambda x: x["gamma"])
    ratio_big = ratios[str(big["gamma"])] if str(big["gamma"]) in ratios else ratios.get(big["gamma"])
    verdict = ("H_struct (<0.5)" if ratio_big < 0.5 else "H_comparable (0.5-2)" if ratio_big <= 2 else "H_inv (>2)")
    r11["Salpha"] = (f"read matched-gamma={[x['gamma'] for x in sa_read]}, instrument-limited {sa_lim} "
                     f"(unconverged at T=2e5, G_max {[round(x['gmax'], 1) for x in sa if not x['rail_ok']]} not read); "
                     f"max |dHenrici/H0| = {max(abs(x['henrici_rel']) for x in sa_read):.2e}; "
                     f"rand/circ at largest read norm = {ratio_big:.2f} -> {verdict}")
    chk(0.5 <= ratio_big <= 2.0, f"R11 pin: matched-norm rand/circ ratio moved to {ratio_big:.2f}")
    chk(sa_lim == [0.32], f"R11 pin: instrument-limited alpha rows changed: {sa_lim}")
    # S-eps
    se = [x for x in NR if x["arm"] == "Seps"]
    chk(all(x["rail_ok"] for x in se), "R11 an S-eps row is not converged")
    gm = [x["gmax"] for x in sorted(se, key=lambda x: x["eps"])]
    mono = all(b < a for a, b in zip([G0] + gm, gm))
    r11["Seps"] = (f"G_max(eps) = {[round(v, 4) for v in gm]} from G0={G0:.4f}: "
                   f"{'monotone decreasing -> H_pin PASS, H_plan FAIL' if mono else 'NOT monotone'}; "
                   f"exponent of |G_max-G0| vs eps = {NN['fits']['exp_gmax_eps']:.2f}; "
                   f"kappa {[round(x['kappa'], 4) for x in sorted(se, key=lambda x: x['eps'])]} >= G_max on every "
                   f"pinned row; max |dHenrici/H0| = {max(abs(x['henrici_rel']) for x in se):.2e}; "
                   f"gap {[round(x['gap'], 3) for x in sorted(se, key=lambda x: x['eps'])]} (unchanged)")
    chk(mono, "R11 pin: G_max(eps) monotone decrease lost")
    chk(0.7 <= NN["fits"]["exp_gmax_eps"] <= 1.0, f"R11 pin: G_max(eps) exponent moved to {NN['fits']['exp_gmax_eps']:.2f}")
    chk(all(x["kappa"] >= x["gmax"] - 1e-6 for x in se), "R11 kappa < G_max on a pinned row (theorem: G_max <= kappa at t->inf only for the marginal case; pinned rows must satisfy G_max <= kappa)")
    r11["headline"] = (f"symmetric attractor: Henrici {H0:.3f} ({100 * H0 / s0['frob']:.0f}% of |J|_F), numerical-spectral "
                       f"gap {s0['gap']:.3f}, G0 = kappa0 = K0 = {G0:.3f}; no read row in a 16x gamma, matched-norm "
                       f"random, or 100x eps sweep moves Henrici by > 0.2%; the gap is ~0.178 everywhere")

# R12 — Stage 3a
lpath = os.path.join(HERE, "stage3_lift_measured.json")
chk(os.path.exists(lpath), "R12 stage3_lift_measured.json missing — run stage3_lift.py")
LF = json.load(open(lpath)) if os.path.exists(lpath) else None
r12 = {}
if LF:
    LR = LF["rows"]
    A = [x for x in LR if x["cloud"] == "A" and x["arm"] == "L2"]
    readable = [x for x in A if x.get("readable") and x.get("mode") == "standard"]
    fallback = [x for x in A if x.get("readable") and x.get("mode") != "standard"]
    # L1: rho=50, bin 0.5
    l1 = [x for x in readable if x["rho"] == 50.0 and x["bin"] == 0.5]
    ok1 = (len(l1) == 3 and all(x["n_est"] == x["n_true"] == 3 for x in l1)
           and all(0.9 <= x["k_est"] <= 1.1 for x in l1) and all(x["theta_rms"] < 0.1 for x in l1))
    r12["L1"] = ("PASS" if ok1 else "FAIL") + (f" |n| {[x['n_est'] for x in l1]}/3, k {[round(x['k_est'], 2) for x in l1]}, "
                                              f"theta_rms {[round(x['theta_rms'], 3) for x in l1]} (affine-only "
                                              f"{[round(x['theta_rms_affine_only'], 2) for x in l1]}), sign {[x['sign'] for x in l1]}")
    chk(ok1, "R12 pin: L1 readout regressed")
    # L2: every readable row has |n| exact; every fallback row is not read; at least one fallback count is WRONG
    chk(all(x["n_est"] == x["n_true"] for x in readable), "R12 pin: a readable row has a wrong count")
    chk(any(x["n_est"] != x["n_true"] for x in fallback),
        "R12 pin: the nonstandard-range fallback no longer produces a wrong count — re-examine before trusting it")
    edge = {}
    for b in (0.5, 0.1):
        rr = sorted({x["rho"] for x in readable if x["bin"] == b})
        edge[b] = min(rr) if rr else None
    chk(edge == {0.5: 5.0, 0.1: 15.0}, f"R12 pin: smallest readable rho per bin moved: {edge}")
    # theta exponent over readable rho at bin 0.5
    import math
    pts = {}
    for x in readable:
        if x["bin"] == 0.5:
            pts.setdefault(x["rho"], []).append(x["theta_rms"])
    xs = sorted(pts); ys = [_st.median(pts[r]) for r in xs]
    slope = None
    if len(xs) >= 3:
        lx, ly = [math.log(v) for v in xs], [math.log(v) for v in ys]
        mx, my = sum(lx) / len(lx), sum(ly) / len(ly)
        slope = sum((a - mx) * (b - my) for a, b in zip(lx, ly)) / sum((a - mx) ** 2 for a in lx)
    big_theta_readable = [x for x in readable if x["theta_rms"] > 0.3]
    r12["L2"] = (f"readable rho (bin 0.5) {xs} theta_rms {[round(v, 3) for v in ys]} -> exponent "
                 f"{slope if slope is None else round(slope, 2)} vs sealed -0.5+-0.15: "
                 f"{'PASS' if slope is not None and abs(slope + 0.5) <= 0.15 else 'FAIL (floor-limited, flat)'}; "
                 f"protection claim: {'PASS' if big_theta_readable else 'NOT REACHED'} — no readable row has theta > 0.3 rad; "
                 f"the class disappears first (smallest readable rho: {edge}, CENSORED edges); fallback rows: "
                 f"{sum(1 for x in fallback if x['n_est'] != x['n_true'])}/{len(fallback)} wrong counts (not read)")
    # L3
    ind = [x for x in LR if x["cloud"] == "IND"]
    ok_ind = len(ind) == 3 and all(x.get("readable") and x["n_est"] == 3 and x["continuity"] > 0.95 for x in ind)
    cord = [x for x in LR if x["cloud"] == "C_ord"]
    ok_cord = all(x.get("readable") and abs(x["wind_est"] - 0.94) < 0.15 and x["continuity"] > 0.95 for x in cord)
    cperm = [x for x in LR if x["cloud"] == "C_perm"]
    cperm_cont = [x["continuity"] for x in cperm if x.get("readable")]
    ok_cperm_sealed = all(c < 0.5 for c in cperm_cont)
    r12["L3"] = (f"IND {'PASS' if ok_ind else 'FAIL'} (|n| {[x.get('n_est') for x in ind]}, continuity "
                 f"{[round(x.get('continuity', 0), 3) for x in ind]}) — the kinematic ceiling: path-lift cannot separate "
                 f"the attractor from the independent construction; C_ord {'PASS' if ok_cord else 'FAIL'} (wind "
                 f"{[round(x.get('wind_est', 0), 2) for x in cord]}); C_perm sealed prediction "
                 f"{'PASS' if ok_cperm_sealed else 'FAIL'}: continuity {[round(c, 3) for c in cperm_cont]}, |n| "
                 f"{[x.get('n_est') for x in cperm]} — the per-step statistic is defeated by smoothing + rare jumps "
                 f"(15 boundaries in 2000 steps); a total-variation/net-winding statistic is the candidate replacement")
    chk(ok_ind, "R12 pin: IND no longer reads like A — the kinematic ceiling moved")
    chk(all(c > 0.9 for c in cperm_cont), "R12 pin: C_perm continuity dropped — the defeated statistic changed behaviour")
    # L4
    l4 = {}
    for x in LR:
        if x["arm"] == "L4" and x.get("readable"):
            l4.setdefault(x["seed"], {})[x["cloud"]] = x["tau_tr_tau"]
    ratios = [v["A_n"] / v["IND_n"] for v in l4.values() if "A_n" in v and "IND_n" in v]
    ok4 = len(ratios) == 3 and all(r > 2 for r in ratios)
    r12["L4"] = (("PASS" if ok4 else "FAIL") + f" tau_tr(A_n)/tau_tr(IND_n) = {[round(r, 2) for r in ratios]}; both at "
                 f"the smoothing floor (~0.4 tau). Rate-level probe (brief): no separation without spikes either -> the "
                 f"32-bin manifold estimate leaves along-manifold motion in the 'transverse' residual; instrument, not SNR. "
                 f"L4b (tangent-projected residual) is the next pre-registration; the attractor rung stays DECLARED")
    chk(all(0.7 < r < 1.4 for r in ratios), f"R12 pin: L4 ratio moved out of [0.7,1.4]: {ratios} — re-read before re-scoping")

# R13 — Stage 3b
bpath = os.path.join(HERE, "stage3b_recurrence_measured.json")
chk(os.path.exists(bpath), "R13 stage3b_recurrence_measured.json missing — run stage3b_recurrence.py")
RB = json.load(open(bpath)) if os.path.exists(bpath) else None
r13 = {}
if RB:
    BR = RB["rows"]
    # L4b: sealed to fail at the rate level (ratio < 2 in >= 2/3 seeds)
    l4 = {}
    for x in BR:
        if x["arm"] == "L4b" and x.get("readable"):
            l4.setdefault((x["level"], x["seed"]), {})[x["cloud"]] = x["tau_perp_tau"]
    rat = {lvl: [v["A_n"] / v["IND_n"] for (l, sd), v in sorted(l4.items()) if l == lvl and len(v) == 2]
           for lvl in ("rates", "spikes")}
    ok4b = sum(r < 2 for r in rat["rates"]) >= 2
    r13["L4b"] = (f"sealed-to-fail {'CONFIRMED' if ok4b else 'NOT CONFIRMED (it separated!)'}: rate-level ratio "
                  f"{[round(r, 2) for r in rat['rates']]} (IND_n, with zero true transverse fluctuation, reads "
                  f"{[round(v['IND_n'], 2) for (l, sd), v in sorted(l4.items()) if l == 'rates']} tau — model error, "
                  f"smooth in phi(t)); spikes {[round(r, 2) for r in rat['spikes']]} at the floor")
    chk(ok4b, "R13 pin: L4b now separates at the rate level — re-read before re-scoping the attractor rung")
    # I1
    def ret(system):
        return [x["retention"] for x in BR if x["arm"] == "I" and x["kick"] == "along" and x["system"] == system]
    rc, rp, ri = ret("ring_eps0"), ret("ring_eps0.1"), ret("IND_u")
    ok_c, ok_i, ok_p = all(r > 0.9 for r in rc), all(r < 0.05 for r in ri), all(r < 0.1 for r in rp)
    r13["I1"] = (f"continuous attractor retention {[round(r, 3) for r in rc]} {'PASS' if ok_c else 'FAIL'} (>0.9); "
                 f"IND_u {[round(r, 3) for r in ri]} {'PASS' if ok_i else 'FAIL'} (<0.05); driven pinned ring "
                 f"{[round(r, 3) for r in rp]} {'PASS' if ok_p else 'FAIL'} (<0.1) — drive omega=0.02 >> c*eps=2.9e-3, the "
                 f"bump is not trapped, no mean restoring force; the discrete-attractor negative is re-posed TRAPPED (I1b)")
    chk(ok_c and ok_i, "R13 pin: the I1 kind-level separation (attractor retains, input-driven restores) regressed")
    chk(all(0.7 < r < 0.95 for r in rp), f"R13 pin: driven pinned ring retention moved out of [0.7,0.95]: {rp}")
    # I2
    def dp10(system):
        return [x["dperp_10"] / x["dperp_0"] for x in BR if x["arm"] == "I" and x["kick"] == "transverse"
                and x["system"] == system]
    t_c, t_i, t_p = dp10("ring_eps0"), dp10("IND_u"), dp10("ring_eps0.1")
    r13["I2"] = (f"transverse return at 10 tau (fraction remaining): ring {[round(v, 3) for v in t_c]}, IND_u "
                 f"{[round(v, 3) for v in t_i]} (both <0.1: {'PASS' if all(v < 0.1 for v in t_c + t_i) else 'FAIL'}); "
                 f"pinned {[round(v, 3) for v in t_p]} (position-dependent bump shape leaves a residual) — rate not kind")
    chk(all(v < 0.1 for v in t_c + t_i), "R13 pin: transverse kicks no longer return in the ring/IND_u")
    # T1 + detector
    def T1(cloud, key):
        return [x[key] for x in BR if x["arm"] == "T1" and x["cloud"] == cloud and x.get("readable")]
    okA = all(r < 1.5 for r in T1("A", "R")) and all(j == 0 for j in T1("A", "J"))
    okI = all(r < 1.5 for r in T1("IND", "R")) and all(j == 0 for j in T1("IND", "J"))
    okO = all(r < 1.5 for r in T1("C_ord", "R"))
    okP = all((r > 3 or j >= 8) for r, j in zip(T1("C_perm", "R"), T1("C_perm", "J")))
    dread = [x.get("readable") for x in BR if x["arm"] == "T1" and x["cloud"] == "D"]
    r13["T1"] = (f"A R={[round(r, 2) for r in T1('A', 'R')]} J={T1('A', 'J')} {'PASS' if okA else 'FAIL'}; IND R="
                 f"{[round(r, 2) for r in T1('IND', 'R')]} {'PASS' if okI else 'FAIL'}; C_ord R={[round(r, 2) for r in T1('C_ord', 'R')]} "
                 f"{'PASS' if okO else 'FAIL (R-1 ~ noise-TV/net: a stepwise traversal with small net reads high; R needs a noise correction before 1.5 is a threshold)'}; "
                 f"C_perm R={[round(r, 2) for r in T1('C_perm', 'R')]} J={T1('C_perm', 'J')} {'PASS (via R; J clause fails: smoothing merges 13/15 boundaries)' if okP else 'FAIL'}; "
                 f"D readable={dread} (unreadable => silent)")
    chk(okA and okI and okP, "R13 pin: T1's separation of A/IND from C_perm regressed")
    chk(not okO and all(1.5 <= r <= 3 for r in T1("C_ord", "R")), "R13 pin: C_ord's R moved out of [1.5,3] — the false-negative channel changed")
    chk(not any(dread), "R13 pin: D became readable — a 3-cluster static cloud has no H1 class")
    # detector: with_continuous_traversal on its DECLARED sets
    spec3 = D.ph_with_continuous_traversal_spec()
    fireA = okA; fireI = okI
    spec3.record("driven_ring_A", fireA)
    spec3.record("independent_units_IND", fireI)
    spec3.record("random_order_static_C_perm", not okP)
    spec3.record("converged_pinned_D", any(dread))
    spec3.record("unreadable_low_rho", False)      # silent by rule (R12 pins the fallback's wrong counts)
    try:
        rates3 = spec3.certify()
    except DetectorNotCertified as e:
        chk(False, f"R13 {e}"); rates3 = spec3.rates()
    _tp3, _np3 = map(int, rates3["sensitivity"].split("/")); _tn3, _nn3 = map(int, rates3["specificity"].split("/"))
    s3c, p3c = _br(_tp3, _np3), _br(_tn3, _nn3)
    r13["detector"] = (f"ph_topology_with_continuous_traversal certified on its DECLARED sets: sens {rates3['sensitivity']} "
                       f"CP95 {s3c['honest_claim']} [{s3c['treatment']}], spec {rates3['specificity']} CP95 {p3c['honest_claim']} "
                       f"[{p3c['treatment']}]; CAVEAT PINNED: a stepwise traversal (C_ord, not in the declared sets) reads "
                       f"R=2.1 and would be a false negative under the R<1.5 clause")

# R13b — I1b
tpath = os.path.join(HERE, "stage3c_trapped_measured.json")
chk(os.path.exists(tpath), "R13b stage3c_trapped_measured.json missing — run stage3c_trapped.py")
TR = json.load(open(tpath)) if os.path.exists(tpath) else None
if TR:
    def R(eps, g):
        return [x["retention"] for x in TR["rows"] if x["eps"] == eps and x["gamma"] == g][0]
    r0, r20 = R(0.1, 0.0), R(0.1, 0.02)
    chk(r0 < 0.1, f"R13b pin: trapped discrete attractor no longer restores (R={r0:.3f})")
    chk(r20 > 0.5, f"R13b pin: sliding pinned ring no longer retains (R={r20:.3f})")
    seq = [R(0.1, g) for g in (0.0, 0.001, 0.003, 0.01, 0.02)]
    mono = all(b >= a - 1e-9 for a, b in zip(seq, seq[1:]))
    chk(TR["depinning"]["0.1"] == {"last_below": 0.01, "first_above": 0.02},
        f"R13b pin: depinning interval at eps=0.1 moved: {TR['depinning']['0.1']}")
    r03 = R(0.03, 0.0)
    chk(0.5 <= r03 <= 0.95, f"R13b pin: eps=0.03 gamma=0 retention moved out of [0.5,0.95]: {r03:.3f}")
    mono_txt = "PASS" if mono else "FAIL (well-dependent restoring rate after the drive tilts the landscape)"
    r13["I1b"] = (f"eps=0.1: R(gamma) = {[round(v, 3) for v in seq]} for gamma 0/1e-3/3e-3/1e-2/2e-2 — trapped restores "
                  f"(0.02 < 0.1 PASS), sliding retains (0.72 > 0.5 PASS), monotone {mono_txt}; depinning crossing in "
                  f"(0.01, 0.02] — above the 3*c*eps guess (0.0087); eps=0.03: R(0)={r03:.2f} — INAPPLICABLE at T_obs=300 "
                  f"(sealed as marginal; worse than marginal), needs ~3000 tau")

# R13c — I1c
lpath3 = os.path.join(HERE, "stage3d_trapped_long_measured.json")
chk(os.path.exists(lpath3), "R13c stage3d_trapped_long_measured.json missing — run stage3d_trapped_long.py")
L3 = json.load(open(lpath3)) if os.path.exists(lpath3) else None
if L3:
    Rg = {x["gamma"]: x["retention"] for x in L3["rows"]}
    chk(Rg[0.001] < 0.5 and Rg[0.003] > 0.5, f"R13c pin: retention crossing no longer straddles the 4b edge: {Rg}")
    chk(all(Rg[g] > 0.8 for g in (0.01, 0.02)), f"R13c pin: sliding retention dropped: {Rg}")
    chk(0.2 < Rg[0.0] < 0.6, f"R13c pin: R(gamma=0) at 3000 tau moved out of [0.2,0.6]: {Rg[0.0]:.3f}")
    lam_eff = -math.log(max(Rg[0.0], 1e-12)) / 3000.0
    r13["I1c"] = (f"eps=0.03, T_obs=3000: R = {[round(Rg[g], 3) for g in (0.0, 0.001, 0.003, 0.01, 0.02)]}; crossing "
                  f"between 0.001 and 0.003 PASS (4b edge 2.25e-3); R(0)={Rg[0.0]:.3f} FAIL (<0.1 sealed): this well's "
                  f"lambda_eff = {lam_eff:.1e}, 10x below the Stage 1 median 3.8e-3; R(0.003)={Rg[0.003]:.2f} > 1 — retention "
                  f"is bounded only for trapped systems, sliding phase offsets wander")

# R16 — intervention-class detector on banked data
if RB and TR:
    spec_m = D.attractor_by_along_manifold_memory_spec()
    rc_ = [x["retention"] for x in RB["rows"] if x["arm"] == "I" and x["kick"] == "along" and x["system"] == "ring_eps0"]
    ri_ = [x["retention"] for x in RB["rows"] if x["arm"] == "I" and x["kick"] == "along" and x["system"] == "IND_u"]
    rt_ = [x["retention"] for x in TR["rows"] if x["eps"] == 0.1 and x["gamma"] == 0.0]
    spec_m.record("ring_eps0_driven", all(r > 0.9 for r in rc_) and len(rc_) == 3)
    spec_m.record("IND_u", any(r > 0.9 for r in ri_))
    spec_m.record("pinned_ring_trapped", any(r > 0.9 for r in rt_))
    try:
        rates_m = spec_m.certify()
    except DetectorNotCertified as e:
        chk(False, f"R16 {e}"); rates_m = spec_m.rates()
    _tpm, _npm = map(int, rates_m["sensitivity"].split("/")); _tnm, _nnm = map(int, rates_m["specificity"].split("/"))
    smc, pmc = _br(_tpm, _npm), _br(_tnm, _nnm)
    r13["memory_detector"] = (f"attractor_by_along_manifold_memory certified: sens {rates_m['sensitivity']} CP95 "
                              f"{smc['honest_claim']} [{smc['treatment']}], spec {rates_m['specificity']} CP95 "
                              f"{pmc['honest_claim']} [{pmc['treatment']}]; margins: positive retention "
                              f"{[round(r, 3) for r in rc_]} vs negatives {[round(r, 3) for r in ri_]} / {[round(r, 3) for r in rt_]}")

# R17 — Stage 3e MSD
mpath = os.path.join(HERE, "stage3e_msd_measured.json")
chk(os.path.exists(mpath), "R17 stage3e_msd_measured.json missing — run stage3e_msd.py")
MS = json.load(open(mpath)) if os.path.exists(mpath) else None
r17 = {}
if MS:
    rows_m = MS["rows"]
    lam1 = abs(MS["lambda1_ref"])
    cont = [x for x in rows_m if x["system"] == "continuum"]
    trap = [x for x in rows_m if x["system"] == "trapped"]
    ind = [x for x in rows_m if x["system"] == "IND_u"]
    Dm = float(_st.mean(x["D"] for x in cont))
    # continuum
    c_slope = [x["slope_10_1000"] for x in cont]; c_ratio = [x["ratio_1000_100"] for x in cont]
    ok_cs = all(abs(v - 1) <= 0.15 for v in c_slope); n_cr = sum(7 <= v <= 13 for v in c_ratio)
    r17["continuum"] = (f"slope[10,1000] {[round(v, 2) for v in c_slope]} (1.0+-0.15) {'PASS' if ok_cs else 'FAIL'}; "
                        f"MSD(1000)/MSD(100) {[round(v, 1) for v in c_ratio]} in [7,13]: {n_cr}/3 "
                        f"{'PASS' if n_cr == 3 else 'FAIL (long-lag MSD has ~20 independent segments at T=20000: +-30%)'}; "
                        f"D = {Dm:.2e} rad^2/tau")
    # trapped
    t_slope = [x["slope_200_2000"] for x in trap]; t_sat = [x["msd_sat"] for x in trap]; t_cross = [x["crossover_lag"] for x in trap]
    pred_sat = 2 * Dm / lam1; pred_cross = 1 / lam1
    n_ts = sum(v < 0.3 for v in t_slope)
    n_sat = sum(0.5 <= v / pred_sat <= 2 for v in t_sat)
    n_cx = sum(pred_cross / 3 <= v <= pred_cross * 3 for v in t_cross)
    lam_eff = [1 / v for v in t_cross]
    sat_eff = [2 * Dm / v for v in lam_eff]
    r17["trapped"] = (f"slope[200,2000] {[round(v, 2) for v in t_slope]} (<0.3): {n_ts}/3; MSD_sat {[f'{v:.1e}' for v in t_sat]} vs "
                      f"2D/|lambda1| = {pred_sat:.1e} (x2): {n_sat}/3 FAIL; crossover {t_cross} vs 1/|lambda1| = {pred_cross:.0f} (x3): "
                      f"{n_cx}/3 FAIL — ONE CAUSE: lambda_eff = 1/crossover = {[f'{v:.1e}' for v in lam_eff]} = "
                      f"{[round(v / lam1, 2) for v in lam_eff]} x lambda1, and 2D/lambda_eff = {[f'{v:.1e}' for v in sat_eff]} matches "
                      f"MSD_sat to {[round(a / b, 2) for a, b in zip(t_sat, sat_eff)]}x: noise drives 0.1-rad excursions, where the "
                      f"delta sweep measured a 0.32 restoring ratio (anharmonic well, third instrument)")
    # IND_u
    i_slope = [x["slope_10_1000"] for x in ind]; i_ratio = [x["ratio_1000_10"] for x in ind]
    ok_i = all(v < 0.15 for v in i_slope) and all(v < 1.5 for v in i_ratio)
    r17["IND_u"] = f"slope {[round(v, 2) for v in i_slope]} (<0.15), MSD(1000)/MSD(10) {[round(v, 2) for v in i_ratio]} (<1.5): {'PASS' if ok_i else 'FAIL'}"
    # separation in kind
    seps = [c["slope_200_2000"] - t["slope_200_2000"] for c, t in zip(cont, trap)]
    n_sep = sum(v > 0.5 for v in seps)
    kind_ok = all(c["slope_200_2000"] > 0.6 for c in cont) and all(0.15 < t["slope_200_2000"] < 0.6 for t in trap) and all(abs(i["slope_10_1000"]) < 0.15 for i in ind)
    r17["separation"] = (f"continuum - trapped long-lag slope {[round(v, 2) for v in seps]} (>0.5): {n_sep}/3 "
                         f"{'PASS' if n_sep == 3 else 'FAIL (narrow)'}; IND_u saturation lag < trapped crossover/10: PASS; "
                         f"kind-level ordering (continuum > trapped > IND_u on long-lag slope) holds in "
                         f"{'9/9' if kind_ok else 'NOT all'} rows [post-hoc thresholds, reported not scored]")
    chk(ok_cs and ok_i, "R17 pin: continuum growth law or IND_u flatness regressed")
    chk(kind_ok, "R17 pin: the kind-level ordering of the three systems' growth laws broke")
    chk(all(0.15 <= v / lam1 <= 0.5 for v in lam_eff), f"R17 pin: lambda_eff/lambda1 moved out of [0.15,0.5]: {[round(v / lam1, 2) for v in lam_eff]}")
    r17["verdict"] = ("implies rung NOT certified at sealed precision (trapped clauses sealed against the linear lambda1; "
                      "continuum ratio and separation 2/3); 'unreachable observationally' NOT banked either — the zero "
                      "mode's integration of endogenous noise is a passive signature. Next seal: lambda_eff from the "
                      "delta sweep at the noise-set excursion, T >= 1e5 or 10 seeds for the long-lag +-30%")

# R13d — T2 / T3
t3p = os.path.join(HERE, "stage3g_traversal3_measured.json")
chk(os.path.exists(t3p), "R13d stage3g_traversal3_measured.json missing")
if os.path.exists(t3p):
    T3 = json.load(open(t3p))["rows"]
    def t3(cloud, key):
        return [x[key] for x in T3 if x["cloud"] == cloud and x.get("readable")]
    Mperm, Mord, MA, MI = t3("C_perm", "M"), t3("C_ord", "M"), t3("A", "M"), t3("IND", "M")
    Jperm, Jord, JA, JI = t3("C_perm", "J_mad"), t3("C_ord", "J_mad"), t3("A", "J_mad"), t3("IND", "J_mad")
    ordering = (max(Mperm) < 0.7 and min(Mord) > 0.95 and min(MA + MI) > 0.7
                and max(JA + JI) < 50 and min(Jord + Jperm) > 100)
    chk(ordering, "R13d pin: the T3 ordering (M: perm < smooth <= ordered; J: smooth < stepwise) broke")
    sealed_A = sum(j <= 10 for j in JA + JI); sealed_ord = sum(10 <= j <= 40 for j in Jord)
    r13["T3"] = (f"M: C_perm {[round(v, 2) for v in Mperm]} < 0.7 PASS; C_ord {[round(v, 2) for v in Mord]} >= 0.9 PASS; A/IND "
                 f"{[round(v, 2) for v in MA + MI]} (>= 0.9: {sum(v >= 0.9 for v in MA + MI)}/6). J: A/IND {JA + JI} (<= 10: {sealed_A}/6 FAIL, "
                 f"heavy-tailed coordinate noise); C_ord {Jord} in [10,40]: {sealed_ord}/3 FAIL — kernel support 4 sigma = 8 bins "
                 f"spreads each of 15 boundaries over ~8 steps (the pre-committed 'report before touching the threshold'); "
                 f"C_perm {Jperm} (M < 0.7 PASS). Ordering pinned; thresholds deferred to a negative-set calibration (Will)")

# R14 — Stage 4
cpath4 = os.path.join(HERE, "stage4_circlemap_measured.json")
chk(os.path.exists(cpath4), "R14 stage4_circlemap_measured.json missing — run stage4_circlemap.py")
C4 = json.load(open(cpath4)) if os.path.exists(cpath4) else None
r14 = {}
if C4:
    Ks = C4["K"]
    iK = {k: i for i, k in enumerate(Ks)}
    sub1 = [k for k in Ks if k < 1]
    conv = C4["M1"]["max_abs_drho_1e4_1e5_per_K"]
    for k in sub1:
        chk(conv[iK[k]] < 1.1e-4, f"R14 Denjoy rail: K={k} |rho_1e4-rho_1e5| = {conv[iK[k]]:.2e}")
    r14["M1"] = (f"Denjoy rail PASS for K<1 (max {max(conv[iK[k]] for k in sub1):.1e} < 1.1e-4); above 1: "
                 f"{ {k: round(conv[iK[k]], 5) for k in Ks if k >= 1} } — convergence reported, not assumed")
    # M2 Farey rail + monotone
    res, cov = C4["M2"]["residence"], C4["M2"]["farey_coverage_K0"]
    far_ok, mono_ok, txt = True, True, []
    for key in res:
        f1 = res[key]["frac_f1_per_K"]
        dev = f1[iK[0.0]] / cov[key] - 1
        far_ok &= abs(dev) <= 0.25
        seq = [f1[iK[k]] for k in Ks if k <= 1]
        m = all(b >= a - 1e-12 for a, b in zip(seq, seq[1:]))
        mono_ok &= m
        txt.append(f"{key}: K=0 {f1[iK[0.0]]:.3f} vs Farey {cov[key]:.3f} ({dev:+.0%}); monotone on [0,1] {'yes' if m else 'NO'}")
    chk(far_ok, "R14 Farey-coverage rail at K=0 failed")
    chk(mono_ok, "R14 pin: residence fraction not monotone in K on [0,1]")
    r14["M2"] = ("Farey rail PASS; monotone PASS; " if far_ok and mono_ok else "FAIL; ") + "; ".join(txt)
    st = C4["M2"]["staircase_q50_1e3_per_K"]
    k1, k0 = st["1.0"], st["0.0"]
    r14["M2_staircase"] = (f"K=1 coverage {k1:.3f} > 0.85 as sealed, BUT K=0 (rigid rotation, the rival) reads {k0:.3f}: "
                           f"the test is INAPPLICABLE AS POSED (q<=50 at tol 1e-3 saturates the Farey coverage); the "
                           f"informative read is the K-dependence {[round(st[str(k)], 3) for k in Ks]}")
    chk(k0 > 0.8, "R14 pin: the staircase test's rival (K=0) no longer passes it — re-examine before re-posing")
    # M3 exact boundary within one grid step
    m3 = C4["M3"]; dOm = m3["grid_step"]
    for k in (0.25, 0.5, 0.75, 0.9):
        for proto in ("omega_c_ind", "omega_c_up", "omega_c_dn"):
            v = m3[proto][iK[k]]
            chk(v is not None and abs(v - k / (2 * 3.141592653589793)) <= dOm + 1e-12,
                f"R14 exact-tongue rail: K={k} {proto} = {v} vs K/2pi = {k / 6.2832:.4f}")
    r14["M3"] = "0/1 tongue boundary within one grid step (0.005) of K/2pi at K in {0.25, 0.5, 0.75, 0.9}, all three protocols"
    # M4 dead region + multistability rail + can-fire
    D4 = C4["M4"]["D_per_K"]; mu = C4["M4"]["multistability_frac_per_K"]
    for k in sub1:
        chk(D4[iK[k]] is not None and D4[iK[k]] <= dOm + 1e-12, f"R14 hysteresis in the dead region: K={k} D={D4[iK[k]]}")
        chk(mu[iK[k]] == 0.0, f"R14 multistability for K<1: K={k} frac={mu[iK[k]]}")
    chk(any(mu[iK[k]] > 0 for k in Ks if k > 1), "R14 witness: multistability never fires above K=1 — the arm cannot fire")
    r14["M4"] = (f"D(K) = {D4} (grid 0.005): dead region K<1 PASS; no hysteresis observed at K>1 either (admissible, "
                 f"no prediction); multistability {[round(m, 3) for m in mu]}: 0 for K<=1 (rail PASS), fires at K>1 "
                 f"(witness PASS)")

# R14b — M2b / M2c
for fn, tag in (("stage4c_staircase_measured.json", "M2b(grid)"), ("stage4d_staircase_random_measured.json", "M2c(random)")):
    fp_ = os.path.join(HERE, fn)
    chk(os.path.exists(fp_), f"R14b {fn} missing")
    if os.path.exists(fp_):
        cv = json.load(open(fp_))["coverage"]["1e-05"]
        k0, k1, k5, far = cv["0"], cv["1"], cv["0.5"], cv["farey_K0"]
        sep_ok = (k1 > 0.5) and (k1 - k0 > 0.3) and (k0 <= k5 <= k1)
        chk(sep_ok, f"R14b {tag}: separation failed (K0={k0:.3f}, K0.5={k5:.3f}, K1={k1:.3f})")
        if tag.startswith("M2b"):
            chk(abs(k0 * 1001 - 29) < 0.5, f"R14b pin: rational-grid K=0 coverage no longer the 29 Farey grid points ({k0 * 1001:.1f})")
            r14["M2b"] = (f"tol 1e-5: K=1 {k1:.3f} > 0.5 PASS, separation {k1 - k0:.2f} > 0.3 PASS; K=0 {k0:.4f} = 29/1001 exactly — "
                          f"phi(1)+phi(7)+phi(11)+phi(13) grid points of j/1001 ARE Farey fractions (B-grid rail); Farey clause FAIL, cause exact")
        else:
            chk(abs(k0 / far - 1) <= 0.30, f"R14b M2c: random-Omega K=0 coverage {k0:.4f} vs Farey {far:.4f} outside 30%")
            r14["M2c"] = (f"random Omega, tol 1e-5: K=0 {k0:.4f} vs Farey {far:.4f} ({k0 / far - 1:+.0%}) PASS; K=1 {k1:.3f} PASS; "
                          f"separation {k1 - k0:.2f} PASS; the staircase test now discriminates against its rival")

# R15 — Stage 4b
tpath4 = os.path.join(HERE, "stage4b_ringtongue_measured.json")
chk(os.path.exists(tpath4), "R15 stage4b_ringtongue_measured.json missing — run stage4b_ringtongue.py")
T4 = json.load(open(tpath4)) if os.path.exists(tpath4) else None
r15 = {}
if T4:
    vp1, vp3 = T4["vpin"]["0.1"]["max_speed"], T4["vpin"]["0.03"]["max_speed"]
    tg = T4["tongue"]
    step_g = tg["0.1"]["gamma"][1] - tg["0.1"]["gamma"][0]
    # rail: eps = 0 -> rho = 1 for gamma > 0
    rho0 = [r for g, r in zip(tg["0.0"]["gamma"], tg["0.0"]["rho"]) if g > 0]
    chk(all(abs(r - 1) < 1e-3 for r in rho0), f"R15 rail: eps=0 rho != 1 (min {min(rho0):.4f}, max {max(rho0):.4f})")
    # sealed: gamma*_pred(0.1) in (0.01, 0.02]
    in_i1b = 0.01 < vp1 <= 0.02
    # sealed: gamma*_pred(0.03) = 0.3 * gamma*_pred(0.1) within 25%
    scale_ok = abs(vp3 / (0.3 * vp1) - 1) <= 0.25
    # sealed: gamma*_meas within one grid step of gamma*_pred, each eps
    gm1, gm3 = tg["0.1"]["gamma_star_meas"], tg["0.03"]["gamma_star_meas"]
    meas_ok1 = gm1 is not None and abs(gm1 - vp1) <= step_g + 1e-12
    meas_ok3 = gm3 is not None and abs(gm3 - vp3) <= step_g + 1e-12
    # monotone rho(gamma) and rho -> 1
    mono = {e: all(b >= a - 1e-3 for a, b in zip(tg[e]["rho"], tg[e]["rho"][1:])) for e in ("0.03", "0.1")}
    r15["prediction"] = (f"gamma*_pred(0.1) = {vp1:.4f} {'PASS' if in_i1b else 'FAIL'} vs I1b (0.01, 0.02]; "
                         f"gamma*_pred(0.03) = {vp3:.4f} = {vp3 / vp1:.2f} x gamma*_pred(0.1) {'PASS' if scale_ok else 'FAIL'} (0.3 +-25%)")
    r15["tongue"] = (f"gamma*_meas(0.1) = {gm1} vs pred {vp1:.4f} {'PASS' if meas_ok1 else 'FAIL'} (one grid step {step_g:.2e}); "
                     f"gamma*_meas(0.03) = {gm3} vs pred {vp3:.4f} {'PASS' if meas_ok3 else 'FAIL'}; rho monotone {mono}; "
                     f"rho(0.03) at eps=0.1 = {tg['0.1']['rho'][-1]:.3f} ({'PASS' if tg['0.1']['rho'][-1] > 0.8 else 'FAIL'} > 0.8)")
    # pins (values recorded at banking; a change is a re-read, not a re-scope)
    chk(gm1 is not None and gm3 is not None, "R15 pin: a measured gamma* vanished (never unlocked on the grid)")
    r15["rail"] = f"eps=0: rho in [{min(rho0):.4f}, {max(rho0):.4f}] (omega = gamma) PASS"

# R7 — plan hygiene
plan = os.path.join(HERE, "rotational-dynamics-build-plan.md")
txt = open(plan).read()
chk(txt.startswith("# Rotational Dynamics / Attractor Geometry — Build Plan v5"), "R7 plan header not v5")
chk("verify ID" not in txt, "R7 'verify ID' tag survives in plan")
chk(not any(f.endswith("Zone.Identifier") for f in os.listdir(HERE)), "R7 Zone.Identifier stray in ring/")

_margin = abs(row(T_long, 1e-4)["lam1_median"]) / D.LAM1_TOL
print(f"ring board: {len(fails)} failure(s).")
print(f"  R6 built detector: nearest confusable silent by {_margin:.0f}x on lam1 "
      f"(the number doing the work); floor |lam1|={abs(row(T_long, 0.0)['lam1_median']):.1e}")
print(f"     tallies: sens {rates['sensitivity']} CP95 {sens_ci['honest_claim']} "
      f"[{sens_ci['treatment']}]; spec {rates['specificity']} CP95 "
      f"{spec_ci['honest_claim']} [{spec_ci['treatment']}] -- tallies this "
      f"small are not verdicts")
print(f"  R4 standing invariant: {sum(1 for t in r4 if t[2].startswith('CONVERGED rel_err'))} "
      f"converged-above-floor row(s) compared, "
      f"{sum(1 for t in r4 if t[2] == 'CONVERGED_FLOOR')} at floor, "
      f"{sum(1 for t in r4 if t[2].startswith('NOT_CONVERGED'))} not converged (attributed)")
print(f"  R5 collapse is an eps*T contour: T={T_short}:"
      f"{[r_['n_distinct'] for r_ in sorted([x for x in rows if x['T'] == T_short], key=lambda x: x['eps'])]} "
      f"T={T_long}:{[r_['n_distinct'] for r_ in long_rows]}")
print(f"  R1 declared-only (not certified, by design): {sorted(D.DECLARED_ONLY)}; "
      f"Stage 1 cannot certify: {sorted(D.STAGE1_CANNOT_CERTIFY)}")
print(f"  R8 contour: c = {fit['c']:.4e} rad/tau per unit eps (max rel resid "
      f"{fit['max_rel_resid']:.3f}, {fit['n_rows']} rows); per-P: " +
      "; ".join(f"P={k:g}: {v}" for k, v in r8.items()))
if w20k:
    print(f"  R4b delta defect pinned: at eps=0.01/T=20000 ratio(delta=0.05)={bad:.2f}, "
          f"ratio(delta=0.005)={good:.2f}")
if r9:
    print("  R9 measure 2, sealed predictions scored as declared:")
    for k, v in r9.items():
        print(f"     {k}: {v}")
if r10:
    print("  R10 coverage test, sealed arms scored as declared:")
    for k, v in r10.items():
        print(f"     {k}: {v}")
if r11:
    print("  R11 Stage 2, sealed hypotheses scored as declared:")
    for k, v in r11.items():
        print(f"     {k}: {v}")
if r12:
    print("  R12 Stage 3a, sealed arms scored as declared:")
    for k, v in r12.items():
        print(f"     {k}: {v}")
if r13:
    print("  R13 Stage 3b, sealed arms scored as declared:")
    for k, v in r13.items():
        print(f"     {k}: {v}")
if r17:
    print("  R17 Stage 3e MSD, sealed clauses per row:")
    for k, v in r17.items():
        print(f"     {k}: {v}")
if r14:
    print("  R14 Stage 4, rails and sealed arms:")
    for k, v in r14.items():
        print(f"     {k}: {v}")
if r15:
    print("  R15 Stage 4b, prediction from a measured quantity:")
    for k, v in r15.items():
        print(f"     {k}: {v}")
for f in fails:
    print("FAIL:", f)
sys.exit(1 if fails else 0)
