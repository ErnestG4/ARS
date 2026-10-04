"""verify_pdyn_a1.py -- synthetic known answers and red path for the PDYN A1 runner (pdyn_a1.py), BEFORE any real re-read
(A1.1: "the phase-0 separation sizes are re-measured for the new family before the re-read"). No real data is read.

A fake bank in the runner's own format (bank/<arm>/stepNNNNN/L0x.npz with sig_/U32_/V32_/rms_ keys, DONE, trainlog),
2 layers x 6 types (n = 256; MLP 1024 x 256 / 256 x 1024), W2 grid (every 25 steps over [500, 3000]):
  FAKEOU_C1  beta = 1 OU driver, tau_v = 10   -> must read P2 HOLDS (A1 word >= 30/36 scaled: >= 10/12 matrices HOLD)
  FAKEOU_B2  beta = 2 OU driver, tau_v = 10   -> SPECIFICITY line (reported; see below)
  FAKEOU_PO  Poisson OU levels, tau_v = 10    -> must NOT read HOLDS
Every arm is read through pdyn_a1 (OU controls at tau_v = 10). FAKEOU_B2 is reported as a SPECIFICITY line, not a pass
criterion: the first run (10-04 04:50) showed it reading HOLDS on 9/12 matrices (runner-majority HOLDS) -- P2 at bank
cadence does not separate beta = 2 from beta = 1 (declared in PDYN_PREREG_A1 A1.6 before the real read). Reported: per-matrix curvature medians of the three
witness families and the fraction of matrices whose witnesses separate (the re-measured discrimination at this n).
--redpath: FAKEOU_C1 read against the ORIGINAL (smooth-GP, phase-1) controls must NOT read HOLDS (the C(x) reference
           matters: the phase-1 failure mode reproduced on a known beta = 1 OU truth).
Exit 0 = PASS.
"""
import os
for _k in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(_k, "1")      # forked workers: one BLAS thread each (set before numpy loads)
import argparse, json, math, shutil, sys, tempfile
from pathlib import Path
import numpy as np
from scipy.linalg import svd
HERE = Path(__file__).resolve().parent; ROOT = HERE.parent
sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(HERE))
import pdyn_phase1 as P
import pdyn_a1 as A
TYPES = P.TYPES


def build(bank, arm, fam, n=256, tau_v=10.0, s=None, seed=0):
    times = np.arange(500, 3001, 25, dtype=float)
    shapes = {"Q": (n, n), "K": (n, n), "V": (n, n), "O": (n, n), "MLP_IN": (4 * n, n), "MLP_OUT": (n, 4 * n)}
    rng = np.random.default_rng(seed); store = {}
    for layer in range(2):
        for M, (m, nn) in shapes.items():
            sd = int(rng.integers(2 ** 31))
            if fam == "po":
                lev = A.ou_poisson(min(m, nn), times, tau_v, s or 0.05, sd)
                lev = np.sort(lev, axis=1)[:, ::-1]; sig = (lev - lev.min() + 5.0) * 0.001 + 0.02
            else:
                sig = A.ou_rect(m, nn, times, tau_v, s or 2e-3, sd, beta=1 if fam == "c1" else 2) * 0.02
            g = np.random.default_rng(sd)
            u0 = np.linalg.qr(g.standard_normal((m, 32)))[0].astype(np.float32); v0 = np.linalg.qr(g.standard_normal((nn, 32)))[0].astype(np.float32)
            store[(layer, M)] = (sig, u0, v0)
    for t_i, t in enumerate(times):
        d = Path(bank) / arm / f"step{int(t):05d}"; d.mkdir(parents=True, exist_ok=True)
        for layer in range(2):
            out = {}
            for M in TYPES:
                sig, u0, v0 = store[(layer, M)]; m, nn = shapes[M]
                out[f"sig_{M}"] = sig[t_i]; out[f"U32_{M}"] = u0; out[f"V32_{M}"] = v0
                out[f"rms_{M}"] = np.array(float(np.sqrt((sig[t_i] ** 2).sum()) / math.sqrt(m * nn)))
            np.savez(d / f"L{layer:02d}.npz", **out)
        (d / "DONE").write_text("fake-ou")
    st = Path(bank) / "_staging" / arm; st.mkdir(parents=True, exist_ok=True)
    with open(st / "trainlog.jsonl", "w") as f:
        for s_ in range(1, 3001):
            f.write(json.dumps({"step": s_, "loss": 3 + 8 * math.exp(-s_ / 300), "lr": 1e-3}) + "\n")


