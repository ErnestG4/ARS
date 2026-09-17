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
for f in fails:
    print("FAIL:", f)
sys.exit(1 if fails else 0)
