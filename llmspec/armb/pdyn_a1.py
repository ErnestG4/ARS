"""PDYN_PREREG_A1 runner (sealed by Will 2026-10-04). The sealed phase-1 runner -- pdyn_phase1.analyse_unit, verdict_p2,
every statistic, tolerance and the majority rule -- UNCHANGED, with only its control generator swapped (A1.1):

  c1 (C1')  beta = 1: W(t) = W(0) + int M, M an Ornstein-Uhlenbeck matrix process with velocity time constant tau_v,
            norm-projected (pdyn_c9.gen_driver, as in the exploratory sweep);
  b2        the SAME driver on complex Gaussian matrices (beta = 2);
  po        independent levels (Poisson, unit density in spacings) moved by the SAME OU velocity (each level its own
            scalar OU momentum), so the discrimination is of beta, not of memory.
  tau_v FIXED per optimizer (A1.1): AdamW 10 steps (beta_1 0.9), Muon 20 steps (momentum 0.95). The driver scale s is
  matched to the real window's vrms in <= 3 passes (vrms is proportional to s); the match is reported per draw.

Arms (A1.2 as sealed): PRIMARY A1, A2 (AdamW), M0s2, M0s3 (Muon); SECONDARY A0, M0s1 (post-sweep, non-blind). W2 only.
Words: per arm, the A1 word = HOLDS iff the per-matrix P2 (verdict_p2: components 1-3 HOLD and the witnesses separate)
holds on >= 30 of the arm's 36 matrices, as the sealed A1.2 text states; the runner's own arm-level majority word
(aggregate_p2: each component holds on > half the resolvable matrices) is reported beside it -- the sealed text calls
>= 30/36 "the runner's majority rule", which it is not; both are reported and the mismatch is flagged. Component 4 (velocity excess kurtosis vs 3 x the C1' draw spread) is reported BESIDE the word.
Note: the runner's C4 matrix floor reads the c1 'tau' field; here that field carries tau_v (C4 is not part of A1).

Usage: pdyn_a1.py run [--arms ...] [--workers 10]  ->  results/armb_pdyn_a1/   ;  pdyn_a1.py words  ->  words.json
"""
import os
for _k in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(_k, "1")      # forked workers: one BLAS thread each (set before numpy loads)
import json, math, sys
from pathlib import Path
import numpy as np
from scipy.linalg import svd
HERE = Path(__file__).resolve().parent; ROOT = HERE.parent
sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(HERE))
import pdyn_phase1 as P
import pdyn_c9 as D

TAU_V = {"A0": 10.0, "A1": 10.0, "A2": 10.0, "A0r": 10.0, "M0s1": 20.0, "M0s2": 20.0, "M0s3": 20.0}
PRIMARY = ["A1", "A2", "M0s2", "M0s3"]; SECONDARY = ["A0", "M0s1"]
OUT = ROOT / "results" / "armb_pdyn_a1"
_CUR = {"tau_v": None}


def ou_rect(m, n, times, tau_v, s, seed, beta=1):
    """W(0) + integrated OU momentum on an m x n real (beta 1) or complex (beta 2) Gaussian matrix, norm-projected."""
    m, n = max(m, n), min(m, n)
    rng = np.random.default_rng(seed)
    cplx = beta == 2
    def g():
        return (rng.standard_normal((m, n)) + 1j * rng.standard_normal((m, n))) / math.sqrt(2) if cplx else rng.standard_normal((m, n))
    t = np.asarray(times, float); W = g(); Mo = g() * s; F0 = np.linalg.norm(W)
    out = [svd(W, compute_uv=False)]
    for i in range(1, len(t)):
        a = (t[i] - t[i - 1]) / tau_v; vm, vw, cv = D._ou_coefs(a); vw *= tau_v ** 2; cv *= tau_v
        z1, z2 = g(), g(); sw = math.sqrt(vw)
        xi_W = s * sw * z1; xi_M = s * ((cv / sw) * z1 + math.sqrt(max(vm - cv ** 2 / vw, 0.0)) * z2)
        W = W + tau_v * (-math.expm1(-a)) * Mo + xi_W; Mo = math.exp(-a) * Mo + xi_M
        W *= F0 / np.linalg.norm(W)
        out.append(svd(W, compute_uv=False))
    return np.array(out)


def ou_poisson(n, times, tau_v, s, seed):
    """n independent levels (unit density, in spacings), each moved by its own scalar OU momentum (same tau_v)."""
    rng = np.random.default_rng(seed)
    t = np.asarray(times, float); x = np.sort(rng.uniform(0, n, n)); v = rng.standard_normal(n) * s
    out = [x.copy()]
    for i in range(1, len(t)):
        a = (t[i] - t[i - 1]) / tau_v; vm, vw, cv = D._ou_coefs(a); vw *= tau_v ** 2; cv *= tau_v
        z1, z2 = rng.standard_normal(n), rng.standard_normal(n); sw = math.sqrt(vw)
        xi_x = s * sw * z1; xi_v = s * ((cv / sw) * z1 + math.sqrt(max(vm - cv ** 2 / vw, 0.0)) * z2)
        x = x + tau_v * (-math.expm1(-a)) * v + xi_x; v = math.exp(-a) * v + xi_v
        out.append(x.copy())
    return np.array(out)


def gen_ou(fam, m, n, times, tau_v, s, seed):
    if fam == "c1": return ou_rect(m, n, times, tau_v, s, seed, 1)
    if fam == "b2": return ou_rect(m, n, times, tau_v, s, seed, 2)
    if fam == "po": return ou_poisson(min(m, n), times, tau_v, s, seed)
    raise ValueError(fam)


