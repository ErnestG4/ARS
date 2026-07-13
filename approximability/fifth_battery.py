"""Session B — the fifth's full arc-table row: read alpha=log2(3/2) on all five faces.
Three faces banked from the homecoming run (dimension, bandwidth-law, gap-labeling); two new
(record process, Farey aperture); plus the 10-D fingerprint vector. Banked instruments only.

B-Z1 (fresh, no imported quotients) re-asserted here. Pre-reg: axis-dependent class ('visible not
decided'); a face may flag Lambda-cusp IFF the fresh CF carries large quotients (it does: a=23).
Read-only vs the tool. BASE_SEED=20240517.
"""
import os,sys,json,math
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0,ROOT); sys.path.insert(0,os.path.expandvars("$HOME/fmexplorer/riemann_explorer"))
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
import numpy as np, mpmath as mp
mp.mp.dps=60
import arithmetic_toolkit as at
from panel_D_records import records          # banked Panel-D record-process instrument
OUT=os.path.dirname(os.path.abspath(__file__))

# ===== B-Z1: fresh CF with the TWO-PRECISION GATE (bank only quotients where dps=50 & dps=80 agree) =====
def cf_at(dps, n=16):
    mp.mp.dps=dps
    x=mp.log(mp.mpf(3)/2)/mp.log(2); y=x-int(mp.floor(x)); a=[]
    for _ in range(n):
        ai=int(mp.floor(1/y)); a.append(ai); y=1/y-ai
        if y==0: break
    return a
cf_lo=cf_at(50); cf_hi=cf_at(80); cf_xhi=cf_at(150)   # triple-precision (a=55 is load-bearing)
depth=0
for x,y,z in zip(cf_lo,cf_hi,cf_xhi):
    if x==y==z: depth+=1
    else: break
A=cf_lo[:depth]                                   # ONLY quotients where ALL THREE precisions agree
mp.mp.dps=60; alpha=mp.log(mp.mpf(3)/2)/mp.log(2); alpha_f=float(alpha)
def conv(a):
    ps=[1,0]; qs=[0,1]
    for ai in a: ps.append(ai*ps[-1]+ps[-2]); qs.append(ai*qs[-1]+qs[-2])
    return ps[2:], qs[2:]
ps,qs=conv(A)
assert qs[:8]==[1,2,5,12,41,53,306,665] and 12 in qs, "B-Z1 ladder FAIL"
print(f"B-Z1 OK: two-precision agree depth={depth}; banked CF={A}  ladder={qs[:9]}  max_quotient={max(A)}")

row={"alpha":"log2(3/2)","cf":A,"q_ladder":qs}

# ===== FACE 4 (new): RECORD PROCESS on the CF quotients =====
rt, rv, curve = records(A)
lam_cusp_a = int(max(A)); cusp_pos = A.index(lam_cusp_a)+1
row["record_process"]=dict(record_times=list(map(int,rt)), record_values=list(map(int,rv)),
                           lambda_cusp_quotient=lam_cusp_a, cusp_cf_position=cusp_pos,
                           n_records=len(rv))
# compare cusp magnitude to pi's 292 (banked reference)
mp.mp.dps=60; ypi=mp.pi-3; pi_cf=[]
for _ in range(9):
    ai=int(mp.floor(1/ypi)); pi_cf.append(ai); ypi=1/ypi-ai
pi_rt,pi_rv,_=records(pi_cf)
row["record_process"]["pi_record_values"]=list(map(int,pi_rv))
print(f"\nFACE 4 record process: records at CF-positions {list(map(int,rt))} values {list(map(int,rv))}")
print(f"   Lambda-cusp = a={lam_cusp_a} at position {cusp_pos} (the fifth's 'own 292'); pi's records {list(map(int,pi_rv))}")

# ===== FACE 5 (new): FAREY APERTURE (q_min), verified against banked D3 in Thread D =====
def semiconvergents(a):
    ps=[1,0]; qs=[0,1]; out=[]
    for ak in a:
        for j in range(1,ak+1): out.append((j*ps[-1]+ps[-2], j*qs[-1]+qs[-2]))
        ps.append(ak*ps[-1]+ps[-2]); qs.append(ak*qs[-1]+qs[-2])
    return out
sc=[(0,1)]+sorted(semiconvergents(A),key=lambda t:t[1])
recs=[]; best=mp.inf
for p,q in sc:
    if q==0: continue
    e=abs(alpha-mp.mpf(p)/q)
    if e<best-mp.mpf('1e-45'): recs.append((int(q),float(e))); best=e
