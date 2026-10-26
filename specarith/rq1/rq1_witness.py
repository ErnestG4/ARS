"""RQ1 B2 witness (round 88, TOOLKIT §9.D). Synthetic, mirror-symmetrised sets at the archives' matched N
(N = 2n, n = 227,524,967 at 10¹⁰ and 2,059,026,114 at 10¹¹: the ℤ[√2] manifest row counts; no angle is read).
Every set is n points φ ∈ [0, ½) plus their mirrors 1 − φ, sorted: the archives' structure (θ ≤ ½ stored, 1 − θ
added). The estimator (rq1_read.var_stream), K = round(N^β), the gated cells (rq1_read.GATED) and the rule
(rq1_read.b2_rule) are the read's own.

NULL (false PASS rate). Two independent sets per replicate ("zs2", "zi"), each φ i.i.d. uniform. Nested as the data
are: the 10¹⁰ set is a uniformly random size-n₁₀ subset of the 10¹¹ set's φ (any fixed subset of i.i.d. points is
i.i.d.; the data's 10¹⁰ set is the first n₁₀ primes of the 10¹¹ set). So the gated cells are correlated as in the
read: across β (same data) and across X (nesting). No independence is assumed; the rate is measured.

PLANTED (power). Each set is a mixture: a rigid lattice fraction ρ (points (j + ½)/(2m), j < m = round(ρn), a
mirror-symmetric lattice of 2m points) and n − m i.i.d. points; R ≈ 1 − ρ at every K (the lattice's count variance is
≤ ¼, against N/K ≥ 10⁵). The "zs2" set has ρ_zs2 = ρ_zi − ΔR_X, so it sits above "zi" by ΔR_X by construction.
- ΔR_X = the smallest heuristic offset over the gated β at that X (min of the L = log X and L = log N variants,
  results/HEURISTIC_B_MIRROR.json): the heuristic size, taken at its smallest gated value.
- ρ_zi = 1 − (largest heuristic R_ℤ[i] over the gated cells), so the planted level is as high as the heuristic's
  (SE ∝ R: conservative).
- The 10¹⁰ and 10¹¹ planted sets are generated independently (a random subset of a lattice is not rigid). Independence
  across X gives the conjunction a lower PASS probability than positive correlation would: conservative for power.

CRITERIA (declared before running; committed with this file):
- NULL: 100 replicates. The B2 rule's false PASS count must be ≤ 10 (rate ≤ 0.10).
  A priori (not a criterion): each gated sign is a fair coin under the null; if the β = 0.40 / 0.45 signs correlate at
  0.3–0.6 within an X and the two X are nearly independent, the rate is ≈ 0.09–0.12, so the null arm may land near
  its threshold.
- PLANTED: 100 replicates. The rule must read PASS in ≥ 90.
- Witness OK iff both hold. Witness failure → the read is VOID (round 88). Superseded by round 89 (below): the
  round-88 summary is still written and reported, but the read's rule and its witness are the round-89 ones.
- Reported, not gated: the empirical SD of R per field and cell, and of D per cell, against the sealed model
  R·sqrt(2/(c K)) and SE_diff; the mean planted D against ΔR_X; the null's per-cell positive fractions and the
  pairwise sign agreement between gated cells.

ROUND 89 (declared before any witness result is read; committed with this file). The rule becomes a margin rule,
D > k·s·SE_diff at every remaining gated cell (rq1_read.b2_rule; SE_diff the sealed model on each replicate's own R).
- SE check (select): per gated cell and arm, empirical SE_diff = the SD of D over the 100 replicates; model = the mean
  of the replicates' model SE_diff. ratio = empirical / model, the larger over the two arms. If ratio > 1.2 at any
  gated cell, every gated cell's offset/SE (HEURISTIC_B_MIRROR.json) is recomputed from the empirical SE (divided by
  its ratio); cells below 2 become UNPOWERED, and the remaining cells' rule uses s = ratio (the empirical SE). Else
  s = 1 at every cell.
- Selection (select, no new compute): the round-88 replicates re-scored at k ∈ {0, 0.5, 1.0, 1.5} on the remaining
  cells; chosen k = the smallest with null false PASS ≤ 5 and planted PASS ≥ 90 (of 100). None → B2 UNPOWERED.
- Confirmation (confirm): 100 fresh null and 100 fresh planted replicates (seed base 8889 instead of 8888; the same
  sets, N and planted parameters as round 88), scored at the selected rule; OK iff null false PASS ≤ 5 and planted
  PASS ≥ 90. Fail → B2 UNPOWERED (descriptive read, no verdict).
- Symmetrisation: in both arms every set is n points φ plus their n mirrors 1 − φ; in planted_set the n − m i.i.d.
  points and the m lattice points are merged into the first half and the whole half is mirrored, so the i.i.d. part
  is n − m points plus their mirrors, as in the null arm.

  python rq1_witness.py jobs                                  task list (ARM REP), null and planted interleaved
  python rq1_witness.py task ARM REP OUT_DIR [SEED_BASE]      one replicate → OUT_DIR/{null,planted}_REP.json
  python rq1_witness.py summary OUT_DIR OUT_JSON              round-88 summary (sign rule)
  python rq1_witness.py select OUT_DIR OUT_JSON               round 89: SE check, re-gating, selection table, k
  python rq1_witness.py confirm CONF_DIR SELECTION_JSON OUT_JSON
"""
import hashlib
import json
import math
import os
import sys
import time
from concurrent.futures import ThreadPoolExecutor

