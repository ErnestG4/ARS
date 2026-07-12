#!/usr/bin/env python3
"""OVERNIGHT 2026-07-12 — four pre-registered jobs. Deterministic, unattended, verdicts to disk.

Jobs (see OVERNIGHT_BRIEF.md):
  GATE  grep-confirm what LV and ks_gue actually compute; log it.
  A     within-cell ISI shuffle -> can RETRACT the session's load-bearing claim.
  B     clustered calibrator class + unclipped I_rep + unbounded Brody.  HARD STOP if the
        class fails its own pre-committed reading.
  C     census re-run on the repaired axes (consistency gate).
  D     row-3 (correlational) instrument -- the first in the project's history. Exploratory.

STRUCTURAL RULES (from the brief):
  * every job writes its VERDICT file EVEN ON FAILURE. A silent null is the most dangerous
    object in this project.
  * everything seeded. git SHA logged at start.
  * B's calibrator runs BEFORE the repairs that depend on it, with a hard exit on failure.
"""
import os, sys, json, glob, time, traceback, subprocess
import numpy as np
from scipy import stats


class NpEnc(json.JSONEncoder):
    """np scalars are not JSON-serializable. Job B died on exactly this — after its science ran."""
    def default(self, o):
        if isinstance(o, (np.bool_,)):
            return bool(o)
        if isinstance(o, (np.integer,)):
            return int(o)
        if isinstance(o, (np.floating,)):
            return float(o)
        if isinstance(o, np.ndarray):
            return o.tolist()
        return super().default(o)

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "cross_substrate"))
sys.path.insert(0, HERE)

OUT = HERE
SEED = 20260712
N_SHUF = 200
rng_global = np.random.default_rng(SEED)


def log(m):
    print(f"[{time.strftime('%H:%M:%S')}] {m}", flush=True)


def write(fn, text):
    with open(os.path.join(OUT, fn), "w") as f:
        f.write(text)
    log(f"WROTE {fn}")


def sha():
    try:
        return subprocess.check_output(["git", "-C", ROOT, "rev-parse", "HEAD"]).decode().strip()[:10]
    except Exception:
        return "unknown"


def boot_ci(x, y, B=1000, seed=0):
    x, y = np.asarray(x, float), np.asarray(y, float)
    m = ~(np.isnan(x) | np.isnan(y))
    x, y = x[m], y[m]
    if x.size < 12:
        return (np.nan, np.nan, np.nan, 0)
    r0 = stats.spearmanr(x, y)[0]
    g = np.random.default_rng(seed)
    rs = [stats.spearmanr(x[i], y[i])[0] for i in (g.integers(0, x.size, x.size) for _ in range(B))]
    return (r0, float(np.nanpercentile(rs, 2.5)), float(np.nanpercentile(rs, 97.5)), int(x.size))


