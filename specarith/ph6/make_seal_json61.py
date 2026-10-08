"""Build seals/PH6_SEAL_6.1.json (run only on Will's go). Refuses unless every 6.1 known answer and convergence check
passed. Pins: code (ph6lib.py, preread.py, tests61.py), inputs (bands61.json), each readable candidate's level file
(res2) and its T3 band (results/bands61/), the declared constants, the pre-read results, and the pre-read verdicts of
the candidates that are not read (C3a NOT RESOLVABLE — not converged, A2; C3b INAPPLICABLE, A1; BBM and Sierra's
δ-mirror Dirac INAPPLICABLE — circular, 6.0 §6.3)."""
import hashlib
import json
import os

import numpy as np

import tests61 as T

HERE = os.path.dirname(os.path.abspath(__file__))
P = lambda *a: os.path.join(HERE, *a)
sha = lambda p: hashlib.sha256(open(p, "rb").read()).hexdigest()
READ = ("C1a", "C1b", "C2", "C4")


def main():
    known = json.load(open(P("results", "preread61", "tests61_known.json")))
    conv = json.load(open(P("results", "candidates", "convergence61.json")))
    sred = json.load(open(P("results", "preread61", "srednicki61.json")))
    checks = {
        "zeros_known_answer": known["zeros"]["tuple"] == ["PASS", "PASS", "PASS", "GUE"],
        "picket_T1_PASS": known["picket"]["T1"]["verdict"] == "PASS",
        "rp_t1_constant_FAIL": known["rp_t1_constant"]["T1"]["verdict"] == "FAIL",
        "rp_t1_density_FAIL": known["rp_t1_density"]["T1"]["verdict"] == "FAIL",
        "cue_null_T2_FAIL": known["cue_null"]["T2"]["verdict"] == "FAIL",
        "cue_null_T3_FAIL": known["cue_null"]["T3"]["verdict"] == "FAIL",
        "picket_T4_INAPPLICABLE": known["picket"]["T4"]["verdict"] == "INAPPLICABLE",
        "srednicki_PASS": all(r["PASS"] for r in sred),
        **{f"{c}_converged": bool(conv[c]["converged"]) for c in READ},
        "C3a_not_converged": not conv["C3a"]["converged"],
    }
    if not all(checks.values()):
        raise SystemExit(f"REFUSED: pre-read checks failed: {[k for k, v in checks.items() if not v]}")
    cands = {}
    for c in READ:
        lev = os.path.join("results", "candidates", f"{c}_res2.npy")
        meta = json.load(open(P("results", "candidates", f"{c}_res2.json")))
        if sha(P(lev)) != meta["sha256"]:
            raise SystemExit(f"REFUSED: {lev} sha256 differs from its build metadata")
        band = os.path.join("results", "bands61", f"band61_{c}.npy")
        binfo = json.load(open(P("results", "bands61", f"band61_{c}.json")))
        cands[c] = dict(levels=lev, levels_sha256=meta["sha256"], n_levels=meta["n"], band=band,
                        band_sha256=sha(P(band)), config_top=binfo["config"]["E_hi"], band_info=binfo)
    cands["C3a"] = dict(pre_verdict="NOT RESOLVABLE", reason="not converged (A2): N = 3e4 vs 6e4 low-|E| levels differ "
                        f"by up to {conv['C3a']['max_dev_in_spacings']:.0f} mean spacings")
    cands["C3b"] = dict(pre_verdict="INAPPLICABLE", reason="A1: BEK define no single spectrum for the E-linked torus")
    cands["BBM"] = dict(pre_verdict="INAPPLICABLE", reason="levels defined by the zeros (6.0 §6.3)")
    cands["Sierra_mirror"] = dict(pre_verdict="INAPPLICABLE", reason="levels defined by the zeros (6.0 §6.3)")
    pre = [os.path.join("results", "preread61", f) for f in
           ("tests61_known.json", "redpaths61.json", "srednicki61.json", "bands61.json", "preread61_zeros_bands.json")
           if os.path.exists(P("results", "preread61", f))] + [os.path.join("results", "candidates", "convergence61.json")]
    seal = dict(seal="PH6_SEAL_6.1", text="PH6_1_SEAL_6.1.md", amendments=["A1", "A2", "A3"],
                code_sha256={f: sha(P(f)) for f in ("ph6lib.py", "preread.py", "tests61.py")},
                inputs_sha256={os.path.join("results", "preread61", "bands61.json"):
                               sha(P("results", "preread61", "bands61.json"))},
                constants=dict(TAU1=T.TAU1, CRYSTAL_RTILDE=T.CRYSTAL_RTILDE, BOOT_BLOCK=T.BOOT_BLOCK, BOOT_B=T.BOOT_B,
                               SEP_T4=T.SEP_T4, SEED=T.SEED),
                candidates=cands, preread_checks=checks, preread_sha256={p: sha(P(p)) for p in pre})
    os.makedirs(P("seals"), exist_ok=True)
    json.dump(seal, open(T.SEAL61, "w"), indent=1, default=float)
    print("wrote", T.SEAL61)


if __name__ == "__main__":
    main()
