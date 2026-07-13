"""
OVERNIGHT Task 3 (D3 turn) — Farey window-scaling max_gap/mean vs Q to Q=1e6, all five targets.

PARAMETER TURN on the FROZEN clean-room refsuite (imports its functions; NO logic edits). If any needed call is
missing/needs a code change, ABORT and report (per the overnight constitution).

PRE-REGISTERED (before run): golden & √2 curves flat/bounded; π's cusp (a=292 @ q=33102) persists once Q>33102;
e's growing quotients begin entering around Q~1e6 ⇒ FIRST grid where e's drift becomes visible. Registered
discriminating signature: π = cusp-then-stable, e = progressive drift. e's curve is exactly precomputable from Euler's CF.
Seed 20240517.
"""
import os, sys, json, math
_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MATHTEST = os.path.expandvars("$HOME/fmexplorer/mathtest")
sys.path.insert(0, MATHTEST)
import numpy as np, mpmath as mp
mp.mp.dps = 80
OUT = os.path.dirname(os.path.abspath(__file__))

# import FROZEN refsuite d3 (no edits); abort-and-report if the parameter surface isn't there
try:
    from refsuite.d3_farey import enumerate_window, window_gap_stats, window_width_for_count
except Exception as e:
    json.dump({"task": "3_d3", "ABORT": f"refsuite import/parameter surface failure: {e}"},
              open(os.path.join(OUT, "task3_d3.json"), "w"), indent=2)
    print("TASK3-D3 ABORT (parameter surface):", e); sys.exit(0)

LIOUVILLE = sum(mp.mpf(10) ** (-math.factorial(n)) for n in range(1, 8))
TARGETS = {"golden": (mp.sqrt(5) - 1) / 2, "sqrt2": mp.sqrt(2) - 1, "pi": mp.pi - 3,
           "e": mp.e - 2, "liouville": LIOUVILLE}
QS = [10**4, 10**5, 10**6]


def cf_frac(x, n):
    a = []; y = mp.mpf(x); y = y - int(mp.floor(y))
    for _ in range(n):
        ai = int(mp.floor(1 / y)); y = 1 / y - ai; a.append(ai)
        if y == 0: break
    return a


if __name__ == "__main__":
    # pre-register e: its max accessible quotient at each Q (Euler CF spine drives the cusp)
    e_cf = cf_frac(mp.e, 60)
    # convergent denominators of e to know which quotients are "inside" a window at order Q
    qd = [0, 1]
    for a in e_cf:
        qd.append(a * qd[-1] + qd[-2])
    qd = qd[2:]
    e_maxq_at = {}
    for Q in QS:
        inside = [e_cf[i] for i in range(len(qd)) if qd[i] <= Q]
        e_maxq_at[Q] = max(inside) if inside else None
    print(f"[pre-register] e: max quotient with q<=Q — " +
          ", ".join(f"Q={Q}:a_max={e_maxq_at[Q]}(q up to {max([q for q in qd if q<=Q], default=0)})" for Q in QS))
    print("  ⇒ e's cusp grows as bigger quotients enter; golden/√2 stay a_max=1/2 (flat).")

    results = {}
    print(f"\n{'target':10s} " + " ".join(f"Q={Q:g}".rjust(16) for Q in QS) + "   (max_gap/mean ; n)")
    for name, alpha in TARGETS.items():
        af = float(alpha); row = {}
        cells = []
        for Q in QS:
            try:
                w = window_width_for_count(Q, 12000)
                fr = enumerate_window(af, w, Q)                 # list of (num, den)
                gaps, inv_ok = window_gap_stats(fr)             # frozen: (gaps, p'q-pq'==1 ok)
                mg = (max(gaps) / (sum(gaps) / len(gaps))) if gaps else None
                n = len(fr)
                row[Q] = {"max_gap_over_mean": mg, "n": n, "w": w, "invariant_ok": bool(inv_ok)}
                cells.append((f"{mg:.1f};{n}" + ("" if inv_ok else "!INV")).rjust(16) if mg else "—".rjust(16))
            except Exception as ex:
                row[Q] = {"error": str(ex)}; cells.append("ERR".rjust(16))
        results[name] = row
        print(f"{name:10s} " + " ".join(cells))

    # discriminator: does π stabilize (cusp then flat) while e drifts up across Q?
    def mg(name, Q):
        r = results[name].get(Q, {}); return r.get("max_gap_over_mean")
    verdict = {}
    for name in TARGETS:
        seq = [mg(name, Q) for Q in QS]
        if all(v is not None for v in seq):
            drift = seq[-1] - seq[0]
            verdict[name] = {"seq": seq, "drift_Q1e4_to_1e6": drift}
    print("\n[discriminator] max_gap/mean drift 1e4→1e6:")
    for name, v in verdict.items():
        print(f"   {name:10s} {v['seq']}  drift={v['drift_Q1e4_to_1e6']:+.1f}")
    print("   registered: golden/√2 ~flat; π cusp persists (>33102); e first shows progressive drift at Q~1e6.")

    json.dump({"task": "3_d3", "seed": 20240517, "QS": QS, "e_maxq_at_Q": e_maxq_at,
               "results": results, "verdict": verdict},
              open(os.path.join(OUT, "task3_d3.json"), "w"), indent=2, default=str)
    print("\nwrote approximability/task3_d3.json — DONE.")
