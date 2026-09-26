"""The pytorch_model.bin path (CkptBin) must equal the safetensors path (Ckpt) for every parameter, on the one model that
ships both (EleutherAI/pythia-410m, step1000). Compares the fp16 GPU caches bit-for-bit after fetch_all; the key sets
must match exactly. Exit 1 on any difference.
--redpath: compare the .bin of step1000 against the safetensors of step2000; it must differ (exit 0 iff it does)."""
import sys
import torch
import stage3_extract as X
red = "--redpath" in sys.argv
a = X.Ckpt("pythia-410m", "step2000" if red else "step1000"); a.fetch_all()
b = X.CkptBin("pythia-410m", "step1000", repo="EleutherAI/pythia-410m"); b.fetch_all()
ka, kb = set(a.gpu), set(b.gpu)
diff = [k for k in sorted(ka & kb) if not torch.equal(a.gpu[k], b.gpu[k])]
print(f"keys safetensors {len(ka)} bin {len(kb)} only-st {sorted(ka - kb)[:3]} only-bin {sorted(kb - ka)[:3]}; "
      f"tensors differing: {len(diff)}" + (" [REDPATH]" if red else ""))
b.close()
bad = bool(diff or ka != kb)
sys.exit((0 if diff else 1) if red else (1 if bad else 0))
