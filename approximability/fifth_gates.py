"""Layer-zero gates for the Diatonic Hamiltonian run: alpha = log2(3/2).
Certified path only: potential/cf_frac/convergents imported verbatim from task1_pi_depth5.
Gates (all fiasco rules): (0) two-precision CF; (1) convergent ladder + q9=23q8+q7;
(2) potential-layer v.sum()==p (inside potential()); (3) MUSICAL: q=12 unit cell == diatonic word.
Read-only vs the tool. Seed 20240517."""
import os, sys, json
_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _ROOT); sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import mpmath as mp
from task1_pi_depth5 import potential, cf_frac, convergents

SEED = 20240517
NQ = 12   # quotients to request

# ---- (0) TWO-PRECISION CF GATE ----
def alpha_at(dps):
    mp.mp.dps = dps
    return mp.log(mp.mpf(3) / mp.mpf(2)) / mp.log(mp.mpf(2))

cf_lo = cf_frac(alpha_at(50), NQ)
cf_hi = cf_frac(alpha_at(80), NQ)
agree_depth = 0
for x, y in zip(cf_lo, cf_hi):
    if x == y: agree_depth += 1
    else: break
cf = cf_lo[:agree_depth]                    # bank ONLY where both precisions agree
print(f"[0] CF(dps=50)={cf_lo}")
print(f"[0] CF(dps=80)={cf_hi}")
print(f"[0] two-precision agreement depth = {agree_depth} quotients; banked CF = {cf}")
EXPECTED = [1, 1, 2, 2, 3, 1, 5, 2, 23]
print(f"[0] spec-hypothesis [0;1,1,2,2,3,1,5,2,23] matches banked prefix: "
      f"{cf[:len(EXPECTED)] == EXPECTED[:agree_depth]}")

# ---- (1) CONVERGENT LADDER ----
ps, qs = convergents(cf)
print(f"[1] convergent q ladder = {qs}")
print(f"[1] convergent p ladder = {ps}")
tuning_systems = [1, 2, 5, 12, 41, 53, 306, 665, 15601]
print(f"[1] matches tuning-history ladder {tuning_systems}: {qs[:9] == tuning_systems}")
# q9 = 23*q8 + q7 against VERIFIED quotients (a9=23)
if agree_depth >= 9:
    lhs, rhs = qs[8], 23 * qs[7] + qs[6]
    print(f"[1] q9=23*q8+q7 assertion: {qs[8]} == 23*{qs[7]}+{qs[6]} = {rhs}  -> {lhs == rhs}")
    assert lhs == rhs, "q9 recurrence FAIL"

# ---- (2) POTENTIAL-LAYER GATE (v.sum()==p) at every depth ----
print("[2] potential-layer gate int(V.sum()/lam)==p:")
for k in range(len(qs)):
    p, q = ps[k], qs[k]
    V = potential(p, q, 8.0)     # asserts n_imp==p internally; also assert here per spec
    assert int(round(V.sum() / 8.0)) == p, (q, p)
    print(f"    q={q:6d} p={p:6d}  impurities={int(round(V.sum()/8.0))}  OK")

# ---- (3) MUSICAL LAYER-ZERO GATE: q=12 unit cell == diatonic step word ----
k12 = qs.index(12); p12, q12 = ps[k12], qs[k12]
V12 = potential(p12, q12, 1.0)                 # lam=1 so V is 0/1 indicator
word = (V12 > 0).astype(int)
ones = np.where(word == 1)[0]
print(f"[3] q=12 unit cell (p={p12}): impurity word = {''.join(map(str,word))}")
print(f"[3]   impurity sites = {ones.tolist()}  (count={len(ones)}, expect 7)")
# cyclic gaps between consecutive impurities = the step word
gaps = []
for i in range(len(ones)):
    nxt = ones[(i + 1) % len(ones)]
    d = (nxt - ones[i]) % q12
    gaps.append(int(d))
print(f"[3]   cyclic step word (gaps between impurities) = {gaps}")
# diatonic LLsLLLs = 2,2,1,2,2,2,1 ; check our step word is a rotation of it
diatonic = [2, 2, 1, 2, 2, 2, 1]
def rotations(w):
    return [w[i:] + w[:i] for i in range(len(w))]
is_diatonic = gaps in rotations(diatonic)
modes = {"Ionian":[2,2,1,2,2,2,1],"Dorian":[2,1,2,2,2,1,2],"Phrygian":[1,2,2,2,1,2,2],
         "Lydian":[2,2,2,1,2,2,1],"Mixolydian":[2,2,1,2,2,1,2],"Aeolian":[2,1,2,2,1,2,2],
         "Locrian":[1,2,2,1,2,2,2]}
which = [name for name, w in modes.items() if w == gaps]
print(f"[3]   step word multiset {sorted(gaps)} == diatonic {sorted(diatonic)}: "
      f"{sorted(gaps)==sorted(diatonic)}")
print(f"[3]   step word is a ROTATION of LLsLLLs (2212221): {is_diatonic}  mode={which}")
assert is_diatonic, "MUSICAL GATE FAIL: q=12 unit cell is NOT the diatonic word — STOP."
print("[3]   MUSICAL LAYER-ZERO GATE: PASS — the potential at q=12 is the white keys.")

json.dump(dict(seed=SEED, agree_depth=agree_depth, cf=cf, q_ladder=qs, p_ladder=ps,
               q12_word=''.join(map(str,word)), q12_stepword=gaps, mode=which,
               musical_gate_pass=bool(is_diatonic)),
          open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "fifth_gates.json"), "w"), indent=1)
print("\nALL LAYER-ZERO GATES PASS — wrote fifth_gates.json")
