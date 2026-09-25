"""Known-answer check for s3stats (the ONE pipeline used by witnesses and real data). Exit 1 on any failure.
Wishart (square 2048^2 and 2048x8192, 4 each) must read beta=1; i.i.d. uniform levels must read Poisson.
--redpath: feed the Poisson levels to the beta=1 checks; they must FAIL (exit 0 iff they do)."""
import sys
import numpy as np, torch
import s3stats as S

g = torch.Generator(device="cuda").manual_seed(0)
sq = list(torch.linalg.svdvals(torch.randn((4, 2048, 2048), generator=g, device="cuda", dtype=torch.float64)).cpu().numpy())
rc = list(torch.linalg.svdvals(torch.randn((4, 2048, 8192), generator=g, device="cuda", dtype=torch.float64)).cpu().numpy())
rng = np.random.default_rng(1)
poi = [np.sqrt(np.sort(rng.uniform(0, 1, 2048))) for _ in range(4)]
GOE_S2 = np.array([0.442, 0.583, 0.768, 0.909])
fails = []
def beta1(name, sp):
    r = S.local_stats(sp, "bulk")
    if abs(r["rt"] - 0.5307) > 0.006: fails.append(f"{name} rt {r['rt']:.4f}")
    if abs(r["q_kde"] - 1.0) > 0.06: fails.append(f"{name} q {r['q_kde']:.3f}")
    rel = np.abs(np.array(r["sigma2"])[1:] - GOE_S2[1:]) / GOE_S2[1:]
    if rel.max() > 0.15: fails.append(f"{name} sigma2 {np.round(r['sigma2'], 3)}")
    print(name, round(r["rt"], 4), round(r["q_kde"], 3), np.round(r["sigma2"], 3), np.round(r["delta3"], 3))
if "--redpath" in sys.argv:
    beta1("poisson-as-beta1", poi)
    print("REDPATH failures:", fails); sys.exit(0 if fails else 1)
beta1("wishart-square", sq); beta1("wishart-1:4", rc)
r = S.local_stats(poi, "bulk")
if abs(r["rt"] - 0.3863) > 0.01: fails.append(f"poisson rt {r['rt']:.4f}")
if not r["sigma2"][-1] > 5: fails.append(f"poisson sigma2(10) {r['sigma2'][-1]:.2f}")
print("poisson", round(r["rt"], 4), round(r["q_kde"], 3), np.round(r["sigma2"], 3))
print("FAILURES:", fails or "none"); sys.exit(1 if fails else 0)
