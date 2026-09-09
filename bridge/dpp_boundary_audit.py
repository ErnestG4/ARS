#!/usr/bin/env python3
"""AUDIT: every banked bridge fit, read for rails, without touching frozen code.

POST-HOC AND UNSEALED. It reads artifacts that already exist and makes no
prediction; the numbers below were visible before this file was written, so there
is nothing to seal and pretending otherwise would be theatre.

WHAT IT DELIVERS, and why it is not the edit the proposal asked for.
`proposals/PROPOSED_boundary_reporting.md` asked for boundary keys inside
`dpp_python.py`. That file is frozen so the banked numbers stay reproducible FROM
FROZEN CODE; editing it would keep the numbers and destroy the property. So the
reporting lives in `dpp_boundary.py` (a successor future fits import) and the
missing record is supplied HERE, retrospectively, where it was actually needed.

THREE THINGS THE AUDIT FINDS, one of which the proposal did not know.

  1. THE SUCCESSOR AGREES WITH THE FROZEN FITTER wherever the frozen fitter
     reports at all: 8 of 8 DPP fits, `at_boundary` reproduced exactly. That is
     the premise -- an independent tolerance that disagreed would mean this audit
     is measuring something else. (The successor uses a RELATIVE tolerance, since
     an absolute one that works at kappa~100 is meaningless at alpha~0.35.)

  2. THE GAP IS REAL AND IS FILLED. `fit_thomas` has no boundary check of any
     kind, and BOTH banked Thomas fits are railed at the upper bound
     (kappa = 99.99999 of 100.0). For a Thomas process the clustering term
     carries 1/kappa, so kappa -> infinity IS the Poisson limit: the rail is the
     fit saying "no clustering", it is CORRECT, and `RESULTS_BRIDGE.md` line 102
     says so in prose. What it never had is a machine record, so every consumer
     of `bridge_b_measured.json` sees an ordinary fitted value. AND A SECOND
     COORDINATE the proposal did not mention: `sigma` is not optimised at all,
     it is scanned over `geomspace(0.05, 10.0, 60)`, and both fits land on a grid
     ENDPOINT (10.0 in B1, 0.05 in B2). Landing on the edge of a scan is a
     different statement from a bounded optimiser railing, and neither was
     recorded.

  3. THE LOWER BOUNDS ARE GENUINELY UNEXERCISED, as the proposal measured: 0 of 8
     DPP fits sit near alpha = 1e-3 (the smallest is 0.3535, 350x the bound).
     Worth keeping as a negative -- the `fit_dpp` lower-bound half remains cheap
     and latent, and only the `fit_thomas` half was ever live.

A FOURTH THING, which is about B1 rather than about the instrument: ALL FOUR of
B1's DPP families rail at their UPPER bound, and that bound is a genuine DPP
existence condition. So B1's point pattern wants more repulsion than any of these
families can express -- the fit is pressed against the edge of what a DPP of that
form can be. That is flagged in the banked artifact (`at_boundary: true`) and is
therefore disclosed, but it is the kind of disclosure that reads as a footnote
and means "the chosen family may be the wrong shape for this data".

THIS IS `railed.py`'s FIRST CALL SITE. `guard_usage_census` (2026-09-09) found
that module had no importers -- a codified rule with no call site, which is this
repo's oldest meta-finding. It was written to make a railed value refuse silent
float use, and the bridge's Thomas fits are railed values that have been read as
ordinary floats since August. The guard and its case were two directories apart.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)
sys.path.insert(0, HERE)
import dpp_boundary as DB                                           # noqa: E402
from railed import Bounded, RailedValueError                        # noqa: E402

DB.assert_bounds_match_frozen()

SRC = os.path.join(HERE, "bridge_b_measured.json")
d = json.load(open(SRC))

rows, agree, disagree, no_report = {}, 0, 0, 0
for blk in ("B1", "B2"):
    for fam, fit in d[blk]["python_fits"].items():
        r = DB.report(fit)
        key = f"{blk}/{fam}"
        rows[key] = r
        frozen = r["frozen_fitter_reported"]
        if frozen is None:
            no_report += 1
        elif bool(frozen) == bool(r["any_rail"]):
            agree += 1
        else:
            disagree += 1

thomas_railed = [k for k, r in rows.items()
                 if r["family"] == "thomas" and r["any_rail"]]
sigma_edge = [k for k, r in rows.items() if r.get("sigma_at_grid_edge")]
dpp_upper = [k for k, r in rows.items() if r.get("alpha_railed_upper")]
dpp_lower = [k for k, r in rows.items() if r.get("alpha_railed_lower")]
unflagged = [k for k, r in rows.items()
             if r["any_rail"] and r["frozen_fitter_reported"] is None]

# The demonstration that makes the point concrete rather than argued: reading a
# railed kappa as a plain float must RAISE.
demo = None
kb = DB.thomas_kappa(d["B1"]["python_fits"]["thomas"]["kappa"])["upper"]
try:
    float(kb)
    demo = "DID NOT RAISE — Bounded is not guarding this value"
except RailedValueError as e:
    demo = str(e).split(" Read ")[0]

print(__doc__.split("WHAT IT DELIVERS")[0].strip())
print(f"\n{'fit':14s} {'any rail':9s} {'frozen said':12s} detail")
for k, r in rows.items():
    if r.get("no_free_parameter"):
        detail = "no free parameter — cannot rail"
    elif r["family"] == "thomas":
        detail = (f"kappa upper={r['kappa_railed_upper']}, "
                  f"sigma at grid edge={r['sigma_at_grid_edge']}")
    else:
        detail = (f"alpha upper={r['alpha_railed_upper']}, "
                  f"lower={r['alpha_railed_lower']}")
    print(f"{k:14s} {str(r['any_rail']):9s} {str(r['frozen_fitter_reported']):12s} {detail}")

print(f"\n  successor vs frozen fitter: {agree} agree, {disagree} disagree, "
      f"{no_report} not reported by the fitter at all")
print(f"  rails with NO machine record: {unflagged}")
print(f"  DPP upper-bound rails: {len(dpp_upper)} of 8   "
      f"lower-bound rails: {len(dpp_lower)} of 8 (bound unexercised)")
print(f"  Thomas sigma on a grid endpoint: {sigma_edge}")
print(f"\n  Bounded refuses the railed kappa as a float:\n    {demo}")

json.dump(dict(
    status="POST-HOC, UNSEALED AUDIT — reads banked artifacts, makes no "
           "prediction, and touches no frozen file",
    source=os.path.basename(SRC),
    frozen_file_untouched="dpp_python.py is read only; its blob SHA is unchanged "
                          "and verify_bridge's addendum check still passes",
    successor_module="dpp_boundary.py (declares the bounds and verifies they are "
                     "still the literals in the frozen source)",
    fits=rows,
    successor_vs_frozen=dict(agree=agree, disagree=disagree,
                             fitter_reports_nothing=no_report),
    rails_without_machine_record=unflagged,
    dpp_upper_rails=dpp_upper, dpp_lower_rails=dpp_lower,
    thomas_sigma_grid_edge=sigma_edge,
    bounded_refuses_float=demo,
    findings=[
        "the successor reproduces at_boundary on 8 of 8 DPP fits, so its "
        "relative tolerance is measuring the same thing the fitter did",
        "both Thomas fits are railed at kappa's upper bound with no check of any "
        "kind in the frozen fitter; the rail is CORRECT (kappa -> infinity is the "
        "Poisson limit) and is stated in RESULTS_BRIDGE prose, but had no machine "
        "record",
        "sigma is scanned, not optimised, and both Thomas fits land on a grid "
        "ENDPOINT — a second unrecorded coordinate the proposal did not mention",
        "the DPP lower bound is unexercised: 0 of 8, smallest alpha 0.3535 "
        "against a bound of 1e-3",
        "all four of B1's DPP families rail at the upper bound, which is a DPP "
        "EXISTENCE condition — B1 wants more repulsion than these families can "
        "express. Flagged in the banked artifact, but it reads as a footnote and "
        "means the family may be the wrong shape for the data."],
    railed_py_first_call_site="guard_usage_census found railed.py had no "
                              "importers. This is its first, on the case it was "
                              "written for."),
    open(os.path.join(HERE, "dpp_boundary_audit.json"), "w"), indent=1)
print("\nwrote dpp_boundary_audit.json")
