"""G3 refactor regression: the model-general stage3_extract must reproduce banked pythia-1.4b extraction bit-for-bit.
Re-extracts step8000 layer 5 (all six matrices, per-head spectra, circuits) and compares every array with the banked
cache/s3/pythia-1.4b/step8000/L05.npz. Exit 1 on any difference.
--redpath: compare against layer 6 of the same checkpoint instead; it must differ (exit 0 iff it does)."""
import sys
import numpy as np, torch
import stage3_extract as X
X.set_model("pythia-1.4b")
ck = X.Ckpt("pythia-1.4b", "step8000")
gf = ck.t("gpt_neox.final_layer_norm.weight"); WE16, WU16 = ck.get32("gpt_neox.embed_in.weight"), ck.get32("embed_out.weight")
EU = torch.zeros(X.D, X.D, device=X.DEV, dtype=torch.float64)
for i in range(0, WE16.shape[0], 4096):
    EU += WE16[i:i + 4096].double().T @ (WU16[i:i + 4096].double() * gf)
new = X.layer(ck, 5, EU)
ref = np.load(f"cache/s3/pythia-1.4b/step8000/L{6 if '--redpath' in sys.argv else 5:02d}.npz")
diff = [k for k in ref.files if k != "estimator_version" and not np.array_equal(ref[k], new[k])]
print(f"arrays compared: {len(ref.files) - 1}; differing: {len(diff)} {diff[:6]}" + (" [REDPATH]" if "--redpath" in sys.argv else ""))
sys.exit((0 if diff else 1) if "--redpath" in sys.argv else (1 if diff else 0))
