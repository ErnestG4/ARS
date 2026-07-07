"""O2 — scout near-optimality dimension, measured by counting near-optimal Stern-Brocot cells.
SEALED prereg (O2_scout_prereg_SEALED.json): reward R=-log(q*|q*alpha-p|); near-maximal iff R>=R_max(h)-Delta,
Delta=log2 (factor-2 Farey-mediant band). d* = limsup log2 N(h) / h.  phi MUST give d*=0 (harness gate).
No parameter is tuned after seeing counts. Pruning keep-band is 6*Delta (>> the log2 counting band) so the
counted near-optimal set is complete; capped-frontier events are logged (no silent truncation)."""
import sys, json, math
import mpmath as mp
mp.mp.dps = 60

DELTA = math.log(2.0)          # SEALED near-maximal band (factor 2)
KEEP  = 6.0 * DELTA            # pruning slack, generous vs counting band -> completeness
QMAX  = mp.mpf('1e12')         # depth cap: stop when alpha-path convergent q exceeds this
HMAX  = 240                    # hard depth cap
FRONTIER_CAP = 200000          # safety; log if ever hit

# --- substrate pool: 13 J-cubics (generic-CF wilderness) + controls phi, fifth, pi, e ---
cbrt = mp.cbrt
targets = {
    'cbrt2':cbrt(2),'cbrt3':cbrt(3),'cbrt4':cbrt(4),'cbrt5':cbrt(5),'cbrt6':cbrt(6),'cbrt7':cbrt(7),
    'cbrt9':cbrt(9),'cbrt10':cbrt(10),'cbrt11':cbrt(11),'cbrt12':cbrt(12),
    'plastic':mp.findroot(lambda x:x**3-x-1,1.3),'cbrt2p1':cbrt(2)+1,
    'root_x3_3x_1':mp.findroot(lambda x:x**3-3*x-1,1.9),
    # controls
    'phi':(1+mp.sqrt(5))/2,'fifth':mp.log(mp.mpf(3)/2)/mp.log(2),'pi':mp.pi,'e':mp.e,
}
CUBICS = ['cbrt2','cbrt3','cbrt4','cbrt5','cbrt6','cbrt7','cbrt9','cbrt10','cbrt11','cbrt12',
          'plastic','cbrt2p1','root_x3_3x_1']

def reward(p, q, alpha):
    # R = -log(q*|q*alpha - p|).  q*|q*alpha-p| in (0,inf); good approximants -> small -> large R.
    e = abs(q*alpha - p)
    if e == 0: return mp.mpf('inf')
    return -mp.log(q*e)

