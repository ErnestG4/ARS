"""GEO-TOT1 outputs (brief 2026-10-27, "Outputs"), from the hashed merged enumeration, after the sealed read (7658da82).
Descriptive only: nothing here enters a verdict.

  python geotot1_outputs.py NPZ READ_JSON

Writes, under this directory:
  data/GEOTOT1_perq.parquet       per-q scalars, q = 2 … Q (gitignored; sha256 in results/OUTPUTS.json)
  data/GEOTOT1_perq_hist.parquet  per-q histograms of L, log2 S, log2 M (gitignored; sha256 listed)
  results/GEOTOT1_q_le_1e5.json   compact columns for q ≤ 10⁵ (the bench page's Totient keys tab)
  results/figures/*.png           count vs q per N; c_N(q) by type; mean depth vs the corrected Yao–Knuth law;
                                  depth distributions at a few q
  results/OUTPUTS.json            sha256 of all of the above, and the consistency checks below
Checks (assert): the input's sha256 is the hashed one; the arithmetic types from the spf sieve equal arith_type() on a
seeded sample and give READ_JSON's window counts; the exact depth lists at the figure's q sum to the enumeration's
S_sum and fill its log2 S histogram.
"""
import hashlib
import json
import math
import os
import sys

import numpy as np

from geotot1 import KEYS
from geotot1_analyze import DELTA, MU, KAPPA, SEED, arith_type, bins, theory_surrogate

HERE = os.path.dirname(os.path.abspath(__file__))
MERGED_SHA = "5a89ab74ce67b7788fe6945712e977549452fb2e50e9af9dc879463ad1e45c9f"     # results/ENUM_HASHES.json
TYPES = ("prime", "prime_power", "smooth", "other")
B_YK = 1.574             # second-order coefficient, fixed-q form (GEOTOT1_STEP0.md §1c; INFERENCE from Zhabitskaya/MST)
DEPTH_Q = (360, 99991, 720720, 999983)
# reference palette (dataviz skill, light mode): categorical slots 1–4, text and surface tokens
SERIES = ("#2a78d6", "#eb6834", "#1baf7a", "#eda100")
INK, INK2, MUTED, GRID, SURF = "#0b0b0b", "#52514e", "#8a8984", "#e4e3df", "#fcfcfb"


