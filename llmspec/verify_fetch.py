"""remote_st.fetch_many must be byte-identical to remote_st.fetch (the path every banked result used).
Checks 12 tensors of pythia-1.4b step12000 (two layers + embed_out). Exit 1 on any mismatch.
--redpath: compare fetch_many(step12000) against fetch(step8000); it must MISMATCH (exit 0 iff it does)."""
import sys, time
import numpy as np
import remote_st as R
idx = R.index("EleutherAI/pythia-1.4b", "step12000")
ref_idx = R.index("EleutherAI/pythia-1.4b", "step8000") if "--redpath" in sys.argv else idx
names = [k for k in idx if (".layers.5." in k or ".layers.17." in k) and k.endswith("weight")] + ["embed_out.weight"]
t = time.time(); got = {n: a for n, a, _ in R.fetch_many(idx, names)}; dt = time.time() - t
bad = [n for n in names if not np.array_equal(got[n], R.fetch(ref_idx, n)[0])]
mb = sum(a.nbytes for a in got.values()) / 1e6
print(f"fetch_many {len(names)} tensors {mb:.0f} MB at {mb/dt:.0f} MB/s; mismatches: {len(bad)}" + (" [REDPATH]" if ref_idx is not idx else ""))
sys.exit((0 if bad else 1) if "--redpath" in sys.argv else (1 if bad else 0))
