"""Is OLMo-2-0425-1B `main` the same training run as the released checkpoint lineage?

Three checks (Will, 2026-10-01), all read-only, streamed by HTTP range:
  1. Correlate tensors a rotary row layout cannot touch (norms, embeddings, MLP, O) between main, the stage-2
     ingredient-3 final, stage-1 end and ingredient 1.
  2. Apply both standard rotary row permutations (interleaved <-> half-split, within each head) to main's Q/K/V and
     correlate again.
  3. (HF history; done by API, recorded in the JSON notes.)
Reading rule, declared before running: layout difference = norms/embeddings/MLP correlate highly and only Q/K are ~0;
different run = everything ~0. Lineage self-consistency (ing3 ~ s1end, ing1 ~ ing3) is the positive control.
Output: results/olmo_main_provenance.json
"""
import json, sys, numpy as np
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
import remote_st as R
from huggingface_hub import hf_hub_url
REPO = "allenai/OLMo-2-0425-1B"
REVS = {"main": "main", "ing3": "stage2-ingredient3-step23852-tokens51B",
        "s1end": "stage1-step1907359-tokens4001B", "ing1": "stage2-ingredient1-step23852-tokens51B"}
idx = {k: R.index(REPO, v) for k, v in REVS.items()}

def get(rev, name):
    a, _ = R.fetch(idx[rev], name); return np.asarray(a, dtype=np.float64)

def rows(rev, name, n):
    h = idx[rev][name]; t = h["tensors"][name]; a, b = t["data_offsets"]; shp = t["shape"]
    nb = {"F32": 4, "BF16": 2, "F16": 2}[t["dtype"]]; width = shp[1] * nb
    raw = R._get_parallel(hf_hub_url(h["repo"], h["fn"], revision=h["rev"]), h["data_start"] + a, h["data_start"] + a + n * width - 1)
    return np.frombuffer(raw, dtype=R.DT[t["dtype"]]).reshape(n, shp[1]).astype(np.float64)

c = lambda x, y: float(np.corrcoef(x.ravel(), y.ravel())[0, 1])
PAIRS = [("main", "ing3"), ("main", "s1end"), ("ing3", "s1end"), ("ing1", "ing3")]
out = {"repo": REPO, "revisions": REVS, "layout_invariant": {}, "rotary_permuted": {}, "notes": [
    "HF history: every checkpoint branch was created from the single 2025-04-17 upload (commit fc6f5279) and had its "
    "safetensors re-uploaded 2025-04-26..28; main was never re-uploaded (its LFS oids equal fc6f5279's).",
    "config.json is identical across main, ing3 and s1end.",
    "Model card (2025-04-28+): '1B Model: only 1 version is trained on a 50B mix (ingredient 3), we did not merge.'"]}
INV = ["model.norm.weight", "model.layers.0.post_attention_layernorm.weight", "model.layers.7.post_feedforward_layernorm.weight",
       "model.layers.0.self_attn.q_norm.weight", "model.layers.0.mlp.down_proj.weight", "model.layers.7.mlp.gate_proj.weight",
       "model.layers.0.self_attn.o_proj.weight"]
for name in INV:
    T = {r: get(r, name) for r in REVS}
    out["layout_invariant"][name] = {"corr": {f"{a}~{b}": c(T[a], T[b]) for a, b in PAIRS},
                                     "rms": {r: float(T[r].std()) for r in T}, "mean": {r: float(T[r].mean()) for r in T}}
E = {r: rows(r, "model.embed_tokens.weight", 3000) for r in ["main", "ing3", "s1end"]}
out["layout_invariant"]["model.embed_tokens.weight[:3000]"] = {
    "corr": {f"{a}~{b}": c(E[a], E[b]) for a, b in PAIRS[:3]}, "rms": {r: float(E[r].std()) for r in E}}

def half_to_inter(w, nh=16, dh=128): return w.reshape(nh, dh // 2, 2, -1).transpose(0, 2, 1, 3).reshape(w.shape)
def inter_to_half(w, nh=16, dh=128): return w.reshape(nh, 2, dh // 2, -1).transpose(0, 2, 1, 3).reshape(w.shape)
for name in ["model.layers.0.self_attn.q_proj.weight", "model.layers.0.self_attn.k_proj.weight", "model.layers.0.self_attn.v_proj.weight"]:
    T = {r: get(r, name) for r in ["main", "ing3", "s1end"]}; m = T["main"]
    sv = lambda w: [float(np.linalg.svd(w[h * 128:(h + 1) * 128], compute_uv=False)[0]) for h in range(16)]
    out["rotary_permuted"][name] = {
        "corr_raw": {"main~ing3": c(m, T["ing3"]), "main~s1end": c(m, T["s1end"]), "ing3~s1end": c(T["ing3"], T["s1end"])},
        "corr_main_half_to_inter~ing3": c(half_to_inter(m), T["ing3"]), "corr_main_inter_to_half~ing3": c(inter_to_half(m), T["ing3"]),
        "rms": {r: float(T[r].std()) for r in T}, "per_head_top_sv": {"main": sv(m), "ing3": sv(T["ing3"])}}
inv_max = max(abs(v["corr"]["main~ing3"]) for v in out["layout_invariant"].values())
lin_min = min(v["corr"]["ing3~s1end"] for v in out["layout_invariant"].values())
out["verdict"] = ("DIFFERENT_RUN" if inv_max < 0.1 and lin_min > 0.9 else "LAYOUT_DIFFERENCE" if lin_min > 0.9 else "UNDETERMINED")
out["verdict_basis"] = {"max |corr main~ing3| over layout-invariant tensors": inv_max, "min corr ing3~s1end": lin_min}
Path("results/olmo_main_provenance.json").write_text(json.dumps(out, indent=1))
print(out["verdict"], out["verdict_basis"])
