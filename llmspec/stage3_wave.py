"""POST-HOC (declared 2026-09-25 23:45, after Stage 3 found compression too fast for the schedule): per-layer
compression timing ("wave", Liu) using EVERY extracted revision (schedule + pythia_1.4b_dense_V.txt).
Per layer and type: the first step at which stable rank <= half its step-0 value; Spearman(layer, log10 step).
Descriptive; the timing resolution is the checkpoint grid and is reported with it."""
import json
from pathlib import Path
import numpy as np
from scipy.stats import spearmanr
ROOT = Path(__file__).resolve().parent
revs = sorted([p.name for p in (ROOT / "cache" / "s3" / "pythia-1.4b").iterdir() if (p / "DONE").exists()],
              key=lambda r: int(r[4:]))
steps = [int(r[4:]) for r in revs]
out = {"doc": __doc__, "steps": steps, "types": {}}
for M in ("Q", "K", "V", "O", "MLP_IN", "MLP_OUT"):
    sr = np.array([[float((lambda s: (s ** 2).sum() / s.max() ** 2)(np.load(ROOT / "cache" / "s3" / "pythia-1.4b" / r / f"L{l:02d}.npz")[f"sig_{M}"]))
                    for l in range(24)] for r in revs])          # (n_rev, 24)
    half = []
    for l in range(24):
        idx = np.where((np.array(steps) > 0) & (sr[:, l] <= 0.5 * sr[0, l]))[0]
        half.append(steps[idx[0]] if len(idx) else None)
    ok = [i for i, h in enumerate(half) if h]
    rho, p = spearmanr(ok, np.log10([half[i] for i in ok])) if len(ok) > 3 else (np.nan, np.nan)
    out["types"][M] = {"half_step_by_layer": half, "spearman_rho": float(rho), "p": float(p)}
    print(M, half, f"rho={rho:+.2f} p={p:.3g}")
(ROOT / "results" / "stage3_wave.json").write_text(json.dumps(out, indent=1))
