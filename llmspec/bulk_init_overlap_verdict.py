"""Reading rule of BULK_INIT_OVERLAP_PREREG.md S3 + Amendment A1 applied to results/bulk_init_overlap/<model>.json
(bulk_init_overlap.py). NO threshold differs from the sealed text.

Rows (A1: pythia-1.4b and the 410M seeds are SEPARATE verdict rows; the pooled 864-matrix count of S3 is kept as a third,
descriptive row). Per row, at the final checkpoint (step143000), rho_bulk = the cosine on k in [32, e_last) -- the deepest
octave is EXCLUDED from the counted set and reported as its own row, as is (A1) the [32, 64) octave next to the spike:
  INIT-DOMINATED BULK  iff  frac(rho_bulk >= 0.80) >= 0.90  AND  frac(|rho_bulk_gauss| <= 0.05) >= 0.99
  LEARNED BULK         iff  frac(rho_bulk <= 0.20) >= 0.90
  MIXED                otherwise (distribution + trajectory + per-type / per-layer tables reported)
  INCOMPLETE           a model of the row is missing or short of 24 x 6 matrices (unless --partial, testing)
  INAPPLICABLE         every run of the row failed the continuity gate
Step-0 continuity gate per run (A1, pythia issue #203): on the step1 revision, every matrix must satisfy
  dist_raw = ||W_1 - W_0||_F / ||W_0||_F  <=  GATE_FACTOR (10) x lr(1) / rms(W_0),      lr(1) = lr_max / warmup_steps,
the expectation being Adam's first step (every element moves by exactly lr(1); ratio = lr(1)/sigma_init ~ 1e-5). A run whose
"step 0" is a different instance reads dist_raw ~ sqrt(2), five decades above the band: it is INAPPLICABLE (its W_0 is not
its init), excluded from its row, reported, never substituted. The gate is ONE-SIDED on purpose: the stored checkpoints sit
on the fp16 grid (relative spacing ~1e-3 >> 1e-5), and GPT-NeoX's first update runs at lr(0) = 0 under the sealed
convention (armb/q1_models.py), so a legitimate run can read dist_raw ~ 0 at step1; the low side (< lr(1)/rms/10) is
REPORTED as a flag, not failed. A run with no step1 revision in the bank is UNEVALUATED = INAPPLICABLE (fail closed; extract
step1 first). Reported-only lines (A1 declared expectations, never thresholds): frac(alpha_hat > alpha_wd) per row (red flag),
the Kosson prior einit_pred / rho_pred, sign-agreement rho_from_sign beside rho_full, per-type medians (W_O prediction),
the near / deep octave rows, and the full trajectory per row.
Allow-list: pythia-1.4b, pythia-410m-seed1..5; anything else (seeds 6-9, 410m-std, 1b, 70m, Arm B) is REFUSED.
Usage: bulk_init_overlap_verdict.py [--results DIR] [--models m ...] [--final step143000] [--partial] [--out verdict.json]
verdict(rows, thr) is the pure rule (rows: dicts with rho_bulk, rho_bulk_gauss); continuity_gate(J) the gate;
verify_bulk_init_overlap.py (vi) exercises both on synthetic banks and red-paths the INIT-DOMINATED threshold.
"""
import sys, json, argparse
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
import bulk_init_overlap as B

ALLOW = B.ALLOW
SEEDS = tuple(m for m in ALLOW if m.startswith("pythia-410m-seed"))
ROWS = {"pythia-1.4b": ("pythia-1.4b",), "pythia-410m-seeds": SEEDS, "pooled": ALLOW}
FINAL = "step143000"
GATE_REV = "step1"
GATE_FACTOR = 10.0
N_LAYERS = 24
THRESH = dict(init_rho=0.80, init_frac=0.90, gauss_abs=0.05, gauss_frac=0.99, learned_rho=0.20, learned_frac=0.90)
WORDS = ("INIT-DOMINATED BULK", "LEARNED BULK", "MIXED", "INCOMPLETE", "INAPPLICABLE")


def _arr(rows, key):
    return np.array([r[key] if r.get(key) is not None else np.nan for r in rows], dtype=np.float64)


def _q(x):
    x = np.asarray(x, dtype=np.float64)
    x = x[np.isfinite(x)]
    if len(x) == 0:
        return {"n": 0}
    p = np.percentile(x, [10, 25, 50, 75, 90])
    return {"n": int(len(x)), "p10": float(p[0]), "p25": float(p[1]), "median": float(p[2]), "p75": float(p[3]), "p90": float(p[4]),
            "min": float(x.min()), "max": float(x.max())}


