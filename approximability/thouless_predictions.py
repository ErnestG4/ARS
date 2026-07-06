"""Will's pre-registered checks on BANKED pi data (zero new expensive compute).

(3) closed form  W_k ~ 4/lambda^{m_k},  m_k = #{j<=k : a_j>=2}
(2) per-band histogram: depth-3 (q=113) = 106 inherited (unmoved) + 7 narrow newcomers (<1e-6)
(1) a_3 step ratio to many figures: BIST forbids exact preservation -> expect deficit below 1,
    plausibly ~ (q1/q3)^power = (7/113)^p.  float64 pass here; mpmath refinement in a companion.
"""
import sys, math
sys.path.insert(0, ".")
import numpy as np
from numpy.linalg import eigvalsh
from task1_pi_depth5 import potential, cf_frac, convergents
import mpmath as mp; mp.mp.dps = 40

cf = cf_frac(mp.pi, 6); ps, qs = convergents(cf)     # frac(pi) CF = [7,15,1,292,1,1]
print("frac(pi) CF =", cf, " convergent q =", qs)

def floquet_edges(V):
    q = len(V)
    H = np.zeros((q, q)); np.fill_diagonal(H, V)
    idx = np.arange(q - 1); H[idx, idx + 1] = 1; H[idx + 1, idx] = 1
    Hp = H.copy(); Hp[0, q - 1] = 1; Hp[q - 1, 0] = 1
    Ha = H.copy(); Ha[0, q - 1] = -1; Ha[q - 1, 0] = -1
    e = np.sort(np.concatenate([eigvalsh(Hp), eigvalsh(Ha)]))
    lo = e[0::2]; hi = e[1::2]
    return lo, hi, (hi - lo)

# ---- banked totals (from FLOQUET/depths123 jsons) ----
banked = {
 8.0:  {1:0.49243580482385524, 2:0.06050808028893595, 3:0.06050808028887127, 4:0.007434711},
 24.0: {1:0.16637833577668776, 2:0.006918942099228942, 3:0.0069189420992247785, 4:0.0002877284373556388},
 32.0: {1:0.12487817121832445, 2:0.0038981646627032074, 3:0.003898164662664183, 4:0.00012168397079225998},
}
a = {1:cf[0],2:cf[1],3:cf[2],4:cf[3]}            # 7,15,1,292
m = {k: sum(1 for j in range(1,k+1) if a[j] >= 2) for k in (1,2,3,4)}
print("\n(3) CLOSED FORM  W_k ~ 4/lam^m_k :   m =", m)
print(f"{'lam':>4} {'depth':>5} {'a_k':>4} {'m_k':>3} | {'W (banked)':>13} {'4/lam^m':>13} {'ratio W/pred':>13}")
for lam in (8.0,24.0,32.0):
    for k in (1,2,3,4):
        pred = 4.0/lam**m[k]
        print(f"{lam:>4.0f} {k:>5} {a[k]:>4} {m[k]:>3} | {banked[lam][k]:13.6e} {pred:13.6e} {banked[lam][k]/pred:13.6f}")
    print()

# ---- (2) per-band histogram, depth-2 (q=106) vs depth-3 (q=113), lam=8 ----
print("(2) PER-BAND: does depth-3 = 106 inherited + 7 narrow newcomers?")
for lam in (8.0,):
    lo2,hi2,w2 = floquet_edges(potential(ps[1],qs[1],lam))   # q=106
    lo3,hi3,w3 = floquet_edges(potential(ps[2],qs[2],lam))   # q=113
    w2s=np.sort(w2)[::-1]; w3s=np.sort(w3)[::-1]
    print(f"  lam={lam:.0f}  q2=106 widths: max {w2s[0]:.3e} min {w2s[-1]:.3e}")
    print(f"           q3=113 widths: max {w3s[0]:.3e} min {w3s[-1]:.3e}")
    # the 7 newcomers = the 7 narrowest of the 113? test bimodality via log10 histogram
    lw3 = np.log10(np.clip(w3,1e-18,None))
    for edge in [-2,-3,-4,-5,-6,-7,-8,-10,-12,-14]:
        print(f"    #bands width<1e{edge}: {(w3<10.0**edge).sum():>4}")
    # width carried by the 7 narrowest
    narrow7 = w3s[-7:]
    print(f"    7 narrowest widths: {['%.2e'%x for x in narrow7]}")
    print(f"    width in 7 narrowest / total = {narrow7.sum()/w3.sum():.3e}   (6-fig equality budget ~1e-6)")
    # compare the 106 widest of depth-3 to depth-2's 106 (inheritance check)
    w3_top106 = np.sort(w3)[::-1][:106]
    inherit_err = np.abs(np.sort(w3_top106)-np.sort(w2)).max()
    print(f"    max|sorted(depth3 top106) - sorted(depth2)| = {inherit_err:.3e}  (unmoved if ~0)")

# ---- (1) a_3 ratio, float64 pass (direction + scale; mpmath refinement separate) ----
print("\n(1) a_3 STEP  W_3/W_2  (BIST: must be < 1, not exact):")
for lam in (8.0,24.0,32.0):
    r = banked[lam][3]/banked[lam][2]      # W_3/W_2
    print(f"  lam={lam:.0f}:  W3/W2 = {r:.15f}   deficit(1-r) = {1-r:.3e}   [float64, sum-noise ~1e-13 rel]")
print("  (float64 sum-noise ~1e-13 rel; a robust deficit needs the mpmath edge-refinement pass)")