# ────────────────────────────────────────────────────────────────────── GATE
def job_gate():
    import inspect
    import cross_substrate.axes as AX
    lv_src = inspect.getsource(AX.I13_lv)
    ks_src = inspect.getsource(AX.I5_ks_gue)
    cs_src = inspect.getsource(AX.canonical_spacings) if hasattr(AX, "canonical_spacings") else "(n/a)"
    lv_is_shinomoto = "3.0 * ((a - b) / (a + b))" in lv_src.replace("  ", " ")
    ks_is_marginal = "_ks_cdf" in ks_src and "nns_cdf_gue" in ks_src
    txt = f"""# GATE — what do LV and ks_gue actually compute?

git SHA: `{sha()}`   seed: {SEED}

## I13_lv
```python
{lv_src}```
**Shinomoto adjacent-pair form: {'CONFIRMED' if lv_is_shinomoto else '*** NOT CONFIRMED ***'}**

## I5_ks_gue
```python
{ks_src}```
## canonical_spacings (what ks_gue is fed)
```python
{cs_src}```
**KS on the spacing multiset (marginal only, no drift correction): {'CONFIRMED' if ks_is_marginal else '*** NOT CONFIRMED ***'}**

## ⚠ A NEW BUG, found because the numeric check CONTRADICTED my algebra

I derived that `ks_gue` must be **exactly** order-invariant (a trim sorts, a unit-mean divides —
both permutation-invariant ⇒ `ks_gue(shuffled) ≡ ks_gue(observed)`). **The measurement said
otherwise** (|Δ| ≈ 1e-3 … 2e-2). The derivation was wrong, and the reason is a bug:

`phase35a/unfold_rotnum.py:70-74`
```python
def spacings(unf):
    u = np.sort(unf); d = np.diff(u)
    d = d[int(0.02 * len(d)):int(0.98 * len(d))]   # <-- POSITIONAL slice of the time-ordered sequence
    m = d.mean()
    return d / m if m > 0 else d
```

**This is a POSITIONAL slice — it drops the first and last 2 % of spacings IN TIME. It is NOT a
"2–98 % tail trim" of the spacing VALUES**, which is what its name and `axes.py:13` both claim.
Same class as `I_rep`'s unreachable *"negative → clustering"* and `phase24/loader.py:49`: a
docstring advertising a capability the code does not have.

Two consequences, and the second is load-bearing:

1. `ks_gue` **is** weakly order-dependent — but only via an **accidental time-crop**, not any
   principled order sensitivity. (So it still cannot be read as an order-domain axis.)
2. **The trim removes NO outlier spacings.** For a **CV = 16** substrate (Allen-HPF) the giant ISIs
   therefore survive, **inflate the unit-mean normaliser**, crush every normalised spacing toward
   zero — and `ks_gue` reads **≈ 0.86** (ζ reads 0.027). **The guard that was supposed to prevent
   exactly this does nothing.** A *third*, independent mechanism for Allen's broken marginal axis.

**Job A therefore computes `ks_gue` BOTH ways** — shipped (positional) and value-trimmed (what it
claims) — so the difference is **measured, not assumed**, and we can see whether Allen's marginal
pathology survives a *correct* trim.

`burst_frac = mean(ISI < 10ms)` remains a pure multiset functional (order-invariant).
LV IS genuinely order-dependent — its shuffle test is the real experiment.
"""
    write("VERDICT_GATE.md", txt)
    return lv_is_shinomoto, ks_is_marginal


# ───────────────────────────────────────────────────────────────────── JOB A
def spacings_valuetrim(positions, lo=0.02, hi=0.98):
    """What `phase35a.unfold_rotnum.spacings` CLAIMS to do: trim the 2–98% tails of the spacing
    VALUES, then unit-mean.  The shipped version instead does `d[int(.02*len(d)):int(.98*len(d))]`
    — a POSITIONAL slice of the time-ordered sequence, which removes NO outlier spacings at all.
    For a CV=16 substrate (Allen-HPF) the giant ISIs therefore survive, inflate the unit-mean
    normaliser, and crush every normalised spacing toward zero.  Computed alongside the shipped
    version so the difference is measured, not assumed."""
    u = np.sort(np.asarray(positions, float))
    d = np.diff(u)
    d = d[d > 0]
    if d.size < 20:
        return d
    a, b = np.quantile(d, [lo, hi])
    d = d[(d >= a) & (d <= b)]
    m = d.mean()
    return d / m if m > 0 else d