def _frac(x, pred):
    x = np.asarray(x, dtype=np.float64)
    return float(np.mean(np.isfinite(x) & pred(x))) if len(x) else None


def verdict(rows, thr=THRESH):
    """The S3 rule on per-matrix rows (rho_bulk, rho_bulk_gauss). NaN rho (empty bulk set) counts as a matrix that fails
    both inequalities (fail closed). Returns (word, stats)."""
    rho, g = _arr(rows, "rho_bulk"), _arr(rows, "rho_bulk_gauss")
    n = len(rho)
    ok = np.isfinite(rho)
    f_init = float(np.sum(ok & (rho >= thr["init_rho"])) / n) if n else 0.0
    f_learn = float(np.sum(ok & (rho <= thr["learned_rho"])) / n) if n else 0.0
    f_gauss = float(np.sum(np.isfinite(g) & (np.abs(g) <= thr["gauss_abs"])) / n) if n else 0.0
    st = {"n_matrices": n, "n_nan": int((~ok).sum()), "frac_rho_ge_init": f_init, "frac_rho_le_learned": f_learn,
          "frac_gauss_abs_le": f_gauss, "thresholds": dict(thr), "rho_bulk": _q(rho), "rho_bulk_gauss_abs": _q(np.abs(g))}
    if n == 0:
        return "INCOMPLETE", st
    if f_init >= thr["init_frac"] and f_gauss >= thr["gauss_frac"]:
        return "INIT-DOMINATED BULK", st
    if f_learn >= thr["learned_frac"]:
        return "LEARNED BULK", st
    st["note"] = ("rho condition for INIT-DOMINATED met but the Gaussian-null gate failed" if f_init >= thr["init_frac"] else None)
    return "MIXED", st


def continuity_gate(J, rev=GATE_REV, factor=GATE_FACTOR):
    """A1 step-0 continuity gate for one model JSON. Returns a dict with status PASS / FAIL / UNEVALUATED and the per-matrix
    ratio dist_raw / (lr(1)/rms(W_0)) summary; flag_low marks matrices below 1/factor (reported, not failed)."""
    out = {"rev": rev, "factor": factor, "status": "UNEVALUATED", "n_matrices": 0,
           "rule": "FAIL iff any matrix has dist_raw > factor x lr(1)/rms(W_0); low side reported only (fp16 grid; lr(0) = 0)"}
    rows = B.final_rows(J, rev)
    if not rows:
        out["note"] = f"{rev} not in the bank: run bulk_init_overlap.py {J['model']} {rev} first"
        return out
    lr1 = rows[0]["lr_1"]
    dist, rms = _arr(rows, "dist_raw"), _arr(rows, "rms_w0")
    expect = lr1 / rms
    ratio = dist / expect
    worst = int(np.nanargmax(ratio))
    out.update(status="FAIL" if np.any(~np.isfinite(ratio)) or np.nanmax(ratio) > factor else "PASS", n_matrices=len(rows), lr_1=lr1,
               ratio_over_expect=_q(ratio), dist_raw=_q(dist), expect=_q(expect), n_over=int(np.sum(ratio > factor)),
               n_low=int(np.sum(ratio < 1 / factor)), flag_low=bool(np.any(ratio < 1 / factor)),
               worst={"layer": rows[worst]["layer"], "M": rows[worst]["M"], "dist_raw": float(dist[worst]), "expect": float(expect[worst]),
                      "ratio": float(ratio[worst])})
    return out


