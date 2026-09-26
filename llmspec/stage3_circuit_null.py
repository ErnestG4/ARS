"""Product-Ginibre circuit null (brief v1.1 §4D): OV score = sum(lambda)/sum|lambda| over eig(V O), V 128x2048 and
O 2048x128 independent Gaussian; QK symmetric-energy fraction of M = Q^T K, Q and K 96x2048 independent Gaussian
(the non-rotary shape). 4000 draws each. Reports the null median and 1/5/95/99th percentiles, to be read against the
per-head distributions in stage3_long.parquet. The full-circuit copying score keeps step 0 as its empirical null
(it involves the real embeddings)."""
import json
from pathlib import Path
import numpy as np, torch
ROOT = Path(__file__).resolve().parent
g = torch.Generator(device="cuda").manual_seed(4)
ov, qk = [], []
for i in range(0, 4000, 200):
    V = torch.randn((200, 128, 2048), generator=g, device="cuda", dtype=torch.float64)
    O = torch.randn((200, 2048, 128), generator=g, device="cuda", dtype=torch.float64)
    ev = torch.linalg.eigvals(V @ O)
    ov.append((ev.real.sum(-1) / ev.abs().sum(-1)).cpu().numpy())
    Q = torch.randn((200, 96, 2048), generator=g, device="cuda", dtype=torch.float64)
    K = torch.randn((200, 96, 2048), generator=g, device="cuda", dtype=torch.float64)
    AA, BB, BA = Q @ Q.transpose(1, 2), K @ K.transpose(1, 2), K @ Q.transpose(1, 2)
    f2 = torch.einsum("bij,bji->b", AA, BB); tr = torch.einsum("bij,bji->b", BA, BA)
    qk.append(((f2 + tr) / (2 * f2)).cpu().numpy())
ov, qk = np.concatenate(ov), np.concatenate(qk)
q = lambda x: {p: float(np.quantile(x, p / 100)) for p in (1, 5, 50, 95, 99)}
out = {"doc": __doc__, "ov_score": q(ov), "qk_sym_nr": q(qk), "n": len(ov)}
(ROOT / "results" / "stage3_circuit_null.json").write_text(json.dumps(out, indent=1))
print(json.dumps({k: out[k] for k in ("ov_score", "qk_sym_nr")}, indent=1))