def fsha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def types_sieve(Q):
    """Arithmetic type of every q in [0, Q] (codes index TYPES; −1 for q < 2) from a smallest-prime-factor sieve."""
    spf = np.zeros(Q + 1, np.int64)
    for p in range(2, math.isqrt(Q) + 1):
        if spf[p] == 0:
            s = spf[p * p::p]
            s[s == 0] = p
    spf[spf == 0] = np.arange(Q + 1)[spf == 0]
    n = np.arange(Q + 1)
    distinct = np.zeros(Q + 1, np.int64)
    total = np.zeros(Q + 1, np.int64)
    maxp = np.zeros(Q + 1, np.int64)
    prev = np.zeros(Q + 1, np.int64)
    live = n > 1
    while live.any():
        p = np.where(live, spf[n], 0)
        distinct += live & (p != prev)
        total += live
        maxp = np.maximum(maxp, p)
        prev = np.where(live, p, prev)
        n = np.where(live, n // np.maximum(p, 1), n)
        live = n > 1
    code = np.where(distinct == 1, np.where(total == 1, 0, 1), np.where(maxp <= 100, 2, 3))
    code[:2] = -1
    return code


def depths(q):
    """Exact Σ a_i (canonical) for every a coprime to q, 0 < a < q."""
    out = []
    for a in range(1, q):
        x, y, s = q, a, 0
        while y:
            t = x // y
            x, y = y, x - t * y
            s += t
        if x == 1:
            out.append(s)
    return np.array(out, np.int64)


def binned(q, v, lo_q=2, weights=None, mask=None):
    """Bin means (10 per decade) of v over q ≥ lo_q: x = mean q in the bin, y = mean v."""
    xs, ys = [], []
    for j, lo, hi in bins(0, 61):
        m = (q >= max(lo, lo_q)) & (q < hi)
        if mask is not None:
            m &= mask
        if m.sum() >= 5:
            xs.append(float(np.exp(np.mean(np.log(q[m])))))
            ys.append(float(v[m].mean()))
    return np.array(xs), np.array(ys)


def style(ax):
    ax.set_facecolor(SURF)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    for s in ("left", "bottom"):
        ax.spines[s].set_color(MUTED)
    ax.tick_params(colors=INK2, labelsize=8)
    ax.grid(True, which="major", color=GRID, lw=0.6)
    ax.xaxis.label.set_color(INK2)
    ax.yaxis.label.set_color(INK2)


def main(npz, read_json):
    assert fsha(npz) == MERGED_SHA
    import pyarrow as pa
    import pyarrow.parquet as pq
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    d = np.load(npz)
    d = {k: d[k] for k in d.files}
    q = d["q"]
    Q = int(q[-1])
    rd = json.load(open(read_json))
    os.makedirs(os.path.join(HERE, "data"), exist_ok=True)
    os.makedirs(os.path.join(HERE, "results", "figures"), exist_ok=True)
    checks = {}

    # arithmetic types: sieve against arith_type() on a seeded sample, and against the sealed read's window counts
    code = types_sieve(Q)[q]
    samp = np.random.default_rng(SEED).choice(len(q), 5000, replace=False)
    checks["types_sieve_equals_arith_type_on_5000"] = all(TYPES[code[i]] == arith_type(int(q[i])) for i in samp)
    w = (q >= rd["window"][0]) & (q <= rd["window"][1])
    checks["types_window_counts_equal_read"] = all(int((code[w] == i).sum()) == rd["c_N_by_type"]["3"][t]["n"]
                                                   for i, t in enumerate(TYPES))

    # per-q table
    phi = d["phi"]
    cols = dict(q=q.astype(np.int32), phi=phi.astype(np.int32),
                type=pa.DictionaryArray.from_arrays(pa.array(code.astype(np.int8)), pa.array(list(TYPES))))
    for i, N in enumerate(range(2, 7)):
        cols[f"E{N}_canon"] = d["cnt_canon"][:, i].astype(np.int32)
    for i, N in enumerate(range(2, 7)):
        cols[f"E{N}_alt"] = d["cnt_alt"][:, i].astype(np.int32)
    cols.update(S_sum=d["S_sum"], L_sum=d["L_sum"], L_sq_sum=d["L_sq"],
                mean_depth=d["S_sum"] / phi - 1.0, mean_L=d["L_sum"] / phi)
    for N in (3, 4, 5):
        c = d["cnt_canon"][:, N - 2] / q.astype(float) ** (2 * DELTA[N] - 1)
        cols[f"c{N}"] = c
        cols[f"c{N}_q_over_phi"] = c * q / phi
    meta = {b"source": f"specarith/geotot1 GEOTOT1_Q1e6.npz sha256 {MERGED_SHA}".encode(),
            b"conventions": b"canonical CF (last >= 2): E_N = all a_i <= N; alt = either form; depth = S_sum/phi - 1 "
                            b"(Stern-Brocot); c_N = E_N / q^(2 delta_N - 1); types: smooth = >= 2 distinct primes, all <= 100"}
    t1 = pa.table(cols).replace_schema_metadata(meta)
    p1 = os.path.join(HERE, "data", "GEOTOT1_perq.parquet")
    pq.write_table(t1, p1, compression="zstd")
    hc = {"q": q.astype(np.int32)}
    for k, n in (("L_hist", "L"), ("S_hist", "log2S"), ("M_hist", "log2M")):
        for j in range(d[k].shape[1]):
            hc[f"{n}_{j:02d}"] = d[k][:, j].astype(np.int32)
    p2 = os.path.join(HERE, "data", "GEOTOT1_perq_hist.parquet")
    pq.write_table(pa.table(hc).replace_schema_metadata(
        {**meta, b"bins": b"L_j: length L = j (47 = >= 47); log2S_j, log2M_j: 2^j <= x < 2^(j+1) (39 = >= 2^39)"}),
        p2, compression="zstd")
    checks["parquet_roundtrip"] = bool(np.array_equal(pq.read_table(p1, columns=["E4_canon"]).column(0).to_numpy(),
                                                      d["cnt_canon"][:, 2]))

    # compact JSON for q ≤ 1e5
    m5 = q <= 100000
    js = dict(schema="GEO-TOT1 per-q columns, q = q0 … q1 (index i is q0 + i). E_canon[N][i]: keys a/q, gcd(a,q) = 1, "
                     "0 < a < q, all partial quotients <= N (canonical CF, last >= 2). depth_sum: sum over keys of "
                     "sum a_i (mean Stern-Brocot depth = depth_sum/phi - 1). len_sum: sum of CF lengths. type: index "
                     "into types.",
              source=f"GEOTOT1_Q1e6.npz sha256 {MERGED_SHA}", q0=2, q1=100000, types=list(TYPES),
              delta={str(N): DELTA[N] for N in range(2, 7)},
              sealed_slopes={N: rd["per_q"][N]["slope"] for N in ("3", "4", "5")},
              phi=phi[m5].tolist(), type=code[m5].tolist(),
              E_canon={str(N): d["cnt_canon"][m5, N - 2].tolist() for N in range(2, 7)},
              depth_sum=d["S_sum"][m5].tolist(), len_sum=d["L_sum"][m5].tolist())
    pj = os.path.join(HERE, "results", "GEOTOT1_q_le_1e5.json")
    with open(pj, "w") as f:
        json.dump(js, f, separators=(",", ":"))

    plt.rcParams.update({"font.size": 9, "axes.titlesize": 10, "axes.titleweight": "regular",
                         "figure.facecolor": SURF, "savefig.facecolor": SURF, "text.color": INK})
    figs = {}
    j0, j1 = 50, 60
    rng = np.random.default_rng(SEED)
    cloud = np.sort(np.concatenate([np.arange(len(q))[q <= 2000], rng.choice(np.arange(len(q))[q > 2000], 60000,
                                                                              replace=False)]))

    # 1. count vs q per N, with 2δ_N − 1 and the dwell-blind surrogate exponent
    fig, axs = plt.subplots(1, 3, figsize=(12, 4.0), constrained_layout=True)
    for ax, N, col in zip(axs, (3, 4, 5), SERIES):
        style(ax)
        cnt = d["cnt_canon"][:, N - 2].astype(float)
        ax.scatter(q[cloud], np.maximum(cnt[cloud], 0.5), s=0.4, color=col, alpha=0.08, lw=0, rasterized=True)
        bx, by = binned(q, cnt)
        ax.plot(bx, by, "-o", color=col, lw=2, ms=3.2, label="bin mean (10 per decade)")
        wm = (bx >= 1e5) & (bx < 1e6)
        lx = np.log(bx[wm])
        ly = np.log(by[wm])
        xx = np.array([10.0, 2e6])
        for s, ls, lab in ((2 * DELTA[N] - 1, "--", f"2δ$_{N}$ − 1 = {2 * DELTA[N] - 1:.4f}"),
                           (theory_surrogate(N), ":", f"dwell-blind surrogate {theory_surrogate(N):.4f}")):
            a0 = float(np.mean(ly - s * lx))
            ax.plot(xx, np.exp(a0) * xx ** s, ls, color=INK, lw=1.2, label=lab)
        ax.axvspan(1e5, 1e6, color=GRID, alpha=0.5, lw=0)
        r = rd["per_q"][str(N)]
        ax.set_title(f"N = {N}: fitted slope {r['slope']:.4f} (SE {r['SE']:.1e})", color=INK)
        ax.set_xscale("log")
        ax.set_yscale("log")
        ax.set_xlim(2, 1.2e6)
        ax.set_ylim(0.7, None)
        ax.set_xlabel("q")
        ax.legend(fontsize=7.5, frameon=False, loc="upper left", labelcolor=INK2)
    axs[0].set_ylabel("#{a/q in E$_N$}  (keys with all partial quotients ≤ N)")
    fig.suptitle("GEO-TOT1: bounded-dwell keys per q (shaded: sealed fit window [10$^5$, 10$^6$); "
                 "reference lines share the window's intercept)", color=INK, fontsize=10)
    figs["count_vs_q"] = fig

    # 2. c_N(q) by arithmetic type, raw and with the local factor q/φ(q) removed
    fig, axs = plt.subplots(2, 3, figsize=(12, 6.4), constrained_layout=True, sharex=True)
    for k, N in enumerate((3, 4, 5)):
        for row, key, lab in ((0, f"c{N}", "c$_N$(q) = count / q$^{2δ_N − 1}$"),
                              (1, f"c{N}_q_over_phi", "c$_N$(q) · q/φ(q)")):
            ax = axs[row, k]
            style(ax)
            v = cols[key]
            for i, (t, col) in enumerate(zip(TYPES, SERIES)):
                bx, by = binned(q, v, lo_q=100, mask=code == i)
                ax.plot(bx, by, "-o", color=col, lw=2, ms=3, label=t.replace("_", " "))
            ax.axvspan(1e5, 1e6, color=GRID, alpha=0.5, lw=0)
            ax.set_xscale("log")
            if row == 0:
                ax.set_title(f"N = {N}", color=INK)
            if k == 0:
                ax.set_ylabel(lab)
            if row == 1:
                ax.set_xlabel("q")
    h, l = axs[0, 0].get_legend_handles_labels()
    fig.legend(h, l, loc="outside lower center", ncol=4, fontsize=8, frameon=False, labelcolor=INK2,
               title="type of q (bin means, bins with ≥ 5 q)", title_fontsize=8)
    fig.suptitle("GEO-TOT1: the per-q constant by arithmetic type; the local factor φ(q)/q (Bourgain–Kontorovich "
                 "singular series) carries most of the type dependence (descriptive)", color=INK, fontsize=10)
    figs["cN_by_type"] = fig

    # 3. mean depth against the corrected Yao–Knuth law
    md = cols["mean_depth"]
    mdx = np.where(phi > 2, (d["S_sum"] - 2 * q) / np.maximum(phi - 2, 1) - 1.0, np.nan)
    lead = lambda x: 6 / math.pi ** 2 * np.log(x) ** 2
    corr = lambda x: lead(x) + B_YK * np.log(x)
    fig, axs = plt.subplots(1, 2, figsize=(12, 4.4), constrained_layout=True)
    ax = axs[0]
    style(ax)
    ax.scatter(q[cloud], md[cloud], s=0.4, color=MUTED, alpha=0.12, lw=0, rasterized=True)
    bx, by = binned(q, md)
    ax.plot(bx, by, "-o", color=SERIES[0], lw=2, ms=3, label="mean depth Σa$_i$ − 1 (bin mean)")
    bx2, by2 = binned(q, mdx, lo_q=3)
    ax.plot(bx2, by2, "-o", color=SERIES[1], lw=2, ms=3, label="same, without a = 1 and a = q − 1")
    xx = np.logspace(0.3, 6.05, 200)
    ax.plot(xx, lead(xx), ":", color=INK, lw=1.2, label="(6/π²) ln²q  (Panov–Liehl leading term)")
    ax.plot(xx, corr(xx), "--", color=INK, lw=1.2, label=f"+ {B_YK} ln q  (second order, inferred; O(1) not fitted)")
    ax.set_xscale("log")
    ax.set_ylim(0, 1.08 * float(by.max()))
    ax.set_xlabel("q")
    ax.set_ylabel("mean depth over the φ(q) keys")
    ax.legend(fontsize=7.5, frameon=False, labelcolor=INK2, loc="upper left")
    ax.set_title("Mean Stern–Brocot depth per q", color=INK)
    ax = axs[1]
    style(ax)
    for i, (t, col) in enumerate(zip(TYPES, SERIES)):
        bx, by = binned(q, md - corr(q.astype(float)), lo_q=100, mask=code == i)
        ax.plot(bx, by, "-o", color=col, lw=2, ms=3, label=t.replace("_", " "))
    ax.axhline(0, color=MUTED, lw=1)
    ax.set_xscale("log")
    ax.set_xlabel("q")
    ax.set_ylabel("mean depth − corrected law")
    ax.legend(fontsize=7.5, frameon=False, labelcolor=INK2, title="type of q", title_fontsize=7.5)
    ax.set_title("Residual by arithmetic type (a = 1, q − 1 add 2q/φ(q))", color=INK)
    fig.suptitle("GEO-TOT1: mean depth against the corrected Yao–Knuth law (coprime average)", color=INK, fontsize=10)
    figs["mean_depth"] = fig

    # 4. depth distribution at a few q (exact lists, checked against the enumeration)
    fig, axs = plt.subplots(1, 2, figsize=(12, 4.2), constrained_layout=True)
    checks["depth_lists"] = {}
    for qq, col in zip(DEPTH_Q, SERIES):
        S = depths(qq)
        i = qq - 2
        h = np.bincount(np.minimum(np.floor(np.log2(S)).astype(int), 39), minlength=40)
        checks["depth_lists"][str(qq)] = dict(n=len(S), sum_equals=int(S.sum()) == int(d["S_sum"][i]),
                                              log2_hist_equals=bool(np.array_equal(h, d["S_hist"][i])),
                                              mean_depth=float(S.mean() - 1), median_depth=float(np.median(S) - 1))
        x = np.sort(S - 1)
        lab = f"q = {qq:,} ({TYPES[code[i]].replace('_', ' ')}; φ = {len(S):,})"
        style(axs[0])
        axs[0].step(x, np.arange(1, len(x) + 1) / len(x), where="post", color=col, lw=2, label=lab)
        style(axs[1])
        z = (x - 12 / math.pi ** 2 * math.log(qq) * math.log(math.log(qq))) / math.log(qq)
        axs[1].step(z, 1 - np.arange(len(z)) / len(z), where="post", color=col, lw=2, label=lab)
    axs[0].set_xscale("log")
    axs[0].set_xlabel("depth Σa$_i$ − 1")
    axs[0].set_ylabel("fraction of keys with depth ≤ x")
    axs[0].legend(fontsize=7.5, frameon=False, labelcolor=INK2, loc="lower right")
    axs[0].set_title("Distribution of depth over the keys of q", color=INK)
    axs[1].set_xscale("symlog", linthresh=1)
    axs[1].set_yscale("log")
    axs[1].set_xlabel("(depth − (12/π²) ln q ln ln q) / ln q")
    axs[1].set_ylabel("fraction of keys with larger value")
    axs[1].set_title("Upper tail, centred and scaled (Bettin–Drappeau / ABH typical size)", color=INK)
    fig.suptitle("GEO-TOT1: depth distributions at a few q (exact; heavy tail of index 1)", color=INK, fontsize=10)
    figs["depth_distribution"] = fig

    paths = {}
    for k, f in figs.items():
        p = os.path.join(HERE, "results", "figures", f"geotot1_{k}.png")
        f.savefig(p, dpi=150, metadata={"Software": None})
        paths[os.path.relpath(p, HERE)] = p
    checks["depth_lists_ok"] = all(v["sum_equals"] and v["log2_hist_equals"] for v in checks["depth_lists"].values())
    ok = checks["types_sieve_equals_arith_type_on_5000"] and checks["types_window_counts_equal_read"] and \
        checks["parquet_roundtrip"] and checks["depth_lists_ok"]
    files = {os.path.relpath(p, HERE): dict(sha256=fsha(p), bytes=os.path.getsize(p)) for p in (p1, p2, pj, *paths.values())}
    json.dump(dict(source=dict(file="GEOTOT1_Q1e6.npz", sha256=MERGED_SHA), read=os.path.relpath(read_json, HERE),
                   files=files, checks=checks, PASS=ok, B_YK=B_YK, reference_slopes="2 delta_N - 1 and the surrogate's "
                   "own exponent 1 + mu ln P_N + kappa/2 (ln P_N)^2, both through the window's mean point"),
              open(os.path.join(HERE, "results", "OUTPUTS.json"), "w"), indent=1)
    for k, v in files.items():
        print(f"{v['bytes']:>12,}  {k}")
    print("checks", json.dumps({k: v for k, v in checks.items() if k != "depth_lists"}), "PASS", ok)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1], sys.argv[2]))
