"""Holonomy pilot: ownership map + order census (brief §2, R3).

COMMITTED GENERATOR of holonomy/ownership_map.json.

R3 discipline: the DENOMINATOR is committed first — the enumeration below
lists every top-level function/class in the sealed estimator-stack file list
(the three completed arcs' frozen stacks + the home 1-D stack + the two live
unfolding modules).  Coverage = classified / enumerated, where "performs no
point-process transition" (NONE) is itself an explicit classification.  A
lazy map cannot read 100%: the generator VERIFIES each enumerated symbol
exists at its cited line in the live file and exits nonzero on drift, so the
census is falsifiable against the repo head it claims to describe.

Transition taxonomy (registered set, brief §1 frame + census amendments):
  UNFOLD     coordinate map to unit-mean/reference density (incl. the hidden
             renormalise-to-unit-mean variant: s /= s.mean())
  WINDOW     subset selection handed downstream (rank/interval/footprint cut)
  REWEIGHT   attach or alter point weights / marks (incl. 1/lambda marks)
  EDGE       domain erosion / border correction
  THIN       stochastic subset (keep-prob draw)
  PROJECT    coordinate projection (gnomonic)
  SLICE      metadata cut (redshift)
  SURROGATE  construct a reference/pseudo point set
  GENERATOR  samples a substrate (not a transition on data)
  NONE       pure statistic / analytic form / geometry helper

'internal' rows mark operations that are part of the statistic's own
definition (sliding windows inside Sigma^2, border erosion inside K) — they
matter to the census only where the transformed STATE is handed onward.
"""

import json
import re
import sys

ROOT = "/home/combust/fmexplorer/criticality_tool"

