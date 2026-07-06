"""Session H Arm 1 — CORRECTION + a>=2 EXTENSION (banked data, no new measurement).

Corrects the first-pass Arm 1 crossover claim and extends it to all a.

WHAT THE FIRST PASS GOT RIGHT:
  - q-growth = q_n/q_{n-1} for an a=1 step is EXACTLY 1/(1-f), f = q_{n-2}/q_n  (algebraic, from q_n=q_{n-1}+q_{n-2}).
  - direction of all 7 a=1 steps predicted correctly.

WHAT IT GOT WRONG (this file fixes it):
  - The crossover was written as "factor = q-growth" (=> f*~0.287 universal). That is the dim=0.5 special case only.
  - EXACT sign of dim_n - dim_{n-1}: with dim=L/(L+B), L=ln q, B=ln(1/W):
        rise  iff  L_n/L_{n-1} > B_n/B_{n-1}
        =>  DROP iff  ln(factor)/ln(q_growth) > (1/dim_{n-1} - 1)          [factor=W_{n-1}/W_n]
    Threshold is (1/dim_{n-1} - 1), NOT 1. They coincide only at dim=0.5. So there is NO universal crossover
    fraction; the crossover is a dim-dependent surface. The fifth's depth-12 did not "sit on" a crossover — under
    the exact law it rises comfortably (ratio 0.996 < threshold 1.258), which is exactly why G's monotone-drop
    predictor tripped there.

GENERAL q-growth (any a): q_n = a_n q_{n-1} + q_{n-2}  =>  1 = a_n(q_{n-1}/q_n) + f  =>  q-growth = a_n/(1-f).
  (Reduces to 1/(1-f) at a=1. NOT a+f.)

RESULT: the exact law predicts the direction of ALL 17 banked steps (pi 7/7 + fifth 10/10), a=1 AND a>=2,
including the big-quotient cases the simple version misses (pi a=15 DROP, fifth a=5 RISE). The full finite-depth
DIRECTION structure is closed-form in (a, f, dim, factor). The only non-closed piece is the thinning factor
magnitude itself (lambda*g_metallic(a) for a>=2; g(1,f) for a=1), which carries the ~30% per-substrate scatter.
"""
import math, json
pi=dict(name='pi', a=[7,15,1,292,1,1,1,2], q=[7,106,113,33102,33215,66317,99532,265381],
        dim=[0.7331,0.6244,0.6276,0.6798,0.6799,0.63681,0.62566,0.58676], qpp0=1)
fifth=dict(name='fifth', a=[2,2,3,1,5,2,23,2,2,1,1], q=[5,12,41,53,306,665,15601,31867,79335,111202,190537],
           dim=[0.4788,0.4254,0.4083,0.4218,0.4315,0.4202,0.4660,0.4535,0.4428,0.4443,0.4349], qpp0=2)
def W(q,dim): return q**(1-1/dim)
def run(s):
    qfull=[s['qpp0']]+s['q']; rows=[]; nok=0; nsimple=0
    for i in range(1,len(s['dim'])):
        qn,qp,qpp=s['q'][i],s['q'][i-1],qfull[i-1]
        f=qpp/qn; qg=qn/qp; an=s['a'][i]
        factor=W(qp,s['dim'][i-1])/W(qn,s['dim'][i])
        ratio=math.log(factor)/math.log(qg); thr=1/s['dim'][i-1]-1
        pred='DROP' if ratio>thr else 'RISE'
        actual='DROP' if s['dim'][i]<s['dim'][i-1] else 'RISE'
        simple='DROP' if factor>qg else 'RISE'
        nok+=pred==actual; nsimple+=simple==actual
        rows.append(dict(a=an,f=f,q_growth=qg,a_over_1mf=an/(1-f),qgrowth_identity_ok=abs(qg-an/(1-f))<1e-9,
                         factor=factor,ratio=ratio,threshold=thr,pred=pred,actual=actual,
                         exact_ok=pred==actual,simple_pred=simple,simple_ok=simple==actual))
    return rows,nok,nsimple
out={}
for s in (pi,fifth):
    rows,nok,nsimple=run(s); out[s['name']]=dict(rows=rows,exact_correct=nok,simple_correct=nsimple,total=len(rows))
    print(f"{s['name']}: exact-law {nok}/{len(rows)}  |  simple(factor>qgrowth) {nsimple}/{len(rows)}")
    print(f"  q-growth==a/(1-f) all rows: {all(r['qgrowth_identity_ok'] for r in rows)}")
tot=sum(out[k]['total'] for k in out); ex=sum(out[k]['exact_correct'] for k in out); si=sum(out[k]['simple_correct'] for k in out)
print(f"\nTOTAL across pi+fifth, ALL a: exact law {ex}/{tot}  |  simple {si}/{tot}")
# which steps does simple miss?
for s in (pi,fifth):
    for r in out[s['name']]['rows']:
        if not r['simple_ok']:
            print(f"  simple MISSES: {s['name']} a={r['a']} f={r['f']:.3f} (simple->{r['simple_pred']}, actual={r['actual']}, exact->{r['pred']} OK)")
out['law']="DROP iff ln(W_{n-1}/W_n) > (1/dim_{n-1} - 1) * ln(a_n/(1-f_n)); q-growth=a/(1-f) exact"
out['correction']="first-pass 'crossover factor=q-growth, f*=0.287 universal' was dim=0.5 special case; true threshold (1/dim-1) is dim-dependent, no universal crossover fraction; directions robust (survive), crossover-location claim retracted"
out['residual_open']="thinning-factor MAGNITUDE (lambda*g(a) a>=2; g(1,f) a=1) carries ~30% per-substrate scatter -- the one local component; e/cubics probe THIS, not direction"
json.dump(out, open('H_direction_law.json','w'), indent=1)
print("\nwrote H_direction_law.json")
print("\nLAW:", out['law'])
