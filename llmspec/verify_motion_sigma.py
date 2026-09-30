"""stage3_motion.sigma_max (Gram top eigenvalue) must agree with torch matrix_norm(ord=2) to 1e-10 relative on real
Delta W (pythia-1.4b step1000 -> step2000, layer 3, all six types) and on a synthetic rank-1 + noise matrix.
--redpath: compare against the SECOND singular value instead; it must disagree (exit 0 iff it does)."""
import sys
import numpy as np, torch
import remote_st as R
import stage3_motion as MO
bad = []
redp = "--redpath" in sys.argv
a = MO.fetch_layer(R.index("EleutherAI/pythia-1.4b", "step1000"), 3)
b = MO.fetch_layer(R.index("EleutherAI/pythia-1.4b", "step2000"), 3)
cases = [(M, b[M].double() - a[M].double()) for M in MO.MATS]
g = torch.Generator(device="cuda").manual_seed(0)
u = torch.randn(2048, 1, generator=g, device="cuda", dtype=torch.float64); v = torch.randn(1, 8192, generator=g, device="cuda", dtype=torch.float64)
cases.append(("synthetic", 3 * u @ v + torch.randn(2048, 8192, generator=g, device="cuda", dtype=torch.float64)))
for name, dW in cases:
    ref = torch.linalg.svdvals(dW)
    r = float(ref[1] if redp else ref[0])
    got = MO.sigma_max(dW)
    rel = abs(got - r) / r
    print(f"{name}: gram {got:.12e} svd {r:.12e} rel {rel:.1e}")
    if rel > 1e-10: bad.append(name)
print("disagreements:", bad or "none")
sys.exit((0 if bad else 1) if redp else (1 if bad else 0))
