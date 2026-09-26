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
for _m in MODELS.values():
    _m["ROT"] = _m["DH"] // 4


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
