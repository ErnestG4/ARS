"""Cross-machine check for route (a)'s inputs (Will, 2026-10-12: "keep the split, add the cross-machine check").

The route (a) terms and the ζ T₅ values were computed on three x86 CPUs with the same code: spot (Xeon E5-2690 v4, the
reference), this machine (Ryzen 5900X, WSL) and char (i5-6600K). Double rounding differs between CPUs and Python builds,
so results agree to rounding level, not bit for bit (a spot route (a) job recomputed here: T₂, T₃ exact, T₄ 7.2e-16).

The check, declared before it is run: jobs already computed on spot are recomputed on each other machine (the
symmetric direction is equivalent and far faster: spot is ~5× slower per process). Every recomputed quantity must agree
with spot's to ≤ TOL = 1e-12 absolute: route (a) T₂, T₃, T₄ (ζ and sine); ζ T₅. If each machine agrees with spot, they
agree with each other within 2·TOL. The route (a) merge requires this check's PASS before the prediction is tagged.

  python xcheck.py recompute ra  SPOT_TERMS_DIR N OUT.jsonl     N spot route (a) jobs (s > 0.45, largest s first)
  python xcheck.py recompute t5  SPOT_T5_DIR    N OUT.jsonl [SKIP]   N spot T₅ jobs (p ≤ 1000), after SKIP
  python xcheck.py compare REF_DIR_RA REF_DIR_T5 RECOMP.jsonl [RECOMP.jsonl …] [--dups COLLECTED_RA_DIR]
                                                       → results/xcheck.json (duplicated jobs included as pairs)
"""
import glob
import json
import math
import os
import socket
import sys
import time

TOL = 1e-12


def _rows(d, pat):
    out = []
    for fn in sorted(glob.glob(os.path.join(d, pat))):
        for line in open(fn):
            try:
                out.append(json.loads(line))
            except ValueError:
                pass
    return out


def recompute(kind, ref_dir, n, out, skip=0):
    host = socket.gethostname()
    if kind == "ra":
        import route_a_zeta as RA
        rows = [r for r in _rows(ref_dir, "terms_c[0-9]*.jsonl") if r["s"] > 0.45 and "host" not in r]
        rows = sorted(rows, key=lambda r: (-r["s"], r["pmax"], r["m"]))
        # spread over files and quadrature/cutoff settings
        seen, pick = set(), []
        for r in rows:
            k = (r["file"], r["pmax"], r["m"])
            if k not in seen:
                seen.add(k)
                pick.append(r)
            if len(pick) == n:
                break
        for r in pick:
            j = (r["file"], r["which"], r["pmax"], r["m"], r["s"])
            t0 = time.time()
            new = RA._run_one(j)
            rec = dict(kind="ra", host=host, job=list(j), zeta=new["zeta"], sine=new["sine"], secs=time.time() - t0)
            open(out, "a").write(json.dumps(rec) + "\n")
            print(rec, flush=True)
    elif kind == "t5":
        import ratios_t5 as T
        import route_a_zeta as RA
        rows = [r for r in _rows(ref_dir, "t5_c*.jsonl") if r["pmax"] == T.PMAX_T5][skip:skip + n]
        for r in rows:
            t0 = time.time()
            M = T.Model("zeta", RA.ell_of(r["t"]), pmax=r["pmax"])
            v = T.T5_model(M, r["s"])
            rec = dict(kind="t5", host=host, job=[r["file"], r["s"], r["pmax"]], T5_zeta=v, secs=time.time() - t0)
            open(out, "a").write(json.dumps(rec) + "\n")
            print(rec, flush=True)


def duplicate_pairs(ra_dir):
    """Jobs that ended up computed twice (the 2026-10-12 hand-over race): every pair of rows with the same job key in
    the collected route (a) directory. Host: the row's "host" field, else spot (legacy rows predate the field); rows
    from this machine's pool are in files terms_cjL*."""
    by = {}
    for fn in sorted(glob.glob(os.path.join(ra_dir, "terms_c*.jsonl"))):
        b = os.path.basename(fn)
        for line in open(fn):
            r = json.loads(line)
            host = "local" if b.startswith("terms_cjL") else r.get("host", "spot")
            by.setdefault((r["file"], r["which"], r["pmax"], r["m"], r["s"]), []).append((host, r))
    out = []
    for k, v in by.items():
        for (h1, r1), (h2, r2) in zip(v, v[1:]):
            d = max(abs(r1[side][t] - r2[side][t]) for side in ("zeta", "sine") for t in ("T2", "T3", "T4"))
            out.append(dict(kind="ra-duplicate", hosts=[h1, h2], job=list(k), max_abs_diff=d))
    return out


def compare(ref_ra, ref_t5, recs, dup_dir=None):
    ra = {(r["file"], r["which"], r["pmax"], r["m"], r["s"]): r for r in _rows(ref_ra, "terms_c[0-9]*.jsonl")}
    t5 = {(r["file"], r["s"], r["pmax"]): r for r in _rows(ref_t5, "t5_c*.jsonl")}
    rows, worst = [], 0.0
    for fn in recs:
        for line in open(fn):
            x = json.loads(line)
            if x["kind"] == "ra":
                ref = ra[tuple(x["job"])]
                d = max(abs(ref[side][k] - x[side][k]) for side in ("zeta", "sine") for k in ("T2", "T3", "T4"))
            else:
                ref = t5[tuple(x["job"])]
                d = abs(ref["T5_zeta"] - x["T5_zeta"])
            worst = max(worst, d)
            rows.append(dict(kind=x["kind"], host=x["host"], job=x["job"], max_abs_diff=d))
    dups = duplicate_pairs(dup_dir) if dup_dir else []
    for r in dups:
        worst = max(worst, r["max_abs_diff"])
        rows.append(dict(kind=r["kind"], host="+".join(r["hosts"]), job=r["job"], max_abs_diff=r["max_abs_diff"]))
    by_host = {}
    for r in rows:
        by_host.setdefault(r["host"], []).append(r["max_abs_diff"])
    out = dict(tol=TOL, reference="spot", n=len(rows), worst=worst,
               by_host={h: dict(n=len(v), worst=max(v)) for h, v in by_host.items()}, rows=rows,
               PASS=bool(rows) and worst <= TOL)
    os.makedirs(os.path.join(os.path.dirname(os.path.abspath(__file__)), "results"), exist_ok=True)
    json.dump(out, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "results", "xcheck.json"), "w"), indent=1)
    print(f"cross-machine check: {len(rows)} recomputed jobs, worst |diff| {worst:.2e} vs {TOL:.0e}: "
          f"{'PASS' if out['PASS'] else 'FAIL'}; by host {out['by_host']}")
    return out


if __name__ == "__main__":
    a = sys.argv[1:]
    if a[0] == "recompute":
        recompute(a[1], a[2], int(a[3]), a[4], int(a[5]) if len(a) > 5 else 0)
    elif a[0] == "compare":
        dup = None
        rest = a[3:]
        if "--dups" in rest:
            i = rest.index("--dups")
            dup = rest[i + 1]
            rest = rest[:i] + rest[i + 2:]
        compare(a[1], a[2], rest, dup)
    else:
        raise SystemExit(__doc__)
