# SPDX-License-Identifier: AGPL-3.0-or-later
"""FN1 stage-2 pins builder (TOOLKIT §9.I: reads manifests read-only; writes only under scratch).

  python fn1_make_pins2.py real STAGE1_PINS OUT_REL
      archives: ℤ[√2], ℤ[i], ℤ[ω] as stage 1 (same dirs and manifest sha256); the seven w = 2 fields from
      /mnt/data/fn1/archive_1e11_D*/MANIFEST.json (sha256 computed here; all_integrity must be True; the manifest must
      cover 1010 segments); stage1_manifests: /mnt/data/fn1/archive_1e10_D*/MANIFEST.json with the stage-1 pinned sha256.
  python fn1_make_pins2.py dry STAGE1_PINS DRY10_PINS OUT_REL RED_OUT_REL
      the real block (stage-1 dirs for w = 2; only the dry block is used by the dry read) plus a "dry" block: the
      stage-1 synthetic archives (dry10) and, as their "stage-1 manifests", truncated copies (first 3 segments) written
      under scratch; a RED pins file whose −7 truncated manifest has one sha256 altered (prefix guard must raise).
"""
import json, os, sys
_H = os.path.dirname(os.path.abspath(__file__))
sys.path[:0] = [_H, os.path.join(_H, "..")]
import safeio
safeio.enforce()

W2 = ["-7", "-8", "-11", "-19", "-43", "-67", "-163"]


def base(stage1):
    a = {k: stage1["archives"][k] for k in ("zs2", "zi", "zw")}
    s1 = {D: {"path": os.path.join(stage1["archives"][D]["dir"], "MANIFEST.json"),
              "sha256": stage1["archives"][D]["manifest_sha256"]} for D in W2}
    return a, s1


def real(stage1_pins, out_rel):
    st = safeio.read_json(stage1_pins)
    a, s1 = base(st)
    for D in W2:
        d = f"/mnt/data/fn1/archive_1e11_D{D[1:]}"
        mp = os.path.join(d, "MANIFEST.json")
        m = safeio.read_json(mp)
        assert m["all_integrity"] is True and len(m["segments"]) == 1010 and m["X"] == 101000000000, (D, "manifest")
        a[D] = {"dir": d, "manifest_sha256": safeio.sha256_file(mp)}
    p = safeio.write_json(safeio.scratch(out_rel), {"archives": a, "stage1_manifests": s1})
    print("written", p)


def dry(stage1_pins, dry10_pins, out_rel, red_rel):
    st, dp = safeio.read_json(stage1_pins), safeio.read_json(dry10_pins)
    a, s1 = base(st)
    for D in W2:
        a[D] = st["archives"][D]
    dry_a = dp["dry"]["archives"]
    dry_s1, red_s1 = {}, {}
    for D in W2:
        m = safeio.read_json(os.path.join(dry_a[D]["dir"], "MANIFEST.json"), expect_sha256=dry_a[D]["manifest_sha256"])
        t = dict(m); t["segments"] = m["segments"][:3]
        tp = safeio.write_json(safeio.scratch(f"specarith/fn1/dry2/stage1_trunc_D{D[1:]}.json"), t, overwrite=True)
        dry_s1[D] = {"path": tp, "sha256": safeio.sha256_file(tp)}
        if D == "-7":
            r = json.loads(json.dumps(t)); s = r["segments"][1]["sha256"]
            r["segments"][1]["sha256"] = ("0" if s[0] != "0" else "1") + s[1:]
            rp = safeio.write_json(safeio.scratch("specarith/fn1/dry2/RED_stage1_trunc_D7.json"), r, overwrite=True)
            red_s1[D] = {"path": rp, "sha256": safeio.sha256_file(rp)}
        else:
            red_s1[D] = dry_s1[D]
    good = {"archives": a, "stage1_manifests": s1, "dry": {"archives": dry_a, "stage1_manifests": dry_s1}}
    red = {"archives": a, "stage1_manifests": s1, "dry": {"archives": dry_a, "stage1_manifests": red_s1}}
    print("written", safeio.write_json(safeio.scratch(out_rel), good, overwrite=True))
    print("written", safeio.write_json(safeio.scratch(red_rel), red, overwrite=True))


if __name__ == "__main__":
    if sys.argv[1] == "real":
        real(sys.argv[2], sys.argv[3])
    else:
        dry(sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5])