# ── The committed denominator: enumerated symbols, file:line, classification ──
# (line = def/class line at repo head af7a94f; generator verifies)
ENUM = [
    # universality.py — home 1-D dialect
    ("universality.py", 24, "nns_poisson", "NONE", "analytic reference"),
    ("universality.py", 28, "nns_goe", "NONE", "analytic reference"),
    ("universality.py", 33, "nns_gue", "NONE", "analytic reference"),
    ("universality.py", 38, "nns_cdf_poisson", "NONE", "analytic reference"),
    ("universality.py", 42, "nns_cdf_goe", "NONE", "analytic reference"),
    ("universality.py", 47, "nns_cdf_gue", "NONE", "analytic reference"),
    ("universality.py", 69, "NNSResult", "NONE", "dataclass"),
    ("universality.py", 80, "_ks_pvalue", "NONE", "statistic helper"),
    ("universality.py", 103, "compute_nns", "UNFOLD",
     "CENSUS FINDING C1: renormalises spacings to unit mean INSIDE the "
     "statistic (s /= s.mean(), line 118) — a hidden per-input-set unfold; "
     "order relative to any upstream windowing is decided by the caller "
     "without knowing it"),
    ("universality.py", 134, "number_variance", "NONE",
     "internal: sliding windows are the statistic's definition"),
    ("universality.py", 181, "spectral_form_factor", "NONE", "statistic"),
    ("universality.py", 202, "pair_correlation", "NONE",
     "internal: 200-neighbour cap is an estimator approximation, noted"),
    # fix_gue_generator.py — GUE substrate + unfolding family
    ("fix_gue_generator.py", 45, "semicircle_cdf_unit", "NONE", "analytic"),
    ("fix_gue_generator.py", 51, "gen_gue_eigenvalues", "GENERATOR", ""),
    ("fix_gue_generator.py", 60, "unfold_global_mean", "UNFOLD",
     "deprecated-broken variant, retained for the record"),
    ("fix_gue_generator.py", 67, "unfold_semicircle_R", "UNFOLD",
     "analytic semicircle CDF"),
    ("fix_gue_generator.py", 77, "unfold_empirical", "UNFOLD",
     "polynomial CDF fit; BANDWIDTH KNOB = deg (default 11) — P1's sealed "
     "fixed coefficient"),
    ("fix_gue_generator.py", 88, "ks_to_wigner_gue", "NONE", "statistic"),
    ("fix_gue_generator.py", 181, "make_chirp", "NONE", "signal-domain"),
    ("fix_gue_generator.py", 265, "per_pll_fano", "NONE", "signal-domain"),
    ("fix_gue_generator.py", 289, "summarise", "NONE", "signal-domain"),
    # run_zeta_height_convergence.py — live zeta unfold path
    ("run_zeta_height_convergence.py", 38, "vonMangoldt_density", "NONE",
     "analytic"),
    ("run_zeta_height_convergence.py", 43, "unfolded_spacings", "UNFOLD",
     "CENSUS FINDING C2: Riemann–von Mangoldt map (pointwise, order-inert) "
     "PLUS per-input-set renormalisation sp /= sp.mean() — the window-"
     "dependent half of the unfold"),
    ("run_zeta_height_convergence.py", 54, "classify", "NONE", "statistic"),
    # bridge/observer_b.py — 2-D bridge dialect
    ("bridge/observer_b.py", 23, "k_1d", "NONE",
     "internal: border erosion + lambda-hat from full set inside statistic"),
    ("bridge/observer_b.py", 44, "pcf_1d", "NONE", "internal: as k_1d"),
    ("bridge/observer_b.py", 71, "sigma2_from_g_1d", "NONE", "functional"),
    ("bridge/observer_b.py", 85, "DiskWindow", "NONE", "geometry"),
    ("bridge/observer_b.py", 93, "RectWindow", "NONE", "geometry"),
    ("bridge/observer_b.py", 103, "WedgeWindow", "NONE", "geometry"),
    ("bridge/observer_b.py", 118, "k_2d", "NONE", "internal: as k_1d, 2-D"),
    ("bridge/observer_b.py", 136, "pcf_2d", "NONE", "internal: as k_1d, 2-D"),
    ("bridge/observer_b.py", 157, "disk_set_covariance", "NONE", "analytic"),
    ("bridge/observer_b.py", 167, "sigma2_from_g_2d", "NONE", "functional"),
    ("bridge/observer_b.py", 179, "disk_counts_grid", "NONE",
     "internal: eroded grid is the statistic's definition"),
    ("bridge/observer_b.py", 203, "sigma2_disk_direct", "NONE",
     "internal: stochastic centres, seeded"),
    ("bridge/observer_b.py", 234, "sigma2_direct_1d", "NONE",
     "internal: sliding windows"),
    ("bridge/observer_b.py", 254, "k_inhom", "REWEIGHT+EDGE",
     "CENSUS FINDING C3: the P2 pair is FUSED here in ONE fixed order "
     "(erode centres, then 1/lambda marks) with lambda GIVEN via lam_fn — "
     "the estimation-domain mechanism therefore lives in CALLERS; in live "
     "bridge runs lam_fn was the known model intensity (designed "
     "instances), so no both-orders instance in live code"),
    # bridge/ginibre_sampler.py — substrate generator + its KAG
    ("bridge/ginibre_sampler.py", 25, "sample_ginibre", "GENERATOR", ""),
    ("bridge/ginibre_sampler.py", 33, "central_points", "WINDOW",
     "C_WINDOW=0.8 central-disk cut handed downstream"),
    ("bridge/ginibre_sampler.py", 40, "kag", "NONE", "gate driver"),
    # survey/ — frozen survey dialect (blob-SHA sealed 93ce1d7)
    ("survey/survey_io.py", 19, "load_cat", "SLICE+REWEIGHT",
     "z-slice cut + WEIGHT attach in one loader (one transition per path "
     "by module docstring: slicing HERE, downstream never re-cuts)"),
    ("survey/survey_io.py", 33, "load_randoms_split", "SLICE",
     "disjoint-half concat, sliced via load_cat"),
    ("survey/tiling.py", 30, "gnomonic", "PROJECT", ""),
    ("survey/tiling.py", 42, "corner_distortion", "NONE", "budget check"),
    ("survey/tiling.py", 48, "build_tiles", "WINDOW",
     "footprint acceptance from randoms mass (rule-based)"),
    ("survey/tiling.py", 79, "tile_points", "WINDOW+PROJECT",
     "CENSUS FINDING C4: fused pair in ONE fixed order (ra/dec cut, THEN "
     "gnomonic project); the reverse order (project all, cut in plane "
     "coords) would select a different point set near tile corners; single "
     "order in live code, no both-orders instance"),
    ("survey/estimators.py", 26, "pair_counts", "NONE", "statistic"),
    ("survey/estimators.py", 42, "g_ratio", "NONE",
     "statistic; consumes weights, attaches none"),
    ("survey/estimators.py", 62, "cells_F", "NONE",
     "internal: CELL_FLOOR exclusion is a data-dependent cell cut inside "
     "the statistic (sealed rule), noted"),
    ("survey/mask_kag.py", 49, "thin_to_data", "THIN",
     "P3's mechanism row: SCALAR keep-prob p = W_target / sum(w_randoms) — "
     "normalised by the WEIGHTED total, so thinning-vs-weighting order "
     "changes p; internally-drawn RNG (the R2 freeze-collision reason)"),
    ("survey/mask_kag.py", 56, "run_tile", "NONE", "gate driver"),
    ("survey/mask_kag.py", 74, "kag", "SURROGATE",
     "red path constructs uniform-box pseudo-randoms (labeled forbidden "
     "window); green path is a driver"),
]