import numpy as np
from numba import njit

import rq1_read as Q

N_SPLIT = {10 ** 10: 227524967, 10 ** 11: 2059026114}
N_REP = 100
NULL_MAX_PASS = 10
PLANTED_MIN_PASS = 90
K_GRID = [0.0, 0.5, 1.0, 1.5]          # round 89
SEL_NULL_MAX_PASS = 5
SEL_PLANTED_MIN_PASS = 90
SE_RATIO_MAX = 1.2
OFFSET_SE_MIN = 2.0
CONFIRM_SEED_BASE = 8889
HEUR = "results/HEURISTIC_B_MIRROR.json"
XL = {10 ** 10: "1e10", 10 ** 11: "1e11"}


def planted_params():
    h = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), HEUR)))
    dR, rzi = {}, 0.0
    for X in Q.XS:
        rows = {r["beta"]: r for r in h["rows"][XL[X]]["rows"]}
        offs = []
        for b in Q.GATED[X]:
            hh = rows[b]["heuristic"]
            offs.append(min(hh["logX"]["offset"], hh["logN"]["offset"]))
            rzi = max(rzi, hh["logX"]["R_zi"], hh["logN"]["R_zi"])
        dR[X] = min(offs)
    rho_zi = 1.0 - rzi
    return dict(rho_zi=rho_zi, rho_zs2={X: rho_zi - dR[X] for X in Q.XS}, dR=dR, c_used=h["c_used"])


def mirror_into(buf, n):
    np.subtract(1.0, buf[:n][::-1], out=buf[n:2 * n])


@njit(cache=False)
def _select_s(src, k, seed, out):
    """Knuth's selection sampling (Algorithm S): item t is kept with probability (k − kept)/(n − t); exactly k kept,
    every size-k subset equally likely, order preserved. numba's own generator, seeded from the task's rng."""
    np.random.seed(seed)
    n = src.shape[0]
    kept = 0
    for t in range(n):
        if (n - t) * np.random.random() < k - kept:
            out[kept] = src[t]
            kept += 1
            if kept == k:
                break
    return kept


def select_sorted(src, k, rng):
    """A uniformly random size-k subset of the sorted array src, in order. (Round 88 fix: the first version split k
    over chunks with rng.multivariate_hypergeometric, which refuses populations ≥ 10⁹; it failed on spot before any
    replicate completed.)"""
    out = np.empty(k, np.float64)
    assert _select_s(src, k, int(rng.integers(2 ** 32)), out) == k
    return out


@njit(cache=False, nogil=True)
def merge_lattice(iid, m, out):
    """out[:len(iid) + m] = sorted union of iid (sorted) and the lattice (j + ½)/(2m), j < m."""
    i, j, ni = 0, 0, iid.shape[0]
    M2 = 2.0 * m
    for t in range(ni + m):
        lat = (j + 0.5) / M2 if j < m else 2.0
        if i < ni and iid[i] <= lat:
            out[t] = iid[i]
            i += 1
        else:
            out[t] = lat
            j += 1


def cells(th, X, pool):
    N = len(th)
    Ks = [int(round(N ** b)) for b in Q.GATED[X]]
    vs = list(pool.map(lambda K: Q.var_stream(th, K), Ks))
    return {str(b): dict(K=K, R=v / (N / K)) for b, K, v in zip(Q.GATED[X], Ks, vs)}


