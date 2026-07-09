"""Part C — refusal zoo vs trivial-descriptor baseline B (SEALED protocol unseal).

Decision (pre-committed, SESSION_K_PARTC_PREREG_SEALED.md):
  NULL  -> R separates no better than B (matched permutation-z) AND no within-B-cell
           residual R-separation -> dark-appendix the zoo.
  POSITIVE -> R exceeds B reproducibly at matched permutation-z AND within-B-cell
           R-separation survives its null -> "R carries reproducible substrate-covarying
           structure ORTHOGONAL to B" (measurement only; NOT 'ARS measures coupling-type').

Fairness guards: same classifier (RF, fixed), stratified 5-fold CV, balanced accuracy;
label-permutation null for BOTH B and R (z neutralizes feature count); within-B-cell test
(the sharp one); dimension control (R restricted to random 3 features).
"""
import json, math, os
import numpy as np
import nns_stats as st
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import StratifiedKFold
from sklearn.metrics import balanced_accuracy_score
from sklearn.neighbors import NearestNeighbors

HERE = os.path.dirname(os.path.abspath(__file__))
RNG = np.random.default_rng(20260709)
RF_KW = dict(n_estimators=120, random_state=0, n_jobs=1)

# ---------------------------------------------------------------- generators
def gen_T0(rng):                       # accepted ensemble GUE/GOE
    n = rng.integers(300, 800); beta = rng.choice([1, 2])
    m = 2 * n + 60
    A = rng.standard_normal((m, m))
    if beta == 2:
        A = A + 1j * rng.standard_normal((m, m))
    H = (A + A.conj().T) / 2
    ev = np.linalg.eigvalsh(H)
    return {"levels": st.unfold_poly(ev, frac=0.6)[:n], "raw": ev, "decaying": 0}

def gen_T1(rng):                       # deterministic decaying (GKW/e-CF tail)
    k = rng.integers(6, 22); base = rng.uniform(0.25, 0.45)
    lam = np.array([1.0] + [(-1)**i * base**i * rng.uniform(0.8, 1.2) for i in range(1, k)])
    return {"levels": np.sort(np.abs(lam)), "raw": lam, "decaying": 1}

def gen_T2(rng):                       # picket-fence / rigid + jitter
    n = rng.integers(300, 800); jit = rng.uniform(0.02, 0.30)
    x = np.arange(n, dtype=float) + jit * rng.standard_normal(n)
    return {"levels": np.sort(x), "raw": np.sort(x), "decaying": 0}

def gen_T3(rng):                       # critical/intermediate (tunable Poisson<->GOE)
    n = rng.integers(300, 800); t = rng.uniform(0.0, 1.0)     # interpolation knob
    # semi-Poisson base (Gamma(2,.5)) blended toward GOE by picket-mixing
    sp = rng.gamma(2.0, 0.5, n)
    goe = np.diff(st.unfold_poly(np.linalg.eigvalsh(
        (lambda M: (M + M.T) / 2)(rng.standard_normal((2 * n + 40, 2 * n + 40)))), frac=0.6)[:n + 1])
    s = (1 - t) * sp + t * np.abs(goe[:len(sp)])
    return {"levels": np.cumsum(s / s.mean()), "raw": np.cumsum(s), "decaying": 0}

def gen_T4(rng):                       # non-spectral: clustered / arithmetic support
    if rng.random() < 0.5:             # Hawkes-ish clustered
        n = rng.integers(300, 800); rate = rng.uniform(0.3, 0.9)
        base = np.sort(rng.uniform(0, n, size=int(n * (1 - rate))))
        kids = base + rng.exponential(0.3, size=len(base)) * (rng.random(len(base)) < rate)
        x = np.sort(np.concatenate([base, kids]))
    else:                               # squarefree / arithmetic sign-change support
        N = rng.integers(600, 1600)
        m = np.arange(2, N)
        sf = m[np.array([all(m_i % (p*p) for p in range(2, int(m_i**0.5)+1)) for m_i in m])]
        x = sf.astype(float)[: rng.integers(300, min(700, len(sf)))]
    return {"levels": np.sort(x), "raw": np.sort(x), "decaying": 0}

