"""Verify the committed route (a) F3 read (results/read/) against the seal, without decoding anything.

Checks: run1 and run2 bit-identical and as COMPARE.json records; all exits 0; the result was produced under the sealed
interpreter and seal; and the verdict, row, pooled μ̃ and SE recompute exactly from the stored per-file records through
the sealed rule (route_a_sealread.evaluate). Exit 0 only if all hold.
"""
import hashlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import route_a_sealread as S  # noqa: E402

D = os.path.join(HERE, "results", "read")
h = [hashlib.sha256(open(os.path.join(D, r, "ROUTE_A_READ.json"), "rb").read()).hexdigest() for r in ("run1", "run2")]
cmp_ = json.load(open(os.path.join(D, "COMPARE.json")))
seal = json.load(open(S.SEAL))
r = json.load(open(os.path.join(D, "run1", "ROUTE_A_READ.json")))
per = {f: {k: r["records"][f][k] for k in ("mu", "flag", "se", "n", "n_window", "chi2")} for f in r["records"]}
v = S.evaluate(per)
ok = dict(bit_identical=h[0] == h[1] == cmp_["run1_sha256"] == cmp_["run2_sha256"] and cmp_["bit_identical"] is True,
          exits=all(open(os.path.join(D, f)).read().strip() == "exit=0" for f in ("run1.exit", "run2.exit", "compare.exit")),
          sealed_env=r["env"] == seal["env"], sealed_run=r["seal"] == "ROUTE_A_SEAL",
          seal_text_pinned=hashlib.sha256(open(S.TEXT, "rb").read()).hexdigest() == seal["text_sha256"],
          verdict_recomputes=all(v[k] == r["result"][k] for k in ("verdict", "row", "mu_pool", "se_pool", "misfit_files",
                                                                   "files_within_3se", "gof_pass_files", "attribution")))
print(json.dumps(ok, indent=1))
print(f"verdict {v['verdict']}, row ({v['row']}), mu_pool {v['mu_pool']:.4f} +- {2 * v['se_pool']:.4f}")
sys.exit(0 if all(ok.values()) else 1)
