# SPDX-License-Identifier: AGPL-3.0-or-later
"""L13 §9.G method calibration (Will, 2026-11-03; descriptive; method and cost committed before running).

Brief (verbatim): "run methods A, B and slices on planted witnesses whose true SE is known from replicates: (i) iid
uniform angles, where the model is exact; (ii) iid angles with a planted smooth angular modulation sized to give the
observed R excess; (iii) (i) plus a planted linear and a planted quadratic drift along prime order; (iv) real primes'
order and residues with synthetic angles, with and without a planted angle–residue coupling. Report each method's
estimate ÷ the true SE in each case. The hypothesis to test: method A inflates under (ii), because angular structure
leaks into arc-based noise estimates. A method that fails its witness is recorded as invalid for L13."

**Scale.** A replicate is an ordered sequence of J = 9 slices × n = 2·10⁶ half-angles θ ∈ [0, ½); each slice is
mirror-symmetrised as in the read (N = 4·10⁶ per slice). The cells are L13's 10¹⁰ K values,
K ∈ {2,906; 7,873; 57,801; 156,616} (β 0.40, 0.45, 0.55, 0.60 at the real N). The witness N is smaller than the real
one; the SE model √(2/(cK)) depends on K only. N/K ranges from 1,376 down to 25.5.

**The three methods, exactly as L13 and the slices run apply them** (rq1_l13.py, rq1_l13_slices.py):
- **A, block arcs:** on slice 0, `var_stream_blocks(th, K, M)` → `r_se`, with M = m_primary(K) (1,000 if
  K·10⁻³ ≥ 10, else 250). M = 250 and 1,000 are both reported.
- **B, residue subsets:** on slice 0, classes p mod m for m ∈ {5, 7, 13} (residues coprime to m), each cut to n_min.
  - R_j is computed at K_sub = round(N_sub^β_eff), with β_eff = log K / log N, and relSD_m = SD(R_j)/mean.
  - It is scaled by √(K_sub/K), pooled over m with weights q_m − 1, and SE_B = R·relSD_pooled.
  - For (i)–(iii) the labels are i.i.d. uniform over the 288 residues coprime to 455. For (iv) they are the real
    p mod 455.
- **Slices:** R_j for j = 0 … 8 at K; σ̂² = Σ_t (R_t − 2R_{t+1} + R_{t+2})² / (6·7).

**The truth:** the SD over replicates of R(slice 0) at K (ddof 1). This is the estimand all three methods target:
A and B are applied to slice 0, and slices estimates the per-slice SD.

**Witnesses** (half-angle densities on [0, ½); the mirror makes them symmetric on the circle):
- **(i) iid:** uniform.
- **(ii) modulation:** density ∝ 1 + a·cos(2π·3θ), a smooth ℓ = 3 modulation, by rejection sampling.
  - Expected effect ΔR = (N/K)·a²/2 (for ℓ ≪ K).
  - **Sizing** (my reading of "the observed R excess", stated for Will to correct): per cell, ΔR = |1 − R_ℤ[i]|, with
    R_ℤ[i] the sealed 10¹⁰ value at that β (results/read/read1.json), so a = √(2ΔR·K/N). Also at 0.1× that ΔR
    (ii-small). The modulation is the same in every slice and every replicate.
- **(iii) drift along order:** in each consecutive pair (2k, 2k+1) of the ordered sequence, θ_{2k+1} = θ_{2k} with
  probability f(i).
  - The fraction of points in pairs is f, so R = 1 + f exactly, with the angle marginal unchanged.
  - Linear: f(i) = F·i/(Jn). Quadratic: f(i) = F·(i/(Jn))², with F = 0.082. The linear case gives about 0.0091 per
    slice, ℤ[i]'s observed drift at β 0.55.
- **(iv) real primes:** the first J·n split primes of `archive_1e12_zi` and of `archive_1e12_zs2`, in archive (prime)
  order, with their real p mod 455. The angles are synthetic.
  - **Uncoupled:** uniform angles.
  - **Coupled:** the classes p ≡ 1 and 2 (mod 5) get densities 1 + a·cos(2π·3θ) and 1 − a·cos(2π·3θ); classes 3 and 4
    stay uniform. The full set stays uniform to the class-count imbalance.
  - a is sized per cell so that the modulated classes' subset ΔR = (N_sub/K_sub)·a²/2 equals (ii)'s ΔR (N_sub = N/4).
- **Replicates:** 160 per case (16 chunks of 10). Seed = 20261104 + 10⁶·case + replicate.

**Report** (summarise mode), per case and cell:
- each method's estimate ÷ the truth, with the estimate aggregated as the RMS over replicates;
- a 90% bootstrap interval (2,000 resamples of replicates, recomputing both the truth and the estimate);
- B per m, and A at both M.

**Rule (Will):** "A method that fails its witness is recorded as invalid for L13."
- **Declared failure:** the 90% interval of estimate ÷ truth lies entirely outside [0.8, 1.25] in a case.
- Witness (i) is the baseline: a method failing (i) is invalid outright.
- Failing (ii), (iii) or (iv)-coupled says the method is not robust to that planted structure. Its relevance to the
  real sets is Will's reading.
- **The hypothesis named in the brief:** A ÷ truth > 1.25 under (ii).
- Nothing is relabelled.

**Cost model** (rq1_l13's spot constants: m_pass(N) = 3.7·10⁻⁸·N s; sort plus generation about 0.35 s per slice at
N = 4·10⁶):
- a 4-K unit (one generation, all four K) ≈ 14 s; a 1-K unit (one generation per cell) ≈ 6.6 s;
- per replicate: 5 four-K units ((i), (iii)×2, (iv)-uncoupled ×2) + 16 one-K units ((ii)×8, (iv)-coupled ×8)
  ≈ 176 s;
- per chunk of 10 replicates ≈ 1,760 s; 16 chunks ≈ **7.8 core-h**.

**§9.H:** every chunk has the same composition (all cases, 10 replicates), so the cheapest, median and most expensive
chunk coincide. The first wave is chunk 0 alone. The rest are queued only if chunk 0's CPU is ≤ 1.25× its model, and
the 1.25× rule is checked again over all chunks at the end. Free cores: pueue group specarith-filler (idle CPU weight).

  python rq1_l13_calib.py selftest                    small-N plumbing: (i) ratios near 1, (ii) ΔR near target
  python rq1_l13_calib.py task CHUNK ZS2_DIR ZI_DIR OUT_DIR
  python rq1_l13_calib.py summarise OUT_DIR OUT_JSON
"""
import glob, json, math, os, sys, time

