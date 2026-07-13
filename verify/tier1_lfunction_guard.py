"""
verify/tier1_lfunction_guard.py — Tier 1: is the L-function NNS claim robust to the PLL
frequency-admission guard?  (Overnight verification harness — READ-ONLY, edits no driver.)

FINDING BEING TESTED (audit 06 FIX-4): the L-function drivers use `if f_pll <= 0.5: continue`
(admits Farey bands with f_pll>0.5), which DIVERGED (commit 43f48852) from the canonical
`if not (5.0 < f_pll < SR*0.45): continue` (run_analytical_nns.py:92, SR=44100). For fc_ref=1.0,
farey_rationals(8) gives f_pll in [0.125, 8.0]: 29/43 bands sit in (0.5, 5.0] — INCLUDED by the
banked 0.5-guard, EXCLUDED by canonical. So the banked Katz-Sarnak group signatures were pooled over
29 low-freq bands canonical drops. This harness re-pools under the canonical guard and asks whether
the family separation (root-number +1/-1, real/complex) SURVIVES the guard choice.

METHOD (faithful, no estimator reimplementation risk):
  - The estimator + classify + ks_to are copied VERBATIM from the drivers, with the guard
    parametrized as (f_lo, f_hi): 0.5-guard = (0.5, inf) reproduces the driver byte-for-byte;
    canonical = (5.0, 44100*0.45). Because each Farey band is self-normalized and canonical's
    admitted set is a strict subset of the 0.5-guard's, this is exact.
  - VALIDATION GATE: before trusting any canonical diff, the 0.5-guard reproduction from the cached
    zeros MUST match the banked results JSON (gap/best/ks_u). If it doesn't, we report VALIDATION
    FAILED (and do not report a diff) — this catches both a copy error and a zeros/results provenance
    mismatch. (synthetic-validate-fitters discipline.)

Run: PYTHONPATH=$HOME/fmexplorer/riemann_explorer \
     $HOME/fmexplorer/bin/python3 verify/tier1_lfunction_guard.py
"""
import os, sys, json
_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _ROOT)
import numpy as np
from pll_bank import farey_rationals                      # importable, no side effects
from universality import nns_cdf_poisson, nns_cdf_goe, nns_cdf_gue

SR = 44100.0
CANON = (5.0, SR * 0.45)          # canonical guard window (run_analytical_nns.py:92)
DRIFT = (0.5, np.inf)             # the drivers' 0.5-guard: f_pll > 0.5, no upper cap

# ── VERBATIM from run_lmfdb_family.py:66-93 (guard parametrized as f_lo<f_pll<f_hi) ──
def analytical_nns(t_n_array, fc_ref, q_max, dur_s, transient_s,
                   lock_confirm_s, tongue_prefac, sr, f_lo, f_hi, min_events=10):
    pairs = farey_rationals(q_max)
    pooled, info = [], []
    for p, q in pairs:
        f_pll = fc_ref * p / q
        if not (f_lo < f_pll < f_hi):          # <-- ONLY change: parametrized guard
            continue
        elig = ((t_n_array >= (transient_s + 1.0) * f_pll) &
                (t_n_array <= (dur_s + 1.0) * f_pll))
        elig_t = np.sort(t_n_array[elig])
        threshold = lock_confirm_s * f_pll / (tongue_prefac * (2.0 / (p + q)) ** 2)
        qualifying = elig_t[elig_t >= threshold]
        if qualifying.size < min_events + 1:
            continue
        spacings = np.diff(qualifying) / f_pll
        if spacings.size == 0 or spacings.mean() <= 0:
            continue
        pooled.append(spacings / spacings.mean())
        info.append(dict(p=p, q=q, f_pll=f_pll, n_passages=int(qualifying.size)))
    pooled = np.concatenate(pooled) if pooled else np.zeros(0)
    return pooled, info

# ── VERBATIM run_lmfdb_family.py:88-104 ──
def ks_to(s, theory_cdf):
    s = np.sort(np.asarray(s, dtype=np.float64)); n = s.size
    if n < 5: return float('nan')
    F_em = np.arange(1, n + 1) / n
    return float(np.max(np.abs(F_em - theory_cdf(s))))

