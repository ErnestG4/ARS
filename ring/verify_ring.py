"""Board row for ring/ — Stage 0 port + Stage 1 measure 1. Nonzero exit on any failure.

What green means here (AUDIT.md caveat, verbatim): the checkers pass, not that
the instrument measures what we claim. Specifically this row certifies:
  R0  the package imports with torch BLOCKED (guard is real, not a comment)
  R1  every declared detector constructs (negative set + confusable named);
      declared-only detectors are NOT certified and cannot be read as passed
  R2  the banked Stage 1 table exists, its instrument is sealed, and the eps=0
      row is at the floor: |lam1| < 1e-12, drift < 1e-9
  R3  the dial does what it must: lam1 strictly decreases with eps at T=2000
      once above the floor; the eps=0.1 row is CONVERGED and collapsed
  R4  spectral and dynamic reads agree where both are valid (converged row)
  R5  the T-dependence is banked, not hidden: n_distinct differs between the
      two T rows at the same eps — a collapse threshold is not a substrate
      property until T is stated
  R6  the built detector is two-sided-correct on the banked rows and certifies;
      the nearest confusable is silent by a stated margin, not by luck
  R7  plan hygiene: no 'verify ID' tags, no Zone.Identifier stray, v5 header
"""
import os
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")

import json
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
sys.path.insert(0, REPO)
PY = sys.executable
fails = []


def chk(c, m):
    if not c:
        fails.append(m)


# R0 — torch guard is real
r = subprocess.run([PY, "-c",
                    "import sys; sys.modules['torch']=None; "
                    "import ring, ring.ringnet, ring.detectors; "
                    "assert ring.HAVE_TORCH is False; print('guard ok')"],
                   cwd=REPO, capture_output=True, text=True)
chk(r.returncode == 0 and "guard ok" in r.stdout,
    f"R0 torch guard: package failed to import with torch blocked: {r.stderr[-300:]}")

# R1 — detectors construct; declared-only are not certified
from ring import detectors as D                                      # noqa: E402
from detector_spec import DetectorNotCertified                       # noqa: E402
for name, mk in {**D.BUILT, **D.DECLARED_ONLY}.items():
    try:
        s = mk()
        chk(s.name == name, f"R1 {name}: spec name mismatch {s.name}")
    except Exception as e:                                           # noqa: BLE001
        chk(False, f"R1 {name}: spec failed to construct: {e}")
for name, mk in D.DECLARED_ONLY.items():
    try:
        mk().certify()
        chk(False, f"R1 {name}: DECLARED-ONLY detector certified with no "
                   "recorded outcomes — that is the laundering this row exists to stop")
    except DetectorNotCertified:
        pass

# R2 — banked table, sealed instrument, floor
path = os.path.join(HERE, "stage1_marginal_measured.json")
chk(os.path.exists(path), "R2 stage1_marginal_measured.json missing — run stage1_marginal.py")
if not os.path.exists(path):
    print("\n".join(fails)); sys.exit(1)
M = json.load(open(path))
inst = M["instrument"]
chk(inst["n_tested"] == 2 and inst["n_declared"] >= 7,
    f"R2 instrument seal shape changed: {inst['n_tested']} tested / {inst['n_declared']} declared")
rows = [x for x in M["rows"] if x["control"] == "bump"]
ctrl = [x for x in M["rows"] if x["control"] != "bump"]
T_long = max(x["T"] for x in rows)
T_short = min(x["T"] for x in rows)
chk(T_long > T_short, "R2 only one T banked")


def row(T, eps):
    m = [x for x in rows if x["T"] == T and abs(x["eps"] - eps) < 1e-12]
    return m[0] if m else None


for T in (T_short, T_long):
    z = row(T, 0.0)
    chk(z is not None, f"R2 eps=0 row missing at T={T}")
    if z:
        chk(abs(z["lam1_median"]) < 1e-12, f"R2 floor: |lam1| at eps=0,T={T} = {z['lam1_median']:.2e}")
        chk(z["drift_median"] < 1e-9, f"R2 floor: drift at eps=0,T={T} = {z['drift_median']:.2e}")
        chk(z["resid_max"] < 1e-10, f"R2 floor: eps=0 not a fixed point, resid {z['resid_max']:.1e}")
        chk(z["bump_amp_median"] > D.AMP_MIN, f"R2 no bump at eps=0,T={T}")
        chk(z["lam2_median"] < -0.3, f"R2 transverse mode not stable: lam2={z['lam2_median']:.3f}")

