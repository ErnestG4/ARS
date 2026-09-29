"""Seal-time dry run of armb/b4_analyze.py on a FABRICATED cache (no arm data is read). Exercises every analysis
branch end to end and plants one known answer: A1/A2 stable-rank trajectories of O and MLP_OUT are A0's curve mapped
through the WARMUP time map (+ noise), so Q1 must say WARMUP (via E4 where the fixture noise is licensed).
Writes everything under a temp root; the real cache/results are untouched."""
import json, shutil, sys, tempfile
from pathlib import Path
import numpy as np

HERE = Path(__file__).resolve().parent; ROOT = HERE.parent
sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(HERE))
import b4_analyze as B
import q1_warp as QW

rng = np.random.default_rng(7)
TMP = Path(tempfile.mkdtemp()); (TMP / "results").mkdir()
for f in ("armb_q1_licence.json", "armb_q1_warp_licence.json", "armb_q1_warp_licence_v2.json", "armb_q2_licence.json", "armb_bulk_power_70m.json", "armb_noise_calibration.json"):
    shutil.copy(ROOT / "results" / f, TMP / "results" / f)
shutil.copy(ROOT / "results" / "probes.npz", TMP / "results" / "probes.npz")
B.ROOT, B.RES = TMP, TMP / "results"

BASE_SQ = np.sort(np.linalg.svd(rng.standard_normal((512, 512)), compute_uv=False))[::-1]
BASE_MLP = np.sort(np.linalg.svd(rng.standard_normal((2048, 512)), compute_uv=False))[::-1]
HEADS = np.stack([np.sort(np.linalg.svd(rng.standard_normal((64, 512)), compute_uv=False))[::-1] for _ in range(8)])
HEADS_O = np.stack([np.sort(np.linalg.svd(rng.standard_normal((512, 64)), compute_uv=False))[::-1] for _ in range(8)])
g0 = np.arange(0, 6001, 5, dtype=float)
CURVE = 20 + 100 * np.where(g0 < 2000, ((np.log(2016) - np.log(g0 + 16)) / np.log(2016)) ** 2, 0) + np.where(g0 >= 2000, 25 * (1 - np.exp(-(g0 - 2000) / 800)), 0)


def sr_curve(arm, t):
    tau = t if arm in ("A0", "M0s1", "M0s2") or arm.startswith("pythia") else QW.tau(np.array([t], float), arm, "WARMUP")[0]
    return float(np.interp(max(tau, 0), g0, CURVE)) * (1 + 0.004 * rng.standard_normal())


def spec(base, target_sr):
    R = (base[1:] ** 2).sum(); s1 = np.sqrt(R / max(target_sr - 1, 1e-3)); out = base.copy(); out[0] = max(s1, base[1] * 1.0001)
    return out


def write_step(d, src, t):
    d.mkdir(parents=True, exist_ok=True)
    for L in range(6):
        z = {}
        for M in ("Q", "K", "V", "O", "MLP_IN", "MLP_OUT"):
            base = BASE_MLP if M.startswith("MLP") else BASE_SQ
            z[f"sig_{M}"] = spec(base, sr_curve(src, t) if M in ("O", "MLP_OUT") else 40 * np.exp(-t / 800) + 10)
        for M in "QKV":
            z[f"sighead_{M}"] = HEADS
        z["sighead_O"] = HEADS_O
        frac = 1 / (1 + np.exp(-(np.log(t + 16) - np.log(700)) / 0.2))
        z["ov_eig"] = (rng.standard_normal((8, 64)) + frac * 3) + 1j * rng.standard_normal((8, 64))
        z["qk_sym_nr"] = 0.5 + 0.03 * frac * np.sign(rng.standard_normal(8)) + 0.0002 * rng.standard_normal(8)
        np.savez(d / f"L{L:02d}.npz", **z)
    ind = 0.9 / (1 + np.exp(-(np.log(t + 16) - np.log(800)) / 0.1))
    np.savez(d / "MARKERS.npz", induction=np.full((6, 8), ind) + 0.01 * rng.random((6, 8)), loss_text=np.array(10 * np.exp(-t / 600) + 3))