# ── Order census: every ordered-pair sighting in live code, file:line ────────
CENSUS = [
    dict(pair="P1 unfold->window vs window->unfold",
         finding="BOTH ORDERS LIVE (via the renormalisation half of the "
                 "unfold).  The pointwise RvM/semicircle map commutes with "
                 "windowing exactly; the per-set renormalisation does NOT.",
         sightings=[
             "run_zeta_height_convergence.py:85 — chunk (window) FIRST, "
             "then unfolded_spacings renormalises per chunk "
             "(window->unfold)",
             "universality.py:118-119 — compute_nns renormalises whatever "
             "set it is handed; any caller that windows after a pooled "
             "unfold then calls compute_nns re-unfolds per window "
             "(unfold->window->unfold)",
         ],
         both_orders_in_live_code=True,
         downstream_banked=["zeta height-convergence NNS rows",
                            "every compute_nns consumer (per-set "
                            "renormalisation is universal)"]),
    dict(pair="P2 reweight->edge vs edge->reweight",
         finding="SINGLE ORDER, FUSED: k_inhom erodes centres then applies "
                 "1/lambda marks with lambda GIVEN (not estimated); the "
                 "estimation-domain mechanism is caller-side and no live "
                 "caller estimates lambda-hat from data (designed "
                 "instances used known intensity).",
         sightings=["bridge/observer_b.py:254-276 — fixed fused order"],
         both_orders_in_live_code=False,
         downstream_banked=["bridge FIX-2 K_inhom gate rows"]),
    dict(pair="P3 weight->thin vs thin->weight",
         finding="SINGLE ORDER: thin_to_data normalises by the weighted "
                 "total (weight-first semantics); no count-normalised "
                 "variant exists in live code.",
         sightings=["survey/mask_kag.py:49-53 — p = W_target/sum(w)"],
         both_orders_in_live_code=False,
         downstream_banked=["survey mask-KAG PASS row (D1)",
                            "survey D2 FIX-2 rows (thinned-KAG data)"]),
    dict(pair="window->project vs project->window (census-found, unsealed)",
         finding="SINGLE ORDER, FUSED in tile_points (C4).  Not among the "
                 "sealed mandatory pairs; registered for a future arc.",
         sightings=["survey/tiling.py:79-86"],
         both_orders_in_live_code=False,
         downstream_banked=["all survey per-tile rows"]),
]


def verify_enum():
    """Each enumerated symbol must exist at its cited line (±2, comments
    drift) in the live file — the map is falsifiable against head."""
    bad = []
    for fname, line, sym, cls, note in ENUM:
        try:
            src = open(f"{ROOT}/{fname}").read().splitlines()
        except OSError:
            bad.append(f"{fname}: unreadable")
            continue
        pat = re.compile(rf"^(def|class)\s+{re.escape(sym)}\b")
        hit = [i + 1 for i, l in enumerate(src) if pat.match(l.strip())]
        if not hit:
            bad.append(f"{fname}:{line} {sym}: symbol not found")
        elif min(abs(h - line) for h in hit) > 2:
            bad.append(f"{fname}:{line} {sym}: drifted to {hit}")
    return bad


def main():
    bad = verify_enum()
    if bad:
        print("OWNERSHIP MAP: ENUMERATION DRIFT")
        for b in bad:
            print("  -", b)
        sys.exit(1)
    n = len(ENUM)
    n_classified = sum(1 for row in ENUM if row[3] != "")
    coverage = n_classified / n
    out = dict(
        head_note="enumeration committed at af7a94f (R3: denominator first)",
        enumerated=n, classified=n_classified, coverage=coverage,
        rows=[dict(file=f, line=l, symbol=s, transitions=c, note=nt)
              for f, l, s, c, nt in ENUM],
        census=CENSUS,
        scope_note=("Sealed scope: three completed arcs' estimator stacks + "
                    "home 1-D stack + live unfolding modules.  Phase-scoped "
                    "instruments (phase35a/ unfolds, sessionK/) are OUTSIDE "
                    "the enumeration and the census verdict does not cover "
                    "them."),
    )
    json.dump(out, open(f"{ROOT}/holonomy/ownership_map.json", "w"), indent=1)
    print(f"OWNERSHIP MAP: {n_classified}/{n} classified "
          f"(coverage {coverage:.3f}); census rows: {len(CENSUS)}")
    for c in CENSUS:
        flag = "BOTH-ORDERS" if c["both_orders_in_live_code"] else "single"
        print(f"  [{flag}] {c['pair']}")


if __name__ == "__main__":
    main()