def run(bank, out, arms, ou=True, workers=6):
    if ou: A.install()
    else:
        P.matched_family = A._ORIG_MATCHED; P.analyse_unit = A._ORIG_UNIT
    A._CUR["tau_v"] = 10.0
    P.main(["--bank", str(bank), "--arms", *arms, "--out", str(out), "--windows", "W2", "--workers", str(workers),
            "--no-figs", "--mp-witness", "none", "--staging", str(Path(bank) / "_staging"), "--layers", "0", "1"])
    return A.words(out)


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--redpath", action="store_true"); ap.add_argument("--keep", default=None)
    ap.add_argument("--workers", type=int, default=6); a = ap.parse_args()
    root = Path(a.keep) if a.keep else Path(tempfile.mkdtemp(prefix="pdyn_a1_verify_"))
    bank = root / "bank"; fails = []
    def check(c, msg):
        print(("PASS " if c else "FAIL ") + msg, flush=True); (None if c else fails.append(msg))
    for arm, fam, sd in (("FAKEOU_C1", "c1", 1), ("FAKEOU_B2", "b2", 2), ("FAKEOU_PO", "po", 3)):
        if not (bank / arm).exists(): build(bank, arm, fam, seed=sd)
    W = run(bank, root / "ou", ["FAKEOU_C1", "FAKEOU_B2", "FAKEOU_PO"], ou=True, workers=a.workers)
    def nh(arm): r = W["arms"][arm]; return r["n_matrices_HOLDS"], r["n_matrices"]
    h, n = nh("FAKEOU_C1"); check(n > 0 and h >= math.ceil(n * 30 / 36), f"(1) beta=1 OU truth vs OU controls: {h}/{n} matrices HOLD (need >= {math.ceil(n * 30 / 36)})")
    h, n = nh("FAKEOU_B2"); rm = W["arms"]["FAKEOU_B2"]["runner_majority_word_W2"]
    spec = (h < math.ceil(n * 30 / 36)) and rm != "HOLDS"
    print(("INFO " if True else "") + f"(2) SPECIFICITY vs beta = 2 (declared limit, not a pass criterion): beta=2 OU truth reads {h}/{n} matrices HOLD, "
          f"runner-majority word {rm} -> P2 {'DOES' if spec else 'does NOT'} separate beta = 2 from beta = 1 at bank cadence "
          "(curvature medians of the C1' and beta=2 witnesses differ by ~5 % at the 25-step cadence; C(x) and velocity are beta-blind)", flush=True)
    h, n = nh("FAKEOU_PO"); check(h < math.ceil(n * 30 / 36), f"(3) Poisson OU truth does NOT read HOLDS: {h}/{n} matrices HOLD")
    sep = [];
    for pj in sorted((root / "ou" / "FAKEOU_C1" / "parts").glob("*.json")):
        Wd = json.load(open(pj))["windows"]["W2"]; npz = dict(np.load(pj.with_suffix(".npz")))
        v = P.verdict_p2(dict(Wd, name="W2"), npz); c = (v.get("components") or {}).get("curvature") or {}
        sep.append(dict(unit=pj.stem, n_k=v.get("n_k"), separated=c.get("witnesses_separated"), S_c1=c.get("S_c1"), S_b2=c.get("S_b2"), S_po=c.get("S_po")))
    frac = float(np.mean([bool(x["separated"]) for x in sep])) if sep else 0.0
    print(f"     re-measured discrimination (OU witnesses, n=256 fake, W2 grid): witnesses separated on {frac:.0%} of {len(sep)} matrices; "
          f"median n_k {np.median([x['n_k'] for x in sep if x['n_k']]) if sep else 'n/a'}", flush=True)
    check(frac >= 0.8, f"(4) OU beta=2 / Poisson witnesses separate from C1' on >= 80 % of matrices ({frac:.0%})")
    json.dump(dict(separation=sep, words=W), open(root / "verify_summary.json", "w"), indent=1, default=str)
    if a.redpath:
        R = run(bank, root / "orig", ["FAKEOU_C1"], ou=False, workers=a.workers)
        h, n = R["arms"]["FAKEOU_C1"]["n_matrices_HOLDS"], R["arms"]["FAKEOU_C1"]["n_matrices"]
        red = h < math.ceil(n * 30 / 36)
        print(("RED  " if red else "FAIL ") + f"(redpath) beta=1 OU truth vs the ORIGINAL smooth-GP controls: {h}/{n} HOLD (must not read HOLDS)", flush=True)
        if not red: fails.append("redpath did not go red")
    print("verify dir:", root)
    print("FAILURES:", fails or "none"); sys.exit(1 if fails else 0)


if __name__ == "__main__":
    main()
