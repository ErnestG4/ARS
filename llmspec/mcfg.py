"""Model configuration for the Stage 3 pipeline (G3 replication refactor, 2026-09-26).

The active model is LLMSPEC_MODEL (default "pythia-1.4b", so every existing 1.4B cache path and result filename is
unchanged). Output files of any other model carry SUFFIX = "_<model>". Shapes come from the models' HF config.json
(checked 2026-09-26); rotary dims = rotary_pct (0.25) x d_head. All three share the GPT-NeoX code path, the
tokenizer (vocab 50304), Adam lr schedule family and the 154-revision checkpoint grid.
"""
import os

MODELS = {
    "pythia-1.4b": dict(repo="EleutherAI/pythia-1.4b", n_layer=24, H=16, DH=128, D=2048, FF=8192,
                        sched="pythia_1.4b_schedule.txt"),
    "pythia-1b": dict(repo="EleutherAI/pythia-1b", n_layer=16, H=8, DH=256, D=2048, FF=8192,
                      sched="pythia_1.4b_schedule.txt"),
    "pythia-410m": dict(repo="EleutherAI/pythia-410m", n_layer=24, H=16, DH=64, D=1024, FF=4096,
                        sched="pythia_1.4b_schedule.txt"),
}
for _k in range(1, 10):   # PolyPythias seed leg: same architecture/config as 410M; weights only as pytorch_model.bin
    MODELS[f"pythia-410m-seed{_k}"] = dict(repo=f"EleutherAI/pythia-410m-seed{_k}", n_layer=24, H=16, DH=64, D=1024,
                                           FF=4096, sched="pythia_1.4b_schedule.txt", fmt="bin")
LR_PEAK = {"pythia-1.4b": 2.0e-4, "pythia-1b": 2.5e-4, "pythia-410m": 3.0e-4}   # EleutherAI/pythia models/*.yml
for _k, _m in MODELS.items():
    _m["lr_peak"] = LR_PEAK.get(_k, 3.0e-4 if _k.startswith("pythia-410m") else None)
    _m["lr_min"] = _m["lr_peak"] / 10 if _m["lr_peak"] else None      # cosine decay to 10% of peak (all sizes)
    _m["warmup"] = 1430                                               # 0.01 x 143000 (all sizes)
for _m in MODELS.values():
    _m["ROT"] = _m["DH"] // 4
    _m.setdefault("fmt", "safetensors")


def name():
    return os.environ.get("LLMSPEC_MODEL", "pythia-1.4b")


def get(model=None):
    return MODELS[model or name()]


def suffix(model=None):
    m = model or name()
    return "" if m == "pythia-1.4b" else f"_{m}"


def full_shapes(model=None):
    c = get(model)
    D, FF = c["D"], c["FF"]
    return {"Q": (D, D), "K": (D, D), "V": (D, D), "O": (D, D), "MLP_IN": (FF, D), "MLP_OUT": (D, FF)}


def witness_suffix(model=None):
    """Seed-leg witness selection (STAGE3_SEED_PREREG.md, declared reuse + scale check): a model's OWN witness file if it
    exists (seeds that fail the +-20% scale check get one), else the declared reuse LLMSPEC_WITNESS, else its own suffix."""
    import os
    from pathlib import Path
    m = model or name()
    own = Path(__file__).resolve().parent / "results" / f"stage3_witness{suffix(m)}.json"
    if own.exists():
        return suffix(m)
    w = os.environ.get("LLMSPEC_WITNESS")
    return suffix(w) if w else suffix(m)
