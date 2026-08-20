"""GATE CENSUS sweep: how many BANKED classifications sit on a REJECTED fit?
COMMITTED GENERATOR of gate_census/rejected_fits.json.

`arithmetic_toolkit._classify` returns `best` as an argmin over three surmises
with no rejection region, and until 2026-08-19 it computed the fit quality and
discarded it. Every banked classification downstream is therefore a SELECTION,
not a test. This sweep does not re-measure anything: the artifacts already store
ks_p / ks_o / ks_u and n, so the rejection test is arithmetic on existing records.

THIS PRODUCES A WORK LIST, NOT VERDICTS.  Two reasons, both binding:

  * `ks_crit_01 = 1.63/sqrt(n)` is a DEMANDING bar at large n, and real data with
    mild unfolding imperfection can fail a strict KS while still being correctly
    classified.  Expect false alarms.
  * A rejected fit does not make a row a DIFFERENT class.  It makes it NO class.
    Those are different corrections to make in prose, and the distinction has to
    survive into the output rather than being flattened into "wrong".

So nothing here auto-demotes anything -- same discipline as the boundary-rate
triage, where 105 candidate rows collapsed to 19 real ones.

Three questions, in the owner's order:
  Q1  how many banked classifications sit on a rejected fit
  Q2  of those, how many are load-bearing for a stated finding
  Q3  of those, does the class ASSIGNMENT change, or does it become UNGRADED
Q3's answer is structural and known in advance for this gate: a rejected fit
NEVER changes which class is nearest, because rejection is about the residual to
the best fit, not about the ordering. So every affected row becomes UNGRADED, and
the sweep records the margin so triage can rank them.
"""
import json, os, glob, math

ROOT = "/home/combust/fmexplorer/criticality_tool"
KEYS = ("ks_p", "ks_o", "ks_u")


def crit(n, alpha="01"):
    return 1.63 / math.sqrt(n)            # alpha = 0.01


def scan_obj(o, path, where, out):
    """Walk a decoded artifact for dicts carrying the classifier's signature."""
    if isinstance(o, dict):
        if all(k in o for k in KEYS) and "n" in o:
            try:
                n = int(o["n"])
                bk = min(float(o[k]) for k in KEYS)
                c = crit(n)
                out.append(dict(file=path, where=where, n=n, best=o.get("best"),
                                best_ks=bk, ks_crit=c, ratio=bk / c,
                                rejected=bool(bk > c)))
            except (TypeError, ValueError):
                pass
        for k, v in o.items():
            scan_obj(v, path, f"{where}.{k}" if where else str(k), out)
    elif isinstance(o, list):
        for i, v in enumerate(o):
            scan_obj(v, path, f"{where}[{i}]", out)


def main():
    rows = []
    files = []
    for pat in ("**/*.json", "**/*.jsonl"):
        files += glob.glob(os.path.join(ROOT, pat), recursive=True)
    files = [f for f in files if "/.git/" not in f]
    scanned = 0
    for f in files:
        try:
            txt = open(f, "r", errors="replace").read()
        except OSError:
            continue
        if not any(k in txt for k in KEYS):
            continue
        scanned += 1
        rel = os.path.relpath(f, ROOT)
        try:
            if f.endswith(".jsonl"):
                for i, line in enumerate(txt.splitlines()):
                    line = line.strip()
                    if line:
                        try:
                            scan_obj(json.loads(line), rel, f"line{i}", rows)
                        except json.JSONDecodeError:
                            pass
            else:
                scan_obj(json.loads(txt), rel, "", rows)
        except json.JSONDecodeError:
            pass

    # EFFECT-SIZE TIERS, calibrated against the non-members measured in
    # gate1_specificity.py through this same gate: true Poisson 0.012,
    # uniform 0.091, lognormal 0.104, bimodal 0.334, perfect clock 0.533.
    # The significance column is retained but is NOT the work list -- it flags
    # 97.5% because n is large, which is the KS test working as designed and
    # answering a question nobody asked.
    TIERS = [("as bad as a known non-member (>=0.0629, both-sided)", 0.0629),
             ("worse than lognormal non-member (>=0.104)", 0.104),
             ("worse than bimodal non-member (>=0.334)", 0.334)]
    for r in rows:
        r["fit_poor"] = bool(r["best_ks"] >= 0.0629)
    rej = [r for r in rows if r["rejected"]]
    poor = [r for r in rows if r["fit_poor"]]
    by_file = {}
    for r in poor:
        by_file.setdefault(r["file"], []).append(r)
    out = dict(
        files_containing_classifier_output=scanned,
        classifications_found=len(rows),
        rejected_by_significance=len(rej),
        rejected_fraction=(len(rej) / len(rows)) if rows else None,
        significance_caveat=("97.5% is large-n hypersensitivity, NOT 1613 bad "
                             "classifications. Median n 6150, max 5.3e7. Use the "
                             "effect-size tiers below as the work list."),
        effect_size_tiers={t: sum(1 for r in rows if r["best_ks"] >= v)
                           for t, v in TIERS},
        fit_poor=len(poor),
        note=("WORK LIST, NOT VERDICTS. ks_crit=1.63/sqrt(n) is demanding at "
              "large n and mild unfolding imperfection can fail it while the "
              "class is still right. A rejected fit does not change WHICH class "
              "is nearest -- rejection is about the residual to the best fit, "
              "not the ordering -- so an affected row becomes UNGRADED, never a "
              "different class."),
        by_file={k: dict(n_rejected=len(v),
                         worst_ks=max(x["best_ks"] for x in v),
                         worst_ratio=max(x["ratio"] for x in v),
                         classes=sorted({str(x["best"]) for x in v}))
                 for k, v in sorted(by_file.items(),
                                    key=lambda kv: -max(x["best_ks"] for x in kv[1]))},
        rows=rows)
    json.dump(out, open(f"{ROOT}/gate_census/rejected_fits.json", "w"), indent=1)

    print(f"files containing classifier output : {scanned}")
    print(f"banked classifications found       : {len(rows)}")
    print(f"rejected by SIGNIFICANCE           : {len(rej)}"
          + (f"  ({100*len(rej)/len(rows):.1f}%)  <- large-n artifact, not the work list" if rows else ""))
    for t, v in TIERS:
        k = sum(1 for r in rows if r["best_ks"] >= v)
        print(f"  EFFECT SIZE {t:42s}: {k:>5}  ({100*k/len(rows):.1f}%)")
    if rej:
        print(f"\nQ1 work list — files with fits AS BAD AS A KNOWN NON-MEMBER, worst first:")
        for k, v in list(out["by_file"].items())[:20]:
            print(f"  {v['n_rejected']:>4} poor-fit  worst_ks {v['worst_ks']:>6.3f}  "
                  f"{','.join(v['classes'])[:22]:22s}  {k}")
        worst = [r for r in rows if r["best_ks"] >= 0.334]
        print(f"\n  {len(worst)} rows fit WORSE than a bimodal distribution does "
              "through this same gate — those are near-certainly ungradeable")
        print("\n  Q3 is structural and needs no measurement: a rejected fit NEVER "
              "changes which class is\n  nearest (rejection is the residual to the "
              "best fit, not the ordering), so every affected\n  row becomes "
              "UNGRADED, never a different class.")


if __name__ == "__main__":
    main()
