"""Build seals/PH2_SEAL_2.1.json from the pre-read (run only after Will's decisions on the proposed amendments).

  python make_seal_json.py --pa2 sum|max --adopted PA1,PA2,PA3[,...]

Pins: code sha256 (ph2lib.py, preread.py, run.py), data hashes (Platt md5 from §3; zeros6 sha256 from DATA_MANIFEST;
zeros3/4/5 sha256 recorded at download), estimator constants, per-bin tolerances and pre-data verdicts, pre-read result
hashes. Fails closed if any G0 known answer did not pass or a Platt file is missing or mismatched.
"""
import argparse
import glob
import hashlib
import json
import os

import ph2lib as P
import preread as R
import run

HERE = os.path.dirname(os.path.abspath(__file__))
ZEROS6_SHA256 = "2ef7b752c2f17405222e670a61098250c8e4e09047f823f41e2b41a7b378e7c6"     # DATA_MANIFEST.md
HIGH_SHA256 = {   # recorded at download 2026-10-07 (results/logs/fetch_data.log); no upstream checksum exists
    "zeros3": "75a1f1a978d5e3eddd16518f661d41a95a40b33782389ba02ec4ed0ce0764807",
    "zeros4": "10d9f7dab2bbfff6b8befbe6f765969b0b3f38f6110ed1df423931addd52da8f",
    "zeros5": "250ac4ba722c6face4d07c05777376fc2b9bc021b05232e8f53c91b1eb2b7e0d",
}
PLATT_MD5 = {   # PH2_SEAL_2.1.md §3, pinned before download
    "zeros_2546000.dat": "5642999b13dc52270064a055b1b6b15f",
    "zeros_19346000.dat": "24dedbc917f3a006690026dd7cda930b",
    "zeros_151646000.dat": "242ca86d1691d1a93623b2f8ce2cbf33",
    "zeros_1119746000.dat": "8d01c4c244daf4751f3c251de53008af",
    "zeros_8284946000.dat": "8adc69731784c1958ca60d67686e98b4",
    "zeros_30404246000.dat": "95f2c89b2b4572e5529cd25a79e9def8",
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pa2", choices=("sum", "max"), required=True)
    ap.add_argument("--adopted", required=True)
    a = ap.parse_args()
    res = lambda f: os.path.join(R.RES, f)
    g0a, g0b = json.load(open(res("g0a.json"))), json.load(open(res("g0b.json")))
    chain = json.load(open(res("g0d_chain.json")))
    if not (g0a["PASS"] and g0b["PASS"] and chain["PASS"]):
        raise SystemExit("REFUSED: a G0 known answer did not pass")
    for f, md5 in PLATT_MD5.items():
        got = run._hash(os.path.join(HERE, "data", "platt", f), "md5")
        if got != md5:
            raise SystemExit(f"REFUSED: {f} md5 {got} != pinned {md5}")
    for k, h in HIGH_SHA256.items():
        if run._hash(run.SOURCES[k], "sha256") != h:
            raise SystemExit(f"REFUSED: {k} sha256 changed since download")
    if run._hash(run.SOURCES["zeros6"], "sha256") != ZEROS6_SHA256:
        raise SystemExit("REFUSED: zeros6 sha256 != DATA_MANIFEST")
    summ = json.load(open(res("summary.json")))
    g0c = {b["bin"]: b for b in json.load(open(res("g0c.json")))["bins"]}
    bins = []
    for r in summ["rows"]:
        r = dict(r)
        r["prim"] = dict(r["prim"], allowance=g0c[r["bin"]][f"allowance_{a.pa2}"],
                         NOT_RESOLVABLE=r["prim"][f"NOT_RESOLVABLE_{a.pa2}"])
        bins.append(r)
    preread_hashes = {os.path.relpath(f, HERE): run._hash(f, "sha256")
                      for f in sorted(glob.glob(res("*.json")) + glob.glob(res("g0d/*.json")))}
    seal = dict(
        seal="PH2_SEAL_2.1", text="PH2_SEAL_2.1.md", adopted_amendments=a.adopted.split(","), pa2=a.pa2,
        code_sha256={f: run._hash(os.path.join(HERE, f), "sha256") for f in ("ph2lib.py", "preread.py", "run.py")},
        data=dict(platt_md5=PLATT_MD5, sha256=dict(zeros6=ZEROS6_SHA256, **HIGH_SHA256)),
        constants=dict(Lambda=P.LAMBDA, Q=P.Q_CONST, S_C=P.S_C, S_BRACKET=P.S_BRACKET, S_TINY=P.S_TINY,
                       abar_grid=[float(P.SECONDARY_ABAR_GRID[0]), float(P.SECONDARY_ABAR_GRID[-1]),
                                  len(P.SECONDARY_ABAR_GRID)],
                       block_factors=list(R.BLOCK_FACTORS), bootstrap_B=200, z=R.Z95, floor=R.FLOOR,
                       mean_spacing_band_numerator=R.MEAN_SPACING_BAND, unfolding_dps=run.DPS),
        bins=bins, preread_sha256=preread_hashes)
    os.makedirs(os.path.join(HERE, "seals"), exist_ok=True)
    with open(run.SEAL, "w") as f:
        json.dump(seal, f, indent=1, default=float)
    print("wrote", run.SEAL)


if __name__ == "__main__":
    main()
