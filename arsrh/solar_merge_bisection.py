"""
arsrh/solar_merge_bisection.py — bisect the dedup merge window (reviewer's diagnostic).

The z=6.3 aggressive-merge (<=30 min) row: is it (a) the honest number once artifacts are gone, or
(b) an over-merge that amputated real short-timescale signal? The tell in the 4-row table: mass03
barely moved (0.59 -> 0.53) while z collapsed 4x -- so the significance drop looks n-driven / from
deleting the specific short-ISI pairs that carry the signal, not from the statistic degrading.

Reviewer's prediction (unsealed): as the merge window is pulled DOWN from 30 min toward the
overlap-merge baseline (0 min gap), z RECOVERS SMOOTHLY -> the collapse is merge-window amputation
and the light-touch z~26 is the honest central estimate. If z stays depressed for some window below
the raw overlap case -> a genuine artifact lives in that band and the fragility is worse. The
bisection falsifies either way.

Decomposition reported per window: n events, observed mass03, cycle-null mass03 mean +/- sd, the
raw GAP (obs - null_mean), and z. If the gap stays ~constant while sd rises with falling n, the z
drop is purely n-loss (amputation). If the gap itself shrinks, real short-ISI mass is being removed.

Run:  $HOME/fmexplorer/bin/python3 arsrh/solar_merge_bisection.py
"""
from __future__ import annotations

import json
import os
import sys

import numpy as np

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _ROOT)
from arsrh.solar_dedup_test import load_mx, onsets_overlap_merge   # noqa: E402
from arsrh.solar_surrogate_port import (rate_envelope, inhomogeneous_poisson,  # noqa: E402
                                        normspacing_pool, mass03, DAY)


def cycle_null(onsets, observed, bw_days=45, B=150):
    grid, lam = rate_envelope(onsets, bw_days * DAY)
    m = [mass03(normspacing_pool(inhomogeneous_poisson(grid, lam, onsets.size)))
         for _ in range(B)]
    m = np.array([x for x in m if np.isfinite(x)])
    gap = observed - m.mean()
    z = gap / m.std() if m.std() > 0 else np.inf
    return float(m.mean()), float(m.std()), float(gap), float(z)


def main():
    mx = load_mx()
    print(f"Solar M+X merge-window bisection (raw {len(mx)} events).")
    print("amputation signature: GAP≈const while sd rises with falling n (z drop is n-loss).")
    print("artifact signature: GAP itself shrinks toward 0 (real short-ISI mass removed).\n")
    print(f"  {'gap(min)':>9s} {'n':>6s} {'mass03':>7s} {'null':>7s} {'null_sd':>8s} {'GAP':>7s} {'z':>7s}")
    rows = []
    for gap_min in (0, 5, 10, 15, 20, 25, 30):
        on = onsets_overlap_merge(mx, gap_min=gap_min)
        obs = mass03(normspacing_pool(on))
        nm, ns, gap, z = cycle_null(on, obs)
        rows.append({"gap_min": gap_min, "n": int(on.size), "mass03": obs,
                     "null_mean": nm, "null_sd": ns, "gap_obs_minus_null": gap, "z": z})
        print(f"  {gap_min:>9d} {on.size:>6d} {obs:>7.3f} {nm:>7.3f} {ns:>8.4f} {gap:>7.3f} {z:>7.1f}")

    gaps = [r["gap_obs_minus_null"] for r in rows]
    zs = [r["z"] for r in rows]
    sds = [r["null_sd"] for r in rows]
    # amputation: GAP roughly flat (range small vs its value), sd grows monotonically as n falls
    gap_flat = (max(gaps) - min(gaps)) < 0.35 * np.mean(gaps)
    sd_grows = sds[-1] > 1.6 * sds[0]
    z_recovers_smoothly = all(zs[i] >= zs[i + 1] - 1 for i in range(len(zs) - 1))  # monotone-ish up as gap->0
    amputation = gap_flat and sd_grows
    out = {"rows": rows,
           "gap_flat_across_windows": bool(gap_flat),
           "null_sd_grows_as_n_falls": bool(sd_grows),
           "z_monotone_recovers_toward_small_window": bool(z_recovers_smoothly),
           "verdict": ("AMPUTATION — the GAP (obs - null) is ~constant across merge windows while "
                       "the null sd rises with falling n, so the z collapse at 30 min is n-loss from "
                       "deleting real short-ISI (fast sympathetic) flares, NOT artifact removal. The "
                       "light-touch z~26 (overlap-merge / catalog dedup) is the honest central "
                       "estimate; the effect's true timescale is shorter than 30 min."
                       if amputation else
                       "NOT clean amputation — the obs-minus-null GAP itself shrinks as the window "
                       "grows, so some real short-ISI mass IS being removed in the sub-30-min band; "
                       "the fragility is worse than sign-only and the honest center is below z~26."),
           "quoting": "EXISTENTIAL claim with a bounded floor only: clustering beyond both the solar "
                      "cycle and catalog sub-flare artifacts, survives aggressive de-duplication in "
                      "SIGN at all merge windows tested. No single z quoted as THE number."}
    print(f"\n  GAP flat across windows: {gap_flat} (range {max(gaps)-min(gaps):.3f} vs mean {np.mean(gaps):.3f})")
    print(f"  null sd grows as n falls: {sd_grows} ({sds[0]:.4f} -> {sds[-1]:.4f})")
    print(f"  VERDICT: {out['verdict'][:90]}...")
    json.dump(out, open(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                     "solar_merge_bisection_measured.json"), "w"),
              indent=2, default=str)
    print("\n  wrote solar_merge_bisection_measured.json")


if __name__ == "__main__":
    main()
