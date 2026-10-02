"""Compare the two M4 A/B runs (same resume.pt, 100 steps, hook off vs on): per-tensor equality of the final weights,
loss-curve equality, hook rows written, peak GPU memory sampled during the ON run. Writes results/armb_m4_ab.json."""
import json, sys, torch
from pathlib import Path
HERE = Path(__file__).resolve().parent; RES = HERE.parent / "results"
off, on = torch.load(HERE / "staging/_m4ab/ab_off.pt", map_location="cpu", weights_only=False), torch.load(HERE / "staging/_m4ab/ab_on.pt", map_location="cpu", weights_only=False)
mo, mn = off["model"], on["model"]
neq = [k for k in mo if not torch.equal(mo[k], mn[k])]
maxrel = max((float((mo[k].float() - mn[k].float()).abs().max() / (mo[k].float().abs().max() + 1e-30)) for k in neq), default=0.0)
lo = [json.loads(l) for l in open(HERE / "staging/_m4ab/trainlog_off.jsonl")]
ln = [json.loads(l) for l in open(HERE / "staging/_m4ab/trainlog_on.jsonl")]
loss_eq = [a["step"] for a, b in zip(lo, ln) if a["loss"] != b["loss"]]
gram = HERE / "staging/_m4ab/m4_gram.jsonl"
rows = sum(1 for _ in open(gram)) if gram.exists() else 0
mem = [int(x) for x in open(HERE / "staging/_m4ab/gpu_mem_on.txt").read().split()] if (HERE / "staging/_m4ab/gpu_mem_on.txt").exists() else []
out = {"step_start": off["step"] - len(lo), "steps": len(lo), "tensors": len(mo), "tensors_unequal": len(neq), "max_rel_diff": maxrel,
       "loss_unequal_steps": loss_eq, "m4_rows": rows, "peak_gpu_mem_on_MiB": max(mem) if mem else None,
       "hook_disabled": any("M4 hook DISABLED" in l for l in open(HERE / "train_A0_test.log")) if (HERE / "train_A0_test.log").exists() else None}
out["VERDICT"] = ("PASS: weights bit-identical, losses identical" if not neq and not loss_eq else
                  f"DIFF: {len(neq)} tensors differ (max rel {maxrel:.2e}); losses differ at {len(loss_eq)} steps")
RES.mkdir(exist_ok=True); (RES / "armb_m4_ab.json").write_text(json.dumps(out, indent=1)); print(json.dumps(out, indent=1))
