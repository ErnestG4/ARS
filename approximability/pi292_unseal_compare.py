"""UNSEAL + compare — run ONLY after pi292_measured.json (blind) is written.
Opens pi292_prediction_SEALED.json and tests the measured dims against the locked Session-D prediction,
applying the sealed falsifier verbatim. Anchor dim5=0.6799 (banked homecoming, pi lam=8 depth-5)."""
import json,math,os
OUT=os.path.dirname(os.path.abspath(__file__))
meas=json.load(open(os.path.join(OUT,"pi292_measured.json")))["depths"]
seal=json.load(open(os.path.join(OUT,"pi292_prediction_SEALED.json")))
DIM5=0.6799   # banked pi depth-5 dim, lam=8 (the flat anchor)

pred={str(s["depth"]):s["dim"] for s in seal["per_step"]}     # predicted dims at 6,7,8
pdir=seal["prediction_direction"]; falsifier=seal["falsifier"]; soft=seal["least_certain_step"]

depths=sorted(int(d) for d in meas)
series=[DIM5]+[meas[str(d)]["dim"] for d in depths]
labels=[5]+depths
print("="*74); print("UNSEAL — pi (a=292) finite-depth dimension vs the locked Session-D prediction")
print(f"anchor dim5={DIM5} (banked)")
print(f"{'depth':>6} {'q':>8} {'dim_measured':>13} {'dim_predicted':>13} {'Δ':>8} {'step_dir':>9}")
print(f"{5:>6} {33215:>8} {DIM5:>13.5f} {'0.680(anchor)':>13} {'—':>8} {'—':>9}")
prev=DIM5; monotone_retreat=True; rose=False
for d in depths:
    dm=meas[str(d)]["dim"]; dp=pred.get(str(d),float('nan'))
    step="DROP" if dm<prev else "RISE"
    if dm>=prev: monotone_retreat=False; rose=True
    print(f"{d:>6} {meas[str(d)]['q']:>8} {dm:>13.5f} {dp:>13.5f} {dm-dp:>8.3f} {step:>9}")
    prev=dm

print("\n--- VERDICT ---")
print(f"predicted direction: {pdir}")
print(f"measured direction : dim5→{'→'.join(f'{x:.4f}' for x in series[1:])} ; monotone retreat = {monotone_retreat}")
# apply sealed falsifier verbatim: "if ... dim RISING (or non-monotone up) across depths 6-8 ... falsified"
falsified = rose
if monotone_retreat and not falsified:
    verdict="CONFIRMED — monotone retreat as predicted; sealed falsifier NOT tripped."
else:
    verdict="FALSIFIED — sealed falsifier tripped (dim rose / non-monotone up)."
print(f"sealed falsifier: {falsifier}")
print(f"depth-7 (flagged softest): measured dim={meas.get('7',{}).get('dim')}")
print(f"\n>>> {verdict}")
# magnitude note (secondary; seal flagged magnitudes as estimates)
mags=[abs(meas[str(d)]['dim']-pred[str(d)]) for d in depths if str(d) in pred]
print(f"magnitude |measured−predicted|: {[round(m,3) for m in mags]} "
      f"(seal flagged magnitudes as ESTIMATES; direction is the load-bearing test)")
json.dump(dict(measured={str(d):meas[str(d)]['dim'] for d in depths}, predicted=pred, anchor_dim5=DIM5,
               monotone_retreat=monotone_retreat, falsified=bool(falsified), verdict=verdict),
          open(os.path.join(OUT,"pi292_seal_verdict.json"),"w"), indent=1)
print("wrote pi292_seal_verdict.json")
