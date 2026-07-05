"""Post-run analysis for the Diatonic Hamiltonian (alpha=log2(3/2)):
fifth-vs-pi comparison, per-step bandwidth law (P2), a=1 law (P3), K-coupling (P1),
Bellissard gap-labeling (q=12,q=53), and the depth-ladder spectrum figure.
Reads fifth_ladder.json + fifth_edges_*.npy. Read-only vs the tool."""
import os, sys, math, json
OUT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, OUT)
import numpy as np
import mpmath as mp
mp.mp.dps = 80

L = json.load(open(os.path.join(OUT, "fifth_ladder.json")))
cf = L["cf"]; ladder = L["ladder"]
alpha = float(mp.log(mp.mpf(3)/2)/mp.log(2))
res = L["results"]

# --- EXACT q=2 override: Floquet is degenerate at q=2 (wrap-bond collides with the sole
# nn-bond -> periodic==antiperiodic -> zero-width bands). Period-2 discriminant is closed
# form: tr = E^2 - lam E - 2, bands |.|<=2  =>  W2 = sqrt(lam^2+16) - lam (verified vs
# disc_direct grid to 1e-4). This is the certified direct-discriminant path, not new physics.
def q2_exact(lam):
    W = math.sqrt(lam*lam + 16.0) - lam
    lo1 = (lam - math.sqrt(lam*lam+16.0))/2.0
    bands = [(lo1, 0.0), (lam, (lam + math.sqrt(lam*lam+16.0))/2.0)]
    return W, bands
for lamv in (8.0, 24.0, 32.0):
    key=f"lam{lamv}"
    if key in res and str(2) in res[key]:
        W2,_ = q2_exact(lamv)
        res[key][str(2)]["total_width"] = W2
        res[key][str(2)]["_q2_exact_override"] = True

# ---- banked pi Floquet reference (band-scaling dim), certified ----
PI = {  # lam: {depth_label: (q, dim, total_width)}
 8.0:  {"d1":(7,0.7331,0.49244),"d2":(106,0.6244,0.060508),"d3":(113,0.6276,0.060508),
        "d4":(33102,0.6798,0.007434960),"d5":(33215,0.6799,0.007434960)},
 24.0: {"d1":(7,0.5204,0.16638),"d2":(106,0.4839,0.0069189),"d3":(113,0.4873,0.0069189),
        "d4":(33102,0.5607,0.0002877284),"d5":(33215,None,None)},
 32.0: {"d1":(7,0.4833,0.12488),"d2":(106,0.4567,0.0038982),"d3":(113,0.4601,0.0038982),
        "d4":(33102,0.5359,0.00012168),"d5":(33215,None,None)},
}
# banked metallic g(a) (lam=8), Thread-1
G_BANKED = {1:0.313, 2:0.638, 3:0.918}   # golden/silver/bronze; g->1 saturated large a
# banked pi a3=1 deficits (1 - W3/W2), lam 8/24/32
PI_A1_DEFICIT = {8.0:1.271e-12, 24.0:1.066e-18, 32.0:2.588e-20}

def kalpha_nearest(ids, kmax=60):
    best=None
    for k in range(0,kmax+1):
        v=(k*alpha)%1.0
        d=min(abs(v-ids),abs(v-ids+1),abs(v-ids-1))
        if best is None or d<best[2]: best=(k,v,d)
    return best

print("="*90)
print("DIATONIC HAMILTONIAN  alpha=log2(3/2)  cf=",cf)
print("K running:", {q:round(float(v),4) for q,v in L["K_running"].items()})
print("="*90)