# R3 — dial monotone above floor; last row converged and collapsed
long_rows = sorted([x for x in rows if x["T"] == T_long], key=lambda x: x["eps"])
lam = [x["lam1_median"] for x in long_rows if x["eps"] > 0]
chk(all(b < a for a, b in zip(lam, lam[1:])),
    f"R3 lam1 not strictly decreasing with eps at T={T_long}: {['%.2e' % v for v in lam]}")
last = long_rows[-1]
chk(last["resid_max"] < 1e-8, f"R3 eps={last['eps']} row not converged: resid {last['resid_max']:.1e}")
chk(last["n_distinct"] <= last["B"] // 2,
    f"R3 no collapse at eps={last['eps']}: n_distinct={last['n_distinct']} of B={last['B']}")
chk(last["lam1_median"] < -1e-3, f"R3 pinned row lam1 too close to zero: {last['lam1_median']:.2e}")

# R4 — spectral vs dynamic agree on the converged row only (scoped, see ringnet)
rel = abs(last["relax_rate_median"] - (-last["lam1_median"])) / abs(last["lam1_median"])
chk(rel < 0.2, f"R4 spectral/dynamic disagree on converged row: rel err {rel:.2f}")

# R5 — T-dependence banked and visible
diffs = [(e, row(T_short, e)["n_distinct"], row(T_long, e)["n_distinct"])
         for e in [x["eps"] for x in long_rows] if row(T_short, e) and row(T_long, e)]
chk(any(a != b for _, a, b in diffs),
    f"R5 n_distinct identical at every eps across T={T_short},{T_long}: {diffs} — "
    "either the sweep is too short to show collapse or T stopped mattering; both need saying")

# R6 — built detector two-sided-correct, confusable silent by margin
spec = D.marginal_mode_spec()


def fires(x):
    return (x["bump_amp_median"] > D.AMP_MIN and x["lam1_median"] > -D.LAM1_TOL
            and x["resid_max"] < 1e-8)


spec.record("intact_eps0_T200", fires(row(T_short, 0.0)))
spec.record("intact_eps0_T2000", fires(row(T_long, 0.0)))
w = row(T_long, 1e-4)
spec.record("weak_pin_eps1e-4_T2000", fires(w) if w else True)
spec.record("pinned_eps0.1_T2000", fires(last))
nb = [x for x in ctrl if x["T"] == T_long]
spec.record("no_bump_J1=1.0_T2000", fires(nb[0]) if nb else True)
try:
    rates = spec.certify()
except DetectorNotCertified as e:
    chk(False, f"R6 {e}")
    rates = spec.rates()
if w:
    margin = abs(w["lam1_median"]) / D.LAM1_TOL
    chk(margin > 10, f"R6 nearest confusable silent by only {margin:.1f}x — threshold is luck")
    # NOTE (honest): the weak-pin row has resid ~1e-5 (still drifting) so the
    # amplitude+lam1 read is at a non-fixed-point; the detector's convergence
    # gate keeps it silent for THAT reason too. Both reasons are recorded.
    w_silent_by_lam1 = w["lam1_median"] <= -D.LAM1_TOL
    chk(w_silent_by_lam1, "R6 confusable is silent only via the convergence gate, "
                          "not via lam1 — the spectral threshold is not doing work")

# R7 — plan hygiene
plan = os.path.join(HERE, "rotational-dynamics-build-plan.md")
txt = open(plan).read()
chk(txt.startswith("# Rotational Dynamics / Attractor Geometry — Build Plan v5"), "R7 plan header not v5")
chk("verify ID" not in txt, "R7 'verify ID' tag survives in plan")
chk(not any(f.endswith("Zone.Identifier") for f in os.listdir(HERE)), "R7 Zone.Identifier stray in ring/")

print(f"ring board: {len(fails)} failure(s); built detector rates: "
      f"sens {rates['sensitivity']} spec {rates['specificity']}; "
      f"floor |lam1|={abs(row(T_long, 0.0)['lam1_median']):.1e}, "
      f"confusable margin {abs(row(T_long, 1e-4)['lam1_median']) / D.LAM1_TOL:.0f}x, "
      f"collapse T={T_short}:{[r_['n_distinct'] for r_ in sorted([x for x in rows if x['T'] == T_short], key=lambda x: x['eps'])]} "
      f"T={T_long}:{[r_['n_distinct'] for r_ in long_rows]}")
for f in fails:
    print("FAIL:", f)
sys.exit(1 if fails else 0)