def matched_family_ou(fam, m, n, times_w, v_target, seed, dt_ref):
    """Drop-in for pdyn_phase1.matched_family (same return contract): OU family at the arm's tau_v, scale matched."""
    tau_v = _CUR["tau_v"]; assert tau_v, "tau_v not set"
    s = 1e-3 if fam != "po" else 0.05
    v1 = float("nan"); it = 0; S = r = None
    for it in range(1, 4):
        S = gen_ou(fam, m, n, times_w, tau_v, s, seed)
        r = P.m2_single(S, times_w)
        v1 = float(r["vrms"]) if "vrms" in r else float("nan")
        if not np.isfinite(v1) or v1 <= 0: break
        if abs(v1 / v_target - 1) < P.XSTEP_MATCH_TOL: break
        s *= v_target / v1
    return S, r, dict(tau=float(tau_v), tau_v=float(tau_v), s=float(s), family="OU", amp=None, passes=it, vrms_measured=v1,
                      v_target=float(v_target), matched=bool(np.isfinite(v1) and abs(v1 / v_target - 1) < P.XSTEP_MATCH_TOL))


_ORIG_UNIT = P.analyse_unit
_ORIG_MATCHED = P.matched_family


def analyse_unit_a1(bank, arm, *a, **k):
    _CUR["tau_v"] = TAU_V.get(arm, TAU_V.get(arm.split("_")[0], 10.0)) if not arm.startswith("FAKE") else _CUR["tau_v"] or 10.0
    return _ORIG_UNIT(bank, arm, *a, **k)


def install():
    P.matched_family = matched_family_ou
    P.analyse_unit = analyse_unit_a1


def words(out=OUT):
    """A1 words per arm: P2 = the runner's own arm-level word on W2 (summary.json, aggregate_p2 = the sealed majority rule
    over the arm's matrices, witnesses-separated check included), plus component 4 (velocity excess kurtosis vs
    3 x the C1' draw spread) counted per matrix and reported BESIDE the word, never folded in."""
    out = Path(out); summ = json.load(open(out / "summary.json"))
    res = {"primary": PRIMARY, "secondary": SECONDARY, "arms": {}}
    for arm, S in summ.get("arms", {}).items():
        if S.get("status") != "OK": continue
        p2 = (S.get("P2") or {}).get("W2", {})
        k4 = []; per = []
        for pj in sorted((out / arm / "parts").glob("*.json")):
            W = json.load(open(pj)).get("windows", {}).get("W2") or {}
            if W.get("m2"):
                npz = pj.with_suffix(".npz"); arrays = dict(np.load(npz)) if npz.exists() else {}
                v = P.verdict_p2(dict(W, name="W2"), arrays); per.append(dict(unit=pj.stem, word=v["word"], reason=v.get("reason", "")))
            c1 = [x for x in (W.get("controls") or {}).get("families", {}).get("c1", []) if x.get("status") == "OK"]
            if len(c1) >= 2 and (W.get("m2") or {}).get("status") == "OK":
                ks = [x["velocity"]["ex_kurt"] for x in c1]; sp = float(np.std(ks, ddof=1))
                real = float(W["m2"]["velocity"]["ex_kurt"])
                k4.append(dict(unit=pj.stem, real=real, c1_mean=float(np.mean(ks)), c1_spread=sp, fails=bool(abs(real - np.mean(ks)) > 3 * sp)))
        n_h = sum(x["word"] == "HOLDS" for x in per); n_m = len(per)
        need = math.ceil(n_m * 30 / 36) if n_m else 30                      # 30 of 36 on the real bank; scaled on a fake bank
        a1_word = "HOLDS" if n_h >= need else ("NOT RESOLVABLE" if sum(x["word"] == "NOT RESOLVABLE" for x in per) > n_m - need else "FAILS")
        res["arms"][arm] = {"role": "PRIMARY" if arm in PRIMARY else ("SECONDARY (post-sweep, non-blind)" if arm in SECONDARY else "OTHER"),
                            "tau_v": TAU_V.get(arm),
                            "A1_word_30of36": a1_word, "n_matrices_HOLDS": n_h, "n_matrices": n_m,
                            "runner_majority_word_W2": p2.get("word"), "P2_W2": p2, "per_matrix": per,
                            "component4_ex_kurt": {"fails": int(sum(x["fails"] for x in k4)), "n": len(k4),
                                                   "median_real": float(np.median([x["real"] for x in k4])) if k4 else None,
                                                   "median_c1prime": float(np.median([x["c1_mean"] for x in k4])) if k4 else None,
                                                   "per_matrix": k4}}
        print(f"{arm:10s} {res['arms'][arm]['role'][:9]:9s} tau_v={TAU_V.get(arm)}  A1 word (>=30/36 scaled) = {a1_word} ({n_h}/{n_m} HOLD)  runner-majority = {p2.get('word')}  "
              f"[holds {p2.get('n_holds')}, fails {p2.get('n_fails')}, NR {p2.get('n_not_resolvable')} of {p2.get('n_matrices')}]  "
              f"comp4 ex-kurt fails {res['arms'][arm]['component4_ex_kurt']['fails']}/{len(k4)}", flush=True)
    (out / "words.json").write_text(json.dumps(res, indent=1, default=str))
    return res


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "run"
    if cmd == "words":
        words(); sys.exit(0)
    install()
    argv = sys.argv[2:]
    if "--arms" not in argv: argv += ["--arms"] + PRIMARY + SECONDARY
    if "--out" not in argv: argv += ["--out", str(OUT)]
    if "--windows" not in argv: argv += ["--windows", "W2"]
    P.main(argv)
    words(Path(argv[argv.index("--out") + 1]))
    print("PDYN_A1_DONE")
