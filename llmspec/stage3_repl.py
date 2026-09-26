"""G3 replication scorer (STAGE3_REPL_PREREG.md, 8147f53): R1-R6 for the model in LLMSPEC_MODEL. Model-general.
Run on pythia-1.4b first: it must reproduce the values stage3_confounds2 / stage3_headnull / stage3_circuit_null /
stage3_motion_eq produced (consistency check of this code), then on 1B and 410M. Writes results/stage3_repl.json,
keyed by model (merged, not overwritten).
"""
import json, sys
from pathlib import Path
import numpy as np, pandas as pd, torch
import remote_st as R
import mcfg

ROOT = Path(__file__).resolve().parent
DEV = "cuda"
MODEL, C = mcfg.name(), mcfg.get()
H, DH, D, ROT, NL = C["H"], C["DH"], C["D"], C["ROT"], C["n_layer"]
SUF = mcfg.suffix()
gen = torch.Generator(device=DEV).manual_seed(12)


def haar(n, k=None):
    shape = (n, n) if k is None else (k, n, n)
    Q, Rr = torch.linalg.qr(torch.randn(shape, generator=gen, device=DEV, dtype=torch.float64))
    d = torch.sign(torch.diagonal(Rr, dim1=-2, dim2=-1))
    return Q * d[..., None, :]


def top_left(W, k=8):
    return torch.linalg.eigh(W @ W.T)[1][:, -k:]


def r1_r2():
    idx = R.index(C["repo"], "step143000")
    rot_obs, rot_null, rot_rows, th = [], [], [], {"Q": [], "K": []}
    for L in range(NL):
        R.check_stop()
        a, _ = R.fetch(idx, f"gpt_neox.layers.{L}.attention.query_key_value.weight")
        qkv = torch.from_numpy(a.astype(np.float64)).to(DEV).reshape(H, 3, DH, D)
        for j, M in ((0, "Q"), (1, "K")):
            Wh = qkv[:, j]; W = Wh.reshape(H * DH, D)
            U = top_left(W) ** 2
            if M == "K":
                rot_obs.append(float(U.reshape(H, DH, 8)[:, :ROT].sum((0, 1)).mean()))
                rn = []
                for _ in range(3):
                    Un = top_left((haar(DH, H) @ Wh).reshape(H * DH, D)) ** 2
                    rn.append(float(Un.reshape(H, DH, 8)[:, :ROT].sum((0, 1)).mean()))
                rot_null.append(np.mean(rn))
                rot_rows.append(float((Wh[:, :ROT] ** 2).sum() / (Wh ** 2).sum()))
            obs = float(U.reshape(H, DH, 8).sum(1).max(0).values.mean())
            nul = []
            for _ in range(2):
                Wn = torch.stack([Wh[h] @ haar(D) for h in range(H)]).reshape(H * DH, D)
                nul.append(float((top_left(Wn) ** 2).reshape(H, DH, 8).sum(1).max(0).values.mean()))
            th[M].append((obs, float(np.mean(nul))))
    r1 = {"K_rotary_mass": float(np.mean(rot_obs)), "within_head_rotation_null": float(np.mean(rot_null)),
          "rotary_rows_frob_share": float(np.mean(rot_rows)), "isotropic": ROT / DH}
    r1["REPLICATES"] = bool(r1["K_rotary_mass"] >= r1["within_head_rotation_null"] + 0.10 and r1["rotary_rows_frob_share"] <= 0.27)
    r2 = {M: {"observed": float(np.mean([o for o, _ in v])), "input_rotation_null": float(np.mean([n for _, n in v]))} for M, v in th.items()}
    r2["REPLICATES"] = bool(all(r2[M]["observed"] < r2[M]["input_rotation_null"] for M in ("Q", "K")))
    return r1, r2


def r3():
    d = ROOT / "cache" / f"s3_motion_eq{SUF}"
    a, b = np.load(d / "step1000__step2000.npz"), np.load(d / "step15000__step16000.npz")
    out = {}
    for M in ("Q", "K", "V", "O", "MLP_IN", "MLP_OUT"):
        x = np.mean([float(a[f"L{L:02d}_{M}_dW_stable_rank"]) for L in range(NL)])
        y = np.mean([float(b[f"L{L:02d}_{M}_dW_stable_rank"]) for L in range(NL)])
        out[M] = {"sr_1k_2k": x, "sr_15k_16k": y, "ratio": y / x}
    out["REPLICATES"] = bool(all(out[M]["ratio"] >= 3 for M in ("Q", "K", "V", "O", "MLP_IN", "MLP_OUT")))
    return out