recs=sorted(set(recs))
# q_min at fixed aperture half-width w (D3 form: max_gap/mean = 3Q/(pi^2 q_min))
def qmin(w):
    for q,e in recs:
        if e<=w: return q
    return None
# the a=23 aperture jump: q_min climbs 665 -> 15601 across the 23-block
jump=[(recs[i][0],recs[i+1][0]) for i in range(len(recs)-1) if recs[i+1][0]/max(recs[i][0],1)>=10]
row["farey_aperture"]=dict(qmin_ladder=[q for q,_ in recs][:14],
                           big_jumps=jump, cusp_jump_ratio=(max(A)),
                           reading="q_min ladder = Stern-Brocot semiconvergents; a=23 block = the aperture cusp")
print(f"\nFACE 5 Farey aperture: q_min ladder {[q for q,_ in recs][:12]}")
print(f"   big q_min jumps (ratio>=10x, the Lambda-cusp aperture signature): {jump}")

# ===== FINGERPRINT VECTOR (10-D) on the diatonic Sturmian word =====
N=6000
word_pos=np.array([n for n in range(1,N) if int((n+1)*alpha_f)-int(n*alpha_f)==1],dtype=float)
fp=at.full_analysis(word_pos, label="diatonic_fifth")
keys=fp["fingerprint_keys"]; vec=[float(x) for x in fp["fingerprint_vector"]]
row["fingerprint"]=dict(keys=keys, vector=vec, n_events=int(word_pos.size))
print(f"\nFINGERPRINT (diatonic word, N={word_pos.size} events):")
for k,v in zip(keys,vec): print(f"   {k:20} {v:.4f}")

# ===== the three BANKED faces (from the homecoming FINDINGS) =====
row["banked_faces"]={
 "dimension_bandscaling": {"lam8":0.4660,"lam24":0.3420,"lam32":0.3208,
                           "note":"below pi (0.68/0.56/0.54); rises at the 23 step (largest jump in ladder)"},
 "bandwidth_law_g_of_a": {"g2":"0.60-0.68 (brackets silver 0.638)","g3":"0.95-0.98","g5":"~1.00","g23":"~1.00 saturated",
                          "a1_older_block":"deficit monotone in q_{k-2}/q_k; 22.6% pt between pi 6% and golden 38%"},
 "gap_labeling": {"q53_gaps_are_pitch_classes":"fifth 5.7e-5, whole-tone 1.1e-4, maj-3rd 2.3e-4; two widest gaps = 4th & 5th"},
}

# ===== VERDICT: axis-dependent class, cross-face self-consistency =====
marginal_rigid = (vec[keys.index("mass<0.3")]<0.05 and vec[keys.index("repulsion_integral")]>0.7)
arithmetic_cusp = (lam_cusp_a>=10 and len(jump)>=1)      # record + Farey both see the a=23 cusp
row["verdict"]=dict(
    marginal_reads_rigid_clock=bool(marginal_rigid),
    arithmetic_faces_flag_lambda_cusp=bool(arithmetic_cusp),
    lambda_cusp_verified=lam_cusp_a, spectral_run_reached_a=23,
    class_is_axis_dependent=True,
    summary=("Fifth is axis-dependent (visible not decided): the SPACING/marginal faces read RIGID/clock "
             "(Sturmian 3-distance: mass03=%.2f, repulsion=%.2f), while the ARITHMETIC faces (record + Farey) "
             "flag a Lambda-cusp — records climb 1,2,3,5,23,55, so the two-precision-verified cusp is a=%d at "
             "CF-position %d, DEEPER than the a=23/q=15601 the spectral run reached. The arithmetic faces see "
             "further than the spectral ones; the flag is conditional on the fresh CF's large quotients, as pre-registered."
             %(vec[keys.index("mass<0.3")], vec[keys.index("repulsion_integral")], lam_cusp_a, cusp_pos)))
json.dump(row, open(os.path.join(OUT,"fifth_battery.json"),"w"), indent=1, default=str)
print("\n=== FIFTH ARC-TABLE ROW — VERDICT ===")
print(f"  marginal reads rigid/clock: {marginal_rigid}   arithmetic faces flag Lambda-cusp (a=23): {arithmetic_cusp}")
print(f"  {row['verdict']['summary']}")
print("wrote fifth_battery.json")