def tables(rows):
    """Descriptive splits (never verdicts): per type, per layer, near / deep octaves, nulls, alpha and sign lines."""
    out = {"per_type": {}, "per_layer": {}}
    for M in B.MATS:
        rr = [r for r in rows if r["M"] == M]
        rb = _arr(rr, "rho_bulk")
        out["per_type"][M] = {"rho_bulk": _q(rb), "frac_ge_080": _frac(rb, lambda x: x >= 0.80), "frac_le_020": _frac(rb, lambda x: x <= 0.20),
                              "einit_bulk": _q(_arr(rr, "einit_bulk")), "rho_near": _q(_arr(rr, "rho_near")), "rho_deep": _q(_arr(rr, "rho_deep")),
                              "rho_top": _q(_arr(rr, "rho_top")), "rho_full": _q(_arr(rr, "rho_full")), "alpha_hat": _q(_arr(rr, "alpha_hat"))}
    for L in sorted({r["layer"] for r in rows}):
        rr = [r for r in rows if r["layer"] == L]
        rb = _arr(rr, "rho_bulk")
        out["per_layer"][str(L)] = {"rho_bulk": _q(rb), "frac_ge_080": _frac(rb, lambda x: x >= 0.80), "frac_le_020": _frac(rb, lambda x: x <= 0.20)}
    for name, key in (("near_octave_32_64", "rho_near"), ("deep_octave", "rho_deep"), ("bulk_core_64_elast", "rho_bulk_core"),
                      ("bulk_all_incl_deep", "rho_bulk_all")):
        x = _arr(rows, key)
        out[name] = {key: _q(x), "frac_ge_080": _frac(x, lambda v: v >= 0.80), "frac_le_020": _frac(x, lambda v: v <= 0.20),
                     "note": "descriptive row only; not in the counted set" if name != "bulk_core_64_elast" else "bulk minus near; descriptive"}
    out["deep_octave"]["einit_deep"] = _q(_arr(rows, "einit_deep"))
    out["near_octave_32_64"]["einit_near"] = _q(_arr(rows, "einit_near"))
    out["wrong_instance_null"] = {"rho_bulk_wrong_abs": _q(np.abs(_arr(rows, "rho_bulk_wrong"))),
                                  "frac_abs_le_005": _frac(np.abs(_arr(rows, "rho_bulk_wrong")), lambda x: x <= 0.05)}
    ah, aw = _arr(rows, "alpha_hat"), _arr(rows, "alpha_wd")
    out["alpha"] = {"alpha_hat": _q(ah), "alpha_bulk": _q(_arr(rows, "alpha_bulk")), "alpha_wd": sorted({float(a) for a in aw if np.isfinite(a)}),
                    "d": _q(_arr(rows, "d")),
                    "red_flag_frac_alpha_hat_gt_alpha_wd": _frac(ah - aw, lambda x: x > 0),
                    "note": "A1 declared expectation alpha_hat <= alpha_wd (Bordt 2025); alpha_hat > alpha_wd is a red flag to report, not a threshold"}
    out["sign_agreement"] = {"p_sign": _q(_arr(rows, "p_sign")), "rho_from_sign": _q(_arr(rows, "rho_from_sign")), "rho_full": _q(_arr(rows, "rho_full")),
                             "rho_from_sign_minus_rho_full": _q(_arr(rows, "rho_from_sign") - _arr(rows, "rho_full"))}
    out["kosson_prior"] = {"einit_pred": _q(_arr(rows, "kosson_einit_pred")), "rho_pred": _q(_arr(rows, "kosson_rho_pred")),
                           "einit_bulk_measured": _q(_arr(rows, "einit_bulk")),
                           "note": "A1 reported-only: sqrt(eta/2 lambda) equilibrium rms of the update part vs the shrunk init's rms"}
    return out


