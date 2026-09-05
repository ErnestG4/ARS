"""Session D — π-292 finite-depth dimension direction, DERIVED FROM THE CERTIFIED THOULESS LAW.

The AMO identification failed (operator is Sturmian, not cosine; no |4-4λ| law). But the Thouless per-step
bandwidth law IS the right operator's law (banked, validated) and it governs the finite-depth dim trajectory
(dim = ln q / ln(q/W), homecoming-run mechanism). This replaces the dead Liu-Wen anchor with a DERIVED prediction.

Thouless inputs (banked): a=1 step factor = f(older-block fraction q_{k-2}/q_k); a>=2 step factor ≈ λ·g(a),
g(2)=0.638. π depths 4,5 banked: W4=W5=0.007435 (λ=8), dim≈0.680. Predict depths 6,7,8.
Seals a LOCKED pre-registration the future sparse-eigensolver session will open and test. BASE_SEED=20240517.
"""
import os,sys,math,json
sys.path.insert(0,"/home/combust/fmexplorer/riemann_explorer")
import mpmath as mp; mp.mp.dps=40
import numpy as np
OUT=os.path.dirname(os.path.abspath(__file__)); LAM=8.0; W_BANKED=0.007435  # W4=W5 at λ=8

# π convergents (exact integer)
cf=[7,15,1,292,1,1,1,2]
q=[0,1]
for a in cf: q.append(a*q[-1]+q[-2])
q=q[2:]   # q[0]=q1=7 ...
Q={i+1:q[i] for i in range(len(q))}    # Q[4]=33102 ... Q[8]=265381
print("π convergent denominators:", {k:Q[k] for k in range(4,9)})

# banked a=1 factor calibration: (older-block fraction, factor=W_before/W_after)
# points: π a3=1 6.2%→~1.0006 ; diatonic a6=1 22.6%→1.063 ; golden 38.2%→2.51 ; diatonic 50%→4.237
cal_f=np.array([0.062,0.226,0.382,0.499]); cal_fac=np.array([1.0006,1.063,2.51,4.237])
def a1_factor(frac):
    # monotone interpolation of ln(factor) in fraction (clamped)
    return float(np.exp(np.interp(frac, cal_f, np.log(cal_fac))))
def a2_factor(): return LAM*0.638   # λ·g(2)

steps=[]
W=W_BANKED   # at depth 5 (a5=1 already applied, W5=W4)
dims={}
def dim_of(qk,Wk): return math.log(qk)/math.log(qk/Wk)
dims[5]=dim_of(Q[5],W)
print(f"\ndepth 5 (anchor, banked): q={Q[5]} W={W:.6e} dim={dims[5]:.4f}")
for k in (6,7,8):
    a=cf[k-1]                      # cf index: cf[k-1] is a_k
    frac=Q[k-2]/Q[k]              # older-block fraction q_{k-2}/q_k
    growth=Q[k]/Q[k-1]
    if a==1:
        factor=a1_factor(frac); kind=f"a=1 (older-block {frac:.3f})"
    else:
        factor=a2_factor(); kind=f"a={a}"
    W=W/factor
    dims[k]=dim_of(Q[k],W)
    # DIRECTION robustness: dim drops iff ln(factor) > ln(growth)
    drop = math.log(factor) > math.log(growth)
    margin = math.log(factor)-math.log(growth)
    steps.append(dict(depth=k, a=a, older_block_frac=frac, q=Q[k], q_growth=growth,
                      thin_factor=factor, W=W, dim=dims[k],
                      direction=("DROP" if drop else "RISE"), ln_margin=margin))
    print(f"depth {k}: {kind:24} q={Q[k]:>7} growth×{growth:.3f} thin×{factor:.2f} "
          f"W={W:.3e} dim={dims[k]:.4f}  -> {('DROP' if drop else 'RISE')} (ln-margin {margin:+.2f})")

# ---- sealed direction verdict ----
dirs=[s["direction"] for s in steps]
overall = "MONOTONE_RETREAT" if all(d=="DROP" for d in dirs) else ("_".join(dirs))
print(f"\nSEALED DIRECTION (depths 5→6→7→8): dim {dims[5]:.3f} → {dims[6]:.3f} → {dims[7]:.3f} → {dims[8]:.3f}")
print(f"  = flat(4→5) then {overall} across 6,7,8.")
print("  MECHANISM: after the giant a4=292, the consecutive a5,a6,a7=1 give Fibonacci-like convergents so the")
print("  older-block fractions jump to ~50%(a6), ~33%(a7) — GOLDEN-REGIME a=1 steps that THIN W (unlike a5's 0.3%),")
print("  plus the a8=2 step. Every step 6-8 thins W faster than q grows ⇒ dim retreats.")
print("  This RESURRECTS the 'retreat' direction (dead when Liu-Wen fell out) — now DERIVED from the Thouless law,")
print("  for the correct reason (older-block thinning), not the asymptotic liminf-K reason Liu-Wen wrongly implied.")

sealed=dict(
  sealed_by="Session D (thouless-amo-identify branch)", operator="Sturmian (NOT AMO)",
  derived_from="certified Thouless per-step bandwidth law (a=1 older-block + a>=2 λ·g(a)); dim=ln q/ln(q/W)",
  lambda_=LAM, anchor="depth-5 banked dim≈0.680 (W4=W5=0.007435)",
  prediction_direction="π (a=292) dim FLAT at depth 4→5, then MONOTONE RETREAT across depths 6,7,8",
  per_step=steps, predicted_dims={str(k):dims[k] for k in dims},
  robustness="DIRECTION is robust (each step's ln(thin_factor) > ln(q_growth) with margins "
             f"{[round(s['ln_margin'],2) for s in steps]}); MAGNITUDES are estimates (a=1 factor interpolated "
             "from 4 banked calibration points, λ-dependence not fully modeled) — test the DIRECTION first.",
  falsifier="if the sparse-eigensolver run finds dim RISING (or non-monotone up) across depths 6-8, this Thouless-"
            "derived predictor is falsified and π-292 is genuinely predictor-less (2nd null after Liu-Wen).",
  least_certain_step="depth 7 (a7=1, frac 0.334): smallest ln-margin; if the a=1 factor there is <1.5 it could be near-flat",
  replaces="the dead Liu-Wen finite-depth pre-registration",
  note="AMO identification FAILED at layer-zero (Sturmian step ≠ AMO cosine; no λ=1 collapse; slope≠λ,λ/2). This "
       "predictor does NOT come from AMO — it comes from the certified Thouless law for the actual (Sturmian) operator.")
json.dump(sealed, open(os.path.join(OUT,"pi292_prediction_SEALED.json"),"w"), indent=1)
print("\nwrote pi292_prediction_SEALED.json  (LOCKED pre-registration for the future sparse-eigensolver session)")
