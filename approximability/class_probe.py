"""Arm 1 (PRIMARY) — does the long-range spectral CLASS collapse across the 13-cubic wilderness the way the
marginal g~(a,f) did, or SPLIT? Reuses the CERTIFIED panel_B pipeline (sturmian_eigs tridiagonal +
unfold_empirical + II1_sigma2_at_L). Readout: gamma = slope(log Sigma^2 vs log L) -- the number-variance
growth exponent, normalization-independent. Poisson gamma->1, GUE gamma->0 (layer-zero, MUST pass first).
Verdict COLLAPSE (cubic gamma clustered, matches metallic band) vs SPLIT (cubic gamma spread / substrate-ordered).
Engine read-only from cross_substrate/."""
import os, sys, json, math
_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _ROOT); sys.path.insert(0, os.path.join(_ROOT, "cross_substrate"))
import numpy as np
import mpmath as mp
mp.mp.dps = 60
from cross_substrate.sturmian_hamiltonian_run import sturmian_eigs
from cross_substrate.longrange_discriminator import unfold_empirical
from cross_substrate.axes import II1_sigma2_at_L

LAM = 16.0; N = 4200; UDEG = 16
L_GRID = [2.0, 3.0, 5.0, 8.0, 12.0, 20.0, 30.0]
SEEDS = (0.1234, 0.31, 0.53)
logL = np.log(np.array(L_GRID))

def sigma2_curve(alpha, n=N):
    curves=[]
    for phi in SEEDS:
        e = np.sort(np.asarray(sturmian_eigs(alpha, phi, lam=LAM, n=n), float))
        k=int(len(e)*0.12); e=e[k:len(e)-k]
        u=np.sort(unfold_empirical(e, UDEG))
        curves.append([II1_sigma2_at_L(u,L) for L in L_GRID])
    C=np.array(curves,float)
    return C.mean(0), C.std(0)/math.sqrt(len(SEEDS))

def gamma_of(sig):
    # slope of log Sigma^2 vs log L (number-variance growth exponent)
    return float(np.polyfit(logL, np.log(sig), 1)[0])

def frac(x): return float(mp.frac(mp.mpf(x)))

# --- layer-zero calibrators (must pass before the pool) ---
def calibrators():
    rng=np.random.RandomState(20240517)
    out={}
    # Poisson: sorted uniform -> unfold -> Sigma^2 ~ L (gamma ~ 1)
    e=np.sort(rng.uniform(0,N,N)); u=np.sort(unfold_empirical(e,UDEG))
    sp=np.array([II1_sigma2_at_L(u,L) for L in L_GRID]); out['poisson']=(sp,gamma_of(sp))
    # GUE: eigenvalues of a Hermitian Gaussian matrix -> Sigma^2 ~ (1/pi^2)ln L (gamma ~ 0)
    m=1200; A=(rng.randn(m,m)+1j*rng.randn(m,m))/math.sqrt(2)
    H=(A+A.conj().T)/2; ev=np.linalg.eigvalsh(H)
    kk=int(m*0.15); ev=ev[kk:m-kk]; u=np.sort(unfold_empirical(ev,UDEG))
    sg=np.array([II1_sigma2_at_L(u,L) for L in L_GRID]); out['gue']=(sg,gamma_of(sg))
    return out

CUBICS={'cbrt2':mp.cbrt(2),'cbrt3':mp.cbrt(3),'cbrt4':mp.cbrt(4),'cbrt5':mp.cbrt(5),'cbrt6':mp.cbrt(6),
        'cbrt7':mp.cbrt(7),'cbrt9':mp.cbrt(9),'cbrt10':mp.cbrt(10),'cbrt11':mp.cbrt(11),'cbrt12':mp.cbrt(12),
        'plastic':mp.findroot(lambda x:x**3-x-1,1.3),'cbrt2p1':mp.cbrt(2)+1,
        'root_x3_3x_1':mp.findroot(lambda x:x**3-3*x-1,1.9)}
METALLIC={'golden':(mp.sqrt(5)-1)/2,'silver':mp.sqrt(2)-1,'bronze':(mp.sqrt(13)-3)/2}
CTRL={'fifth':mp.log(mp.mpf(3)/2)/mp.log(2),'pi':mp.pi,'e':mp.e}

def main():
    print("=== LAYER-ZERO CALIBRATION ===",flush=True)
    cal=calibrators()
    print(f"  Poisson: gamma={cal['poisson'][1]:.3f} (expect ~1)   GUE: gamma={cal['gue'][1]:.3f} (expect ~0)",flush=True)
    cal_ok = cal['poisson'][1] > 0.75 and cal['gue'][1] < 0.35
    print(f"  calibration {'PASS' if cal_ok else 'FAIL'}",flush=True)

    res={}
    for group,pool in (('cubic',CUBICS),('metallic',METALLIC),('ctrl',CTRL)):
        for name,x in pool.items():
            a=frac(x); m,se=sigma2_curve(a); g=gamma_of(m)
            res[name]=dict(group=group,alpha=a,sigma2=m.tolist(),sigma2_se=se.tolist(),gamma=g)
            print(f"  [{group:8s}] {name:14s} gamma={g:.3f}  Sigma2(L=30)={m[-1]:.1f}",flush=True)

    cub_g=np.array([res[n]['gamma'] for n in CUBICS])
    met_g=np.array([res[n]['gamma'] for n in METALLIC])
    cub_mean,cub_sd=float(cub_g.mean()),float(cub_g.std())
    met_mean,met_sd=float(met_g.mean()),float(met_g.std())
    # COLLAPSE iff cubic gammas tightly clustered AND cubic band overlaps metallic band
    collapse = cub_sd < 0.05 and abs(cub_mean-met_mean) < 0.06
    verdict=dict(cubic_gamma_mean=round(cub_mean,4),cubic_gamma_sd=round(cub_sd,4),
                 metallic_gamma_mean=round(met_mean,4),metallic_gamma_sd=round(met_sd,4),
                 cubic_gamma_range=[round(float(cub_g.min()),3),round(float(cub_g.max()),3)],
                 calibration_pass=bool(cal_ok),
                 result=('COLLAPSE (class universal across cubic wilderness; matches metallic band)' if collapse
                         else 'SPLIT (cubic class spread / off metallic band -> g~ universality is marginal-only)'))
    print("\n=== VERDICT ===");print(json.dumps(verdict,indent=1))
    json.dump(dict(lam=LAM,n=N,L_grid=L_GRID,calibrators={k:(v[0].tolist(),v[1]) for k,v in cal.items()},
                   results=res,verdict=verdict), open('Arm1_class_measured.json','w'),indent=1,default=float)
    print("wrote Arm1_class_measured.json")

if __name__=='__main__':
    main()
