"""
phase26/aspect_angles.py — per-detector aspect angles for GRB 230307A.

For a Fermi-GBM detector, the aspect angle is the angle between the
detector's outward normal vector and the source direction, both in the
spacecraft frame.  On-axis detectors (aspect ~ 0°) see the source
head-on; off-axis detectors (aspect ~ 90°) see it side-on; back-facing
detectors (aspect > 90°) see it through the spacecraft.

For triggered bursts, Fermi-GBM's on-board trigger algorithm publishes
the source direction in spacecraft coordinates (TR_SCAZ, TR_SCZEN) in
the TRIGDAT file's OB_CALC HDU.  Combined with the static detector
pointing directions in spacecraft frame (Meegan et al. 2009, Table 1),
aspect angles follow directly from the inner product of the two
spacecraft-frame unit vectors.

Caveats:
  * TRIGDAT localization is quantised to ~5° sky pixels (on-board
    algorithm uses a discrete grid).  Aspect angles therefore have
    ~5° uncertainty before considering the published localization
    error radius (3.22° for GRB 230307A).
  * The "spacecraft frame" axis convention here is Z-up (along the
    nominal LAT pointing axis), X toward the +X spacecraft face, Y
    toward +Y.  Zenith angle is measured from +Z; azimuth from +X
    in the XY plane.  Detector vectors and source vector are both
    expressed in this convention.
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from astropy.io import fits


THIS_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(THIS_DIR)
sys.path.insert(0, ROOT_DIR)


# ─── GBM detector pointing directions in spacecraft frame ────────────────
# Source: Meegan et al. 2009, ApJ 702, 791, Table 1 ("GBM Detector
# Locations").  Each detector's outward normal in spacecraft spherical
# coordinates (zenith angle θ from +Z, azimuth φ from +X).  Values in
# degrees.  Used identically across all GBM-triggered bursts since the
# detectors are bolted to the spacecraft.
GBM_DETECTOR_POINTING_DEG = {
    'n0': (45.89,  20.58),
    'n1': (45.11,  45.18),
    'n2': (58.44,  90.21),
    'n3': (314.87, 45.24),
    'n4': (303.15, 90.27),
    'n5': (3.35,   89.79),
    'n6': (224.93, 20.43),
    'n7': (224.62, 46.18),
    'n8': (236.61, 89.97),
    'n9': (135.19, 45.55),
    'na': (123.73, 90.42),
    'nb': (183.74, 90.32),
    'b0': (0.0,    90.0),   # BGO 0, +X side
    'b1': (180.0,  90.0),   # BGO 1, -X side
}
# NOTE: convention here is (azimuth_deg, zenith_deg).  Zenith from +Z;
# azimuth from +X in the XY plane.


def spherical_to_cartesian(az_deg: float, zen_deg: float) -> np.ndarray:
    """Unit vector from spherical (azimuth, zenith) in degrees."""
    az = np.radians(az_deg)
    zen = np.radians(zen_deg)
    return np.array([
        np.sin(zen) * np.cos(az),
        np.sin(zen) * np.sin(az),
        np.cos(zen),
    ])


def aspect_angle_deg(detector_az_zen: tuple, source_az_zen: tuple) -> float:
    """Angle between detector normal and source direction (deg)."""
    d = spherical_to_cartesian(*detector_az_zen)
    s = spherical_to_cartesian(*source_az_zen)
    cos_a = float(np.clip(np.dot(d, s), -1.0, 1.0))
    return float(np.degrees(np.arccos(cos_a)))


def source_direction_from_trigdat(trigdat_path: Path) -> tuple[float, float]:
    """Read source direction in spacecraft frame from TRIGDAT file's
    OB_CALC table.  Returns (TR_SCAZ_deg, TR_SCZEN_deg) from the final
    on-board localization update."""
    with fits.open(trigdat_path) as h:
        ob = h['OB_CALC'].data
        return float(ob['TR_SCAZ'][-1]), float(ob['TR_SCZEN'][-1])


def compute_aspect_table(trigdat_path: Path,
                           detectors: list[str] = None,
                           ) -> pd.DataFrame:
    """For each detector in `detectors` (default: all 14 GBM detectors),
    compute aspect angle relative to the source direction from the
    TRIGDAT file.

    Returns a DataFrame with columns:
      detector  detector_type ("NaI"/"BGO")  az_deg  zen_deg
      source_az_deg  source_zen_deg
      aspect_deg  cos_aspect
    """
    detectors = detectors or list(GBM_DETECTOR_POINTING_DEG.keys())
    src_az, src_zen = source_direction_from_trigdat(trigdat_path)
    rows = []
    for d in detectors:
        if d not in GBM_DETECTOR_POINTING_DEG:
            continue
        az_d, zen_d = GBM_DETECTOR_POINTING_DEG[d]
        asp = aspect_angle_deg((az_d, zen_d), (src_az, src_zen))
        rows.append(dict(
            detector=d,
            detector_type='BGO' if d.startswith('b') else 'NaI',
            az_deg=az_d, zen_deg=zen_d,
            source_az_deg=src_az, source_zen_deg=src_zen,
            aspect_deg=asp,
            cos_aspect=float(np.cos(np.radians(asp))),
        ))
    return pd.DataFrame(rows)


def main():
    """Compute the per-detector aspect table for GRB 230307A and
    pretty-print, plus save to phase26_results."""
    trigdat = (Path(ROOT_DIR) / 'data' / 'phase21_grb_panel'
                / 'raw' / 'bn230307656_aux'
                / 'glg_trigdat_all_bn230307656_v01.fit')
    out_dir = Path(ROOT_DIR) / 'data' / 'phase26_results'
    out_dir.mkdir(parents=True, exist_ok=True)

    if not trigdat.exists():
        raise FileNotFoundError(
            f"TRIGDAT not present at {trigdat}.  Re-download via "
            f"phase26/run_phase26.py --download-aux."
        )

    df = compute_aspect_table(trigdat)
    df.to_parquet(out_dir / 'detector_aspect.parquet', index=False)

    print("=" * 72)
    print("GRB 230307A per-detector aspect angles")
    print("=" * 72)
    print(f"  source in spacecraft frame: az={df['source_az_deg'].iloc[0]:.2f}°  "
          f"zen={df['source_zen_deg'].iloc[0]:.2f}°")
    print()
    df_sorted = df.sort_values('aspect_deg')
    print(f"  {'det':3s}  {'type':4s}  {'az_d':>7s}  {'zen_d':>7s}  "
          f"{'aspect':>7s}  {'cos':>7s}")
    for _, r in df_sorted.iterrows():
        print(f"  {r['detector']:3s}  {r['detector_type']:4s}  "
              f"{r['az_deg']:7.2f}  {r['zen_deg']:7.2f}  "
              f"{r['aspect_deg']:7.2f}  {r['cos_aspect']:+7.3f}")
    print()
    print(f"  → {out_dir}/detector_aspect.parquet")


if __name__ == '__main__':
    main()
