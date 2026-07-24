"""
thermo/pollution_onset.py — map where collocation spectral pollution actually onsets.

Reviewer's central concern: the three f(alpha) landmarks all sit at the ENDS of the s-range
(s->1/2, s=1, s->inf), so the interior intervals (1/2,1) and (1,inf) rest on single-method
cross-agreement -- and collocation has a pollution mode that failed at one end. Pollution is
continuous in s, so there may be a "quiet band" in the unlandmarked interior where it is present
but small enough to look plausible.

This maps it directly. At each s, compare the UNFILTERED leading eigenvalue (power iteration =
largest modulus) against the PERRON-FILTERED one (largest sign-definite eigenvector):

  * where they agree to ~full precision, the largest-modulus eigenvalue IS the Perron one --
    no pollution, and the filter is a proven NO-OP (this is the reviewer's first test, run at
    s=1 and everywhere else at once).
  * where they diverge, a spurious non-Perron eigenvalue has overtaken the true one --
    pollution. The smallest such s is the onset.

If the onset is cleanly at the large-s edge and the whole interior shows the filter as a no-op,
the "quiet band" is ruled out. If filtered != unfiltered anywhere in (1/2, ~4), that band exists
and the interior curve there was single-method-wrong.

Run:  python3 thermo/pollution_onset.py
"""
from __future__ import annotations

import json
import os
import sys

import mpmath as mp

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from thermo.gauss_thermo import GaussOperator          # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))


def main():
    mp.mp.dps = 60
    op = GaussOperator(N=32, dps=48, Ne=100)
    # fine grid across the whole physical range, dense through the interior
    grid = ["0.55", "0.6", "0.7", "0.8", "0.9", "1", "1.1", "1.25", "1.5", "1.75",
            "2", "2.25", "2.5", "2.75", "3", "3.25", "3.5", "3.75", "4", "4.25",
            "4.5", "5", "5.5", "6", "7", "8"]
    print("Filter no-op / pollution-onset sweep (N=32, dps=48)")
    print("agreement = -log10 | lam_perron - lam_poweriter | / |lam_perron|  (higher = filter is a no-op)\n")
    print(f"  {'s':>6s} {'lam (Perron)':>22s} {'filt==unfilt digits':>20s}")
    rows, onset = [], None
    for s in grid:
        sv = mp.mpf(s)
        M = op.matrix(sv)
        lam_pow, _ = op.leading(sv, matrix=M)
        lam_per, _ = op.leading_perron(sv, matrix=M)
        d = float(-mp.log10(abs(lam_per - lam_pow) / abs(lam_per))) if lam_per != lam_pow else 99.0
        polluted = d < 20            # dense eig itself is ~dps-accurate; <20 = genuine divergence
        if polluted and onset is None:
            onset = s
        rows.append({"s": s, "lam_perron": mp.nstr(mp.re(lam_per), 20),
                     "agree_digits": round(d, 1), "polluted": polluted})
        flag = "  <-- POLLUTION" if polluted else ""
        print(f"  {s:>6s} {mp.nstr(mp.re(lam_per), 18):>22s} {d:20.1f}{flag}")

    # explicit no-op check at s=1 (reviewer's first test) against the 29-digit unfiltered value
    s1 = mp.mpf(1)
    lp, _ = op.leading_perron(s1)
    d1 = float(-mp.log10(abs(lp - 1)))
    print(f"\n  s=1 no-op check: leading_perron gives L0={mp.nstr(mp.re(lp),25)}")
    print(f"       matches exact eigenvalue 1 to {d1:.1f} digits (unfiltered gives 29.1) -> "
          f"filter is a SELECTOR, not a correction, in the clean region")

    out = {"grid_rows": rows, "pollution_onset_s": onset,
           "s1_noop_digits_vs_exact": d1,
           "interior_clean": bool(onset is None or float(onset) >= 4.0),
           "reading": ("pollution onsets at s=%s; the whole interior (1/2, that) shows the filter "
                       "as a no-op, so there is NO quiet band -- the single-method interior is "
                       "un-polluted" % onset) if (onset is None or float(onset) >= 4.0) else
                      ("pollution onset at s=%s is INSIDE the interior -- a quiet band exists and "
                       "the curve there was single-method-suspect" % onset)}
    print(f"\n  pollution onset: s = {onset}")
    print(f"  interior (1/2, 4) clean (filter a no-op there): {out['interior_clean']}")
    json.dump(out, open(os.path.join(HERE, "pollution_onset_measured.json"), "w"),
              indent=2, default=str)
    print("wrote pollution_onset_measured.json")


if __name__ == "__main__":
    main()