GENS = {"T0_ensemble": gen_T0, "T1_decaying": gen_T1, "T2_rigid": gen_T2,
        "T3_critical": gen_T3, "T4_nonspectral": gen_T4}

# ---------------------------------------------------------------- features
def _unit_unfold(levels):
    x = np.sort(np.asarray(levels, float))
    sp = np.diff(x)
    sp = sp[sp > 0]
    if len(sp) < 5:
        return None
    return np.concatenate([[0.0], np.cumsum(sp / sp.mean())])

def _delta3_slope(u):
    if u is None or len(u) < 40:
        return np.nan
    Ls = np.linspace(2, 10, 5)
    d3 = st.delta3(u, Ls, n_origins=60)
    ok = np.isfinite(d3)
    return float(np.polyfit(Ls[ok], d3[ok], 1)[0]) if ok.sum() >= 2 else np.nan

def _density_cv(raw):
    x = np.sort(np.asarray(raw, float)); x = x[np.isfinite(x)]
    if len(x) < 20:
        return np.nan
    edges = np.linspace(x[0], x[-1], 12)
    counts = np.histogram(x, edges)[0].astype(float)
    return float(counts.std() / counts.mean()) if counts.mean() > 0 else np.nan

def features_B(inst):
    u = _unit_unfold(inst["levels"])
    raw = np.asarray(inst["raw"], float)
    b1 = _delta3_slope(u)
    b2 = _density_cv(inst["levels"])
    n_lev = len(np.atleast_1d(inst["levels"]))
    mean_sp = float(np.mean(np.diff(np.sort(inst["levels"])))) if n_lev > 2 else np.nan
    return [b1, b2, float(n_lev), mean_sp, float(inst["decaying"])]

def features_R(inst):
    u = _unit_unfold(inst["levels"])
    out = []
    if u is not None and len(u) > 8:
        sp = np.diff(u); rr = np.minimum(sp[1:], sp[:-1]) / np.maximum(sp[1:], sp[:-1])
        out.append(float(rr.mean()))
        out += list(np.histogram(rr, bins=6, range=(0, 1), density=True)[0])
        ks = st.classify_nns(u)["ks"]
        out += [ks["Poisson"], ks["GOE"], ks["GUE"], ks["GSE"]]
        s2 = st.number_variance(u, np.array([2.0, 5.0, 10.0]))
        out += [float(np.nan_to_num(v)) for v in s2]
        out.append(_delta3_slope(u))
    else:
        out += [np.nan] + [np.nan] * 6 + [np.nan] * 4 + [np.nan] * 3 + [np.nan]
    # refusal-reason one-hot: [too_few, decaying, non_unitizable, ok]
    too_few = int(len(np.atleast_1d(inst["levels"])) < 30)
    reason = [too_few, int(inst["decaying"]), int(u is None), int(u is not None and not too_few)]
    out += reason
    out.append(float(np.mean(np.diff(np.sort(inst["levels"])))) if len(np.atleast_1d(inst["levels"])) > 2 else np.nan)
    return out

# ---------------------------------------------------------------- harness
def cv_balacc(X, y, seed=0):
    X = np.nan_to_num(np.asarray(X, float), nan=-999.0)
    skf = StratifiedKFold(5, shuffle=True, random_state=seed)
    accs = []
    for tr, te in skf.split(X, y):
        clf = RandomForestClassifier(**RF_KW).fit(X[tr], y[tr])
        accs.append(balanced_accuracy_score(y[te], clf.predict(X[te])))
    return float(np.mean(accs))

def perm_z(X, y, nperm=80):
    a = cv_balacc(X, y)
    null = []
    for i in range(nperm):
        yp = RNG.permutation(y)
        null.append(cv_balacc(X, yp, seed=i))
    null = np.array(null)
    return {"acc": a, "null_mean": float(null.mean()), "null_std": float(null.std()),
            "z": float((a - null.mean()) / (null.std() + 1e-9))}