# ============ P1: dimension trajectory & fifth-vs-pi ============
print("\n### DIM TRAJECTORY (band-scaling, certified Floquet readout) ###")
report={}
for lam in ("lam8.0","lam24.0","lam32.0"):
    d=res[lam]; lamv=float(lam[3:])
    print(f"\n-- {lam} --")
    print(f"{'q':>7} {'a':>4} {'K':>7} {'dim_bs':>8} {'dim_box':>8} {'agree':>7} {'totW':>13} {'W/Wp':>9}")
    for q in ladder:
        r=d[str(q)]
        print(f"{q:>7} {str(r['step_quotient']):>4} {r['K_running']:>7.3f} {r['dim_bandscaling']:>8.4f} "
              f"{(r['dim_boxcount'] if r['dim_boxcount']==r['dim_boxcount'] else float('nan')):>8.4f} "
              f"{str(r['agree_le_0p02']):>7} {r['total_width']:>13.6e} "
              f"{(('%.4f'%r['width_ratio_vs_prev']) if r['width_ratio_vs_prev'] else '   -'):>9}")

# fifth-vs-pi at matched lam, deepest available
print("\n### FIFTH vs PI  (deepest diatonic q=15601 [K=%.2f] vs pi d4/d5) band-scaling dim ###"%float(L['K_running']['15601']))
for lamv in (8.0,24.0,32.0):
    dq=res[f"lam{lamv}"][str(15601)]
    pid4=PI[lamv]["d4"];
    print(f"  lam={lamv:>4}: diatonic(q15601,K=2.41) dim={dq['dim_bandscaling']:.4f}   "
          f"pi(q33102,K=4.21) dim={pid4[1]}   diatonic {'BELOW' if dq['dim_bandscaling']<pid4[1] else 'ABOVE'} pi")

# ============ P2/P3: per-step bandwidth law ============
print("\n### PER-STEP BANDWIDTH LAW (P2 a>=2, P3 a=1) ###")
qs=ladder
step_tables={}
for lamv in (8.0,24.0,32.0):
    d=res[f"lam{lamv}"]
    rows=[]
    for i in range(1,len(qs)):
        q=qs[i]; qp=qs[i-1]; a=cf[i]  # step producing q_i uses a_{i+1}? -> cf index i (0-based cf[i] is a_{i+1})
        # older-block fraction q_{k-2}/q_k : for step to q_i (k=i in 1-based conv index), q_{k-2}=qs[i-2]
        qkm2 = qs[i-2] if i>=2 else 1
        frac = qkm2/q
        Wp=d[str(qp)]["total_width"]; Wn=d[str(q)]["total_width"]
        factor = Wp/Wn                     # >1, W thins
        ratio  = Wn/Wp                     # <1
        g = factor/lamv                    # g(a)=factor/lam
        deficit = 1.0 - ratio              # 1 - W_new/W_prev
        rows.append(dict(step=f"{qp}->{q}", a=a, frac=frac, Wprev=Wp, Wnew=Wn,
                         factor=factor, ratio=ratio, g=g, deficit=deficit))
    step_tables[lamv]=rows
    print(f"\n-- lam={lamv} --")
    print(f"{'step':>14} {'a':>3} {'oldblk%':>8} {'factor(W-/W+)':>13} {'g=fac/lam':>10} {'ratio':>10} {'1-ratio(deficit)':>18}")
    for r in rows:
        gb = G_BANKED.get(r['a'])
        gtag = f"(bank {gb})" if gb else ("(NEW)" if r['a']>=2 else "")
        print(f"{r['step']:>14} {r['a']:>3} {100*r['frac']:>7.2f}% {r['factor']:>13.5f} {r['g']:>10.4f} "
              f"{r['ratio']:>10.5f} {r['deficit']:>18.12g}  {gtag}")

# closed form W_k ~ 4/lam^{m_k}
print("\n### CLOSED FORM  W_k ~ 4/lam^{m_k},  m_k=#{a_j>=2 up to k} ###")
for lamv in (8.0,24.0,32.0):
    d=res[f"lam{lamv}"]; m=0
    print(f"-- lam={lamv} --")
    for i,q in enumerate(qs):
        a=cf[i]
        if a>=2: m+=1
        pred=4.0/(lamv**m); W=d[str(q)]["total_width"]
        print(f"   q={q:>7} a={a:>3} m={m} W={W:.6e} pred=4/lam^{m}={pred:.6e} W/pred={W/pred:.4f}")

