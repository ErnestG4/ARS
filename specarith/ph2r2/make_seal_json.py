"""Build seals/PH2R2_SEAL_1.0.json (run only on Will's go; the seal commit is his call). Refuses unless: G0a passed; the
five fresh Platt files match the md5s pinned pre-download (697ddbb3); the Platt round trip is exact; the (achieved)
witness fired. Pins: code (r2lib, r2prep, g0b, r2run), the cached kernels, the primary test function (G0b, R3 rule),
per-bin SD(μ̂) from the surrogates and resolvability (power ≥ 0.80), the red paths' required flags, the seed.

  python make_seal_json.py G0B_DIR REDPATHS_JSON DRYRUN_JSON
"""
import hashlib
import json
import os
import sys

import r2prep as P
import r2run as RR

HERE = os.path.dirname(os.path.abspath(__file__))
PINS = {"zeros_6746000.dat": "7da68bfe58799d9ad96d6e47f3c3fb3a", "zeros_55046000.dat": "a702b364cf5f262b9f36963c58e12599",
        "zeros_412046000.dat": "b38965a1e947a9d5ebb69b4fd70bcde5",
        "zeros_3047546000.dat": "75781990d6be699da0e7a80d5e184be3",
        "zeros_22522946000.dat": "7b9726648af12152eda3ec9cde888210"}
sha = lambda p: hashlib.sha256(open(p, "rb").read()).hexdigest()


def main(g0b_dir, rp_path, dry_path):
    g0a = json.load(open(os.path.join(HERE, "results", "g0a.json")))
    S = json.load(open(os.path.join(g0b_dir, "g0b_summary.json")))
    rp = json.load(open(rp_path))
    dry = json.load(open(dry_path))
    checks = dict(g0a_PASS=bool(g0a["PASS"]), roundtrip_PASS=bool(dry["roundtrip"]["PASS"]),
                  achieved_witness_FIRED=bool(dry["achieved_witness"]["FIRED"]))
    for f, m in PINS.items():
        checks[f"md5_{f}"] = hashlib.md5(open(os.path.join(HERE, "data", "platt", f), "rb").read()).hexdigest() == m
    if not all(checks.values()):
        raise SystemExit(f"REFUSED: {[k for k, v in checks.items() if not v]}")
    key = S["primary_choice"]["primary"]
    bins = {}
    for name in P.BINS:
        s = S[name][key]
        bins[name] = dict(sd_surrogate=s["sd_mu"], power_reject_mu0=s["power_reject_mu0"],
                          resolvable=bool(s["power_reject_mu0"] >= 0.80),
                          target_halfwidth=min(3 * max(s["sd_mu"], max(s["boot_sd_over_sd"].values()) * s["sd_mu"]), 0.5),
                          red_paths={k: dict(power=rp[name][k]["power"], required=rp[name][k]["required"])
                                     for k in ("rp_density", "rp_sign", "rp_shuffle")},
                          kernel_sha256=sha(os.path.join(g0b_dir, f"kernel_{name}.npz")))
    seal = dict(seal="PH2R2_SEAL_1.0", text="PH2R2_SEAL_1.0.md", amendments=["A1"],
                primary=[float(x) for x in key.split("_")], u_max_spacings=P.U_MAX, family=P.FAMILY,
                boot_levels=list(__import__("g0b").BOOT_LEVELS), seed=20261009,
                kernel_dir=os.path.relpath(g0b_dir, HERE),
                code_sha256={f: sha(os.path.join(HERE, f)) for f in ("r2lib.py", "r2prep.py", "g0b.py", "r2run.py")},
                platt_md5=PINS, bins=bins, preread_checks=checks,
                preread_sha256={os.path.relpath(p, HERE): sha(p) for p in
                                (os.path.join(HERE, "results", "g0a.json"), os.path.join(g0b_dir, "g0b_summary.json"),
                                 rp_path, dry_path)})
    os.makedirs(os.path.dirname(RR.SEAL), exist_ok=True)
    json.dump(seal, open(RR.SEAL, "w"), indent=1, default=float)
    print("wrote", RR.SEAL)


if __name__ == "__main__":
    main(*sys.argv[1:4])
