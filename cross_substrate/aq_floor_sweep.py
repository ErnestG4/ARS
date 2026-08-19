"""a_q DETECTION FLOOR — SNR-swept, with the deployed operating point marked.
COMMITTED GENERATOR of cross_substrate/aq_floor_sweep.json.

Purpose: decide whether the ~6% of unthinned `periodic_q7` trains that fail
their own period test are failing because the a_q ESTIMATOR has a detection
floor at that operating point (which would propagate to every a_q reading at
that train length, including real substrates) or because the GENERATOR emits
off-spec trains (which perturbs only the calibrated floor).

DESIGN NOTE — an earlier version of this test was "inject a period at high
SNR and confirm detection".  That is a POSITIVE CONTROL, not a test: it
returns ~100% and is equally consistent with "no floor" and "a floor that
only bites at the SNR the generator actually produces".  The informative
form sweeps the operating parameter DOWN TO AND PAST the deployed value and
reports a CURVE with that value marked.

The knob is jitter/period.  The deployed calibrator is
    periodic_q7 = _gen_periodic(period=7.0, jitter=0.05, n=400)
so the deployed operating point is jitter/period = 0.0071 — already a sharp
period.  A detection floor AT that point is therefore the consequential
outcome, not a remote one.

Reading the curve:
  deployed point on the PLATEAU  -> the estimator is not the explanation;
                                    the consequential branch retires and the
                                    6% stays unattributed with its label.
  deployed point on the SHOULDER -> the 6% is explained AND a_q carries a
                                    documented detection floor at its own
                                    operating point.
"""

import json
import os
import sys

import numpy as np

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_HERE)
_RIEMANN = os.path.join(os.path.dirname(_ROOT), "riemann_explorer")
for p in (_HERE, _ROOT, _RIEMANN):
    if p not in sys.path:
        sys.path.insert(0, p)

import rf_decoy_battery as B                                    # noqa: E402
from calibrator_panel import _gen_periodic                      # noqa: E402

PERIOD = 7.0
DEPLOYED_JITTER = 0.05
N_POINTS = 400
N_SEEDS = 40
JITTERS = [0.005, 0.01, 0.02, 0.05, 0.10, 0.20, 0.40, 0.80, 1.60]


def detection_rate(jitter, n_points, floor, seeds=N_SEEDS):
    hit = 0
    tot = 0
    for s in range(seeds):
        t = np.sort(np.asarray(
            _gen_periodic(s, period=PERIOD, jitter=jitter, n=n_points), float))
        if t.size < 50:
            continue
        _, _, df = B.aq_profile(t)
        v = B.aq_at(df, 7)
        tot += 1
        if np.isfinite(v) and v >= floor:
            hit += 1
    return hit, tot


def main():
    _, floor = B.run_ground_truth_and_decoy()
    print(f"\ncalibrated a_q floor = {floor:.3f}")
    print(f"deployed operating point: jitter={DEPLOYED_JITTER} "
          f"(jitter/period = {DEPLOYED_JITTER / PERIOD:.4f}), n={N_POINTS}\n")
    print(f"{'jitter':>8} {'j/period':>9} {'detected':>10} {'rate':>7}   note")
    rows = {}
    for j in JITTERS:
        k, n = detection_rate(j, N_POINTS, floor)
        rate = k / n if n else float("nan")
        mark = "  <-- DEPLOYED" if abs(j - DEPLOYED_JITTER) < 1e-12 else ""
        rows[f"{j}"] = dict(jitter=j, ratio=j / PERIOD, k=k, n=n, rate=rate,
                            deployed=bool(mark))
        print(f"{j:>8.3f} {j / PERIOD:>9.4f} {k:>6}/{n:<3} {rate:>7.2f}{mark}",
              flush=True)

    # secondary axis: train length at the deployed jitter
    print(f"\ntrain-length axis at the deployed jitter={DEPLOYED_JITTER}:")
    length = {}
    for npts in (200, 400, 800, 1600):
        k, n = detection_rate(DEPLOYED_JITTER, npts, floor, seeds=24)
        length[str(npts)] = dict(k=k, n=n, rate=k / n if n else None)
        print(f"  n_points={npts:>5}: {k}/{n} = {k / n:.2f}", flush=True)

    dep = rows[f"{DEPLOYED_JITTER}"]["rate"]
    plateau = max(r["rate"] for r in rows.values())
    on_shoulder = bool(dep < plateau - 0.02)
    out = dict(floor=float(floor), period=PERIOD, n_points=N_POINTS,
               deployed_jitter=DEPLOYED_JITTER, n_seeds=N_SEEDS,
               jitter_sweep=rows, train_length_at_deployed=length,
               deployed_rate=dep, plateau_rate=plateau,
               deployed_on_shoulder=on_shoulder,
               verdict=("SHOULDER — the estimator has a detection floor at "
                        "its own deployed operating point; the ~6% is "
                        "explained and a_q carries a documented floor"
                        if on_shoulder else
                        "PLATEAU — the estimator is not the explanation; the "
                        "consequential branch retires and the ~6% stays "
                        "unattributed with its honest label"))
    json.dump(out, open(f"{_HERE}/aq_floor_sweep.json", "w"), indent=1)
    print(f"\ndeployed rate {dep:.2f} vs plateau {plateau:.2f} -> "
          f"{out['verdict']}", flush=True)


if __name__ == "__main__":
    main()