# ============ P3 deficits to 12 sig figs at the a=1 steps ============
print("\n### P3 a=1 STEPS (older-block fraction ordering) — deficits to 12 sig figs ###")
a1_steps=[(i,cf[i]) for i in range(1,len(qs)) if cf[i]==1]
for lamv in (8.0,24.0,32.0):
    print(f"-- lam={lamv} --  (pi isolated a3=1 deficit @this lam = {PI_A1_DEFICIT[lamv]:.3e}, golden a=1 deficit ~0.60)")
    for r in step_tables[lamv]:
        if r['a']==1:
            print(f"   {r['step']:>10}  oldblk={100*r['frac']:6.2f}%  deficit(1-W+/W-)= {r['deficit']:.12g}")

# ============ §3 GAP LABELING (Bellissard) q=12, q=53 ============
print("\n### GAP LABELING (Bellissard: IDS at gaps live on {k*alpha mod 1} = pitch classes) ###")
gap_out={}
for qlab in (12,53):
    e=np.load(os.path.join(OUT,f"fifth_edges_lam8_q{qlab}.npy"))
    bands=[(e[2*j],e[2*j+1]) for j in range(qlab)]
    gaps=[]
    for j in range(qlab-1):
        g=bands[j+1][0]-bands[j][1]
        ids=(j+1)/qlab
        gaps.append((g,ids,j+1))
    gaps.sort(reverse=True)
    print(f"\n-- q={qlab} approximant, top gaps --")
    print(f"{'gapwidth':>12} {'IDS=(#below)/q':>16} {'k':>4} {'k*alpha mod1':>14} {'|IDS-kalpha|':>13}")
    rows=[]
    for g,ids,nb in gaps[:8]:
        k,v,dd=kalpha_nearest(ids)
        print(f"{g:>12.6e} {ids:>16.6f} {k:>4} {v:>14.6f} {dd:>13.2e}")
        rows.append(dict(gapwidth=g,ids=ids,nbelow=nb,k=k,kalpha=v,dist=dd))
    gap_out[qlab]=rows

json.dump(dict(step_tables={str(k):v for k,v in step_tables.items()}, gap_labeling=gap_out),
          open(os.path.join(OUT,"fifth_analysis.json"),"w"), indent=1, default=float)
print("\nwrote fifth_analysis.json")

# ============ FIGURE: the diatonic quasicrystal assembling ============
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
fig,ax=plt.subplots(figsize=(12,7))
depths=[q for q in ladder if q>=2]
for yi,q in enumerate(depths):
    if q==2:
        _,bands=q2_exact(8.0)                      # exact period-2 bands (Floquet degenerate here)
    else:
        e=np.load(os.path.join(OUT,f"fifth_edges_lam8_q{q}.npy"))
        bands=[(e[2*j],e[2*j+1]) for j in range(q)]
    for lo,hi in bands:
        ax.plot([lo,hi],[yi,yi],lw=2.2,color="#1a3d6d",solid_capstyle="butt")
    ax.text(-3.0,yi,f"q={q}",va="center",ha="right",fontsize=9)
    ax.text(10.6,yi,f"a={cf[ladder.index(q)]}",va="center",ha="left",fontsize=8,color="#888")
ax.set_yticks([])
ax.set_xlabel("energy E   (λ=8)")
ax.set_title("The Diatonic Hamiltonian — quasicrystal spectrum assembling along the fifth's convergents\n"
             r"$\alpha=\log_2(3/2)$,  q = 2, 5, 12(diatonic), 41, 53, 306, 665, 15601")
ax.set_xlim(-3.4,11.4)
ax.margins(y=0.02)
plt.tight_layout()
plt.savefig(os.path.join(OUT,"fifth_spectrum_ladder.png"),dpi=130)
print("wrote fifth_spectrum_ladder.png")
