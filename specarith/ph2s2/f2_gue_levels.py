"""PH2S Stage 2 (F2) baseline: fresh long-GUE sequences, generated now (Will, overnight queue 2026-10-10 item 4); the
tapered statistic is applied only after its taper is declared (cs4/G_S_DESIGN.md §1) and before the F2 seal.
Reuses ph2s/gue_levels.py's construction unchanged (that file is pinned by the Stage 1 seal, so it is imported, not
edited), with a distinct seed base: SEED0 = 20261012 (Stage 1: 20261011; exploration: 20261010).

  python f2_gue_levels.py SEED L OUT
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "ph2s"))
import gue_levels as GL  # noqa: E402

GL.SEED0 = 20261012

if __name__ == "__main__":
    GL.main(int(sys.argv[1]), int(sys.argv[2]), sys.argv[3])
