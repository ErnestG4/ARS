# SPDX-License-Identifier: AGPL-3.0-or-later
"""FN1-h2 pins file for the dry run (and, with the real archives, the read): the h = 1 archives from fn1_pins2.json
(as sealed for stage 2), the committed D2 (b) references and (★) predictions by sha256, and the h = 2 block.

  python fn1h2_make_pins.py dry  REFS_JSON PRED_JSON CONTROLS_JSON H2_ROOT OUT   (H2_ROOT/archive_D{|D|}: fixtures)
  python fn1h2_make_pins.py read REFS_JSON PRED_JSON CONTROLS_JSON H2_ROOT OUT SIM_JSON
                                                        (H2_ROOT/archive_2e10_D{|D|}: real; Will 2026-11-04: plus the
                                                        simulation output that sets D23 and the code hashes)
"""
import hashlib, json, os, sys

import fn1h2_archive as H


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


CODE = ["fn1h2_read.py", "fn1h2_archive.py", "fn1_read2.py", "fn1_archive.py", "rq1_read.py", "rq1_zw.py",
        "rq1_angles.py", "rq1_archive.py"]


def main(mode, refs, pred, controls, root, out, sim=None):
    p2 = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "fn1_pins2.json")))
    pins = dict(archives=p2["archives"], refs=dict(path=os.path.abspath(refs), sha256=sha(refs)),
                pred=dict(path=os.path.abspath(pred), sha256=sha(pred)),
                controls=dict(path=os.path.abspath(controls), sha256=sha(controls)))
    blk = {}
    for D in H.FIELDS:
        d = os.path.join(root, f"archive_D{-D}" if mode == "dry" else f"archive_2e10_D{-D}")
        blk[str(D)] = dict(dir=d, manifest_sha256=sha(os.path.join(d, "MANIFEST.json")))
    pins["dry" if mode == "dry" else "h2"] = blk
    if mode == "read":
        here = os.path.dirname(os.path.abspath(__file__))
        pins["sim"] = dict(path=os.path.abspath(sim), sha256=sha(sim))
        pins["code"] = {c: sha(os.path.join(here, c)) for c in CODE}
    json.dump(pins, open(out, "w"), indent=1, sort_keys=True)
    print("written", out, sha(out))
    return 0


if __name__ == "__main__":
    sys.exit(main(*sys.argv[1:8]))
