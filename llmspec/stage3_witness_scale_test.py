"""Protocol-template question (Addendum S3 item 4): does anything in the G1 witness depend on ABSOLUTE scale? Spacing
statistics are scale-free, and fp16 rounding is relative except in the subnormal range (|x| < 6.1e-5). Here the same
witness construction (identical pipeline, fp16-rounded Gaussians) runs at the standard 410M scale and at 0.17x (the most
extreme seed ratio, seed 4's O / MLP_OUT) for full O (1024^2, 24 per pool) and per-head Q (64 x 1024, 384 per pool),
R = 12 pools each, all bands. It reports the differences against the pooled replicate SE and the subnormal fraction.
The pre-registered +-20% rule still runs as written; this only records whether it protected against anything."""
import json
from pathlib import Path
import numpy as np, torch
import s3stats as S, stage3_witness as W
ROOT = Path(__file__).resolve().parent
sc = json.loads((ROOT / "results" / "stage3_witness_pythia-410m.json").read_text())["scales"]["final"]
g = torch.Generator(device="cuda").manual_seed(31)
out = {"doc": __doc__, "types": {}}
for T, (m, n, K) in {"O": (1024, 1024, 24), "head_Q": (64, 1024, 384)}.items():
    base = sc[T]; res = {}
    for tag, s in (("scale_1.00", base), ("scale_0.17", 0.17 * base)):
        reps = {b: {"rt": [], "q_kde": []} for b in S.BANDS}
        for _ in range(12):
            sp = W.sig_batch(m, n, K, s, True, g)
            for b in S.BANDS:
                st = S.local_stats(sp, b); reps[b]["rt"].append(st["rt"]); reps[b]["q_kde"].append(st["q_kde"])
        res[tag] = {b: {k: (float(np.mean(v)), float(np.std(v, ddof=1))) for k, v in d.items()} for b, d in reps.items()}
    x = torch.randn(10 ** 6, generator=g, device="cuda", dtype=torch.float64) * 0.17 * base
    sub = float((x.abs() < 6.1e-5).double().mean())
    diff = {b: {k: {"diff": res["scale_0.17"][b][k][0] - res["scale_1.00"][b][k][0],
                    "se": float(np.hypot(res["scale_0.17"][b][k][1], res["scale_1.00"][b][k][1]) / np.sqrt(12))}
                for k in ("rt", "q_kde")} for b in S.BANDS}
    out["types"][T] = {"scale": base, "subnormal_fraction_at_0.17x": sub, "means": res, "diff": diff}
    print(T, f"scale {base:.5f}; subnormal fraction at 0.17x: {sub:.4f}")
    for b in S.BANDS:
        print("  ", b, {k: f"{v['diff']:+.4f} (SE {v['se']:.4f})" for k, v in diff[b].items()})
(ROOT / "results" / "stage3_witness_scale_test.json").write_text(json.dumps(out, indent=1))
