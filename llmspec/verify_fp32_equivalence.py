"""stage3_extract.build_model (fp16 storage + transient per-module fp32 upcast) must reproduce a plain fp32
model: logits and attention maps on the fixed probes, max |diff| <= 1e-5 (exit 1 otherwise).
Checked on pythia-160m (same GPT-NeoX code path, small enough to hold both models under the GPU cap).
--redpath: perturb one fp16 weight in the hooked model by one ulp; the check must then FAIL (exit 0 iff it does)."""
import sys, copy
import numpy as np, torch
import stage3_extract as X
from transformers import AutoConfig, GPTNeoXForCausalLM

REV = "step143000"
ck = X.Ckpt("pythia-160m", REV)
ck.fetch_all()
A = X.build_model(ck)
cfg = AutoConfig.from_pretrained(ck.repo, revision=REV); cfg._attn_implementation = "eager"
B = GPTNeoXForCausalLM(cfg).to(X.DEV).float().eval()
missing, unexpected = B.load_state_dict({k: v.float() for k, v in ck.gpu.items()}, strict=False)
assert not missing, missing[:5]
if "--redpath" in sys.argv:
    w = A.gpt_neox.layers[3].attention.dense.weight
    w.data[0, 0] = torch.nextafter(w.data[0, 0].float(), torch.tensor(1e9, device=X.DEV)).half() + w.data[0, 0] * 0.01
probes = np.load("results/probes.npz")
worst = 0.0
with torch.no_grad():
    for ids in (torch.as_tensor(probes["text"][:2], device=X.DEV), torch.as_tensor(probes["rep"][:2], device=X.DEV)):
        oa, ob = A(ids, output_attentions=True), B(ids, output_attentions=True)
        worst = max(worst, float((oa.logits - ob.logits).abs().max()))
        worst = max(worst, max(float((a - b).abs().max()) for a, b in zip(oa.attentions, ob.attentions)))
        assert oa.logits.dtype == torch.float32
ok = worst <= 1e-5
print(f"hooked-fp16-storage vs plain fp32: max |diff| = {worst:.3e} ({'EQUIVALENT' if ok else 'DIFFERENT'})"
      + (" [REDPATH]" if "--redpath" in sys.argv else ""))
sys.exit((0 if not ok else 1) if "--redpath" in sys.argv else (0 if ok else 1))