import numpy as np

import rq1_read as Q
import rq1_l13 as L

HERE = os.path.dirname(os.path.abspath(__file__))
J, NHALF = 9, 2_000_000
KS = [2906, 7873, 57801, 156616]
BETA_OF = {2906: 0.40, 7873: 0.45, 57801: 0.55, 156616: 0.60}
ELL, F_DRIFT, REPS_PER_CHUNK, SEED0 = 3, 0.082, 10, 20261104
MS = [5, 7, 13]
CASES = ["i", "ii", "ii_small", "iii_lin", "iii_quad", "iv_zi", "iv_zi_coupled", "iv_zs2", "iv_zs2_coupled"]
COPRIME = np.array([r for r in range(455) if math.gcd(r, 455) == 1], np.int16)
CHUNK_MODEL_S = 1760.0


def delta_targets():
    read1 = json.load(open(os.path.join(HERE, "results/read/read1.json")))
    rows = {r["beta"]: r for r in read1["rows"][str(10 ** 10)]["rows"]}
    return {K: abs(1 - rows[BETA_OF[K]]["R_zi"]) for K in KS}


def modulated(rng, n, amp):
    """n half-angles on [0, ½) with density ∝ 1 + amp·cos(2π·ELL·θ); amp may be an array (per point)."""
    amp = np.broadcast_to(np.asarray(amp, float), (n,))
    out = np.empty(n); todo = np.arange(n)
    while todo.size:
        th = rng.random(todo.size) * 0.5
        acc = rng.random(todo.size) * (1 + np.abs(amp[todo])) < 1 + amp[todo] * np.cos(2 * np.pi * ELL * th)
        out[todo[acc]] = th[acc]; todo = todo[~acc]
    return out