def r4(df):
    ov, qk = [], []
    for _ in range(20):
        V = torch.randn((200, DH, D), generator=gen, device=DEV, dtype=torch.float64)
        O = torch.randn((200, D, DH), generator=gen, device=DEV, dtype=torch.float64)
        ev = torch.linalg.eigvals(V @ O); ov.append((ev.real.sum(-1) / ev.abs().sum(-1)).cpu().numpy())
        Q = torch.randn((200, DH - ROT, D), generator=gen, device=DEV, dtype=torch.float64)
        K = torch.randn((200, DH - ROT, D), generator=gen, device=DEV, dtype=torch.float64)
        AA, BB, BA = Q @ Q.transpose(1, 2), K @ K.transpose(1, 2), K @ Q.transpose(1, 2)
        f2 = torch.einsum("bij,bji->b", AA, BB); tr = torch.einsum("bij,bji->b", BA, BA)
        qk.append(((f2 + tr) / (2 * f2)).cpu().numpy())
    ov, qk = np.concatenate(ov), np.concatenate(qk)
    band = {"ov": (np.quantile(ov, .01), np.quantile(ov, .99)), "qk": (np.quantile(qk, .01), np.quantile(qk, .99))}
    out = {"null_band_ov": [float(x) for x in band["ov"]], "null_band_qk": [float(x) for x in band["qk"]], "by_step": {}}
    for s in (0, 256, 512, 1000, 2000):
        o = df[(df.step == s) & (df.metric == "ov_score")].value
        q = df[(df.step == s) & (df.metric == "qk_sym_nr")].value
        out["by_step"][s] = {"ov_frac_out": float(((o < band["ov"][0]) | (o > band["ov"][1])).mean()),
                             "qk_frac_out": float(((q < band["qk"][0]) | (q > band["qk"][1])).mean())}
    b = out["by_step"][512]
    out["REPLICATES"] = bool(b["ov_frac_out"] >= 0.5 and b["qk_frac_out"] <= 0.2)
    return out


def r5(df):
    ind = df[(df.matrix == "MODEL") & (df.metric == "induction_max")].set_index("step").value.sort_index()
    first = int(ind[ind >= 0.3].index.min())
    prev = int(ind[ind.index < first].index.max())
    return {"interval": [prev, first], "max_induction_by_step": {int(k): float(v) for k, v in ind.items() if k <= 4000},
            "REPLICATES": first in (1000, 2000)}


def r6():
    wit = json.loads((ROOT / "results" / f"stage3_witness{SUF}.json").read_text())
    def mp_cdf(c):
        a, b = (1 - np.sqrt(c)) ** 2, (1 + np.sqrt(c)) ** 2
        g = np.linspace(a, b, 40001); f = np.sqrt(np.clip((b - g) * (g - a), 0, None)) / (2 * np.pi * c * g + 1e-300)
        F = np.concatenate([[0], np.cumsum((f[1:] + f[:-1]) / 2 * np.diff(g))]); return g, F / F[-1]
    out = {}
    for M in ("Q", "K"):
        g, F = mp_cdf(1.0); med_x = float(np.interp(0.5, F, g))
        fr = {}
        for s in (0, 256, 512, 1000, 2000):
            ks = []
            for l in range(NL):
                sig = np.load(ROOT / "cache" / "s3" / MODEL / f"step{s}" / f"L{l:02d}.npz")[f"sig_{M}"]
                sc = np.median(sig) / np.sqrt(D * med_x)
                x = np.sort(sig ** 2 / (D * sc * sc)); Fx = np.interp(x, g, F); i = np.arange(1, len(x) + 1)
                ks.append(max((i / len(x) - Fx).max(), (Fx - (i - 1) / len(x)).max()))
            fr[s] = float((np.array(ks) > wit["types"][M]["ks95"]).mean())
        out[M] = fr
    out["REPLICATES"] = bool(all(out[M][2000] >= 0.9 for M in ("Q", "K")))
    return out


def main():
    df = pd.read_parquet(ROOT / "results" / f"stage3_long{SUF}.parquet")
    r1, r2 = r1_r2()
    res = {"R1_K_rotary": r1, "R2_cross_head_sharing": r2, "R3_update_rank_rise": r3(), "R4_OV_before_QK": r4(df),
           "R5_induction": r5(df), "R6_MP_fit_collapse": r6()}
    fp = ROOT / "results" / "stage3_repl.json"
    allr = json.loads(fp.read_text()) if fp.exists() else {}
    allr[MODEL] = res
    R.durable_save(fp, lambda p: p.write_text(json.dumps(allr, indent=1, default=float)))
    print(MODEL, {k: v["REPLICATES"] for k, v in res.items()})
    print(json.dumps(res, indent=1, default=float)[:3000])


if __name__ == "__main__":
    try:
        main()
    except R.Stopped as e:
        print("STOPPED:", e); sys.exit(3)