def run_target(name, alpha):
    alpha = mp.mpf(alpha)
    # Stern-Brocot node = open interval (pL/qL, pR/qR); its mediant is the depth-h cell.
    # frontier: list of (pL,qL,pR,qR, has_alpha) whose mediant sits at the current depth.
    # root mediant 1/1 at depth 1, from boundaries 0/1 and 1/0.
    frontier = [(0,1, 1,0, True)]
    Ns = []          # N(h) = # near-maximal cells at depth h
    Rmaxs = []       # R_max(h)
    path_q = []      # q of the alpha-path cell at depth h (best approximant reachable)
    capped = 0
    for h in range(1, HMAX+1):
        if not frontier: break
        # evaluate mediants at this depth
        rec = []      # (R, pm,qm,pL,qL,pR,qR, has_alpha)
        Rmax = mp.mpf('-inf'); pathq = None
        for (pL,qL,pR,qR,ha) in frontier:
            pm, qm = pL+pR, qL+qR
            R = reward(pm, qm, alpha)
            rec.append((R,pm,qm,pL,qL,pR,qR,ha))
            if ha: pathq = qm
            if R > Rmax: Rmax = R
        # count near-maximal (SEALED: R >= Rmax - DELTA)
        thr = Rmax - DELTA
        N = sum(1 for r in rec if r[0] >= thr)
        Ns.append(N); Rmaxs.append(float(Rmax)); path_q.append(int(pathq) if pathq else None)
        # depth cap on alpha-path convergent size
        if pathq is not None and mp.mpf(pathq) > QMAX: break
        # expand: keep nodes within KEEP of Rmax (or containing alpha), branch to both children
        keepthr = Rmax - KEEP
        nxt = []
        for (R,pm,qm,pL,qL,pR,qR,ha) in rec:
            if not (ha or R >= keepthr): continue
            # left child interval (pL/qL, pm/qm) contains alpha iff alpha < pm/qm
            a_lt = alpha < mp.mpf(pm)/qm
            nxt.append((pL,qL, pm,qm, ha and a_lt))
            nxt.append((pm,qm, pR,qR, ha and (not a_lt)))
        if len(nxt) > FRONTIER_CAP:
            capped += 1
            # keep the strongest FRONTIER_CAP by proximity to alpha (never drop alpha-path)
            nxt.sort(key=lambda t: 0 if t[4] else abs(float(mp.mpf(t[0]+t[2])/(t[1]+t[3]) - alpha)))
            nxt = nxt[:FRONTIER_CAP]
        frontier = nxt
    # --- near-optimality dimension d* = limsup log2 N(h)/h ; also classify growth ---
    hs = list(range(1, len(Ns)+1))
    dstar_series = [math.log2(N)/h if N > 0 else 0.0 for h,N in zip(hs,Ns)]
    dstar_peak = max(dstar_series) if dstar_series else 0.0
    # tail estimate over last third
    tail = dstar_series[max(0,2*len(dstar_series)//3):]
    dstar_tail = sum(tail)/len(tail) if tail else 0.0
    Nmax = max(Ns) if Ns else 0
    Nmean = sum(Ns)/len(Ns) if Ns else 0.0
    return dict(name=name, depth_reached=len(Ns), Nmax=Nmax, Nmean=round(Nmean,3),
                dstar_peak=round(dstar_peak,4), dstar_tail=round(dstar_tail,4),
                capped_events=capped, N_series=Ns, Rmax_series=[round(r,3) for r in Rmaxs])

def main():
    results = {}
    for name, a in targets.items():
        r = run_target(name, a)
        results[name] = r
        tag = 'CUBIC' if name in CUBICS else 'ctrl '
        print(f"[{tag}] {name:16s} depth={r['depth_reached']:3d} Nmax={r['Nmax']:5d} "
              f"Nmean={r['Nmean']:6.2f} d*peak={r['dstar_peak']:.3f} d*tail={r['dstar_tail']:.3f}"
              f"{'  CAP!' if r['capped_events'] else ''}", flush=True)
    # pooled cubic verdict
    cub = [results[n] for n in CUBICS]
    ctrl_phi = results['phi']
    cub_dstar_peak = max(r['dstar_peak'] for r in cub)
    cub_dstar_tail_mean = sum(r['dstar_tail'] for r in cub)/len(cub)
    cub_Nmax = max(r['Nmax'] for r in cub)
    verdict = dict(
        phi_control=dict(dstar_peak=ctrl_phi['dstar_peak'], dstar_tail=ctrl_phi['dstar_tail'],
                         Nmax=ctrl_phi['Nmax'],
                         harness_ok=bool(ctrl_phi['dstar_tail'] < 0.05 and ctrl_phi['Nmax'] <= 4)),
        cubic_pool=dict(dstar_peak=round(cub_dstar_peak,4),
                        dstar_tail_mean=round(cub_dstar_tail_mean,4), Nmax=cub_Nmax),
    )
    # GREEN iff tail d* -> 0 (sub-exponential N(h)); RED iff bounded away from 0
    verdict['scout'] = 'GREEN (measured-efficient)' if cub_dstar_tail_mean < 0.05 else \
                       ('AMBER (bounded-poly, inspect)' if cub_dstar_tail_mean < 0.15 else 'RED (measured-inefficient)')
    print("\n=== VERDICT ===")
    print(json.dumps(verdict, indent=1))
    json.dump(dict(delta=DELTA, keep=KEEP, results=results, verdict=verdict),
              open('O2_scout_measured.json','w'), indent=1, default=float)
    print("\nwrote O2_scout_measured.json")

if __name__ == '__main__':
    main()
