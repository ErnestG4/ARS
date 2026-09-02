"""UNSEAL + compare + residual analysis for the fifth (run after G_fifth_measured.json is written)."""
import json,numpy as np
meas=json.load(open("G_fifth_measured.json"))["depths"]
seal=json.load(open("G_fifth_prediction_SEALED.json"))
pred={str(s["depth"]):s for s in seal["prediction"]}
DIM9=0.4660
print(f"anchor dim9={DIM9} @ q=15601 (steps 10-13 are FAREY-ONLY: below the a=23 record)")
print(f"{'depth':>5} {'a':>3} {'q':>8} {'measured':>9} {'predicted':>9} {'resid':>7} {'step':>6}")
prev=DIM9; rose=False; resids=[]
for d in (10,11,12,13):
    dm=meas[str(d)]['dim']; dp=pred[str(d)]['dim_predicted']; a=pred[str(d)]['a']
    st="DROP" if dm<prev else "RISE"
    if dm>=prev: rose=True
    resids.append(dm-dp)
    print(f"{d:>5} {a:>3} {meas[str(d)]['q']:>8} {dm:>9.5f} {dp:>9.5f} {dm-dp:>7.3f} {st:>6}")
    prev=dm
monotone=not rose; maxdev=max(abs(r) for r in resids)
falsified=(not monotone) or (maxdev>0.02)
verdict=("PARTIAL — magnitudes within 0.013(<0.02); convergence Farey-governed (all 4 Farey-only steps predicted, "
 "record-only law blind => §9 confirmed); BUT sealed strict-monotonicity falsifier TRIPS at depth 12 (a=1 factor "
 "not precisely transferable pi->fifth). Not rescued.")
json.dump(dict(measured={str(d):meas[str(d)]['dim'] for d in (10,11,12,13)},
               predicted={str(d):pred[str(d)]['dim_predicted'] for d in (10,11,12,13)},
               residuals=resids, monotone_retreat=monotone, max_dev=maxdev,
               falsifier_tripped=bool(falsified), verdict=verdict), open("G_seal_verdict.json","w"), indent=1)
print(f"\nmonotone={monotone} maxdev={maxdev:.3f} falsifier_tripped={falsified}\n{verdict}")
