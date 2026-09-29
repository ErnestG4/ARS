"""B4 amendment 3 (2026-09-29, pre-data: no B4 statistic exists; extraction of references is running): calibrate the
MEASURED trajectory noise to the licences' INJECTED noise units. Synthetic only.

Defect fixed: the licence rows are indexed by the injected relative (or absolute) noise SD sigma, but b4_analyze measured
the SD of the residual about a Savitzky-Golay smooth, which is systematically SMALLER than sigma (the smoother absorbs
part of the noise). Comparing the two directly selects too low a row -- anti-conservative.
Calibration (per measurement, per grid, per injected level, per noise type), 300 draws each:
  Q1  measurement: residual SD about SG(window 9, order 2) on the grid index, RELATIVE; curves: the q1_licence shape
      families (kinked / smooth minima, plateaus, monotone) on the arm's exact grid -- A0 (grid to 3000), A1 (to 5000),
      A2 (dense, grids.arm_grid); levels 0.5/1/2/5 %.
  Q2  measurement: SG(window 5, order 2); curves: the q2_licence sigmoid / Gompertz trajectories on A0's grid (also used
      for the M0 arms: same grid); RELATIVE levels 0.5/1/2/5 % and ABSOLUTE 0.01/0.03/0.07.
ROW RULE (sealed): the calibrated level for an observed measurement m is the smallest injected level L whose MEDIAN
measured noise is >= m, taken as the MAXIMUM over the two noise types (iid, AR(1) phi 0.5); m above every median -> no
row (NOT LICENSED). A licence cell is then used only if it is licensed for BOTH noise types at that level (so the
lag-1 type classifier plays no part). Output: results/armb_noise_calibration.json.
"""
import json, sys
from pathlib import Path
import numpy as np
from scipy.signal import savgol_filter

HERE = Path(__file__).resolve().parent; ROOT = HERE.parent
sys.path.insert(0, str(HERE))
import q1_licence as QL  # noqa: E402
import q2_licence as Q2L  # noqa: E402
from grids import arm_grid  # noqa: E402

OUT = ROOT / "results" / "armb_noise_calibration.json"
DRAWS, SEED = 300, 20261005
REL = [0.005, 0.01, 0.02, 0.05]
ABS = [0.01, 0.03, 0.07]


def measure(y, win, rel):
    sm = savgol_filter(y, win, 2, axis=-1); r = (y - sm) / sm if rel else (y - sm)
    return np.std(r, axis=-1, ddof=1)


def calib_q1(grid, stop, rng):
    shapes = [f for _, _, f, _, _ in QL.shapes(grid, stop)]
    out = {}
    for ar in (False, True):
        for s in REL:
            ms = []
            for d in range(DRAWS):
                f = shapes[d % len(shapes)]
                ms.append(float(measure(f * (1 + QL.noise(rng, len(grid), 1, s, ar)[0]), 9, True)))
            out[f"{s}_{'ar' if ar else 'iid'}"] = {"median": float(np.median(ms)), "q10": float(np.quantile(ms, .1)), "q90": float(np.quantile(ms, .9))}
    return out


def calib_q2(grid, rng):
    curves = Q2L.curves(grid); out = {}
    for kind, levels in (("rel", REL), ("abs", ABS)):
        for ar in (False, True):
            for s in levels:
                ms = []
                for d in range(DRAWS):
                    _, f, _, _ = curves[d % len(curves)]
                    base = 0.1 + 0.8 * f if kind == "abs" else 20 + 80 * f
                    e = QL.noise(rng, len(grid), 1, s, ar)[0]
                    y = base + e if kind == "abs" else base * (1 + e)
                    ms.append(float(measure(y, 5, kind == "rel")))
                out[f"{kind}_{s}_{'ar' if ar else 'iid'}"] = {"median": float(np.median(ms)), "q10": float(np.quantile(ms, .1)), "q90": float(np.quantile(ms, .9))}
    return out


def level(m, table, levels, prefix=""):
    """Sealed row rule: smallest injected level whose median measured noise >= m, max over iid/AR; None if above all."""
    per = []
    for typ in ("iid", "ar"):
        ok = [L for L in levels if table[f"{prefix}{L}_{typ}"]["median"] >= m]
        if not ok:
            return None
        per.append(min(ok))
    return max(per)


def main():
    rng = np.random.default_rng(SEED)
    res = {"doc": __doc__, "q1": {}, "q2": {}}
    for arm, stop in (("A0", 3000), ("A1", 5000), ("A2", 3000)):
        g = np.array(arm_grid(arm), float)
        res["q1"][arm] = calib_q1(g, stop, rng)
        print("q1", arm, {k: round(v["median"], 5) for k, v in res["q1"][arm].items()}, flush=True)
    res["q2"]["A0grid"] = calib_q2(np.array(arm_grid("A0"), float), rng)
    print("q2", {k: round(v["median"], 5) for k, v in res["q2"]["A0grid"].items()}, flush=True)
    OUT.write_text(json.dumps(res, indent=1))


if __name__ == "__main__":
    main()
