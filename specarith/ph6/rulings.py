"""Phase 6 Layer B gate rulings as code (review M6; PROPOSED AMENDMENT A10, pending Will).

Seal §8 states each gate's Layer B requirement in prose; these functions are the single place that turns readouts into
gate verdicts, so nobody re-types a rule. Each returns (verdict, reasons) with verdict PASS or FAIL.

Conventions (from ph6lib.t3_verdict): verdict in {PASS, FAIL, NOT RESOLVABLE, INAPPLICABLE}; details["failed_arms"] maps
arm -> list of n; details["R"] is the resolvable set; "the required failure" of a cross-reading (e.g. G0 read against
chi_-4 weights) is T3 = FAIL (under proposed A3 the minimum set is taken over the weight vector's support).
"""
import numpy as np

import ph6lib as L

NS = list(L.LINE_NS)
POWERS_OF_2 = [2, 4, 8, 16, 32, 64]


def _idx(n):
    return NS.index(n)


def g0_layer_b(v_own, v_other):
    """G0 (and G0-c): vs zeta weights PASS, and vs chi_-4 weights FAIL."""
    reasons = []
    if v_own[0] != "PASS":
        reasons.append(f"vs zeta: {v_own[0]} {v_own[1].get('failed_arms', {})}")
    if v_other[0] != "FAIL":
        reasons.append(f"vs chi4: {v_other[0]} (required FAIL)")
    return ("PASS" if not reasons else "FAIL"), reasons


def g0c_layer_b(v_own, v_other, r_size_window=(22, 30)):
    """G0-c: as G0, plus M subset of R and |R| inside the sealed window (seal §8b; window subject to proposed A4)."""
    verdict, reasons = g0_layer_b(v_own, v_other)
    R = set(v_own[1].get("R", []))
    if not set(L.T3_MIN_SET) <= R:
        reasons.append(f"M not in R: R = {sorted(R)}")
    lo, hi = r_size_window
    if not lo <= len(R) <= hi:
        reasons.append(f"|R| = {len(R)} outside [{lo}, {hi}]")
    return ("PASS" if not reasons else "FAIL"), reasons


def g2_layer_b(c, B, v_own, v_other):
    """G2: vs chi_-4 weights PASS -- which, through the arms, already requires SILENCE at the powers of 2 and the SIGN of
    every n in R (3 +, 5 -, 7 +, 9 - when in R); vs zeta weights FAIL. The four named sign arms are also reported
    explicitly, and a named sign arm whose n is not in R is reported as NOT RESOLVABLE (never scored)."""
    reasons = []
    if v_own[0] != "PASS":
        reasons.append(f"vs chi4: {v_own[0]} {v_own[1].get('failed_arms', {})}")
    if v_other[0] != "FAIL":
        reasons.append(f"vs zeta: {v_other[0]} (required FAIL)")
    R = set(v_own[1].get("R", []))
    named = {}
    for n, sgn in ((3, +1), (5, -1), (7, +1), (9, -1)):
        if n not in R:
            named[n] = "NOT RESOLVABLE"
        else:
            named[n] = "PASS" if np.sign(np.real(c[_idx(n)])) == sgn else "FAIL"
            if named[n] == "FAIL":
                reasons.append(f"named sign arm at {n} FAIL")
    silent2 = {n: bool(abs(c[_idx(n)]) <= B[_idx(n)]) for n in POWERS_OF_2}
    if not all(silent2.values()):
        reasons.append(f"silence at powers of 2: {silent2}")
    return ("PASS" if not reasons else "FAIL"), reasons + [f"named sign arms: {named}"]


def g4_confusable(c, B, v_zeta, lam):
    """G4, lambda = log 2: POSITION fires at every power of 2 in R (|c| > B); |c - lam| <= B there (c = +log 2 each);
    SILENCE holds at 3, 5, 7; T3 vs zeta = FAIL with WEIGHT or SIGN among the failed arms (attribution CONTAINS
    WEIGHT/SIGN; POSITION at 3, 5, 7 may also be listed, since those n are in R with c = 0)."""
    reasons = []
    R = set(v_zeta[1].get("R", []))
    for n in POWERS_OF_2:
        i = _idx(n)
        if n in R and not abs(c[i]) > B[i]:
            reasons.append(f"POSITION did not fire at {n}")
        if not abs(c[i] - lam) <= B[i]:
            reasons.append(f"c_{n} = {c[i]:.4f} not within B of +log 2")
    for n in (3, 5, 7):
        if not abs(c[_idx(n)]) <= B[_idx(n)]:
            reasons.append(f"not silent at {n}")
    arms = set(v_zeta[1].get("failed_arms", {}))
    if v_zeta[0] != "FAIL" or not ({"WEIGHT", "SIGN"} & arms):
        reasons.append(f"T3 vs zeta = {v_zeta[0]} arms {sorted(arms)} (required FAIL with WEIGHT or SIGN)")
    return ("PASS" if not reasons else "FAIL"), reasons


def g4_incommensurate(v_zero, v_zeta):
    """G4, lambda = 1.2345: silent at all n <= 90 (vs zero weights PASS); T3 vs zeta = FAIL with POSITION among the arms."""
    reasons = []
    if v_zero[0] != "PASS":
        reasons.append(f"vs zero: {v_zero[0]} {v_zero[1].get('failed_arms', {})}")
    arms = set(v_zeta[1].get("failed_arms", {}))
    if v_zeta[0] != "FAIL" or "POSITION" not in arms:
        reasons.append(f"T3 vs zeta = {v_zeta[0]} arms {sorted(arms)} (required FAIL with POSITION)")
    return ("PASS" if not reasons else "FAIL"), reasons


def g3_null(res_kind, kind):
    """G3 / G3-c per family: silence within the binomial allowance; zeta rejection in 100% of draws; GUE positive control
    >= 95%."""
    reasons = []
    if res_kind["silence"] != "PASS":
        reasons.append(f"{kind} silence exceed {res_kind['silence_exceed']} > {res_kind['allowance']}")
    if res_kind["zeta_rejection"] != "PASS":
        reasons.append(f"{kind} zeta rejected only {res_kind['zeta_rejected']}/100")
    if kind == "gue" and res_kind.get("positive_control") != "PASS":
        reasons.append(f"positive control {res_kind.get('positive_control_pass')}/100")
    return ("PASS" if not reasons else "FAIL"), reasons
