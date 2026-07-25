"""
ARS-RH Phase 4 (ii) — arithmetic Maass ENDPOINT classification (confound-free).
Prereg: PHASE4_PREREG_SEALED.json. §0: re-validates the KNOWN Sarnak anomaly via a hand-built
bracket; NOT new, NOT about RH. Per-sector (pooling manufactures false-Poisson -> decoy sentinel).
"""
import csv, json, math, os
import numpy as np
from scipy.linalg import eigh_tridiagonal
HERE=os.path.dirname(os.path.abspath(__file__)); ROOT=os.path.dirname(HERE)
RNG=np.random.default_rng(20260727)
def rtil(x):
    s=np.diff(np.sort(x)); s=s[s>0]
    r=np.minimum(s[:-1],s[1:])/np.maximum(s[:-1],s[1:]); return float(r.mean())
def poisson_rt(N):                       # unit exponential spacings
    return np.cumsum(RNG.exponential(1.0,N))
def beta_central(N,beta):                # DE tridiagonal beta-ensemble, central N-window
    n=4*N
    d=math.sqrt(2.0)*RNG.standard_normal(n)
    b=np.sqrt(RNG.chisquare(beta*np.arange(n-1,0,-1)))
    return np.sort(eigh_tridiagonal(d,b,eigvals_only=True,select="i",
                                    select_range=(int(1.5*N),int(1.5*N)+N-1)))
REF={"Poisson":0.38629,"GOE":0.53070,"GUE":0.60266,"GSE":0.67617}

# ---- load arithmetic Maass level-1 spectrum ----
r=[]; sym=[]
with open(os.path.join(ROOT,"sessionK","maass_level1_partial.csv")) as f:
    for row in csv.DictReader(f):
        r.append(float(row["r"])); sym.append(int(row["symmetry"]))
r=np.array(r); sym=np.array(sym)
print("=== Phase 4 (ii): arithmetic Maass endpoint classification ===",flush=True)
print("loaded %d level-1 Maass r_j; parity counts:"%len(r),
      {int(s):int((sym==s).sum()) for s in np.unique(sym)},flush=True)

# ---- synthetic bracket bands, matched to N (sanity print) ----
def band(genfn,N,B=400):
    v=np.array([rtil(genfn(N)) for _ in range(B)]); return float(v.mean()),float(v.std())
print("\n[bracket sanity, N=300] Poisson r~=%.4f  GOE r~=%.4f  (refs %.3f / %.3f)"%(
      band(poisson_rt,300)[0], band(lambda N:beta_central(N,1),300)[0], REF["Poisson"],REF["GOE"]),flush=True)

res={"anti_claim":"re-validates KNOWN Sarnak anomaly via confound-free bracket; NOT RH","sectors":{}}
print("\n[per-sector classification]  (unfold-free r-tilde vs hand-built matched brackets)",flush=True)
for s in sorted(np.unique(sym)):
    rr=np.sort(r[sym==s]); N=len(rr); rt=rtil(rr)
    pm,ps=band(poisson_rt,N); gm,gs=band(lambda N:beta_central(N,1),N)
    zP=(rt-pm)/ps; zG=(rt-gm)/gs
    nearest=min(REF,key=lambda k:abs(rt-REF[k]))
    print("\n  parity=%d  N=%d  r-tilde=%.4f  -> nearest %s"%(s,N,rt,nearest),flush=True)
    print("    vs Poisson band %.4f+/-%.4f : z=%+.2f"%(pm,ps,zP),flush=True)
    print("    vs GOE     band %.4f+/-%.4f : z=%+.2f  (GOE excluded at %.1f sigma)"%(gm,gs,zG,abs(zG)),flush=True)
    res["sectors"][int(s)]={"N":N,"rtilde":rt,"nearest":nearest,
        "poisson_band":[pm,ps],"z_vs_poisson":zP,"goe_band":[gm,gs],"z_vs_goe":zG}

# ---- POOLING DECOY: false-Poisson is constructible by pooling GOE sectors ----
print("\n[pooling decoy — the specificity sentinel]",flush=True)
Ns=[int((sym==s).sum()) for s in sorted(np.unique(sym))]
# real pooled (both parity together)
rt_real_pool=rtil(r)
# synthetic: 2 independent GOE sectors of the real sizes, pooled/merged-sorted
def pooled_goe(Ns,B=400):
    out=[]
    for _ in range(B):
        merged=np.concatenate([beta_central(n,1) for n in Ns])
        out.append(rtil(merged))
    return np.array(out)
pg=pooled_goe(Ns); single_g=band(lambda N:beta_central(N,1),sum(Ns))
print("  single-sector GOE r~ (N=%d)      : %.4f"%(sum(Ns),single_g[0]),flush=True)
print("  POOLED 2 synthetic GOE sectors r~: %.4f +/- %.4f  (drift toward Poisson %.3f = false-Poisson)"%(
      pg.mean(),pg.std(),REF["Poisson"]),flush=True)
print("  real pooled (both parity) r~     : %.4f  (Poisson+Poisson stays Poisson; informative part is the GOE decoy)"%rt_real_pool,flush=True)
pooling_fakes = pg.mean() < single_g[0] - 2*single_g[1]
print("  -> pooling GOE manufactures Poisson-ward drift: %s"%("YES (per-sector discipline load-bearing; real within-sector Poisson is NOT this artifact)" if pooling_fakes else "no"),flush=True)
res["pooling_decoy"]={"single_sector_goe":single_g[0],"pooled_goe_mean":float(pg.mean()),
    "pooled_goe_sd":float(pg.std()),"real_pooled":rt_real_pool,"pooling_manufactures_poisson":bool(pooling_fakes)}

# ---- verdict ----
allP=all(res["sectors"][int(s)]["nearest"]=="Poisson" and res["sectors"][int(s)]["z_vs_goe"]<-4
         for s in np.unique(sym))
res["verdict"]=("ENDPOINT CONFIRMED: both parity sectors sit at Poisson, synthetic GOE excluded >4sigma each; "
                "CP1 re-validated through an independent construction + pooling guard. NOT about RH."
                if allP else "ENDPOINT NOT confirmed as predicted — inspect sectors.")
print("\nVERDICT:",res["verdict"],flush=True)
json.dump(res,open(os.path.join(HERE,"phase4_maass_endpoint_measured.json"),"w"),indent=2)
print("DONE",flush=True)