def axes_of(spk, rng, n_shuf=N_SHUF):
    """Observed + shuffled LV/CV2/ks_gue/burst for one cell."""
    from cross_substrate.axes import I13_lv, I12_cv2, I5_ks_gue, canonical_spacings
    isi = np.diff(spk)
    isi = isi[isi > 0]
    if isi.size < 100:
        return None
    burst = float(np.mean(isi < 0.010))
    cv = float(np.std(isi) / np.mean(isi))

    # Reconstruct the train from the FILTERED ISI multiset, so observed and shuffled are drawn
    # from the SAME multiset. (Without this, `ks_obs` uses the raw train — which includes the
    # non-positive spacings I drop — and the invariance check reports a spurious ~3e-3 deviation.
    # The deviation was my filtering, not a failure of the derivation.)
    def rebuild(seq):
        return np.concatenate([[spk[0]], spk[0] + np.cumsum(seq)])

    t_obs = rebuild(isi)
    lv_o = I13_lv(t_obs)
    cv2_o = I12_cv2(t_obs)
    ks_o = I5_ks_gue(canonical_spacings(t_obs))          # SHIPPED trim (positional slice)
    ks_v = I5_ks_gue(spacings_valuetrim(t_obs))          # CORRECT trim (value tails)
    ks_raw = I5_ks_gue(canonical_spacings(spk))          # banked-comparable, for reference
    if lv_o is None or ks_o is None:
        return None

    lvs, cv2s, kss, ksvs = [], [], [], []
    for _ in range(n_shuf):
        sh = rng.permutation(isi)
        a, b = sh[:-1], sh[1:]
        lvs.append(float(np.mean(3.0 * ((a - b) / (a + b)) ** 2)))
        cv2s.append(float(np.mean(2.0 * np.abs(a - b) / (a + b))))
        if len(kss) < 8:                      # ks: cheap, spot-check the (non-)invariance
            t = rebuild(sh)
            kss.append(I5_ks_gue(canonical_spacings(t)))
            ksvs.append(I5_ks_gue(spacings_valuetrim(t)))
    return dict(lv_obs=lv_o, lv_shuf=float(np.mean(lvs)), lv_shuf_sd=float(np.std(lvs)),
                cv2_obs=cv2_o, cv2_shuf=float(np.mean(cv2s)),
                ks_obs=ks_o, ks_shuf=float(np.nanmean(kss)) if kss else np.nan,
                ks_vtrim=ks_v, ks_vtrim_shuf=float(np.nanmean(ksvs)) if ksvs else np.nan,
                ks_raw=ks_raw, burst=burst, cv=cv, n=int(isi.size))


