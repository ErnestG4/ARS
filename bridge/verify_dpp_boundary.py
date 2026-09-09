"""Re-derive the boundary audit, and prove the frozen file was never touched.

  1. THE FREEZE IS INTACT. This whole approach exists so `dpp_python.py` keeps
     producing the banked numbers; if its blob moved, the successor's reason for
     existing is gone and the proposal's own objection applies to us.
  2. The successor still describes the fitter it claims to: the bounds it
     declares must still be the literals in the frozen source.
  3. The audit re-derives from the banked fits, per fit.
  4. THE AGREEMENT PREMISE HOLDS. Where the frozen fitter reports at all, the
     successor must agree on every fit. A disagreement means the successor's
     tolerance is measuring something else and none of its extra readings can be
     trusted.
  5. The two Thomas rails are still recorded, and `Bounded` still REFUSES the
     railed kappa as a float. That refusal is the entire mechanism: without it
     this is a document, not a guard.
"""
import hashlib
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)
sys.path.insert(0, HERE)
import dpp_boundary as DB                                           # noqa: E402
from railed import RailedValueError                                 # noqa: E402

bad = []
a = json.load(open(os.path.join(HERE, "dpp_boundary_audit.json")))
src = json.load(open(os.path.join(HERE, a["source"])))

# 1. the freeze
frozen = os.path.join(HERE, "dpp_python.py")
r = subprocess.run(["git", "status", "--porcelain", "--", "bridge/dpp_python.py"],
                   cwd=ROOT, capture_output=True, text=True)
if r.stdout.strip():
    bad.append("dpp_python.py has uncommitted modifications — the successor "
               "approach exists precisely so this file is never edited")
data = open(frozen, "rb").read()
blob = hashlib.sha1(b"blob %d\0" % len(data) + data).hexdigest()
seal = json.load(open(os.path.join(HERE, "prereg_sealed.json")))
want = seal.get("post_seal_addendum_2026_08_15", {}).get(
    "frozen_blob_shas", {}).get("bridge/dpp_python.py")
if want and blob != want:
    bad.append(f"dpp_python.py blob {blob[:12]} != the addendum's {want[:12]} — "
               "the frozen file MOVED, which is the one thing this design "
               "promised not to do")

# 2. the successor still describes the fitter
try:
    DB.assert_bounds_match_frozen()
except AssertionError as e:
    bad.append(str(e))

# 3-4. re-derive every fit, and the agreement premise
agree = disagree = no_report = 0
for blk in ("B1", "B2"):
    for fam, fit in src[blk]["python_fits"].items():
        key = f"{blk}/{fam}"
        got = DB.report(fit)
        banked = a["fits"].get(key)
        if banked is None:
            bad.append(f"{key} missing from the audit")
            continue
        for f in ("any_rail", "alpha_railed_upper", "alpha_railed_lower",
                  "kappa_railed_upper", "sigma_at_grid_edge"):
            if f in banked and banked[f] != got.get(f):
                bad.append(f"{key}.{f}: audit {banked[f]}, re-derived {got.get(f)}")
        fz = got["frozen_fitter_reported"]
        if fz is None:
            no_report += 1
        elif bool(fz) == bool(got["any_rail"]):
            agree += 1
        else:
            disagree += 1
            bad.append(f"{key}: the successor DISAGREES with the frozen fitter "
                       f"({got['any_rail']} vs {fz}) — its tolerance is measuring "
                       "something else and its extra readings cannot be trusted")
if agree != a["successor_vs_frozen"]["agree"] or disagree:
    bad.append(f"agreement changed: {agree} agree / {disagree} disagree vs "
               f"banked {a['successor_vs_frozen']}")

# 5. the rails are recorded, and the refusal actually fires
if sorted(a["rails_without_machine_record"]) != ["B1/thomas", "B2/thomas"]:
    bad.append(f"the unrecorded-rail list changed: "
               f"{a['rails_without_machine_record']} — both Thomas fits are the "
               "case this audit exists to document")
kb = DB.thomas_kappa(src["B1"]["python_fits"]["thomas"]["kappa"])["upper"]
if not kb.railed:
    bad.append("the B1 Thomas kappa no longer reads as railed")
try:
    float(kb)
    bad.append("Bounded did NOT refuse the railed kappa as a float — that "
               "refusal is the mechanism; without it this is a document")
except RailedValueError:
    pass
if a.get("dpp_lower_rails"):
    bad.append(f"a DPP fit now sits at the LOWER bound ({a['dpp_lower_rails']}) — "
               "that half was latent and is now live; re-read the proposal")
if "POST-HOC" not in a["status"].upper():
    bad.append("the audit has lost its POST-HOC label")

print(f"  frozen dpp_python.py blob {blob[:12]} — unchanged, addendum still matches")
print(f"  successor vs frozen fitter: {agree} agree, {disagree} disagree, "
      f"{no_report} unreported by the fitter")
print(f"  rails with no machine record: {a['rails_without_machine_record']}; "
      f"sigma at grid edge: {a['thomas_sigma_grid_edge']}")
print(f"  Bounded refuses the railed kappa as a float: yes")

if bad:
    print("VERIFY_DPP_BOUNDARY: FAIL")
    for b in bad:
        print("  *", b)
    sys.exit(1)
print("VERIFY_DPP_BOUNDARY: PASS — the frozen file is untouched, the successor "
      "still describes it and agrees with it everywhere it reports, and the "
      "Thomas rails now have the machine record they lacked")
