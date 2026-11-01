"""FN1 stage 1 sealed read (FN1_SEAL.md): R_F at matched N at X = 10¹⁰ for the nine class-number-1 imaginary quadratic
fields and ℤ[√2]; rank tests against the conductor constants.

  python fn1_read.py read PINS_JSON OUT_JSON           the sealed read (mount guard, pins, seen-value guards)
  python fn1_read.py dry  PINS_JSON OUT_JSON X_DRY     §9.F rehearsal: same code; fn1 archive dirs from the pins file's
                                                       "dry" block (synthetic rows), X_DRY in place of 10¹⁰, seen-value
                                                       guards active iff X_DRY = 10¹⁰
                                                       (the seen values exist only there)

Per field: the first n rows (n = the ℤ[√2] split-prime count below X, as RQ1), θ and the mirror 1 − θ, sorted,
R(β) = var_stream(θ, K)/(N/K) with K = round(N^β), β ∈ {0.55, 0.40, 0.45}: rq1_read.var_stream, exact, Kahan, single
thread. Every segment's sha256 is checked against its manifest, and every manifest's sha256 against the pins.

Rank test per β: the ranks of R over the nine imaginary fields against the ranks of C_F (fixed order, FIELDS);
Σd² and ρ = 1 − 6Σd²/720; exact one-sided p = #{orderings with Σd² ≤ observed}/9!. PASS iff p < 0.01 and ρ > 0.
Exact ties in R → VOID (ties).
Secondary prediction (β 0.55): PASS iff R_ℚ(√−67) < R_ℤ[√2] < R_ℚ(√−163). Descriptive: the same placement at β 0.40 /
0.45; the near-equal-C pairs (−7, −8) and (ℤ[i], −19); ρ against log|D|.
Read-time noise estimate (Will, 2026-11-01; it does not use the cross-field ranking).
- For each of the nine fields, the first n rows (in prime order) are split into M = 8 contiguous segments of n // 8.
- R_seg is computed at β 0.55 with K_seg = round((2·(n // 8))^0.55).
- relSD_F = SD(R_seg)/mean(R_seg), scaled to the full N by the 1/√K law (×√(K_seg/K)), and pooled over the fields
  (63 dof).
- noise_ratio = pooled relSD / √(2/(cK)), the sealed model's relative SE.
- Primary power at that noise: R_F = b·C_F + σε, with b = 0.0411549 and σ = noise_ratio × 0.0061477 (FN1_POWER.json,
  β 0.55), 200,000 seeded simulations of the exact rule.
- Sealed interpretation: if power ≥ 0.80 a primary FAIL is informative, "near the sealed model". Otherwise a primary
  FAIL reads "FAIL (UNPOWERED at the read-time noise)", "near L13". A PASS is unaffected.
- Segments span different prime ranges, so any slow drift of R with X inflates this estimate. It is conservative
  toward calling a FAIL UNPOWERED.
Fresh-only (descriptive, UNPOWERED): ρ_s and the exact p over 7! orderings on the seven never-read w = 2 fields.
Ties: an exact tie among the compared R values → VOID (ties). There is no mid-rank handling. The C_F are all distinct.
Output: JSON with sorted keys and no timings (sidecar OUT.timing); stdout prints only "done".
"""
import hashlib
import itertools
import json
import math
import os
import sys
import time

import numpy as np

try:
    import rq1_read as Q
except ImportError:                                   # repo layout; on spot the rq1 modules are copied alongside
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "rq1"))
    import rq1_read as Q
import rq1_zw as Z
import fn1_archive as FA

X10 = 10 ** 10
BETAS = [0.55, 0.40, 0.45]
FIELDS = ["-7", "-8", "-11", "zi", "-19", "zw", "-43", "-67", "-163"]
C = dict(zip(FIELDS, [math.log(7), math.log(8), math.log(11), math.log(16), math.log(19), math.log(27),
                      math.log(43), math.log(67), math.log(163)]))
LOGD = dict(zip(FIELDS, [math.log(7), math.log(8), math.log(11), math.log(4), math.log(19), math.log(3),
                         math.log(43), math.log(67), math.log(163)]))