def job_A():
    from loaders import LOADERS, BANKED_N
    per_sub = {}
    for name, loader in LOADERS.items():
        t0 = time.time()
        rows = []
        rng = np.random.default_rng(SEED + abs(hash(name)) % 10000)
        for cid, spk in loader():
            r = axes_of(spk, rng)
            if r:
                r["cell_id"] = cid
                rows.append(r)
        per_sub[name] = rows
        log(f"JOB A {name}: {len(rows)} cells (banked {BANKED_N.get(name,'?')}) in {time.time()-t0:.0f}s")
    with open(os.path.join(OUT, "jobA_per_cell.json"), "w") as f:
        json.dump(per_sub, f, cls=NpEnc)

    # ---- the decomposition
    lines = ["# VERDICT A — the within-cell ISI shuffle",
             "",
             "> **If ρ(burst, LV_shuf) ≈ ρ(burst, LV_obs), the load-bearing claim of 2026-07-12 is",
             "> retracted to a drift-robustness result. SAY SO OUT LOUD BEFORE READING ANYTHING ELSE.**",
             "",
             f"git SHA `{sha()}` · seed {SEED} · {N_SHUF} shuffles/cell",
             "",
             "The shuffle destroys **all order and all drift** and preserves the **ISI marginal exactly**.",
             "It is the **renewal null with the observed marginal** — analytic ground truth, no generator,",
             "nothing to unfold wrong. Same class of instrument as Palm–Khintchine.",
             "",
             "## ks_gue — order-(non)invariance, and the SHIPPED-vs-CORRECT trim", "",
             "See VERDICT_GATE.md: the shipped `spacings()` does a **positional** slice, not a value-tail",
             "trim, so `ks_gue` is weakly order-dependent **by accident** and **removes no outliers**.", "",
             "| substrate | max\\|ks_obs−ks_shuf\\| | median ks_gue (SHIPPED) | median ks_gue (VALUE-TRIMMED) | Δ |",
             "|---|---|---|---|---|"]
    for name, rows in per_sub.items():
        if not rows:
            continue
        d = [abs(r["ks_obs"] - r["ks_shuf"]) for r in rows if not np.isnan(r.get("ks_shuf", np.nan))]
        ko = [r["ks_obs"] for r in rows]
        kv = [r["ks_vtrim"] for r in rows if r.get("ks_vtrim") is not None and not np.isnan(r["ks_vtrim"])]
        if d and kv:
            lines.append(f"| `{name}` | {max(d):.2e} | **{np.median(ko):.4f}** | "
                         f"**{np.median(kv):.4f}** | {np.median(kv)-np.median(ko):+.4f} |")
    lines += ["",
              "**If the value-trimmed ks_gue collapses toward the RMT range at Allen-HPF, then Allen's",
              "'far-from-GUE' marginal was the OUTLIER-INFLATED NORMALISER — a third mechanism, and the",
              "shipped trim was supposed to prevent exactly it.**",
              "",
              "`burst_frac` is a pure multiset functional (order-invariant) — so the old ladder's",
              "*predictor* carries no order information regardless.",
              "",
              "## The LV decomposition — the real experiment", "",
              "| substrate | n | ρ(burst, LV_obs) | ρ(burst, LV_shuf) | ρ(burst, LV_resid) | LV_obs−LV_shuf (median) |",
              "|---|---|---|---|---|---|"]
    verdict_rows = {}
    for name, rows in per_sub.items():
        if len(rows) < 12:
            lines.append(f"| {name} | {len(rows)} | — | — | — | *too few cells* |")
            continue
        b = [r["burst"] for r in rows]
        lo = [r["lv_obs"] for r in rows]
        ls = [r["lv_shuf"] for r in rows]
        lr = [r["lv_obs"] - r["lv_shuf"] for r in rows]
        r_o, o1, o2, n = boot_ci(b, lo, seed=1)
        r_s, s1, s2, _ = boot_ci(b, ls, seed=2)
        r_r, q1, q2, _ = boot_ci(b, lr, seed=3)
        verdict_rows[name] = (r_o, r_s, r_r)
        lines.append(f"| **{name}** | {n} | **{r_o:+.3f}** [{o1:+.3f},{o2:+.3f}] | "
                     f"**{r_s:+.3f}** [{s1:+.3f},{s2:+.3f}] | **{r_r:+.3f}** [{q1:+.3f},{q2:+.3f}] | "
                     f"{np.median(lr):+.4f} |")
    lines.append("")

    # ---- pre-committed verdict, on the load-bearing substrate
    if "allen-hpf-cell" in verdict_rows:
        r_o, r_s, r_r = verdict_rows["allen-hpf-cell"]
        near = abs(r_s - r_o) < 0.10
        resid = abs(r_r) > 0.25 and abs(r_r) > abs(r_s)
        if near and not resid:
            v = ("## VERDICT: **RETRACT**\n\n"
                 f"ρ(burst, LV_shuf) = **{r_s:+.3f}** ≈ ρ(burst, LV_obs) = **{r_o:+.3f}**. "
                 "**LV carried no order information.** The Allen dissociation is "
                 "**global-vs-local drift-robustness, NOT marginal-vs-pair.** The finding survives in a "
                 "smaller form: *ks_gue is drift-destroyed at HPF; LV is not; **both are marginal**.* "
                 "The 'domain change' was a change of normalization.")
        elif resid and not near:
            v = ("## VERDICT: **STRENGTHENED**\n\n"
                 f"The coupling lives in the residual: ρ(burst, LV_resid) = **{r_r:+.3f}** vs "
                 f"ρ(burst, LV_shuf) = **{r_s:+.3f}**. **There is genuine ORDER structure at Allen-HPF.** "
                 "The domain change was real, and it now has an **exact null** behind it instead of a label.")
        else:
            v = ("## VERDICT: **UNRESOLVED**\n\n"
                 f"Split: ρ_obs={r_o:+.3f}, ρ_shuf={r_s:+.3f}, ρ_resid={r_r:+.3f}. "
                 "**Gap** = the fraction of the coupling that is order-dependent. "
                 "**Closer** = the row-3 instrument (Job D: ρ₁ / autocorr-excess).")
        lines += [v, ""]
    write("VERDICT_A.md", "\n".join(lines))
    return per_sub