def null_set(rng, pool, tm):
    n10, n11 = N_SPLIT[10 ** 10], N_SPLIT[10 ** 11]
    buf = np.empty(2 * n11, np.float64)
    t = time.time()
    Q.sorted_uniform(n11, rng, out=buf[:n11], scale=0.5)
    tm["gen"] += time.time() - t
    t = time.time()
    sub = select_sorted(buf[:n11], n10, rng)
    s2 = np.empty(2 * n10, np.float64)
    s2[:n10] = sub
    del sub
    mirror_into(s2, n10)
    tm["select"] += time.time() - t
    t = time.time()
    r10 = cells(s2, 10 ** 10, pool)
    del s2
    tm["var10"] += time.time() - t
    t = time.time()
    mirror_into(buf, n11)
    tm["mirror"] += time.time() - t
    t = time.time()
    r11 = cells(buf, 10 ** 11, pool)
    tm["var11"] += time.time() - t
    del buf
    return {"1e10": r10, "1e11": r11}


def planted_set(rng, pool, rho, tm):
    out = {}
    for X in Q.XS:
        n = N_SPLIT[X]
        m = int(round(rho[X] * n))
        buf = np.empty(2 * n, np.float64)
        t = time.time()
        Q.sorted_uniform(n - m, rng, out=buf[n:2 * n - m], scale=0.5)
        merge_lattice(buf[n:2 * n - m], m, buf[:n])
        mirror_into(buf, n)
        tm["gen"] += time.time() - t
        t = time.time()
        out[XL[X]] = cells(buf, X, pool)
        tm["var11" if X == 10 ** 11 else "var10"] += time.time() - t
        del buf
    return out


def task(arm, rep, out_dir, seed_base=8888):
    path = os.path.join(out_dir, f"{arm}_{rep:03d}.json")
    if os.path.exists(path):
        return 0
    rng = np.random.default_rng([seed_base, 0 if arm == "null" else 1, rep])
    tm = dict(gen=0.0, select=0.0, var10=0.0, mirror=0.0, var11=0.0)
    t0 = time.time()
    res = dict(arm=arm, rep=rep, seed_base=seed_base, sets={})
    pp = planted_params()
    with ThreadPoolExecutor(max(len(v) for v in Q.GATED.values())) as pool:
        for f in ("zs2", "zi"):
            if arm == "null":
                res["sets"][f] = null_set(rng, pool, tm)
            else:
                rho = pp["rho_zs2"] if f == "zs2" else {X: pp["rho_zi"] for X in Q.XS}
                res["sets"][f] = planted_set(rng, pool, rho, tm)
    D = {(X, b): res["sets"]["zs2"][XL[X]][str(b)]["R"] - res["sets"]["zi"][XL[X]][str(b)]["R"]
         for X in Q.XS for b in Q.GATED[X]}
    res["B2"] = Q.b2_rule(D)
    res["wall_s"] = time.time() - t0
    res["cpu_s"] = time.process_time()
    res["timing"] = tm
    tmp = path + f".{os.getpid()}.part"
    json.dump(res, open(tmp, "w"), indent=1, sort_keys=True)
    os.replace(tmp, path)
    print(arm, rep, res["B2"], round(res["wall_s"], 1), round(res["cpu_s"], 1), flush=True)
    return 0


