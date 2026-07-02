"""Panel C rigor — separate arrangement SIGNAL from C-estimator NOISE using cyclic-rotation replicates.

Ground truth (synthetic_validate_fitters discipline): cyclic rotations of a periodic CF are the SAME operator
up to translation => identical spectrum => identical C. The designed run's dedup-by-alpha kept rotations as
separate members, so within-necklace C-spread IS a direct noise measurement. Signal = between-necklace C spread
at FIXED K (digit multiset). Verdict is trustworthy only where signal > noise.
"""
import json, math
import numpy as np

fams = json.load(open("panel_C_designed.json"))

def necklace(period):
    """Canonical (min) rotation of the primitive period — the cyclic-equivalence class label."""
    p = tuple(period); n = len(p)
    return min(tuple(p[i:] + p[:i]) for i in range(n))

noise_spreads, noise_sds = [], []
sig_rows = []
print(f"{'multiset':16s} {'K':>6s} {'#necklaces':>10s} {'noise(sd)':>10s} {'signal(sd)':>10s} {'S/N':>6s}")
for fam in fams:
    groups = {}
    for m in fam["members"]:
        groups.setdefault(necklace(m["period"]), []).append(m)
    # noise: within-necklace C spread (should be 0)
    within = [np.std([m["C"] for m in g]) for g in groups.values() if len(g) >= 2]
    # signal: between-necklace mean-C (each necklace = one true operator), at fixed K
    neck_meanC = {nk: np.mean([m["C"] for m in g]) for nk, g in groups.items()}
    neck_Lam = {nk: np.mean([m["lagrange"] for m in g]) for nk, g in groups.items()}
    noise_sd = float(np.mean(within)) if within else float('nan')
    sig_sd = float(np.std(list(neck_meanC.values()))) if len(neck_meanC) >= 2 else float('nan')
    sn = sig_sd / noise_sd if (noise_sd and not math.isnan(noise_sd) and noise_sd > 0) else float('nan')
    print(f"{str(fam['multiset']):16s} {fam['K']:>6.3f} {len(groups):>10d} "
          f"{noise_sd:>10.4f} {sig_sd:>10.4f} {sn:>6.2f}")
    if not math.isnan(noise_sd):
        noise_sds.append(noise_sd)
    for nk in neck_meanC:
        sig_rows.append({"multiset": fam["multiset"], "K": fam["K"], "necklace": list(nk),
                         "lagrange": neck_Lam[nk], "C_meanrot": neck_meanC[nk],
                         "n_rot": len(groups[nk])})

# pooled noise floor
gn = float(np.mean(noise_sds))
print(f"\nPOOLED C-estimator noise floor (cyclic-rotation replicates, must=0): sd ≈ {gn:.4f}")
print("  -> C values are only distinguishable when they differ by >~2*sd = %.3f" % (2 * gn))

# within-family between-necklace: does C track Lagrange ABOVE noise? (per family, fixed K)
from scipy.stats import pearsonr
print("\nBetween-necklace C-vs-Λ at FIXED K (per family; only necklace means, rotation-averaged):")
allpairs = []
for fam in fams:
    rows = [r for r in sig_rows if r["multiset"] == fam["multiset"]]
    if len(rows) < 3:
        continue
    L = np.array([r["lagrange"] for r in rows]); C = np.array([r["C_meanrot"] for r in rows])
    r = pearsonr(L, C)[0]
    rngC = C.max() - C.min()
    print(f"  {str(fam['multiset']):16s} K={fam['K']:.3f}  n_neck={len(rows)}  "
          f"pearson(Λ,C)={r:+.3f}  C-range={rngC:.3f}  ({'ABOVE' if rngC > 2*gn else 'below'} 2·noise)")
    for a in range(len(rows)):
        for b in range(a + 1, len(rows)):
            allpairs.append((rows[b]["lagrange"] - rows[a]["lagrange"], rows[b]["C_meanrot"] - rows[a]["C_meanrot"]))

dL = np.array([p[0] for p in allpairs]); dC = np.array([p[1] for p in allpairs])
big = np.abs(dL) > 0.3        # large-Λ-gap pairs (well-separated arrangements)
print(f"\nPooled between-necklace pairs (rotation-averaged): {len(allpairs)}")
print(f"  all: sign(ΔΛ)==sign(ΔC) {int(np.sum(np.sign(dL)==np.sign(dC)))}/{len(allpairs)}  pearson={pearsonr(dL,dC)[0]:+.3f}")
print(f"  large-Λ-gap (|ΔΛ|>0.3, above noise): {int(big.sum())} pairs  "
      f"sign-agree {int(np.sum((np.sign(dL)==np.sign(dC))&big))}/{int(big.sum())}  "
      f"pearson={pearsonr(dL[big],dC[big])[0]:+.3f}")
json.dump({"noise_floor_sd": gn, "sig_rows": sig_rows}, open("panel_C_noise.json", "w"), indent=1)
print("\nwrote panel_C_noise.json")