ALPHA = 0.01
FRESH = ["-7", "-8", "-11", "-19", "-43", "-67", "-163"]
M_SEG = 8
SEALED_B, SEALED_SE = 0.041154855674179695, 0.006147699090282484          # FN1_POWER.json, beta 0.55
C_SE = 0.6271633049515984


def sha_file(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 22), b""):
            h.update(b)
    return h.hexdigest()


def theta_fn(field):
    if field in ("zs2", "zi"):
        return lambda rows: Q.field_thetas(rows, field)
    if field == "zw":
        return Z.thetas_zw
    D = int(field)
    return lambda rows: FA.thetas(D, rows)


def load(d, field, n, pinned_sha, keep_half=False):
    mp = os.path.join(d, "MANIFEST.json")
    assert sha_file(mp) == pinned_sha, ("manifest pin", d)
    man = json.load(open(mp))
    th = np.empty(2 * n, np.float64)
    f = theta_fn(field)
    got = 0
    for s in man["segments"]:
        if got >= n:
            break
        path = os.path.join(d, f"seg_{s['k']:04d}.npy")
        assert hashlib.sha256(open(path, "rb").read()).hexdigest() == s["sha256"], path
        rows = np.load(path)[: n - got]
        t1 = f(rows)
        th[got:got + len(rows)] = t1
        th[n + got:n + got + len(rows)] = np.mod(1.0 - t1, 1.0)
        got += len(rows)
    assert got == n, ("rows", d, got, n)
    half = th[:n].copy() if keep_half else None
    th.sort()
    return (th, half) if keep_half else th


def seg_noise(half, n, K):
    ns = n // M_SEG
    Ks = int(round((2 * ns) ** 0.55))
    r = []
    for i in range(M_SEG):
        s = half[i * ns:(i + 1) * ns]
        t = np.concatenate([s, np.mod(1.0 - s, 1.0)])
        t.sort()
        r.append(float(Q.var_stream(t, Ks) / (2 * ns / Ks)))
    r = np.array(r)
    return dict(K_seg=Ks, R_seg=r.tolist(), relSD_full=float(r.std(ddof=1) / r.mean() * math.sqrt(Ks / K)))


def power_at(ratio, counts):
    C_arr = np.array([C[f] for f in FIELDS])
    d2c = max(d for d in range(len(counts)) if counts[: d + 1].sum() / counts.sum() < ALPHA)
    rng = np.random.default_rng(20261117)
    sim = SEALED_B * C_arr[None, :] + ratio * SEALED_SE * rng.standard_normal((200000, 9))
    return float((((sim.argsort(1).argsort(1) - np.arange(9)) ** 2).sum(1) <= d2c).mean())


def exact_null_counts(n=9):
    r0 = np.arange(n)
    d2 = [int(((np.array(p) - r0) ** 2).sum()) for p in itertools.permutations(range(n))]
    return np.bincount(np.array(d2))


def rank_test(Rvals, keyC, counts, fields=None):
    """Rvals: {field: R}; keyC: {field: C}. Returns Σd², ρ, exact p, verdict (over `fields`, default all nine)."""
    fields = FIELDS if fields is None else fields
    m = len(fields)
    vals = [Rvals[f] for f in fields]
    if len(set(vals)) < len(vals):
        return dict(verdict="VOID (ties)")
    rk_R = np.argsort(np.argsort(vals))
    rk_C = np.argsort(np.argsort([keyC[f] for f in fields]))
    d2 = int(((rk_R - rk_C) ** 2).sum())
    rho = 1 - 6 * d2 / (m * (m * m - 1))
    p = float(counts[: d2 + 1].sum() / counts.sum())
    return dict(sum_d2=d2, rho=rho, p_exact=p, verdict="PASS" if (p < ALPHA and rho > 0) else "FAIL",
                ranks_R=dict(zip(fields, rk_R.tolist())))