def summary(out_dir, out):
    pp = planted_params()
    c = pp["c_used"]
    res = dict(label="RQ1 B2 witness (round 88, §9.D); synthetic only", criteria=dict(
        replicates=N_REP, null_max_pass=NULL_MAX_PASS, planted_min_pass=PLANTED_MIN_PASS),
        planted_params=dict(rho_zi=pp["rho_zi"], rho_zs2={XL[X]: v for X, v in pp["rho_zs2"].items()},
                            dR={XL[X]: v for X, v in pp["dR"].items()}), c_used=c, gated={XL[X]: v for X, v in Q.GATED.items()})
    cellkeys = [(XL[X], str(b)) for X in Q.XS for b in Q.GATED[X]]
    for arm in ("null", "planted"):
        reps = [json.load(open(os.path.join(out_dir, f"{arm}_{r:03d}.json"))) for r in range(N_REP)]
        npass = sum(r["B2"] == "PASS" for r in reps)
        se = {}
        for xl, b in cellkeys:
            K = reps[0]["sets"]["zs2"][xl][b]["K"]
            Rs = {f: np.array([r["sets"][f][xl][b]["R"] for r in reps]) for f in ("zs2", "zi")}
            D = Rs["zs2"] - Rs["zi"]
            mod = {f: float(Rs[f].mean() * math.sqrt(2 / (c * K))) for f in Rs}
            se[f"{xl} b={b}"] = dict(
                K=K, R_mean={f: float(v.mean()) for f, v in Rs.items()},
                R_sd_emp={f: float(v.std(ddof=1)) for f, v in Rs.items()}, R_sd_model=mod,
                D_mean=float(D.mean()), D_sd_emp=float(D.std(ddof=1)),
                SE_diff_model=float(math.hypot(mod["zs2"], mod["zi"])),
                frac_D_positive=float((D > 0).mean()))
        entry = dict(pass_count=int(npass), cells=se,
                     cpu_core_h=float(sum(r["cpu_s"] for r in reps) / 3600),
                     wall_h_sum=float(sum(r["wall_s"] for r in reps) / 3600))
        if arm == "null":
            sg = {k: np.array([r["sets"]["zs2"][k[0]][k[1]]["R"] > r["sets"]["zi"][k[0]][k[1]]["R"] for r in reps])
                  for k in cellkeys}
            entry["sign_agreement"] = {f"{a[0]} b={a[1]} vs {b[0]} b={b[1]}": float((sg[a] == sg[b]).mean())
                                       for i, a in enumerate(cellkeys) for b in cellkeys[i + 1:]}
            entry["OK"] = bool(npass <= NULL_MAX_PASS)
        else:
            entry["OK"] = bool(npass >= PLANTED_MIN_PASS)
        res[arm] = entry
    res["OK"] = bool(res["null"]["OK"] and res["planted"]["OK"])
    json.dump(res, open(out, "w"), indent=1, sort_keys=True)
    print("null false PASS", res["null"]["pass_count"], "planted PASS", res["planted"]["pass_count"], "OK", res["OK"])
    return 0


CELLS = [(X, b) for X in Q.XS for b in Q.GATED[X]]


def load_reps(out_dir, seed_base):
    reps = {arm: [json.load(open(os.path.join(out_dir, f"{arm}_{r:03d}.json"))) for r in range(N_REP)]
            for arm in ("null", "planted")}
    for arm, rs in reps.items():
        assert all(r.get("seed_base", 8888) == seed_base for r in rs), (out_dir, arm)
    return reps


def rep_D_SE(r):
    """{(X, β): D}, {(X, β): model SE_diff} for one replicate (rq1_read.se_diff on its own R values)."""
    D, SE = {}, {}
    for X, b in CELLS:
        a, c = r["sets"]["zs2"][XL[X]][str(b)], r["sets"]["zi"][XL[X]][str(b)]
        D[(X, b)] = a["R"] - c["R"]
        SE[(X, b)] = Q.se_diff(a["R"], c["R"], a["K"])
    return D, SE


def count_pass(rs, rule):
    return int(sum(Q.b2_rule(*rep_D_SE(r), rule) == "PASS" for r in rs))


def rule_json(rule):
    return dict(k=rule["k"], cells=[[X, b] for X, b in rule["cells"]],
                scale=[[X, b, rule["scale"][(X, b)]] for X, b in rule["cells"]])