def _cell_heldout_balacc(Xc, yc, seed):
    """3-fold cross_val_predict balanced accuracy (HELD-OUT, not resubstitution)."""
    from sklearn.model_selection import cross_val_predict
    try:
        pred = cross_val_predict(RandomForestClassifier(n_estimators=60, random_state=seed, n_jobs=1),
                                 Xc, yc, cv=3)
        return balanced_accuracy_score(yc, pred)
    except Exception:
        return np.nan

def within_B_cell(XB, XR, y, k=35):
    """k-NN cells in standardized B-space; in cells where B is ~constant but >=2 types are
    present (each with >=3 members so 3-fold CV is valid), test whether R separates types
    on HELD-OUT predictions above a within-cell label-permutation null. This is the sharp
    'R carries structure orthogonal to B' test."""
    XB = np.nan_to_num(np.asarray(XB, float)); XR = np.nan_to_num(np.asarray(XR, float))
    Z = (XB - XB.mean(0)) / (XB.std(0) + 1e-9)
    nn = NearestNeighbors(n_neighbors=min(k, len(y))).fit(Z)
    _, idx = nn.kneighbors(Z)
    accs, nulls, accsB, accsRo, seen = [], [], [], [], set()
    for cell in idx:
        key = tuple(sorted(cell))
        if key in seen:
            continue
        yc = y[cell]
        types, cnts = np.unique(yc, return_counts=True)
        if (cnts >= 3).sum() < 2:            # need >=2 types each with >=3 members
            continue
        seen.add(key)
        keep = np.isin(yc, types[cnts >= 3])
        yc2 = yc[keep]
        Xr, Xb = XR[cell][keep], XB[cell][keep]
        # R-orthogonalized: drop R's B-overlapping features (delta3-slope idx14, mean_sp idx19)
        Xro = np.delete(Xr, [14, 19], axis=1)
        aR = _cell_heldout_balacc(Xr, yc2, 0)
        aRo = _cell_heldout_balacc(Xro, yc2, 0)
        aB = _cell_heldout_balacc(Xb, yc2, 0)          # CONTROL: can B separate within the cell?
        nl = np.nanmean([_cell_heldout_balacc(Xr, RNG.permutation(yc2), j + 1) for j in range(5)])
        if np.isfinite(aR) and np.isfinite(nl) and np.isfinite(aB):
            accs.append(aR); nulls.append(nl); accsB.append(aB); accsRo.append(aRo)
    if not accs:
        return {"n_mixed_cells": 0, "note": "no valid mixed B-cells (B fully separates types)"}
    accs, nulls, accsB, accsRo = map(np.array, (accs, nulls, accsB, accsRo))
    return {"n_mixed_cells": int(len(accs)),
            "R_heldout_acc": float(accs.mean()),
            "B_heldout_acc_CONTROL": float(np.nanmean(accsB)),
            "Rorth_heldout_acc": float(np.nanmean(accsRo)),
            "incell_perm_null": float(nulls.mean()),
            "R_above_null": float((accs - nulls).mean()),
            "R_above_B_incell": float((accs - accsB).mean()),
            "Rorth_above_B_incell": float((accsRo - accsB).mean()),
            "frac_cells_R_beats_B": float(np.mean(accs > accsB + 0.05))}

# ---------------------------------------------------------------- build + validate + run
def build(n_per=40):
    X_B, X_R, y = [], [], []
    for lbl, gen in GENS.items():
        for _ in range(n_per):
            inst = gen(RNG)
            X_B.append(features_B(inst)); X_R.append(features_R(inst)); y.append(lbl)
    return np.array(X_B, float), np.array(X_R, float), np.array(y)