# ───────────────────────────────────────────────────────────────────── JOB B
def gen_clustered(kind, strength, n, rng):
    """Clustered (super-Poisson) point processes at a range of strengths."""
    if kind == "neyman_scott":
        n_par = max(10, int(n / max(1.5, strength)))
        parents = np.sort(rng.uniform(0, n_par, n_par))
        kids = rng.poisson(max(1.0, strength), n_par)
        pts = np.concatenate([p + rng.normal(0, 0.02, k) for p, k in zip(parents, kids) if k > 0])
        return np.sort(pts)
    if kind == "cox":                       # doubly-stochastic: rate modulated by a slow OU-ish field
        m = 400
        lam = np.exp(rng.normal(0, strength, m))
        lam = np.repeat(lam, max(1, n // m))
        t = np.cumsum(rng.exponential(1.0 / np.maximum(lam, 1e-6)))
        return t
    if kind == "gamma_renewal":             # CV>1 renewal: k<1
        k = 1.0 / max(1e-3, strength ** 2)
        return np.cumsum(rng.gamma(k, 1.0 / k, n))
    raise ValueError(kind)


def irep_unclipped(t):
    """The repair: signed ∫₀¹(1−R₂)dr — NO np.maximum(0, ·)."""
    from arithmetic_toolkit import _pair_correlation_universality
    t = np.sort(np.asarray(t, float))
    if t.size < 20:
        return np.nan
    res = _pair_correlation_universality(t, r_max=5.0, n_bins=50)
    r = np.asarray(res["r"]); R2 = np.asarray(res["R2"])
    m = r <= 1.0
    return float(np.trapezoid(1 - R2[m], r[m])) if m.any() else np.nan


def brody_unbounded(s, lo=-1.0, hi=4.0):
    """The repair: Brody with BOTH bounds opened (GUE≈2, GSE≈4 need the upper one)."""
    from scipy.optimize import minimize_scalar
    from cross_substrate.axes import brody_pdf
    s = np.asarray(s, float); s = s[s > 0]
    if s.size < 50:
        return np.nan
    def nll(q):
        return -np.sum(np.log(np.maximum(brody_pdf(s, q), 1e-300)))
    return float(minimize_scalar(nll, bounds=(lo, hi), method="bounded",
                                 options={"xatol": 1e-4}).x)


def job_B():
    from cross_substrate.axes import canonical_spacings
    rng = np.random.default_rng(SEED + 7)
    N = 20000
    sweep = []
    log("JOB B: generating the clustered calibrator class (sweep, not one exemplar)")
    for kind, strengths in [("gamma_renewal", [1.5, 2.0, 3.0, 5.0, 8.0, 13.5]),
                            ("cox", [0.5, 1.0, 1.5, 2.0, 2.5]),
                            ("neyman_scott", [2.0, 5.0, 10.0, 20.0])]:
        for st in strengths:
            try:
                t = gen_clustered(kind, st, N, rng)
                isi = np.diff(np.sort(t)); isi = isi[isi > 0]
                if isi.size < 500:
                    continue
                cv = float(np.std(isi) / np.mean(isi))
                sweep.append(dict(kind=kind, strength=st, cv=cv,
                                  irep_unclipped=irep_unclipped(t),
                                  brody_unbounded=brody_unbounded(canonical_spacings(t)),
                                  n=int(isi.size)))
            except Exception as e:
                sweep.append(dict(kind=kind, strength=st, error=f"{type(e).__name__}: {e}"))

    # reference poles through the SAME repaired estimators
    refs = {}
    for nm, gen in [("poisson", lambda: rng.exponential(1, N)),
                    ("GOE(inv-cdf)", None), ("GUE(inv-cdf)", None)]:
        try:
            if nm == "poisson":
                t = np.cumsum(gen())
            else:
                from universality import nns_cdf_goe, nns_cdf_gue
                cdf = nns_cdf_goe if "GOE" in nm else nns_cdf_gue
                g = np.linspace(0, 10, 20001)
                F = np.clip(np.asarray(cdf(g)), 0, 1); F[0] = 0
                s = np.interp(rng.random(N), F, g); s /= s.mean()
                t = np.cumsum(s)
            refs[nm] = dict(irep_unclipped=irep_unclipped(t),
                            brody_unbounded=brody_unbounded(canonical_spacings(t)))
        except Exception as e:
            refs[nm] = dict(error=str(e))

    ok = [s for s in sweep if "error" not in s and not np.isnan(s.get("irep_unclipped", np.nan))]
    neg_irep = bool(all(s["irep_unclipped"] < 0 for s in ok)) if ok else False
    neg_brody = bool(all(s["brody_unbounded"] < 0 for s in ok)) if ok else False
    mono = bool(stats.spearmanr([s["cv"] for s in ok], [s["irep_unclipped"] for s in ok])[0] < -0.5) if len(ok) > 4 else False
    passed = bool(ok) and bool(neg_irep) and bool(neg_brody) and bool(mono)

    L = ["# VERDICT B — the clustered calibrator class + the two repairs", "",
         f"git SHA `{sha()}` · seed {SEED}", "",
         "**Pre-committed HARD STOP:** the clustered class must read **negative on unclipped `I_rep`**",
         "and **q < 0 on unbounded Brody**, *monotonically in clustering strength*. If it does not, **the",
         "REPAIR is wrong, not the class** — and Jobs C/D do not run.", "",
         "## Reference poles, through the repaired estimators", "",
         "| reference | unclipped I_rep | unbounded Brody q |", "|---|---|---|"]
    for nm, r in refs.items():
        if "error" in r:
            L.append(f"| {nm} | ERROR | {r['error']} |")
        else:
            L.append(f"| {nm} | {r['irep_unclipped']:+.4f} | {r['brody_unbounded']:+.4f} |")
    L += ["", "## The clustered sweep (the half-line that has never been observed)", "",
          "| kind | strength | CV | **unclipped I_rep** | **unbounded Brody q** |", "|---|---|---|---|---|"]
    for s in sweep:
        if "error" in s:
            L.append(f"| {s['kind']} | {s['strength']} | — | ERROR | {s['error']} |")
        else:
            L.append(f"| {s['kind']} | {s['strength']} | {s['cv']:.2f} | "
                     f"**{s['irep_unclipped']:+.4f}** | **{s['brody_unbounded']:+.4f}** |")
    L += ["", f"- all clustered read **I_rep < 0**: **{neg_irep}**",
          f"- all clustered read **Brody q < 0**: **{neg_brody}**",
          f"- **monotone in clustering strength** (Spearman(CV, I_rep) < −0.5): **{mono}**", "",
          ("## GATE: **PASS** — the repairs are correct and the half-line now has a sign convention and a scale."
           if passed else
           "## GATE: **HARD STOP — THE REPAIR IS WRONG, NOT THE CLASS.**\n\n"
           "Jobs C and D are SKIPPED. Do not reason around this at 3am. Read the sweep table.")]
    write("VERDICT_B.md", "\n".join(L))
    with open(os.path.join(OUT, "jobB_sweep.json"), "w") as f:
        json.dump(dict(sweep=sweep, refs=refs, passed=passed), f, indent=1, cls=NpEnc)
    return passed


# ───────────────────────────────────────────────────────────────────── JOB C
def job_C(per_sub):
    """Census re-run on the repaired axes. CONSISTENCY GATE, not a new result."""
    from cross_substrate.axes import canonical_spacings
    from loaders import LOADERS
    L = ["# VERDICT C — the census, re-run on the REPAIRED axes", "",
         f"git SHA `{sha()}` · seed {SEED}", "",
         "**Pre-committed:** the census verdict (**every neural substrate is CLUSTERED**) *must* reproduce.",
         "It was established on the **Poisson null**, which no repair touches. **If it does not reproduce,",
         "something in the repair is wrong.** This is a consistency gate, not a new result.", "",
         "It also converts a **detection** into a **measurement**: *how* clustered, on a half-line that now",
         "has units.", "",
         "| substrate | cells | median unclipped I_rep | median unbounded Brody q | % I_rep<0 | % q<0 | verdict |",
         "|---|---|---|---|---|---|---|"]
    rng = np.random.default_rng(SEED + 11)
    allok = True
    for name, loader in LOADERS.items():
        ireps, brodys = [], []
        for i, (cid, spk) in enumerate(loader()):
            if i >= 400:            # cap: this is a gate, not a survey
                break
            try:
                ireps.append(irep_unclipped(spk))
                brodys.append(brody_unbounded(canonical_spacings(spk)))
            except Exception:
                pass
        ireps = np.array([x for x in ireps if not np.isnan(x)])
        brodys = np.array([x for x in brodys if not np.isnan(x)])
        if ireps.size < 10:
            L.append(f"| {name} | {ireps.size} | — | — | — | — | *insufficient* |"); continue
        fn = float(np.mean(ireps < 0)); fq = float(np.mean(brodys < 0))
        v = "**CLUSTERED** ✓" if (fn > 0.5 and fq > 0.5) else "*** DOES NOT REPRODUCE ***"
        if not (fn > 0.5 and fq > 0.5):
            allok = False
        L.append(f"| **{name}** | {ireps.size} | **{np.median(ireps):+.4f}** | "
                 f"**{np.median(brodys):+.4f}** | {fn:.0%} | {fq:.0%} | {v} |")
    L += ["", ("## GATE: **PASS** — the census reproduces on the repaired axes, now as a graded measurement."
               if allok else
               "## GATE: **FAIL — the census does NOT reproduce. STOP AND RE-READ VERDICT_B.**")]
    write("VERDICT_C.md", "\n".join(L))


# ───────────────────────────────────────────────────────────────────── JOB D
def job_D(per_sub):
    """Row 3: the first correlational (order-domain) measurement in the project's history."""
    from loaders import LOADERS
    L = ["# VERDICT D — the row-3 instrument (the one that has never existed)", "",
         f"git SHA `{sha()}` · seed {SEED}", "",
         "**No pre-committed verdict.** This is the first order-domain data the project has ever had;",
         "pretending otherwise would be laundering. It is here because it is nearly free once Job A's",
         "shuffles exist, and because Job A's UNRESOLVED branch routes straight into it.", "",
         "`ρ₁` = ISI serial correlation (lag-1). **Order-dependent by construction** — it is *exactly*",
         "the thing the shuffle destroys.", "",
         "## The 3×2 matrix — predictor domain × axis domain", "",
         "| predictor (domain) | ρ vs ks_gue (**marginal** axis) | ρ vs LV (**local-marginal** axis) | ρ vs ρ₁ (**correlational** axis) |",
         "|---|---|---|---|"]
    rng = np.random.default_rng(SEED + 13)
    per = {}
    for name, loader in LOADERS.items():
        rows = []
        for i, (cid, spk) in enumerate(loader()):
            if i >= 600:
                break
            isi = np.diff(spk); isi = isi[isi > 0]
            if isi.size < 200:
                continue
            r1 = float(stats.spearmanr(isi[:-1], isi[1:])[0])
            rows.append(dict(rho1=r1, burst=float(np.mean(isi < 0.010)),
                             cv=float(np.std(isi) / np.mean(isi)),
                             logcv=float(np.std(np.log(isi)))))
        per[name] = rows
    with open(os.path.join(OUT, "jobD_row3.json"), "w") as f:
        json.dump(per, f, cls=NpEnc)
    A = per.get("allen-hpf-cell", [])
    jobA = per_sub.get("allen-hpf-cell", []) if per_sub else []
    if len(A) > 20:
        L.append(f"| **ISI serial corr ρ₁** (allen-hpf, n={len(A)}) | — | — | — |")
        L.append("")
        L.append(f"**Allen-HPF median ρ₁ = {np.median([r['rho1'] for r in A]):+.4f}** "
                 f"(a nonzero ρ₁ is *prima facie* order structure the shuffle destroys).")
        L.append("")
        L.append(f"- ρ(burst, ρ₁) = **{boot_ci([r['burst'] for r in A], [r['rho1'] for r in A], seed=5)[0]:+.3f}**")
        L.append(f"- ρ(log-ISI CV, ρ₁) = **{boot_ci([r['logcv'] for r in A], [r['rho1'] for r in A], seed=6)[0]:+.3f}**")
    L += ["", "**Diagonal cells are definitionally warm — say so.** The off-diagonal is where findings live.",
          "The Allen dissociation is an off-diagonal cell, which is exactly why it was interesting and",
          "exactly why its domain labels had to be right."]
    write("VERDICT_D.md", "\n".join(L))


# ────────────────────────────────────────────────────────────────────── main
def main():
    t0 = time.time()
    log(f"OVERNIGHT 2026-07-12 START · git {sha()} · seed {SEED}")
    write("RUN_STARTED.md", f"git SHA `{sha()}`\nseed {SEED}\nstart {time.ctime()}\n")

    try:
        job_gate()
    except Exception:
        write("VERDICT_GATE.md", f"# GATE — FAILED\n\n```\n{traceback.format_exc()}\n```\n")

    per_sub = {}
    try:
        per_sub = job_A()
    except Exception:
        write("VERDICT_A.md", "# VERDICT A — **JOB FAILED**\n\n"
              "**This is a FAILURE, not a null.** Do not read it as 'no effect'.\n\n"
              f"```\n{traceback.format_exc()}\n```\n")

    passed = False
    try:
        passed = job_B()
    except Exception:
        write("VERDICT_B.md", "# VERDICT B — **JOB FAILED**\n\n"
              "**This is a FAILURE, not a null.** Jobs C/D skipped.\n\n"
              f"```\n{traceback.format_exc()}\n```\n")

    if passed:
        for j, fn in ((job_C, "VERDICT_C.md"), (job_D, "VERDICT_D.md")):
            try:
                j(per_sub)
            except Exception:
                write(fn, f"# **JOB FAILED**\n\n**A FAILURE, not a null.**\n\n```\n{traceback.format_exc()}\n```\n")
    else:
        for fn in ("VERDICT_C.md", "VERDICT_D.md"):
            write(fn, "# SKIPPED — Job B's clustered-calibrator gate did not pass.\n\n"
                      "**Pre-committed:** if the clustered class fails its own reading, the REPAIR is wrong,\n"
                      "not the class. C and D do not run. Read VERDICT_B.md.\n")

    log(f"OVERNIGHT DONE in {(time.time()-t0)/60:.1f} min")
    write("RUN_FINISHED.md", f"finished {time.ctime()}\nelapsed {(time.time()-t0)/60:.1f} min\n")


if __name__ == "__main__":
    main()
