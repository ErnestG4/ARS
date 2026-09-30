"""Dry run of seed1_identity.decide on constructed rho tables: every verdict branch fires once (sealed-contingency
discipline), including the red path (a confuser that looks right blocks CONFIRMED). Synthetic only; no training."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import seed1_identity as S  # noqa: E402

T4 = S.CHECK


def tab(K, Km, T, C1, C2):
    return {"K": dict(zip(T4, K)), "Km": dict(zip(T4, Km)), "T": dict(zip(T4, T)), "C1": dict(zip(T4, C1)), "C2": dict(zip(T4, C2))}


hi, lo = [0.95] * 4, [0.40] * 4
cases = [
    ("CONFIRMED", tab(hi, lo, [0.93] * 4, [0.45] * 4, [0.50] * 4)),
    ("REFUTED", tab(hi, lo, [0.42] * 4, [0.94] * 4, [0.45] * 4)),                        # C1 right-like: standard order
    ("INCONCLUSIVE", tab(hi, lo, [0.93] * 4, [0.90] * 4, [0.45] * 4)),                   # red path: C1 also right-like
    ("INCONCLUSIVE", tab(hi, lo, [0.93, 0.93, 0.5, 0.5], [0.45] * 4, [0.45] * 4)),       # T mixed
    ("INCONCLUSIVE (instrument", tab([0.5] * 4, [0.6] * 4, [0.93] * 4, [0.45] * 4, [0.45] * 4)),  # K does not beat Km
]
bad = 0
for want, rho in cases:
    got = S.decide(rho)["VERDICT"]
    ok = got.startswith(want); bad += not ok
    print(("PASS" if ok else "FAIL"), want, "->", got)
sys.exit(1 if bad else 0)