def trajectory(jsons):
    """Per revision (pooled over the given models): quartiles of rho_bulk, E_init_bulk, alpha_hat, d, near / deep rows,
    sign map; alpha_wd / lr_t / kosson_rms_t per model."""
    revs = sorted({rev for J in jsons for rev in J["revs"]}, key=B.step_of)
    out = {}
    for rev in revs:
        rows = [r for J in jsons for r in B.final_rows(J, rev)]
        if not rows:
            continue
        ah, aw = _arr(rows, "alpha_hat"), _arr(rows, "alpha_wd")
        out[rev] = {"step": B.step_of(rev), "n_matrices": len(rows),
                    "schedule": {J["model"]: {k: J["revs"][rev][k] for k in ("alpha_wd", "lr_t", "kosson_rms_t")} for J in jsons if rev in J["revs"]},
                    "rho_bulk": _q(_arr(rows, "rho_bulk")), "einit_bulk": _q(_arr(rows, "einit_bulk")), "rho_near": _q(_arr(rows, "rho_near")),
                    "rho_deep": _q(_arr(rows, "rho_deep")), "rho_top": _q(_arr(rows, "rho_top")), "rho_full": _q(_arr(rows, "rho_full")),
                    "rho_from_sign": _q(_arr(rows, "rho_from_sign")), "alpha_hat": _q(ah), "d": _q(_arr(rows, "d")),
                    "frac_alpha_hat_gt_alpha_wd": _frac(ah - aw, lambda x: x > 0),
                    "kosson_einit_pred": _q(_arr(rows, "kosson_einit_pred")),
                    "rho_bulk_gauss_abs": _q(np.abs(_arr(rows, "rho_bulk_gauss"))),
                    "per_type_median_rho_bulk": {M: (float(np.nanmedian(_arr([r for r in rows if r["M"] == M], "rho_bulk")))
                                                     if [r for r in rows if r["M"] == M] else None) for M in B.MATS}}
    return out


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("--results", default=str(B.RESULTS))
    ap.add_argument("--models", nargs="*", default=list(ALLOW))
    ap.add_argument("--final", default=FINAL)
    ap.add_argument("--partial", action="store_true", help="testing: do not demand full coverage")
    ap.add_argument("--out", default=None)
    ap.add_argument("--thresholds", default=None, help="testing/red-path only: JSON overriding THRESH; recorded in the output")
    a = ap.parse_args(argv)
    bad = [m for m in a.models if m not in ALLOW]
    if bad:
        raise SystemExit(f"REFUSED: {bad} not in the allow-list {list(ALLOW)} (PREREG S1: UNREAD)")
    thr = dict(THRESH, **(json.loads(a.thresholds) if a.thresholds else {}))
    results = Path(a.results)
    jsons, missing, short, gates = {}, [], {}, {}
    for m in a.models:
        p = results / f"{m}.json"
        if not p.exists():
            missing.append(m); continue
        J = json.loads(p.read_text())
        jsons[m] = J
        n = len(B.final_rows(J, a.final))
        if n < N_LAYERS * len(B.MATS):
            short[m] = n
        gates[m] = continuity_gate(J)
    applicable = [m for m in jsons if gates[m]["status"] == "PASS"]
    out = {"final_rev": a.final, "models": a.models, "models_missing": missing, "models_short": short, "partial": a.partial,
           "thresholds_overridden": a.thresholds is not None, "thresholds": thr, "gate_factor": GATE_FACTOR,
           "continuity_gate": gates, "runs_inapplicable": {m: g["status"] for m, g in gates.items() if g["status"] != "PASS"},
           "rule": __doc__.split("\n")[6:12], "rows": {}, "words": {}, "trajectory": {},
           "config": {m: J["config"] for m, J in jsons.items()}}
    for row, members in ROWS.items():
        members = [m for m in members if m in a.models]
        if not members:
            continue
        use = [m for m in members if m in applicable]
        rows = [r for m in use for r in B.final_rows(jsons[m], a.final)]
        word, st = verdict(rows, thr)
        if not use and any(m in jsons for m in members):
            word = "INAPPLICABLE"
        elif (any(m in missing or m in short for m in members)) and not a.partial:
            word = "INCOMPLETE"
        out["rows"][row] = {"word": word, "members": members, "runs_used": use,
                            "runs_inapplicable": {m: gates[m]["status"] for m in members if m in gates and gates[m]["status"] != "PASS"},
                            "runs_missing": [m for m in members if m in missing], "runs_short": {m: short[m] for m in members if m in short},
                            "n_expected": N_LAYERS * len(B.MATS) * len(use), "stats": st, "tables": tables(rows) if rows else {},
                            "descriptive_only": row == "pooled"}
        out["words"][row] = word
        out["trajectory"][row] = trajectory([jsons[m] for m in use])
        print(f"VERDICT [{row}{' (descriptive)' if row == 'pooled' else ''}] {word}: n={st['n_matrices']}/{N_LAYERS * len(B.MATS) * len(members)} "
              f"frac(rho>=0.80)={st['frac_rho_ge_init']:.3f} frac(rho<=0.20)={st['frac_rho_le_learned']:.3f} "
              f"gauss frac(|rho|<=0.05)={st['frac_gauss_abs_le']:.3f} used={use} inapplicable={out['rows'][row]['runs_inapplicable']} "
              f"missing={out['rows'][row]['runs_missing']} short={out['rows'][row]['runs_short']}")
    for m, g in gates.items():
        print(f"  gate {m}: {g['status']}" + (f" max ratio/expect {g['ratio_over_expect']['max']:.3g} (worst L{g['worst']['layer']} {g['worst']['M']}), "
                                             f"n_low {g['n_low']}/{g['n_matrices']}" if g["status"] != "UNEVALUATED" else f" ({g.get('note')})"))
    dest = Path(a.out) if a.out else results / "verdict.json"
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps(out, indent=1))
    print(f"-> {dest}")
    return out


if __name__ == "__main__":
    main(sys.argv[1:])
