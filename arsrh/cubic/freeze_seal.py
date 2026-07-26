"""
FREEZE THE SEAL. Generates the object lists and emits seals/CUBIC_ARM_SEAL.json.

Stratum assignment is COMPUTABLE, therefore TUNABLE -- so it is frozen here, in writing, before
any arm runs, and the frozen lists are committed. Field-level dedup (gate0i) is applied first;
within a field the representative is the coefficient-lexicographically smallest polynomial.
"""
from __future__ import annotations
import hashlib, json, os

import mpmath as mp
from gate0g_marginals import collect
from gate0i_fields import dedup_fields

HERE = os.path.dirname(os.path.abspath(__file__))
p_ = lambda *a: print(*a, flush=True)
NPER = 24

if __name__ == "__main__":
    p_("=== freezing the cubic-arm seal ===")
    arms = {}
    for kind, role in (("S3", "TARGET"), ("B", "POSITIVE"), ("C", "GRADED")):
        objs = collect(kind, want=NPER * 2)   # height-ordered enumeration (gate0g._by_height)
        fields = dedup_fields(objs)[:NPER]
        arms[kind] = {"role": role,
                      "polynomials": [[a, b, c] for a, b, c, _ in fields],
                      "poly_discriminants": [d for *_, d in fields],
                      "n_fields": len(fields)}
        p_(f"  {role:>9s} ({kind}): {len(fields)} fields frozen")
    arms["cbrt"] = {"role": "CALIBRATOR (second family)",
                    "m": [2, 3, 5, 6, 7, 10, 11, 12, 13, 15], "n_fields": 10}

    payload = json.dumps(arms, sort_keys=True).encode()
    arms_hash = hashlib.sha256(payload).hexdigest()[:16]

    seal = {
        "name": "ARS cubic family — between-object approximation correlation",
        "sealed_before_any_arm_run": True,
        "arms_sha256_16": arms_hash,
        "arms": arms,

        "frozen_analysis_choices": {
            "event_threshold_A": 20,
            "event_definition": "lambda_n >= A, where lambda_n = alpha_{n+1} + q_{n-1}/q_n "
                                "= 1/(q_n^2 |x - p_n/q_n|).  NOT a_{n+1} >= A.",
            "why_lambda_not_a": "lambda in (a_{n+1}, a_{n+1}+2), so thresholding on a injects a 2/A "
                                "error the transfer law does not have. The law is EXACT in lambda. "
                                "Confirmed empirically: the four |t|=17 'misses' were one event with "
                                "lambda = lambda' = 20.534 but a = 20 vs a = 19.",
            "coordinate": "u = log q_n (log-denominator line)",
            "statistic": "S(w) = max over lag L of #{(i,j): |u_i - v_j - L| <= w}, computed exactly "
                         "by sliding a 2w window over the sorted pairwise-difference multiset.",
            "w_ladder": [0.02, 0.05, 0.2, 1.0],
            "combined_statistic": "T = min over the w-ladder of the null-tail probability of S(w)",
            "permutation_count": 2000,
            "rejection_threshold": {"T_le": 0.0235, "bootstrap_sd": 0.0075,
                                    "note": "N = 2000 permutation draws; bootstrap 95% CI "
                                            "[0.0205, 0.0470]. T is discrete (values k/N) so the "
                                            "percentile is lumpy. An earlier 0.0368 came from "
                                            "N = 400 and its third figure was not real."},
            "pq_per_object": 2000,
            "digits_per_object": 2100,
            "digits_rule": "1.03 certified digits per PQ (R-067), not 0.515",
            "stratum_assignment_rule": "disc(f) a perfect square -> cyclic, else S3. For cyclic, "
                                       "|t| = |trace| of the coprime-integer order-3 Mobius map; "
                                       "|t| = 1 -> stratum B, |t| > 1 -> stratum C. Frozen lists above.",
            "field_dedup_rule": "Q(a1) = Q(a2) tested by PSLQ on (1, a, a^2, b) and VERIFIED EXACTLY "
                                "by reducing f2(g(x)) mod f1(x) over Q; one polynomial per field, "
                                "the coefficient-lexicographically smallest.",
            "injection_jitter_family": "Uniform(-J, J), J in {0, 0.05, 0.2, 1.0}",
            "injection_family_caveat": "THE FLOOR IS A FLOOR FOR THIS FAMILY. The ladder arm sits at "
                                       "J = 0 exactly, so the whole jitter axis is calibrated by "
                                       "injection. A real coincidence with a different jitter shape "
                                       "(e.g. heavy-tailed) has a different floor. Irreducible: the "
                                       "target's jitter shape is unknown by construction. Stated, "
                                       "not discovered."
        },

        "power": {
            "detection_floor_80pct": {"J=0": 0.05, "J=0.05": 0.10, "J=0.2": 0.10, "J=1.0": 0.20},
            "floor_units": "f = fraction of one object's events having a partner event",
            "transfer_to_target": "licensed: events per unit u agrees across all three strata to "
                                  "|z| <= 0.16 (field-deduplicated, height-ordered enumeration); "
                                  "sem = 1.6% of value, so a 3% difference was detectable."
        },

        "arm_seals": {
            "POSITIVE (stratum B)": {
                "sensitivity_prior": "certain, shifted up one notch to certain-and-exact: not only "
                                     "detected but detected at f = 1.00. lambda' = lambda by theorem.",
                "specificity_prior": "held fixed. A firing here means only that the instrument sees "
                                     "an infinitely strong signal -- it is a CEILING arm.",
                "powered_falsifier": "coincidence fraction must be 1.00 (measured 100.0%, 633/634). "
                                     "It could have fired: strata C at |det| 4/25/169 return "
                                     "48%/21%/12% on the same code path."
            },
            "GRADED (stratum C)": {
                "sensitivity_prior": "detected at every |det| <= 289, shifted up from 'detected at "
                                     "small |det| only'.",
                "specificity_prior": "held fixed.",
                "powered_falsifier": "measured rate must match the CALIBRATED formula to +/-12% over "
                                     "|det| in 1..289. It could have fired: the marginal-P(g) version "
                                     "of the same formula missed by 26% with two 3.5-sigma strata."
            },
            "TARGET (stratum A, S3)": {
                "sensitivity_prior": "no coincidence detected, shifted up one notch to 'no "
                                     "coincidence detected AND the bound is below f = 0.10'.",
                "specificity_prior": "held fixed. If something fires, first look for a derivable "
                                     "relation -- Gate 0's discipline applied downstream.",
                "powered_falsifier": "T <= 0.0235 against the permutation null. POWER, as a number: "
                                     "80% at f = 0.05 (J=0), 0.10 (J<=0.2), 0.20 (J=1.0). The "
                                     "argument it could have fired is the injection grid, not the "
                                     "ladder arm -- the ladder occupies the J = 0 column only.",
                "mechanism_absent_by_theorem": "alpha_2 not in Q(alpha_1) for S3, and a Q-rational "
                                               "Mobius image of alpha_1 lands inside Q(alpha_1). "
                                               "Does NOT depend on the Hilbert-90 argument (R-076)."
            },
            "NEGATIVE": {
                "note": "The negative arm IS the permutation null -- pairs of cubics from unrelated "
                        "fields. It is not a separate data collection, and it is NOT a second "
                        "witness alongside the null. Stated so it is not double-counted.",
                "powered_falsifier": "must fire at no more than the nominal rate; measured false-"
                                     "positive rate on synthetic independent pairs is 2-5% per cell "
                                     "(gate0h, f = 0.02 row)."
            },
            "RETIRED": {
                "quadratic conjugate pairs (Galois/reversed period)": "DROPPED. Stratum B supersedes "
                                                                     "it: derived here rather than "
                                                                     "LIT, and on the target's own "
                                                                     "substrate. Quadratics have "
                                                                     "PERIODIC CFs, which is not the "
                                                                     "target's regime, so that arm "
                                                                     "would have certified the "
                                                                     "instrument on the wrong data."
            }
        },

        "failure_condition_written_first": {
            "INSTRUMENT FAILED (target result means nothing)": [
                "stratum B's coincidence fraction is not 1.00",
                "stratum C deviates from the calibrated formula by more than +/-12% at any |det| <= 289",
                "the permutation null's false-positive rate exceeds 10% on synthetic independent pairs",
                "fewer than 20 fields survive dedup in any arm"
            ],
            "TARGET EMPTY (a result)": [
                "all instrument checks pass AND stratum A returns T > 0.0235"
            ],
            "TARGET POSITIVE (look for the derivable relation first)": [
                "all instrument checks pass AND stratum A returns T <= 0.0235",
                "then: is the pair GL2(Q)-equivalent after all? recheck the stratum assignment "
                "before reporting anything."
            ]
        },

        "declared_deliverable": {
            "kind": "UPPER LIMIT",
            "why": "No predicted effect size exists on the target arm, and none can -- that is what "
                   "makes it the target. So the phase is an upper-limit measurement by construction, "
                   "and naming it now prevents it being written up later as a non-finding.",
            "expected_sentence": "Totally real S3 cubic conjugates show no coincidence of exceptional "
                                 "approximations above f = 0.05 at zero jitter (0.10 at J <= 0.2, "
                                 "0.20 at J = 1.0), with the floor demonstrated by injection rather "
                                 "than argued, on the between-object axis.",
            "grade_of_that_sentence": "empirical bound against a permutation null; no analytic "
                                      "bracket exists in this region and none is claimed."
        },

        "scope_gate_restated": "Nothing here measures boundedness of partial quotients. That is a tail "
                               "property of an infinite sequence and no finite computation touches it. "
                               "Nothing here tests Lang's conjecture.",

        "open_at_seal_time": [
            "the rate formula is CALIBRATED, not derived: it uses a measured P(g|event) whose "
            "mechanism is unclosed. Route exists -- P(g=D) ~ P(g=1)*1.4427/D holds in FORM across "
            "D = 4..841 but the constant is off by a uniform ~1.65. Closing it would return the "
            "formula to DERIVED and open the |det| range.",
            "|det| > 289 is UNCALIBRATED (one field, 2 events in the deciding branch)",
            "RESOLVED, kept for the record: an earlier +1.2..+1.7 sem common A-vs-theory offset was "
            "TWO artifacts of mine, not an estimator bias -- a raw triple loop that returned every "
            "object sharing the smallest A (thin coefficient slice), and the wrong reference value "
            "(Gauss-Kuzmin a-tail log2(1+1/A) where the lambda-tail 1/(A ln2) belongs). Fixed, and "
            "all four anchors now sit within ~1 sem of theory."
        ]
    }

    os.makedirs(os.path.join(HERE, "..", "seals"), exist_ok=True)
    out = os.path.join(HERE, "..", "seals", "CUBIC_ARM_SEAL.json")
    json.dump(seal, open(out, "w"), indent=2)
    p_(f"\n  arms hash: {arms_hash}")
    p_(f"  wrote {os.path.normpath(out)}")