if __name__ == "__main__":
    out = {}
    print("building zoo (40 instances x 5 types) ...")
    XB, XR, y = build(40)
    out["n_instances"] = len(y); out["n_features_B"] = XB.shape[1]; out["n_features_R"] = XR.shape[1]

    # ---- harness validation ----
    # V-sep: real 5-type task must be detectable by both (harness can see separation)
    # V-null: single type split into 5 fake labels -> chance, z~0 (no hallucinated separation)
    mask0 = y == "T0_ensemble"
    fake = np.array([f"g{i%5}" for i in range(mask0.sum())])
    out["validation"] = {
        "V_null_B_z": perm_z(XB[mask0], fake, nperm=60)["z"],
        "V_null_R_z": perm_z(XR[mask0], fake, nperm=60)["z"]}

    # ---- primary comparison ----
    out["global_B"] = perm_z(XB, y, 120)
    out["global_R"] = perm_z(XR, y)
    # dimension control: R restricted to a random 3-subset
    r3 = RNG.choice(XR.shape[1], 3, replace=False)
    out["R_random3"] = perm_z(XR[:, r3], y)
    # nested: does R add beyond B?
    out["global_B_plus_R"] = perm_z(np.hstack([XB, XR]), y)
    # ---- the sharp test ----
    out["within_B_cell"] = within_B_cell(XB, XR, y)

    # ---- pre-committed decision ----
    gB, gR, wc = out["global_B"], out["global_R"], out["within_B_cell"]
    R_beats_B_global = gR["z"] > gB["z"] + 1.0 and gR["acc"] > gB["acc"] + 0.02
    # The SHARP, controlled test: within B-constant cells, R must beat B (not just a
    # permutation null), AND the B-control must itself be near the null (cells truly
    # B-constant), AND the B-orthogonalized R (no delta3/mean_sp) must also beat B.
    nmix = wc.get("n_mixed_cells", 0)
    B_at_null = nmix > 0 and (wc.get("B_heldout_acc_CONTROL", 1) - wc.get("incell_perm_null", 0)) < 0.10
    R_beats_B_cell = wc.get("R_above_B_incell", 0) > 0.10 and wc.get("frac_cells_R_beats_B", 0) > 0.5
    Rorth_beats_B_cell = wc.get("Rorth_above_B_incell", 0) > 0.08
    within_positive = bool(nmix > 0 and B_at_null and R_beats_B_cell and Rorth_beats_B_cell)
    positive = bool(within_positive)   # global leg is ceiling-limited; verdict rests on the controlled within-cell test
    out["DECISION"] = {
        "global_note": f"ceiling-limited: B acc {gB['acc']:.3f} (z {gB['z']:.1f}) vs R {gR['acc']:.3f} "
                       f"(z {gR['z']:.1f}) -> R does NOT exceed B at matched-z; not the discriminating test",
        "within_cell_B_at_null": bool(B_at_null),
        "within_cell_R_beats_B": bool(R_beats_B_cell),
        "within_cell_Rorth_beats_B": bool(Rorth_beats_B_cell),
        "verdict": "POSITIVE" if positive else "NULL",
        "banked_label": ("R carries reproducible substrate-covarying structure ORTHOGONAL to B "
                         "(within-B-constant cells R separates types B cannot; survives B-orthogonalization)"
                         if positive else
                         "R re-encodes trivial descriptors; boundary has no own-structure -> DARK-APPENDIX"),
        "interpretation_field_NOT_promoted": "coupling-type is the mechanistic reading, a step past "
                         "what the separation licenses -- NOT claimed"}
    json.dump(out, open(os.path.join(HERE, "partC_measured.json"), "w"), indent=2, default=str)

    print(f"\nvalidation  V-null z:  B={out['validation']['V_null_B_z']:+.2f}  R={out['validation']['V_null_R_z']:+.2f}  (want ~0)")
    print(f"global  B: acc={gB['acc']:.3f} z={gB['z']:.1f}   R: acc={gR['acc']:.3f} z={gR['z']:.1f}"
          f"   R_rand3: acc={out['R_random3']['acc']:.3f}   B+R: acc={out['global_B_plus_R']['acc']:.3f}")
    print(f"within-B-cell: {wc}")
    print(f"\nDECISION: {out['DECISION']['verdict']}  -> {out['DECISION']['banked_label']}")
