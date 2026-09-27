"""ADDENDUM S3 item 3 (STAGE3_SEED_PREREG.md, a5cd7bf): symmetry discriminator for the per-head-Q drift. LABELLED
DESCRIPTIVE -- not part of, and not a change to, the frozen drift test.
Per head, the non-rotary QK product P = Q_nr^T K_nr (1024 x 1024, rank d_head - rot = 48 for 410M) is invariant under the
QK symmetry (Q -> A Q, K -> A^-T K, A invertible on the non-rotary dims); per-head Q alone is not. Its nonzero singular
values are those of S_q U_q^T K_nr (Q_nr = U_q S_q V_q^T). For each of the 10 410M runs at step 0 and step 143000, the
384 per-head product spectra are pooled through s3stats (bulk band: <r~> and kde(4) Brody q), against a product witness:
independent N(0,1) Q_nr, K_nr factors of the same shapes, same pipeline, R = 20 pools. (Products are scale-free in these
statistics, so no scale matching is needed.)
Reading (descriptive): a late-training q drift in the PRODUCT concerns the function; drift only in Q alone concerns where
each seed sits along the QK symmetry.
Output: results/stage3_qkprod_drift.json.
"""
import json, sys
from pathlib import Path
import numpy as np, torch
import s3stats as S
import stage3_motion as MO
import mcfg

ROOT = Path(__file__).resolve().parent
DEV = "cuda"
RUNS = ["pythia-410m"] + [f"pythia-410m-seed{k}" for k in range(1, 10)]
H, DH, D, ROT = 16, 64, 1024, 16


def prod_sv(Qh, Kh):
    """Qh, Kh: (H, DH, D). Non-rotary product singular values per head, (H, DH-ROT)."""
    Qn, Kn = Qh[:, ROT:], Kh[:, ROT:]
    U, s, _ = torch.linalg.svd(Qn, full_matrices=False)            # Qn = U diag(s) V^T
    M = (U.transpose(1, 2) * s[..., None]) @ Kn                     # S_q U_q^T K_nr
    return torch.linalg.svdvals(M).cpu().numpy()


def witness(R=20, seed=3):
    g = torch.Generator(device=DEV).manual_seed(seed)
    qs, rts = [], []
    for _ in range(R):
        sp = []
        for _ in range(24):
            Q = torch.randn((H, DH, D), generator=g, device=DEV, dtype=torch.float64)
            K = torch.randn((H, DH, D), generator=g, device=DEV, dtype=torch.float64)
            sp.extend(prod_sv(Q, K))
        st = S.local_stats(sp, "bulk"); qs.append(st["q_kde"]); rts.append(st["rt"])
    return {"q_mean": float(np.mean(qs)), "q_sd": float(np.std(qs, ddof=1)), "rt_mean": float(np.mean(rts)),
            "rt_sd": float(np.std(rts, ddof=1)), "R": R}


def main():
    fp = ROOT / "results" / "stage3_qkprod_drift.json"
    out = json.loads(fp.read_text()) if fp.exists() else {"doc": __doc__, "runs": {}}
    if "witness" not in out:
        out["witness"] = witness(); fp.write_text(json.dumps(out, indent=1))
    w = out["witness"]
    print("product witness:", w, flush=True)
    for m in RUNS:
        if m in out["runs"]:
            continue
        rec = {}
        for rev in ("step0", "step143000"):
            src = MO.LayerSource(rev, m)
            sp = []
            for L in range(24):
                mats = src.layer(L)
                Qh = mats["Q"].double().reshape(H, DH, D); Kh = mats["K"].double().reshape(H, DH, D)
                sp.extend(prod_sv(Qh, Kh))
            src.close(); torch.cuda.empty_cache()
            st = S.local_stats(sp, "bulk")
            rec[rev] = {"q": st["q_kde"], "rt": st["rt"], "dq": st["q_kde"] - w["q_mean"], "drt": st["rt"] - w["rt_mean"]}
        out["runs"][m] = rec
        fp.write_text(json.dumps(out, indent=1))
        print(m, {k: (round(v["dq"], 4), round(v["drt"], 4)) for k, v in rec.items()}, flush=True)


if __name__ == "__main__":
    main()