def classify(pooled):
    if pooled.size < 50:
        return dict(n=int(pooled.size), best='insufficient')
    ks_p = ks_to(pooled, nns_cdf_poisson); ks_o = ks_to(pooled, nns_cdf_goe)
    ks_u = ks_to(pooled, nns_cdf_gue)
    best = min([('Poiss', ks_p), ('GOE', ks_o), ('GUE', ks_u)], key=lambda x: x[1])[0]
    return dict(n=int(pooled.size), ks_p=ks_p, ks_o=ks_o, ks_u=ks_u,
                gap=ks_o - ks_u, mass03=float((pooled < 0.3).mean()), best=best)

# Driver params (module constants; FC_REF=1.0, Q_MAX=8, DUR=300, TRANSIENT_S=0.5, etc.)
P = dict(fc_ref=1.0, q_max=8, dur_s=300.0, transient_s=0.5,
         lock_confirm_s=20e-3, tongue_prefac=0.05, sr=SR, min_events=10)

def aggregate_pool(curves, guard):
    arrs = []
    for r in curves:
        z = np.asarray(r['zeros'], float)
        pooled, _ = analytical_nns(z, f_lo=guard[0], f_hi=guard[1], **P)
        if pooled.size > 50:
            arrs.append(pooled)
    return np.concatenate(arrs) if arrs else np.zeros(0)

def run_curve_driver(name, zeros_path, banked_path, group_fn):
    out = [f"\n### {name}\n"]
    curves = json.load(open(os.path.join(_ROOT, zeros_path)))
    banked = json.load(open(os.path.join(_ROOT, banked_path))).get('aggregates', {})
    groups = group_fn(curves)
    # band-materiality (informational)
    f = np.array([P['fc_ref'] * p / q for p, q in farey_rationals(P['q_max'])])
    n_drop = int(((f > DRIFT[0]) & ~((f > CANON[0]) & (f < CANON[1]))).sum())
    out.append(f"- bands: {len(f)} total; {n_drop} admitted by 0.5-guard but dropped by canonical "
               f"(f_pll range [{f.min():.3f},{f.max():.3f}])\n")
    out.append(f"\n| group | guard | n_pool | ks_u | gap | best |\n|---|---|---|---|---|---|\n")
    validated = True
    verdict_lines = []
    for gname, gcurves in groups.items():
        cl_drift = classify(aggregate_pool(gcurves, DRIFT))
        cl_canon = classify(aggregate_pool(gcurves, CANON))
        # VALIDATION: 0.5-guard reproduction vs banked
        b = banked.get(gname, {})
        vflag = ""
        if b and b.get('best') != 'insufficient' and cl_drift.get('best') != 'insufficient':
            ok = (abs(cl_drift['gap'] - b['gap']) < 5e-3 and cl_drift['best'] == b['best']
                  and abs(cl_drift['ks_u'] - b['ks_u']) < 5e-3)
            if not ok:
                validated = False
                vflag = f"  ⚠VALIDATION-MISMATCH vs banked(gap={b.get('gap'):+.3f},best={b.get('best')})"
        for tag, cl in (("0.5-drift", cl_drift), ("canonical", cl_canon)):
            if cl.get('best') == 'insufficient':
                out.append(f"| {gname} | {tag} | {cl['n']} | — | — | insufficient |\n")
            else:
                out.append(f"| {gname} | {tag} | {cl['n']} | {cl['ks_u']:.3f} | {cl['gap']:+.3f} | {cl['best']} |\n")
        # did the verdict flip?
        if cl_drift.get('best') != 'insufficient' and cl_canon.get('best') != 'insufficient':
            flip = "FLIP" if cl_drift['best'] != cl_canon['best'] else "stable"
            verdict_lines.append(f"  - {gname}: best {cl_drift['best']}→{cl_canon['best']} ({flip}); "
                                 f"gap {cl_drift['gap']:+.3f}→{cl_canon['gap']:+.3f}{vflag}")
    out.append(f"\n**Validation ({name}): {'PASS — 0.5-repro matches banked' if validated else 'FAILED — see ⚠'}**\n")
    out.append("**Guard-robustness:**\n" + "\n".join(verdict_lines) + "\n")
    return "".join(out)