def pairs(rng, th, f):
    """θ_{2k+1} = θ_{2k} with probability f(2k): fraction f of points in duplicated pairs."""
    k = np.arange(0, len(th) - 1, 2)
    m = rng.random(k.size) < f[k]
    th = th.copy(); th[k[m] + 1] = th[k[m]]
    return th


def R_at(th_half, K):
    th = L.full_sorted(th_half)
    return Q.var_stream(th, float(K)) / (len(th) / K)


def method_A(th_half, K):
    th = L.full_sorted(th_half); N = len(th)
    return {M: L.r_se(L.var_stream_blocks(th, float(K), M), N, K)[1] for M in (250, 1000)}


def method_B(th_half, md, K, R0):
    N = 2 * len(th_half); beff = math.log(K) / math.log(N)
    num = den = 0.0; per = {}
    for m in MS:
        lab = md % m
        cls = [r for r in range(1, m) if math.gcd(r, m) == 1]
        nmin = int(min((lab == r).sum() for r in cls))
        Ksub = int(round((2 * nmin) ** beff))
        Rj = np.array([R_at(th_half[np.flatnonzero(lab == r)[:nmin]], Ksub) for r in cls])
        relf = float(Rj.std(ddof=1) / Rj.mean()) * math.sqrt(Ksub / K)
        per[m] = R0 * relf
        num += (len(cls) - 1) * relf ** 2; den += len(cls) - 1
    return R0 * math.sqrt(num / den), per


def slices_sigma2(Rs):
    R = np.asarray(Rs); d = R[:-2] - 2 * R[1:-1] + R[2:]
    return float((d ** 2).sum() / (6 * (len(R) - 2)))


def one_unit(seq_half, md_seq, Ks, n):
    """seq_half: J·n ordered half-angles; md_seq: residues. Returns per K: R0, A{M}, B, B_per, slices σ̂²."""
    out = {}
    for K in Ks:
        Rs = [R_at(seq_half[j * n:(j + 1) * n], K) for j in range(J)]
        s0, m0 = seq_half[:n], md_seq[:n]
        B, Bper = method_B(s0, m0, K, Rs[0])
        out[K] = dict(R0=Rs[0], A=method_A(s0, K), B=B, B_per=Bper, sl2=slices_sigma2(Rs))
    return out


def load_primes(d, field, total):
    _, md = L.load_half(d, field, total)
    return md


def replicate(case, rep, n, prime_md, targets):
    rng = np.random.default_rng([SEED0, CASES.index(case), rep])
    tot = J * n; N = 2 * n
    if case in ("i", "iii_lin", "iii_quad"):
        th = rng.random(tot) * 0.5
        md = rng.choice(COPRIME, tot)
        if case != "i":
            x = np.arange(tot) / tot
            th = pairs(rng, th, F_DRIFT * (x if case == "iii_lin" else x * x))
        return one_unit(th, md, KS, n)
    if case in ("ii", "ii_small"):
        res = {}
        for K in KS:
            dR = targets[K] * (1.0 if case == "ii" else 0.1)
            th = modulated(rng, tot, math.sqrt(2 * dR * K / N))
            res.update(one_unit(th, rng.choice(COPRIME, tot), [K], n))
        return res
    field = "zi" if case.startswith("iv_zi") else "zs2"
    md = prime_md[field]
    if not case.endswith("coupled"):
        return one_unit(rng.random(tot) * 0.5, md, KS, n)
    res = {}
    r5 = md % 5
    for K in KS:
        Nsub = N / 4; beff = math.log(K) / math.log(N); Ksub = Nsub ** beff
        a = math.sqrt(2 * targets[K] * Ksub / Nsub)
        amp = np.where(r5 == 1, a, np.where(r5 == 2, -a, 0.0))
        res.update(one_unit(modulated(rng, tot, amp), md, [K], n))
    return res