def run(pins_json, out, X, dry):
    t0 = time.time()
    pins = json.load(open(pins_json))
    assert os.path.ismount("/mnt/data"), "mount guard: /mnt/data is not mounted"
    arch = dict(pins["archives"])
    if dry:
        arch.update(pins["dry"]["archives"])
    n = Q.n_below(arch["zs2"]["dir"], X)
    N = 2 * n
    Ks = {b: int(round(N ** b)) for b in BETAS}
    res = dict(label="FN1 stage-1 read" + (" (DRY RUN: synthetic fn1 rows, not the sealed data)" if dry else ""),
               X=X, n=n, N=N, K={str(b): k for b, k in Ks.items()}, pins_sha256=sha_file(pins_json), R={})
    noise = {}
    for field in FIELDS + ["zs2"]:
        th, half = load(arch[field]["dir"], field, n, arch[field]["manifest_sha256"], keep_half=True)
        res["R"][field] = {str(b): float(Q.var_stream(th, Ks[b]) / (N / Ks[b])) for b in BETAS}
        del th
        if field in FIELDS:
            noise[field] = seg_noise(half, n, Ks[0.55])
        del half
    if X == X10:                                              # seen values: bit-identical, else VOID (also in a dry run at 10¹⁰)
        for key in ("rq1_read1", "rq1c_read1_stripped"):                     # the guard files themselves are pinned
            assert sha_file(pins["guards"][key]) == pins["guard_sha256"][key], ("guard pin", key)
        r1 = json.load(open(pins["guards"]["rq1_read1"]))["rows"][str(X)]["rows"]
        rc = json.load(open(pins["guards"]["rq1c_read1_stripped"]))["R"]
        g = {}
        for b in BETAS:
            row = [r for r in r1 if r["beta"] == b][0]
            g[str(b)] = (row["R_zs2"] == res["R"]["zs2"][str(b)] and row["R_zi"] == res["R"]["zi"][str(b)]
                         and rc[f"1e+10 zw {Ks[b]}"] == res["R"]["zw"][str(b)] and row["K"] == Ks[b])
        res["seen_value_guard"] = g
        guard_ok = all(g.values())
    else:
        guard_ok = True
        res["seen_value_guard"] = "skipped (dry run)"
    counts = exact_null_counts()
    pooled = math.sqrt(float(np.mean([noise[f]["relSD_full"] ** 2 for f in FIELDS])))
    ratio = pooled / math.sqrt(2 / (C_SE * Ks[0.55]))
    pw = power_at(ratio, counts)
    res["read_time_noise"] = dict(M=M_SEG, per_field=noise, pooled_relSD_full=pooled, noise_ratio_to_sealed_model=ratio,
                                  primary_power_at_read_noise=pw, fail_informative=bool(pw >= 0.80))
    counts7 = exact_null_counts(7)
    tests = {}
    for b in BETAS:
        Rb = {f: res["R"][f][str(b)] for f in FIELDS}
        tests[str(b)] = dict(rank_test_C=rank_test(Rb, C, counts), rank_test_logD_descriptive=rank_test(Rb, LOGD, counts),
                             fresh_only_7_descriptive_unpowered=rank_test(Rb, C, counts7, FRESH),
                             zs2_between_m67_m163=bool(Rb["-67"] < res["R"]["zs2"][str(b)] < Rb["-163"]),
                             pairs={"-7/-8": dict(dR=Rb["-8"] - Rb["-7"], dC=C["-8"] - C["-7"]),
                                    "zi/-19": dict(dR=Rb["-19"] - Rb["zi"], dC=C["-19"] - C["zi"])})
    res["tests"] = tests
    if not guard_ok:
        res["verdict"] = dict(overall="VOID (seen-value guard)")
    else:
        pv = tests["0.55"]["rank_test_C"]["verdict"]
        if pv == "FAIL" and not res["read_time_noise"]["fail_informative"]:
            pv = "FAIL (UNPOWERED at the read-time noise)"
        res["verdict"] = dict(primary_beta055=pv,
                              secondary_beta040=tests["0.4"]["rank_test_C"]["verdict"],
                              secondary_beta045=tests["0.45"]["rank_test_C"]["verdict"],
                              secondary_zs2_placement_beta055="PASS" if tests["0.55"]["zs2_between_m67_m163"] else "FAIL")
    json.dump(res, open(out, "w"), indent=1, sort_keys=True)
    open(out + ".timing", "w").write(f"wall_s {time.time() - t0:.1f}\ncpu_s {time.process_time():.1f}\n")
    print("done")
    return 0


if __name__ == "__main__":
    m = sys.argv[1]
    if m == "read":
        sys.exit(run(sys.argv[2], sys.argv[3], X10, False))
    sys.exit(run(sys.argv[2], sys.argv[3], int(float(sys.argv[4])), True))
