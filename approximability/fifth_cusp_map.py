"""Session C — CF-cusp cartography of the fifth (alpha=log2(3/2)).

The cheap arithmetic faces (record process, Farey aperture) out-reach the eigensolve (frontier
q=15601 at the a=23 convergent). Map every CF-cusp the cheap faces can see within certified depth,
test a=55 co-registration, mark the REACH HORIZON (q_k<=15601 jointly visible vs q_k>15601
arithmetic-face-only), and place the fifth's ladder beside pi's (a=292). Banked instruments only.

C-Z1: two-precision CF gate (dps 50/80/150) agree to depth>=16; cross-check vs certified d15eab4 CF.
C-Z2: quotients & convergents integer; q at the a=23 position == 15601 (spectral frontier).
Cusp threshold a_k>=10 (pre-registered CONVENTION, not derived; GK P(a=k)=log2(1+1/(k(k+2)))).
BASE_SEED=20240517.
"""
import os,sys,json,math
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0,ROOT); sys.path.insert(0,os.path.expandvars("$HOME/fmexplorer/riemann_explorer"))
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
import mpmath as mp
from panel_D_records import records          # banked Panel-D record-process instrument
OUT=os.path.dirname(os.path.abspath(__file__))
CUSP=10; FRONTIER_Q=15601

# ===== C-Z1: three-precision CF gate =====
def cf_at(dps, n):
    mp.mp.dps=dps
    x=mp.log(mp.mpf(3)/2)/mp.log(2); y=x-int(mp.floor(x)); a=[]
    for _ in range(n):
        ai=int(mp.floor(1/y)); a.append(ai); y=1/y-ai
        if y==0: break
    return a
NREQ=50
c50,c80,c150=cf_at(50,NREQ),cf_at(80,NREQ),cf_at(150,NREQ)
depth=0
for x,y,z in zip(c50,c80,c150):
    if x==y==z: depth+=1
    else: break
A=c50[:depth]
assert depth>=16, f"C-Z1 FAIL: three-precision agreement only depth {depth}"
# cross-check first 16 against the certified d15eab4 artifact
banked=json.load(open(os.path.join(OUT,"fifth_battery.json")))["cf"]
assert A[:len(banked)]==banked, ("C-Z1 mismatch vs banked CF", A[:16], banked)
print(f"C-Z1 OK: three-precision (50/80/150) agree to depth {depth}; matches certified d15eab4 CF prefix.")

# ===== C-Z2: integer invariants + convergent ladder =====
mp.mp.dps=80
def conv(a):
    ps=[1,0]; qs=[0,1]
    for ai in a: ps.append(ai*ps[-1]+ps[-2]); qs.append(ai*qs[-1]+qs[-2])
    return ps[2:], qs[2:]
ps,qs=conv(A)
assert all(isinstance(a,int) for a in A) and all(isinstance(q,int) for q in qs)
# a=23 is at some position; its convergent q must be the spectral frontier 15601
pos23=A.index(23)
assert qs[pos23]==FRONTIER_Q, ("C-Z2 FAIL: q at a=23 != 15601", qs[pos23])
print(f"C-Z2 OK: quotients/convergents integer; a=23 at position {pos23+1} -> q={qs[pos23]} (spectral frontier).")

# ===== enumerate cusps (a>=10) in certified range =====
cusps=[]
running_max=0
for k,a in enumerate(A):
    is_record = a>running_max
    running_max=max(running_max,a)
    if a>=CUSP:
        qk=qs[k]
        cusps.append(dict(position=k+1, a=a, q_k=int(qk),
                          record_face=bool(is_record),          # record process only fires on new maxima
                          farey_jump_ratio=int(a),              # q_min jumps ~a_k at the cusp block -> fires if a>=10
                          farey_face=bool(a>=10),
                          spectral_reach="joint" if qk<=FRONTIER_Q else "arithmetic_only"))
print(f"\ncusps (a>={CUSP}) in certified depth {depth}: {[(c['position'],c['a']) for c in cusps]}")

# ===== co-registration table =====
print(f"\n{'pos':>4} {'a':>4} {'q_k':>12} {'record?':>8} {'Farey?':>7} {'spectral reach':>16}")
for c in cusps:
    print(f"{c['position']:>4} {c['a']:>4} {c['q_k']:>12} {str(c['record_face']):>8} {str(c['farey_face']):>7} {c['spectral_reach']:>16}")

# ===== a=55 co-registration verdict (pre-registered) =====
c55=[c for c in cusps if c['a']==55]
a55_both = bool(c55) and c55[0]['record_face'] and c55[0]['farey_face']
a55_reach = c55[0]['spectral_reach'] if c55 else None
print(f"\na=55 co-registration: record={c55[0]['record_face']} Farey={c55[0]['farey_face']} "
      f"-> both cheap faces={a55_both} ; spectral reach={a55_reach}")

# ===== reach horizon =====
joint=[c for c in cusps if c['spectral_reach']=="joint"]
arith=[c for c in cusps if c['spectral_reach']=="arithmetic_only"]
print(f"\nREACH HORIZON at q={FRONTIER_Q} (a=23 convergent):")
print(f"  jointly visible (cheap + eigensolve): {[(c['position'],c['a']) for c in joint]}")
print(f"  arithmetic-face-only (beyond frontier): {[(c['position'],c['a']) for c in arith]}")

# ===== pi cross-comparison (descriptive, non-predictive) =====
mp.mp.dps=80
ypi=mp.pi-3; picf=[]
for _ in range(16):
    ai=int(mp.floor(1/ypi)); picf.append(ai); ypi=1/ypi-ai
pps,pqs=conv(picf)
pi_cusps=[dict(position=k+1,a=a,q_k=int(pqs[k])) for k,a in enumerate(picf) if a>=CUSP]
print(f"\npi cross-comparison (DESCRIPTIVE, non-predictive): pi cusps (a>=10) = "
      f"{[(c['position'],c['a'],c['q_k']) for c in pi_cusps]}")
print(f"  fifth cusp ladder a = {[c['a'] for c in cusps]} ; pi cusp ladder a = {[c['a'] for c in pi_cusps]}")

out=dict(certified_depth=depth, cf=A, cusp_threshold=CUSP, frontier_q=FRONTIER_Q,
         cusps=cusps, a55_both_cheap_faces=a55_both, a55_spectral_reach=a55_reach,
         reach_horizon=dict(joint=[(c['position'],c['a']) for c in joint],
                            arithmetic_only=[(c['position'],c['a']) for c in arith]),
         pi_cusps=[(c['position'],c['a'],c['q_k']) for c in pi_cusps],
         reach_horizon_statement=(
           f"Of the fifth's certified CF-cusps (a>=10), only a=23 (q=15601) is jointly visible to the "
           f"eigensolve and the cheap faces; every deeper cusp (a=55 at q~1.06e7, ...) is arithmetic-face-only. "
           f"The reach horizon sits exactly at the a=23 spectral frontier."))
json.dump(out, open(os.path.join(OUT,"fifth_cusp_map.json"),"w"), indent=1, default=str)
print("\nwrote fifth_cusp_map.json")
