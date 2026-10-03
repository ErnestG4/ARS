"""Tokenisation audit (brief §3), run BEFORE sealing: how the GPT-NeoX/Pythia tokenizer splits every item inside every
template; multi-token items flagged; item-final token shared across items flagged. Writes results/divisor/tokenisation_audit.json."""
import json, sys, glob, pathlib, collections
from transformers import AutoTokenizer
sys.path.insert(0, str(pathlib.Path(__file__).parent))
import templates as T
snap = glob.glob("/home/combust/.cache/huggingface/hub/models--EleutherAI--pythia-70m/snapshots/*/tokenizer.json")[0].rsplit("/", 1)[0]
tok = AutoTokenizer.from_pretrained(snap)
out = {"tokenizer": snap, "concepts": {}}
for name, (items, tps, N, bc, role) in T.CONCEPTS.items():
    rows = []
    for it in items:
        ntoks = set(); last = set(); pieces = None
        for t in tps:
            pre = t[:-2].rstrip()                      # template without the item slot
            a = tok.encode(pre); b = tok.encode(t.format(it))
            assert b[:len(a)] == a, (name, it, t)      # item tokens are exactly the suffix
            item_ids = b[len(a):]
            ntoks.add(len(item_ids)); last.add(item_ids[-1]); pieces = [tok.decode([i]) for i in item_ids]
        rows.append({"item": it, "n_tokens": sorted(ntoks), "pieces": pieces, "last_token_id": sorted(last)})
    multi = [r["item"] for r in rows if max(r["n_tokens"]) > 1]
    lastc = collections.Counter(r["last_token_id"][0] for r in rows)
    shared_last = {tok.decode([k]): v for k, v in lastc.items() if v > 1}
    out["concepts"][name] = {"N": N, "boundary": bc, "role": role, "items": rows, "multi_token_items": multi,
                             "n_multi": len(multi), "shared_last_token": shared_last,
                             "prefix_stable_across_templates": all(len(r["n_tokens"]) == 1 for r in rows)}
    print(f"{name:9s} N={N:3d} multi-token items: {len(multi):3d}  shared item-final tokens: {shared_last}")
pathlib.Path("results/divisor").mkdir(parents=True, exist_ok=True)
json.dump(out, open("results/divisor/tokenisation_audit.json", "w"), indent=1)
# alternative hour renderings, descriptive, to inform the sealed choice
for form in ["{}:00", "{:02d}:00", "{}h", "{} o'clock", "{}00 hours"]:
    ex = [form.format(h) for h in (0, 9, 14, 23)]
    print("hour form", repr(form), [[tok.decode([i]) for i in tok.encode(" " + e)] for e in ex])
