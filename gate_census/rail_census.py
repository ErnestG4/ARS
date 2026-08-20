"""RAIL CENSUS: how many banked parameter values sit EXACTLY at a boundary?
COMMITTED GENERATOR of gate_census/rail_census.json.

Unrepresentable data does not land NEAR an endpoint, it lands ON it. So the
signature of a too-narrow class space is a MASS of outputs sitting within
numerical tolerance of a parameter-space boundary. That is checkable across
banked artifacts with the same instrument as the boundary-rate sweep, pointed at
PARAMETERS instead of RATES -- and it is evidence about the INSTRUMENT rather
than about any individual row, which is what makes it cheap and general.

Bounded parameters in this repo and their boundaries, with what a rail means:
  I.8_brody_q            [0, 1]   q=0 is Poisson AND the search floor; clustered
                                  data wants q<0 and cannot go there.
  I.9_berry_robnik_rho   [0, 1]   rho=1 legitimately IS pure-Poisson Berry-Robnik,
                                  so a rail here is NOT automatically a defect --
                                  recorded and flagged, not counted as one.
  ks_* distances         [0, 1]   0 would mean an exact fit (never expected).
  *_rate / *_frac        [0, 1]   0 or 1 with no denominator is the boundary-rate
                                  problem already banked separately.

REPORTS, DOES NOT DEMOTE. A high railed fraction says the class space is likely
too narrow for the data being fed to it; it does not say any particular row is
wrong. Same discipline as the rest of this census.
"""
import json, os, glob, math
from collections import defaultdict

ROOT = "/home/combust/fmexplorer/criticality_tool"
TOL = 1e-3
# key-substring -> (boundary value, is-a-rail-a-defect, note)
PARAMS = {
    "brody_q":       (0.0, True,  "q=0 is Poisson and the search floor; clustered wants q<0"),
    "berry_robnik":  (1.0, False, "rho=1 legitimately IS pure Poisson — flagged, not counted"),
    "rep_int":       (0.0, True,  "the quadrant floor: R2=1 makes the integrand 0"),
}


def walk(o, path, out):
    if isinstance(o, dict):
        for k, v in o.items():
            if isinstance(v, (int, float)) and not isinstance(v, bool):
                for key, (b, defect, note) in PARAMS.items():
                    if key in k.lower():
                        out.append((k, float(v), b, defect, path))
            walk(v, path, out)
    elif isinstance(o, list):
        for v in o:
            walk(v, path, out)


def main():
    files = [f for pat in ("**/*.json", "**/*.jsonl")
             for f in glob.glob(os.path.join(ROOT, pat), recursive=True)
             if "/.git/" not in f]
    hits = []
    for f in files:
        try:
            txt = open(f, "r", errors="replace").read()
        except OSError:
            continue
        if not any(k in txt for k in PARAMS):
            continue
        rel = os.path.relpath(f, ROOT)
        try:
            if f.endswith(".jsonl"):
                for line in txt.splitlines():
                    if line.strip():
                        try:
                            walk(json.loads(line), rel, hits)
                        except json.JSONDecodeError:
                            pass
            else:
                walk(json.loads(txt), rel, hits)
        except json.JSONDecodeError:
            pass

    by_key = defaultdict(list)
    for k, v, b, defect, path in hits:
        for key, (bb, dd, note) in PARAMS.items():
            if key in k.lower():
                by_key[key].append((v, bb, dd, path))
    out = {"tol": TOL, "params": {}}
    print(f"{'parameter':16s} {'n':>7s} {'at boundary':>12s} {'frac':>7s}  interpretation")
    for key, rows in sorted(by_key.items()):
        vals = [r[0] for r in rows]
        b = rows[0][1]; defect = rows[0][2]
        railed = [v for v in vals if abs(v - b) <= TOL]
        frac = len(railed) / len(vals)
        verdict = ("RAILED — class space likely too narrow" if (frac > 0.05 and defect)
                   else "flagged (rail may be legitimate here)" if frac > 0.05
                   else "ok")
        out["params"][key] = dict(n=len(vals), boundary=b, n_railed=len(railed),
                                  railed_fraction=frac, rail_is_defect=defect,
                                  verdict=verdict, note=PARAMS[key][2],
                                  files=sorted({r[3] for r in rows if abs(r[0]-b) <= TOL})[:8])
        print(f"{key:16s} {len(vals):>7} {len(railed):>12} {frac:>7.1%}  {verdict}")
    json.dump(out, open(f"{ROOT}/gate_census/rail_census.json", "w"), indent=1)
    print("\nREPORTS, DOES NOT DEMOTE — a rail says the SPACE is too narrow, "
          "not that a row is wrong.")


if __name__ == "__main__":
    main()