def select(out_dir, out):
    """Round 89: SE check, re-gating, selection table and chosen k on the round-88 replicates (no new compute)."""
    reps = load_reps(out_dir, 8888)
    h = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), HEUR)))
    sealed = {(X, r["beta"]): r["offset_over_SE"] for X in Q.XS for r in h["rows"][XL[X]]["rows"]}
    se = {}
    for X, b in CELLS:
        e = {}
        for arm, rs in reps.items():
            ds = [rep_D_SE(r) for r in rs]
            Dv = np.array([d[0][(X, b)] for d in ds])
            mod = float(np.mean([d[1][(X, b)] for d in ds]))
            emp = float(Dv.std(ddof=1))
            e[arm] = dict(SE_diff_emp=emp, SE_diff_model=mod, ratio=emp / mod, D_mean=float(Dv.mean()))
        e["ratio"] = max(e["null"]["ratio"], e["planted"]["ratio"])
        e["offset_over_SE_sealed"] = sealed[(X, b)]
        se[(X, b)] = e
    triggered = any(e["ratio"] > SE_RATIO_MAX for e in se.values())
    for e in se.values():
        e["offset_over_SE_used"] = e["offset_over_SE_sealed"] / e["ratio"] if triggered else e["offset_over_SE_sealed"]
        e["powered"] = bool(e["offset_over_SE_used"] >= OFFSET_SE_MIN)
    cells = [c for c in CELLS if se[c]["powered"]]
    scale = {c: (se[c]["ratio"] if triggered else 1.0) for c in cells}
    table, chosen = [], None
    for k in K_GRID:
        rule = dict(k=k, cells=cells, scale=scale)
        nf = count_pass(reps["null"], rule) if cells else None
        pp = count_pass(reps["planted"], rule) if cells else None
        ok = bool(cells) and nf <= SEL_NULL_MAX_PASS and pp >= SEL_PLANTED_MIN_PASS
        table.append(dict(k=k, null_false_pass=nf, planted_pass=pp, qualifies=ok))
        if ok and chosen is None:
            chosen = k
    res = dict(label="RQ1 B2 rule selection (round 89; round-88 replicates re-scored, no new compute)",
               criteria=dict(k_grid=K_GRID, null_max_pass=SEL_NULL_MAX_PASS, planted_min_pass=SEL_PLANTED_MIN_PASS,
                             se_ratio_max=SE_RATIO_MAX, offset_over_se_min=OFFSET_SE_MIN, replicates=N_REP),
               se_check=dict(triggered=triggered, cells={f"{XL[X]} b={b}": e for (X, b), e in se.items()}),
               remaining_cells=[[X, b] for X, b in cells], table=table, chosen_k=chosen,
               rule=None if chosen is None else rule_json(dict(k=chosen, cells=cells, scale=scale)),
               B2="UNPOWERED" if chosen is None else "rule selected; confirmation pending")
    json.dump(res, open(out, "w"), indent=1, sort_keys=True)
    for t in table:
        print(t)
    print("SE check triggered", triggered, "remaining", cells, "chosen k", chosen)
    return 0


def confirm(conf_dir, sel_path, out):
    """Round 89: the selected rule on 100 fresh null and 100 fresh planted replicates (seed base 8889)."""
    sel = json.load(open(sel_path))
    assert sel["chosen_k"] is not None, "no k selected: B2 UNPOWERED, nothing to confirm"
    r = sel["rule"]
    rule = dict(k=r["k"], cells=[(X, b) for X, b in r["cells"]], scale={(X, b): s for X, b, s in r["scale"]})
    reps = load_reps(conf_dir, CONFIRM_SEED_BASE)
    nf, pp = count_pass(reps["null"], rule), count_pass(reps["planted"], rule)
    cells = {}
    for X, b in rule["cells"]:
        e = {}
        for arm, rs in reps.items():
            ds = [rep_D_SE(x) for x in rs]
            Dv = np.array([d[0][(X, b)] for d in ds])
            mod = float(np.mean([d[1][(X, b)] for d in ds]))
            e[arm] = dict(SE_diff_emp=float(Dv.std(ddof=1)), SE_diff_model=mod, ratio=float(Dv.std(ddof=1)) / mod,
                          D_mean=float(Dv.mean()))
        cells[f"{XL[X]} b={b}"] = e
    res = dict(label="RQ1 B2 rule confirmation (round 89; fresh seeds)", seed_base=CONFIRM_SEED_BASE,
               selection_sha256=hashlib.sha256(open(sel_path, "rb").read()).hexdigest(),
               rule=r, null_false_pass=nf, planted_pass=pp, cells=cells,
               criteria=dict(null_max_pass=SEL_NULL_MAX_PASS, planted_min_pass=SEL_PLANTED_MIN_PASS, replicates=N_REP),
               cpu_core_h=float(sum(x["cpu_s"] for rs in reps.values() for x in rs) / 3600),
               OK=bool(nf <= SEL_NULL_MAX_PASS and pp >= SEL_PLANTED_MIN_PASS))
    json.dump(res, open(out, "w"), indent=1, sort_keys=True)
    print("confirmation: null false PASS", nf, "planted PASS", pp, "OK", res["OK"])
    return 0


if __name__ == "__main__":
    if sys.argv[1] == "jobs":
        for r in range(N_REP):
            print("null", r)
            print("planted", r)
    elif sys.argv[1] == "task":
        sys.exit(task(sys.argv[2], int(sys.argv[3]), sys.argv[4], *(int(a) for a in sys.argv[5:6])))
    elif sys.argv[1] == "summary":
        sys.exit(summary(sys.argv[2], sys.argv[3]))
    elif sys.argv[1] == "select":
        sys.exit(select(sys.argv[2], sys.argv[3]))
    else:
        sys.exit(confirm(sys.argv[2], sys.argv[3], sys.argv[4]))
