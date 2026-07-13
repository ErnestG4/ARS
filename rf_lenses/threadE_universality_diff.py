"""Thread E — the universality diff the toolkit was built for but hadn't run:
time-domain chaos (Mackey-Glass) vs space-domain quasiperiodicity (the diatonic Hamiltonian
spectrum), diffed on LONG-RANGE RIGIDITY (Family II), not marginal spacing (Family I).

Pre-registration (from the brief):
 - Family I (marginal) is the SHALLOW read (marginal != class); do not bank the Family-I contrast.
 - Real test: Sigma^2(L)/Delta_3(L) at matched N>=200, BOTH unfold lenses (deg-6 empirical + rate-aware).
   Registered: crystal RIGID (Sigma^2 ~ log L), MG chaotic recurrence NOT (Sigma^2 ~ L, Poisson-like).
 - Continuous-system discipline: 3-extractor consensus for MG.
Read-only. BASE_SEED=20240517.
"""
import os,sys,json,math
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0,ROOT); sys.path.insert(0,os.path.expandvars("$HOME/fmexplorer/riemann_explorer"))
import numpy as np
import transition_calibrators_dynamical as tcd
from cross_substrate.longrange_discriminator import longrange_stats, unfold_empirical, rate_aware_unfold
from universality import compute_nns
OUT=os.path.dirname(os.path.abspath(__file__)); SEED=20240517

# ---- substrates (RAW positions; unfolded identically below) ----
def crystal_levels(q=665):
    e=np.load(os.path.join(ROOT,f"approximability/fifth_edges_lam8_q{q}.npy"))
    return np.sort((e[0::2]+e[1::2])/2)                       # band centers = spectral levels
def mg_raw_events(tau=30.0, n_steps=300000):
    x=tcd.mackey_glass(tau=tau, n_steps=n_steps, dt=0.1)
    out={}
    for name,fn in tcd.MACKEY_GLASS_EXTRACTORS.items():
        raw=np.sort(np.asarray(fn(x),dtype=float)); raw=raw[np.isfinite(raw)]
        if raw.size>=200: out[name]=raw
    return out

def rigidity(positions, lens):
    """Sigma^2(L) and Delta_3(L) under a named unfold lens; return growth diagnostics."""
    pos=np.sort(np.asarray(positions,dtype=float))
    if lens=="emp": st=longrange_stats(pos, unfold_deg=6)
    elif lens=="rate": st=longrange_stats(pos, unfold_bw=20.0)
    L=np.asarray(st["L"],float); s2=np.asarray(st["sigma2"],float); d3=np.asarray(st["delta3"],float)
    m=np.isfinite(L)&np.isfinite(s2)&(L>=2)
    L,s2=L[m],s2[m]
    # discriminators: Poisson => Sigma^2=L (ratio->1); rigid => sublinear (ratio->0), ~log growth
    ratio=float(np.mean(s2/L))                              # ~1 Poisson, <<1 rigid
    # fit slope of Sigma^2 vs L (Poisson ~1) and vs ln L
    slope_lin=float(np.polyfit(L,s2,1)[0])
    slope_log=float(np.polyfit(np.log(L),s2,1)[0])
    return dict(lens=lens, n_L=int(L.size), Lmax=float(L.max()),
                sigma2_over_L_mean=ratio, slope_vs_L=slope_lin, slope_vs_lnL=slope_log,
                sigma2_at_Lmax=float(s2[-1]), L_at_max=float(L[-1]),
                Ls=[float(x) for x in L], sigma2=[float(x) for x in s2],
                delta3=[float(x) for x in d3[m][:len(L)]] if d3.size>=L.size else None)

def family_I(positions):
    u=np.sort(unfold_empirical(np.asarray(positions,float), deg=6))
    r=compute_nns(u); return dict(best_fit=r.best_fit, ks_gue=float(r.ks_gue),
                                  ks_poisson=float(r.ks_poisson), cv=float(np.std(np.diff(u))/np.mean(np.diff(u))))

results={"pre_registration":"crystal rigid (Sigma^2~logL), MG chaos Poisson-like (Sigma^2~L), even if marginals coerced"}

# crystal
cr=crystal_levels(665)
results["crystal_q665"]=dict(N=int(cr.size), family_I=family_I(cr),
                             rigidity={l:rigidity(cr,l) for l in ("emp","rate")})
# MG 3-extractor consensus
mg=mg_raw_events(tau=30.0, n_steps=300000)
results["mackey_glass_tau30"]={}
for name,ev in mg.items():
    results["mackey_glass_tau30"][name]=dict(N=int(ev.size), family_I=family_I(ev),
                                             rigidity={l:rigidity(ev,l) for l in ("emp","rate")})

json.dump(results, open(os.path.join(OUT,"threadE.json"),"w"), indent=1)

# ---- report ----
def show(tag, blk):
    fi=blk["family_I"]; print(f"\n{tag}  N={blk['N']}")
    print(f"   Family I (shallow): best_fit={fi['best_fit']}  ks_gue={fi['ks_gue']:.3f}  ks_poisson={fi['ks_poisson']:.3f}  CV={fi['cv']:.3f}")
    for l in ("emp","rate"):
        r=blk["rigidity"][l]
        print(f"   Family II [{l:4}]: Sigma^2/L mean={r['sigma2_over_L_mean']:.3f}  slope_vs_L={r['slope_vs_L']:.3f}"
              f"  slope_vs_lnL={r['slope_vs_lnL']:.3f}  (Lmax={r['Lmax']:.0f})")
print("="*78); print("THREAD E — time-domain chaos vs space-domain quasiperiodicity")
print("Sigma^2/L mean:  ~1 = Poisson (not rigid);  <<1 = rigid.  slope_vs_L: ~1 Poisson, ~0 rigid.")
show("CRYSTAL (diatonic Hamiltonian spectrum, q=665)", results["crystal_q665"])
for name,blk in results["mackey_glass_tau30"].items():
    show(f"MACKEY-GLASS chaos tau=30 [{name}]", blk)
print("\nwrote threadE.json")
