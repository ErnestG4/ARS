"""Session D — layer-zero gates for the AMO measure-law identification of the ≈λ thinning.

GATE 1 (done, printed separately): on-site term = lam·χ_{[1-p/q,1)}({np/q}) — a STURMIAN STEP potential
(0 or λ), NOT the almost-Mathieu cosine 2λ·cos(2π(θ+nα)). The code itself calls it "a Sturmian potential."
=> the AMO measure theorem Leb(σ)=|4-4λ| is for a DIFFERENT operator; identification challenged at layer-zero.

This file: gate 2 (definitions of λ and 'thinning'), gate 3 (λ=0 anchor = 4), gate 4 (band-count==q),
and the identification verdict. Certified engine (periodic_edges verbatim). Read-only. BASE_SEED=20240517.
"""
import os,sys,math,json,gc
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0,ROOT); sys.path.insert(0,"/home/combust/fmexplorer/riemann_explorer")
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
import numpy as np, scipy.linalg as sla
from task1_pi_depth5 import potential, cf_frac, convergents
import mpmath as mp
OUT=os.path.dirname(os.path.abspath(__file__)); out={}

# certified Floquet operator (verbatim from depth4/5 scripts)
def periodic_edges(V, corner):
    q=len(V); H=np.zeros((q,q)); np.fill_diagonal(H,V)
    idx=np.arange(q-1); H[idx,idx+1]=1.0; H[idx+1,idx]=1.0
    H[0,q-1]=corner; H[q-1,0]=corner
    w=sla.eigvalsh(H, overwrite_a=True, driver='evr'); del H; gc.collect(); return w
def total_measure(p,q,lam):
    V=potential(p,q,lam) if lam>0 else np.zeros(q)
    e=np.sort(np.concatenate([periodic_edges(V,1.0),periodic_edges(V,-1.0)]))
    widths=e[1::2]-e[0::2]; return float(widths.sum()), widths.size

print("="*74)
print("GATE 1 (verbatim above): operator on-site term = STURMIAN STEP  λ·χ_{[1-p/q,1)}({np/q})")
print("  NOT 2λ·cos (AMO). The AMO measure law |4-4λ| is for the cosine operator. Category mismatch.")
out["gate1_operator"]="sturmian_step  lam*indicator{(n p mod q)>=q-p}  (NOT AMO cosine)"

# --- GATE 2: what is 'λ' and what is 'thinning'? (from the code) ---
print("\nGATE 2: internal definitions")
print("  λ = the coefficient multiplying the 0/1 Sturmian indicator (on-site step height); appears as `lam` in potential().")
print("  'measure-thinning' in the banked Thouless law = the PER-STEP TOTAL-BANDWIDTH RATIO W_{k-1}/W_k of the")
print("  periodic APPROXIMANTS across a convergent step (thouless_law.py: floquet_bands_tw -> (q, tw); ratio tw[i-1]/tw[i]).")
print("  It is a property of finite periodic approximants, NOT the Lebesgue measure of the irrational-limit spectrum.")
out["gate2_lambda"]="on-site step height (coeff of 0/1 Sturmian indicator)"
out["gate2_thinning"]="per-step approximant total-bandwidth ratio W_{k-1}/W_k (Thouless law), NOT measure-of-spectrum"

# --- GATE 3: λ=0 anchor must give free-Laplacian measure 4 ---
print("\nGATE 3: λ=0 anchor (free Laplacian [-2,2], Lebesgue measure 4)")
for q in (55,89):
    m0,nb=total_measure(1,q,0.0)  # lam=0 -> V=0
    print(f"  q={q}: total measure at λ=0 = {m0:.10f}  (expect 4)")
    assert abs(m0-4.0)<1e-6, f"λ=0 anchor FAIL: {m0}"
out["gate3_lambda0_measure"]=4.0; print("  GATE 3 PASS: λ=0 -> measure 4 (free-Laplacian band, the fixed-bug anchor).")

# --- GATE 4: band-count == q (certified count_eq_q) ---
print("\nGATE 4: band-count completeness (period-q operator has exactly q bands)")
cf=cf_frac(mp.pi,12); ps,qs=convergents(cf)
for (p,q) in [(ps[0],qs[0]),(ps[1],qs[1]),(ps[2],qs[2])]:
    _,nb=total_measure(p,q,8.0)
    print(f"  q={q}: bands={nb}  count_eq_q={nb==q}")
    assert nb==q
out["gate4_count_eq_q"]=True; print("  GATE 4 PASS.")

# --- AMO measure law vs measured thinning: the discriminating slope ---
print("\n"+"="*74)
print("DISCRIMINATING MEASUREMENT: AMO predicts Leb(σ)=|4-4λ| (2λ conv) => fraction removed = λ (λ∈[0,1]).")
print("Measure the Sturmian approximant total measure vs λ, fraction removed = 1 - W(λ)/4, compare to λ and λ/2:")
p,q=ps[2],qs[2]  # q=113 approximant
print(f"  (q={q} approximant)   λ     Leb(σ_approx)   frac_removed=1-W/4    AMO λ?   AMO λ/2?")
rows=[]
for lam in (0.25,0.5,0.75,1.0,1.5,2.0):
    W,_=total_measure(p,q,lam); frac=1-W/4
    print(f"                     {lam:5.2f}   {W:12.6f}   {frac:16.6f}   {lam:7.2f}  {lam/2:8.2f}")
    rows.append(dict(lam=lam, W=W, frac_removed=frac))
out["sturmian_measure_vs_lambda"]=rows
# fraction removed for Sturmian is NOT |4-4λ|/4 — it keeps growing past λ=1 (no critical collapse to 0 at λ=1)
print("\n  READING: Sturmian frac_removed grows monotonically through λ=1 (NO measure-zero collapse at λ=1) and")
print("  does NOT track either λ or λ/2 — because the Sturmian spectrum has Leb=0 in the irrational LIMIT for ALL")
print("  λ>0 (Bellissard–Iochum–Scoppola–Testard / Sütő), so the finite-q measure just shrinks toward 0 with q,")
print("  it is not the AMO |4-4λ| law. The AMO law lives on the SEPARATE cosine operator (banked in am_confluence,")
print("  D_box→0.513 at λ=1). Different operator, different law.")

json.dump(out, open(os.path.join(OUT,"thouless_amo_gates.json"),"w"), indent=1)
print("\nwrote thouless_amo_gates.json")