def task(chunk, zs2, zi, out_dir, n=NHALF):
    t0 = time.process_time()
    targets = delta_targets()
    prime_md = {"zi": load_primes(zi, "zi", J * n), "zs2": load_primes(zs2, "zs2", J * n)}
    res = {c: [] for c in CASES}
    for r in range(chunk * REPS_PER_CHUNK, (chunk + 1) * REPS_PER_CHUNK):
        for c in CASES:
            res[c].append({str(K): v for K, v in replicate(c, r, n, prime_md, targets).items()})
    cpu = time.process_time() - t0
    os.makedirs(out_dir, exist_ok=True)
    json.dump(dict(chunk=chunk, n=n, J=J, targets={str(k): v for k, v in targets.items()}, cpu_s=cpu,
                   model_s=CHUNK_MODEL_S, res=res), open(os.path.join(out_dir, f"chunk_{chunk:02d}.json"), "w"))
    print(f"chunk {chunk} cpu {cpu:.0f} s model {CHUNK_MODEL_S:.0f} ratio {cpu / CHUNK_MODEL_S:.2f}", flush=True)


def summarise(out_dir, out_json):
    ch = [json.load(open(f)) for f in sorted(glob.glob(os.path.join(out_dir, "chunk_*.json")))]
    cpu = sum(c["cpu_s"] for c in ch); model = sum(c["model_s"] for c in ch)
    rng = np.random.default_rng(SEED0 + 7)
    out = dict(chunks=len(ch), cpu_s=cpu, model_s=model, cost_ratio=cpu / model, targets=ch[0]["targets"], cases={})
    for c in CASES:
        rows = [r for x in ch for r in x["res"][c]]
        out["cases"][c] = {}
        for K in map(str, KS):
            R0 = np.array([r[K]["R0"] for r in rows])
            est = {"A_M%d" % M: np.array([r[K]["A"][str(M)] for r in rows]) for M in (250, 1000)}
            est["A"] = est["A_M%d" % L.m_primary(int(K))]
            est["B"] = np.array([r[K]["B"] for r in rows])
            for m in MS:
                est["B_m%d" % m] = np.array([r[K]["B_per"][str(m)] for r in rows])
            est["slices"] = np.sqrt(np.array([r[K]["sl2"] for r in rows]))
            truth = float(R0.std(ddof=1))
            cell = dict(n_rep=len(rows), R0_mean=float(R0.mean()), truth_SE=truth,
                        model_SE=float(R0.mean()) * L.model_rel(int(K)))
            idx = rng.integers(0, len(rows), (2000, len(rows)))
            tb = R0[idx].std(1, ddof=1)
            for k, v in est.items():
                ratio = math.sqrt(float((v ** 2).mean())) / truth
                rb = np.sqrt((v[idx] ** 2).mean(1)) / tb
                lo, hi = float(np.quantile(rb, 0.05)), float(np.quantile(rb, 0.95))
                cell[k] = dict(ratio=ratio, ci90=[lo, hi], fails=bool(hi < 0.8 or lo > 1.25))
            out["cases"][c][K] = cell
    json.dump(out, open(out_json, "w"), indent=1)
    print("cost ratio %.2f" % out["cost_ratio"])
    for c, v in out["cases"].items():
        for K, cell in v.items():
            print(c, K, "truth/model %.2f" % (cell["truth_SE"] / cell["model_SE"]),
                  " ".join("%s %.2f%s" % (m, cell[m]["ratio"], "!" if cell[m]["fails"] else "")
                           for m in ("A", "B", "slices")))


def selftest():
    rng = np.random.default_rng(1)
    n, K = 200_000, 2000
    R = [R_at(rng.random(n) * 0.5, K) for _ in range(30)]
    print("iid: mean R %.3f (expect ≈1), SD %.4f, model %.4f" % (np.mean(R), np.std(R, ddof=1), np.mean(R) * L.model_rel(K)))
    a = math.sqrt(2 * 0.25 * K / (2 * n))
    Rm = [R_at(modulated(rng, n, a), K) for _ in range(10)]
    print("modulated: mean R %.3f (expect ≈1.25)" % np.mean(Rm))
    th = pairs(rng, rng.random(n) * 0.5, np.full(n, 0.1))
    print("pairs f=0.1: R %.3f (expect ≈1.10)" % R_at(th, K))
    print("selftest done")


if __name__ == "__main__":
    if sys.argv[1] == "selftest":
        selftest()
    elif sys.argv[1] == "task":
        task(int(sys.argv[2]), sys.argv[3], sys.argv[4], sys.argv[5])
    elif sys.argv[1] == "summarise":
        summarise(sys.argv[2], sys.argv[3])
