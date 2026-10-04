"""PDYN A1.8 -- POST-HOC known answer for the full-bin C(x) statistic on REALISTIC shapes (designed 10-04 after the A1
read; PDYN_PREREG_A1 A1.8). Truth per real matrix: a beta = 1 OU draw at the arm's tau_v and real shape, warped onto that
matrix's own time-mean W2 density (pdyn_c9 'zero' construction: strip top-16, log-quantile function rank-smoothed at
h = 32, time-mean, fixed map, no drift), scale matched to the real W2 vrms (<= 3 passes). Written as a fake bank in the
runner's format (arms KA_<arm>) and read by pdyn_a1 UNCHANGED (OU controls at the same tau_v). Reading rule in A1.8.

Usage: pdyn_a1_ka.py build [--workers 10]  ->  results/armb_pdyn_a1_ka/bank/KA_<arm>/...
       pdyn_a1_ka.py run   [--workers 10]  ->  results/armb_pdyn_a1_ka/ (runner output) + ka_verdict.json
"""
import os
for _k in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(_k, "1")
import json, math, sys
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
import numpy as np
HERE = Path(__file__).resolve().parent; ROOT = HERE.parent
sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(HERE))
import pdyn_phase1 as P
import pdyn_c9 as D
import pdyn_a1 as A

ARMS = ["M0s1", "M0s2", "M0s3", "A2"]
OUT = ROOT / "results" / "armb_pdyn_a1_ka"; BANK = OUT / "bank"; REAL = ROOT / "results" / "armb_pdyn_a1"
H_RANK = 32


def build_unit(args):
    arm, L, M = args
    pj = REAL / arm / "parts" / f"L{L:02d}_{M}.json"; part = json.load(open(pj))
    W = part["windows"]["W2"]; steps = [int(s) for s in part["steps"] if 500 <= s < 3001]
    m, n = part["shape"]
    D_ = P.load_series(ROOT / "cache" / "armb", arm, steps, L, M); sig = D_["sig"]
    Ls = D.slow_component(D.strip_sort(sig), np.array(steps, float), H_RANK, 0.0).mean(0)       # time-mean, rank-smoothed
    v_target = float(W["m2"]["vrms"]); tau_v = A.TAU_V[arm]; times = np.array(steps, float)
    seed = 7_000_000 + 1000 * L + 10 * P.TYPES.index(M) + ARMS.index(arm)
    s = 1e-3; hist = []
    for it in range(3):
        S = D.warp(A.ou_rect(m, n, times, tau_v, s, seed, 1), Ls)
        r = P.m2_single(S, times); v1 = float(r.get("vrms", float("nan"))); hist.append((s, v1))
        if not np.isfinite(v1) or v1 <= 0 or abs(v1 / v_target - 1) < P.XSTEP_MATCH_TOL: break
        s *= v_target / v1
    return dict(arm=arm, L=L, M=M, steps=steps, shape=[m, n], S=S, match=dict(s=s, v_target=v_target, vrms=v1, passes=len(hist)))


def build(workers=10):
    jobs = [(a, L, M) for a in ARMS for L in range(6) for M in P.TYPES]
    store = {}
    with ProcessPoolExecutor(max_workers=workers) as ex:
        for r in ex.map(build_unit, jobs):
            store[(r["arm"], r["L"], r["M"])] = r
            print(f"built KA_{r['arm']} L{r['L']} {r['M']}: vrms {r['match']['vrms']:.4f} / target {r['match']['v_target']:.4f}", flush=True)
    meta = {}
    for arm in ARMS:
        steps = store[(arm, 0, "Q")]["steps"]
        for t_i, t in enumerate(steps):
            d = BANK / f"KA_{arm}" / f"step{t:05d}"; d.mkdir(parents=True, exist_ok=True)
            for L in range(6):
                out = {}
                for M in P.TYPES:
                    r = store[(arm, L, M)]; m, n = r["shape"]; sg = np.sort(r["S"][t_i])[::-1]
                    out[f"sig_{M}"] = sg; out[f"U32_{M}"] = np.eye(max(m, n), 32, dtype=np.float32)[:m]; out[f"V32_{M}"] = np.eye(n, 32, dtype=np.float32)
                    out[f"rms_{M}"] = np.array(float(np.sqrt((sg ** 2).sum()) / math.sqrt(m * n)))
                np.savez(d / f"L{L:02d}.npz", **out)
            (d / "DONE").write_text("ka")
        st = BANK / "_staging" / f"KA_{arm}"; st.mkdir(parents=True, exist_ok=True)
        src = HERE / "staging" / arm / "trainlog.jsonl"
        (st / "trainlog.jsonl").write_text(src.read_text() if src.exists() else "")
        meta[arm] = {f"L{L}_{M}": store[(arm, L, M)]["match"] for L in range(6) for M in P.TYPES}
    (OUT / "build_meta.json").write_text(json.dumps(meta, indent=1, default=float))
    print("KA_BUILD_DONE", flush=True)


def run(workers=10):
    for arm in ARMS: A.TAU_V[f"KA_{arm}"] = A.TAU_V[arm]
    A.install()
    P.main(["--bank", str(BANK), "--arms", *[f"KA_{a}" for a in ARMS], "--out", str(OUT / "read"), "--windows", "W2",
            "--workers", str(workers), "--no-figs", "--mp-witness", "none", "--staging", str(BANK / "_staging")])
    W = A.words(OUT / "read")
    import collections
    res = {"rule": "h_KA = fraction of KA matrices whose C(x) component HOLDS (full-bin, sealed). <= 0.5 -> STATISTIC; >= 0.8 -> DYNAMICS; else INCONCLUSIVE",
           "arms": {}}
    for arm in ARMS:
        def cx_frac(out_dir, a):
            hold = tot = 0
            for pj in sorted((Path(out_dir) / a / "parts").glob("*.json")):
                Wd = json.load(open(pj))["windows"]["W2"]; arr = dict(np.load(pj.with_suffix(".npz")))
                v = P.verdict_p2(dict(Wd, name="W2"), arr); c = v.get("components") or {}
                if "Cx" in c: tot += 1; hold += int(c["Cx"]["word"] == "HOLDS")
            return hold, tot
        hk, nk = cx_frac(OUT / "read", f"KA_{arm}"); hr, nr = cx_frac(REAL, arm)
        h = hk / nk if nk else float("nan")
        word = "STATISTIC (full-bin C(x) NOT LICENSED on realistic shapes)" if h <= 0.5 else ("DYNAMICS (statistic licensed)" if h >= 0.8 else "INCONCLUSIVE")
        res["arms"][arm] = dict(h_KA=h, ka_cx_hold=hk, ka_n=nk, real_cx_hold=hr, real_n=nr, word=word,
                                ka_P2=W["arms"].get(f"KA_{arm}", {}).get("A1_word_30of36"))
        print(f"{arm}: KA (beta=1 OU truth, real density) C(x) HOLDS {hk}/{nk} (h_KA {h:.2f}) vs real {hr}/{nr} -> {word}", flush=True)
    (OUT / "ka_verdict.json").write_text(json.dumps(res, indent=1, default=float))
    print("KA_DONE", flush=True)


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "all"; w = int(sys.argv[sys.argv.index("--workers") + 1]) if "--workers" in sys.argv else 10
    OUT.mkdir(parents=True, exist_ok=True)
    if cmd in ("build", "all"): build(w)
    if cmd in ("run", "all"): run(w)
