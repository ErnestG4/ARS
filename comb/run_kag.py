"""Committed generator of comb/exact_offsets_kag_measured.json (TOOLKIT §9
committed-generator rule — the estimator KAG must not descend from a session
heredoc).  Deterministic seeds; re-running reproduces the banked numbers."""

import json
import sys

sys.path.insert(0, "/home/combust/fmexplorer/criticality_tool/comb")
from exact_offsets import kag

classes = json.load(open(
    "/home/combust/fmexplorer/criticality_tool/comb/singular_series_banked.json"))["classes"]
res = kag(classes)
json.dump(res, open(
    "/home/combust/fmexplorer/criticality_tool/comb/exact_offsets_kag_measured.json", "w"),
    indent=1)
print("KAG PASS:", res["PASS"])