def write_dw(fp):
    fp.parent.mkdir(parents=True, exist_ok=True)
    np.savez(fp, **{f"L{L:02d}_{M}_{k}": np.array(rng.uniform(5, 50)) for L in range(6) for M in B.TYPES for k in ("sr", "fro")})


import b4_extract as BX  # noqa: E402  (interval definitions)
for arm, stop in B.STOPS.items():
    for t in B.grid(arm):
        write_step(TMP / "cache" / "armb" / arm / f"step{t:05d}", arm, t)
    for a, b in sorted(set(BX.Q3_S + BX.lr_intervals() + [iv for iv in BX.Q4_SHARED_INTERVALS if iv[1] <= stop])):
        write_dw(TMP / "cache" / "armb" / arm / f"DW_{a:05d}_{b:05d}.npz")
for m in B.REFS:
    for t in B.SHARED:
        write_step(TMP / "cache" / "s3" / m / f"step{t}", m, t)
    for a, b in BX.Q4_SHARED_INTERVALS:
        write_dw(TMP / "cache" / "s3" / m / f"DW_{a:05d}_{b:05d}.npz")
wit = {"types": {c: {"ks95": 0.08, "runs": {"witness_fp16_final": {"bulk:rt": {"mean": 0.5305}}}} for c in B.CELLS}}
(TMP / "results" / "stage3_witness_pythia-70m.json").write_text(json.dumps(wit))

ok = True
_full_grid, _full_stops = B.grid, dict(B.STOPS)


def bulk_thin():
    """Bulk branch on A0 only, every 10th checkpoint (dry-run speed; the real run uses every arm and checkpoint)."""
    B.STOPS.clear(); B.STOPS["A0"] = 3000; B.grid = lambda arm: _full_grid(arm)[::10]
    try:
        return B.bulk()
    finally:
        B.grid = _full_grid; B.STOPS.clear(); B.STOPS.update(_full_stops)


for q, fn in (("q1", B.q1), ("q2", B.q2), ("q3", B.q3), ("q4", B.q4), ("bulk", bulk_thin)):
    try:
        r = fn(); print(q, "OK")
        if q == "q1":
            for name in ("TP_O", "TP_MLPOUT"):
                print("  ", name, "VERDICT:", r[name]["VERDICT"], {X: (r[name][X].get("route"), r[name][X].get("decision")) for X in ("A1", "A2")})
        if q == "q2":
            print("   A0 pairs:", r["A0"]["pairs"]); print("   wave:", r["A0"]["wave"]["verdict"], round(r["A0"]["wave"]["S"], 3))
        if q == "q3":
            print("   A0:", r["A0"]["VERDICT"])
        if q == "q4":
            print("   family", r["family"], "T", round(r["T"], 2), "n_diff", r["n_optimizer_different"])
        if q == "bulk":
            print("   ", {a: v["VERDICT"] for a, v in r.items()})
    except Exception as e:
        ok = False; import traceback; traceback.print_exc(); print(q, "FAILED:", repr(e))
# second bulk pass: witness means shifted +0.05 so EVERY cell is VIOLATED and the density-matched ladder runs
wit2 = {"types": {c: {"ks95": 0.08, "runs": {"witness_fp16_final": {"bulk:rt": {"mean": 0.5805}}}} for c in B.CELLS}}
(TMP / "results" / "stage3_witness_pythia-70m.json").write_text(json.dumps(wit2))
B.grid = lambda arm: _full_grid(arm)[::60]; B.STOPS.clear(); B.STOPS["A0"] = 3000
try:
    r = B.bulk(); a = r["A0"]
    labels = sorted({f["label"] for f in a["violated"]})
    good = a["counts"]["VIOLATED"] > 0 and a["counts"]["HOLDS_AT_MDD"] == 0 and bool(labels)
    print("bulk VIOLATED branch", "OK" if good else "BAD", a["counts"], labels, a["VERDICT"]); ok &= good
except Exception as e:
    ok = False; import traceback; traceback.print_exc(); print("bulk VIOLATED branch FAILED:", repr(e))
finally:
    B.grid = _full_grid; B.STOPS.clear(); B.STOPS.update(_full_stops)
print("DRY RUN", "PASS" if ok else "FAIL"); shutil.rmtree(TMP)
sys.exit(0 if ok else 1)