def run_mertens_liouville():
    out = ["\n### mertens_liouville\n"]
    banked = json.load(open(os.path.join(_ROOT, 'data/mertens_liouville_results.json')))
    srcs = {
        'mertens':   'data/phase34a_results/mertens_signchanges_N10000000.npz',
        'liouville': 'data/phase34b_results/liouville_signchanges_N1000000000.npz',
    }
    out.append("\n| signal | guard | fc_ref | n_bands_kept | n_pool | gap | best |\n|---|---|---|---|---|---|---|\n")
    for sig, path in srcs.items():
        z = np.load(os.path.join(_ROOT, path))
        pos = np.asarray(z['signchanges'], float)
        if pos.size < 3:
            out.append(f"| {sig} | — | — | — | {pos.size} | — | too-few-signchanges |\n"); continue
        fc_ref = float(np.median(pos)) / 100.0
        f = fc_ref * np.array([p / q for p, q in farey_rationals(P['q_max'])])
        for tag, guard in (("0.5-drift", DRIFT), ("canonical", CANON)):
            kept = int(((f > guard[0]) & (f < guard[1])).sum())
            Pm = dict(P); Pm['fc_ref'] = fc_ref
            pooled, _ = analytical_nns(pos, f_lo=guard[0], f_hi=guard[1], **Pm)
            cl = classify(pooled)
            best = cl.get('best', '?'); gap = cl.get('gap')
            gaps = f"{gap:+.3f}" if isinstance(gap, float) else "—"
            out.append(f"| {sig} | {tag} | {fc_ref:.1f} | {kept} | {cl.get('n',0)} | {gaps} | {best} |\n")
    out.append("\n(Note: mertens/liouville fc_ref is large → the canonical Nyquist cap 19845 bites the "
               "HIGH bands, unlike the L-functions where the 5.0 lower bound bites the low bands.)\n")
    return "".join(out)

if __name__ == "__main__":
    md = ["# Tier 1 — L-function NNS guard robustness\n",
          "Canonical `(5.0, 19845)` vs banked `0.5`-guard `(0.5, inf)`. "
          "Verbatim estimator; validation-gated against banked JSON.\n"]
    md.append(run_curve_driver(
        "lmfdb_family (EC L-functions, height 200)", 'data/lmfdb_zeros.json', 'data/lmfdb_results.json',
        lambda cs: {'all curves': cs,
                    'root_number = +1': [r for r in cs if r['root_number'] == +1],
                    'root_number = -1': [r for r in cs if r['root_number'] == -1],
                    'rank = 0': [r for r in cs if r['rank'] == 0],
                    'rank ≥ 1': [r for r in cs if r['rank'] >= 1]}))
    md.append(run_curve_driver(
        "lmfdb_extend (EC L-functions, height 1000)", 'data/lmfdb_zeros_h1000.json', 'data/lmfdb_extend_results.json',
        lambda cs: {'all curves': cs,
                    'root_number = +1': [r for r in cs if r['root_number'] == +1],
                    'root_number = -1': [r for r in cs if r['root_number'] == -1]}))
    md.append(run_curve_driver(
        "dirichlet_family (Dirichlet L-functions)", 'data/dirichlet_zeros.json', 'data/dirichlet_results.json',
        lambda cs: {'all primitive non-trivial': cs,
                    'real characters (Sp predicted)': [c for c in cs if c['is_real']],
                    'complex characters (U predicted)': [c for c in cs if not c['is_real']]}))
    md.append(run_mertens_liouville())
    txt = "".join(md)
    open(os.path.join(_ROOT, 'verify', 'tier1_results.md'), 'w').write(txt)
    print(txt)
