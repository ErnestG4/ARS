"""Diagnostic D (round 55; EXPLORATORY, NO VERDICT): scale dependence of the count cumulants at L = 3. The design is
DIAG_D_DESIGN.md (d2506082), committed before this file was run.

  python diag_d.py decode SET FILE OUT_DIR       zeros (SET = F5, F4, F3) or a stand-in (SET = SI): md5 against the pin
                                                 before decoding (stand-ins: against the dry-run record), the sealed
                                                 read's decode and exact-θ unfolding, window counts at L = 3 (.npy), and
                                                 the zero-count completeness record
  python diag_d.py scales SEQ.npy OUT.json IDX [REP]   D1 (k₃) and D2 (k₂) by dyadic sub-block scale
  python diag_d.py null F5FILE OUT_DIR CHUNK NCHUNKS   the same on that file's 200 CUE calibration sequences
  python diag_d.py read                          the declared reading → results/diag_d/DIAG_D.json
"""
import glob
import hashlib
import json
import math
import os
import re
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import followup_read as FR  # noqa: E402
import route_a_read as RR  # noqa: E402

OUT = os.path.join(HERE, "results", "diag_d")
FRESH = os.path.join(HERE, "..", "ph2r2", "data", "platt_fresh")
SYN = os.path.join(HERE, "results", "followup_dryrun_synth")
CALSAMP = os.path.join(HERE, "results", "followup_calsamp")
B_BOOT, MIN_B, BLK = 200, 100, 100
SEED = 20261018
SETS = {"F5": dict(FR.FILES["B"]), "F4": dict(FR.FILES["A"]), "F3": dict(RR.F3)}
SETS["SI"] = dict(FR.FILES["B"])                                   # stand-ins at F5 geometry


def md5(p):
    h = hashlib.md5()
    with open(p, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def pins(S):
    if S in ("F5", "F4"):
        import followup_sealread as SR
        return SR.MD5["B" if S == "F5" else "A"]
    if S == "F3":
        import route_a_sealread as RS
        return RS.F3_MD5
    return json.load(open(os.path.join(HERE, "results", "followup_dryrun", "FOLLOWUP_B_DRYRUN.json")))["md5"]


def theta_count(t0, t1):
    import mpmath as mp
    with mp.workdps(30):
        return float((mp.siegeltheta(t1) - mp.siegeltheta(t0)) / mp.pi)


def decode(S, f, out_dir):
    import followup_sealread as SR
    p = os.path.join(SYN if S == "SI" else FRESH, f)
    if md5(p) != pins(S)[f]:
        raise SystemExit(f"REFUSED: {p} md5 differs from the pin")
    t0, t1 = SETS[S][f]
    g = SR.decode(p, t0, t1)
    n = len(g)
    s, x = FR.unfold(g, t0, dps=SR.DPS - 5)
    del g
    seq = FR.seq_B(x)
    os.makedirs(out_dir, exist_ok=True)
    np.save(os.path.join(out_dir, f"{S}_{f}.npy"), seq)
    tc = theta_count(t0, t1)
    rec = dict(set=S, file=f, n_zeros=n, theta_count=tc, diff=n - tc, complete=bool(abs(n - tc) <= 2), W=len(seq),
               sha256_seq=hashlib.sha256(np.ascontiguousarray(seq).tobytes()).hexdigest())
    json.dump(rec, open(os.path.join(out_dir, f"{S}_{f}.json"), "w"), indent=1)
    print(rec, flush=True)


def kstats(c):
    c = np.asarray(c, float)
    W = len(c)
    d = c - c.mean()
    k2 = float(np.sum(d * d) / (W - 1))
    k3 = float(W * np.sum(d ** 3) / ((W - 1) * (W - 2)))
    return k2, k3


def boot_k23(c, L, n_boot, rng):
    """Moving-block bootstrap of (k₂, k₃) (followup_read.boot_k3's construction, the same resamples for both)."""
    d = np.asarray(c, np.int64) - int(round(float(np.mean(c))))
    W = len(d)
    C = [np.concatenate([[0], np.cumsum(d ** p)]).astype(float) for p in (1, 2, 3)]
    nb = int(math.ceil(W / L))
    last = W - (nb - 1) * L
    starts = rng.integers(0, W - L + 1, (n_boot, nb))
    lens = np.full(nb, L)
    lens[-1] = last
    S1, S2, S3 = ((Cp[starts + lens] - Cp[starts]).sum(axis=1) for Cp in C)
    m1, m2, m3 = S1 / W, S2 / W, S3 / W
    c2 = m2 - m1 ** 2
    c3 = m3 - 3 * m1 * m2 + 2 * m1 ** 3
    return W * c2 / (W - 1), W * W * c3 / ((W - 1) * (W - 2))


def scales(seq, idx, rep=None):
    W = len(seq)
    rows = []
    j = 1
    while W // 2 ** j >= MIN_B:
        b, K = W // 2 ** j, 2 ** j
        L = min(BLK, b // 10)
        k2, k3, s2, s3 = [], [], [], []
        for i in range(K):
            blk = seq[i * b:(i + 1) * b]
            a2, a3 = kstats(blk)
            key = [SEED, 55, idx, j, i] + ([1 + rep] if rep is not None else [])
            b2, b3 = boot_k23(blk, L, B_BOOT, np.random.default_rng(key))
            k2.append(a2)
            k3.append(a3)
            s2.append(float(np.var(b2, ddof=1)))
            s3.append(float(np.var(b3, ddof=1)))
        r = dict(j=j, b=b, K=K, boot_block=L)
        for name, v, s in (("k3", k3, s3), ("k2", k2, s2)):
            v = np.array(v)
            V, Sm = float(np.var(v, ddof=1)), float(np.mean(s))
            r[name] = dict(V=V, S=Sm, R=V / Sm, E=V - Sm, mean=float(v.mean()),
                           V_ci95=[V * (K - 1) / _chi2(0.975, K - 1), V * (K - 1) / _chi2(0.025, K - 1)])
            if K == 2:
                r[name]["halves"] = v.tolist()
                r[name]["halves_se"] = [math.sqrt(x) for x in s]
        rows.append(r)
        j += 1
    out = dict(W=W, scales=rows)
    for name in ("k3", "k2"):
        lb = np.log2([r["b"] for r in rows])
        lr = np.log([max(r[name]["R"], 1e-12) for r in rows])
        out[f"tau_{name}"] = float(np.polyfit(lb, lr, 1)[0])
    out["k2_full"], out["k3_full"] = kstats(seq)
    return out


_C2 = {}


def _chi2(q, dof):
    from scipy.stats import chi2
    return float(chi2.ppf(q, dof))


def null(f, out_dir, chunk, nchunks):
    i_f = list(FR.FILES["B"]).index(f)
    rows = [json.loads(x) for fn in sorted(glob.glob(os.path.join(CALSAMP, "samp_*.jsonl"))) for x in open(fn)]
    rows = sorted((r for r in rows if r["file"] == f), key=lambda r: r["rep"])
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, f"null_{f}_c{chunk:02d}.jsonl")
    done = {json.loads(x)["rep"] for x in open(path)} if os.path.exists(path) else set()
    for k, r in enumerate(rows):
        if k % nchunks != chunk or r["rep"] in done:
            continue
        res = scales(np.load(os.path.join(CALSAMP, r["seq"])), 100 + i_f, rep=r["rep"])
        res.update(rep=r["rep"], file=f)
        with open(path, "a") as fh:
            fh.write(json.dumps(res) + "\n")
        print(f"{f} rep {r['rep']}: tau_k3 {res['tau_k3']:+.3f}", flush=True)


def read():
    """The declared reading of DIAG_D_DESIGN.md, per F5 file, against its CUE null; F4/F3 and the stand-ins beside."""
    pred = json.load(open(FR.PRED["B"]))
    cal = json.load(open(FR.CALIB["B"]))
    out = dict(note="EXPLORATORY, no verdict (round 55)", files={})
    for f in FR.FILES["B"]:
        z = json.load(open(os.path.join(OUT, "scales", f"F5_{f}.json")))
        si = json.load(open(os.path.join(OUT, "scales", f"SI_{f}.json")))
        nul = [json.loads(x) for fn in glob.glob(os.path.join(OUT, "null", f"null_{f}_c*.jsonl")) for x in open(fn)]
        assert len({n["rep"] for n in nul}) == 200, (f, len(nul))
        rec = dict(R_null={}, reading={})
        for name in ("k3", "k2"):
            J = min([len(z["scales"]), len(si["scales"])] + [len(n["scales"]) for n in nul])   # common scales
            pct = {}
            for jj in range(J):
                vals = np.array([n["scales"][jj][name]["R"] for n in nul])
                pct[jj + 1] = dict(p50=float(np.percentile(vals, 50)), p95=float(np.percentile(vals, 95)),
                                   p99=float(np.percentile(vals, 99)))
            taus = np.array([n[f"tau_{name}"] for n in nul])
            t1, t99 = float(np.percentile(taus, 1)), float(np.percentile(taus, 99))

            def classify(x):
                Rz = {r["j"]: r[name]["R"] for r in x["scales"] if r["j"] <= J}
                grow = x[f"tau_{name}"] > t99 and Rz[3] > pct[3]["p95"]
                small = [J, J - 1]
                flat = all(Rz[jj] > pct[jj]["p99"] for jj in small) and t1 <= x[f"tau_{name}"] <= t99
                none = all(Rz[jj] <= pct[jj]["p99"] for jj in Rz) and t1 <= x[f"tau_{name}"] <= t99
                return dict(scale_growing=bool(grow), flat=bool(flat), none=bool(none), tau=x[f"tau_{name}"],
                            R={jj: Rz[jj] for jj in Rz})
            rec["R_null"][name] = dict(percentiles=pct, tau_1=t1, tau_99=t99)
            rec["reading"][name] = dict(zeros=classify(z), standin=classify(si))
        d = pred["files"][f]["dkappa3"]
        h = [r for r in z["scales"] if r["j"] == 1][0]["k3"]
        rec["halves"] = [dict(k3=k, se=s, mu=(k - pred["files"][f]["kappa3_sine"]) / d - cal["files"][f]["bias"],
                              mu_se=s / abs(d)) for k, s in zip(h["halves"], h["halves_se"])]
        rec["excess_mu_units"] = {r["j"]: math.sqrt(max(r["k3"]["E"], 0)) / abs(d) for r in z["scales"]}
        out["files"][f] = rec
    out["descriptive"] = {}
    for fn in sorted(glob.glob(os.path.join(OUT, "scales", "F[34]_*.json"))):
        x = json.load(open(fn))
        out["descriptive"][os.path.basename(fn)[:-5]] = dict(
            tau_k3=x["tau_k3"], tau_k2=x["tau_k2"], k3_full=x["k3_full"], k2_full=x["k2_full"],
            R_k3={r["j"]: r["k3"]["R"] for r in x["scales"]}, R_k2={r["j"]: r["k2"]["R"] for r in x["scales"]})
    out["completeness"] = {os.path.basename(fn)[:-5]: json.load(open(fn))
                           for fn in sorted(glob.glob(os.path.join(OUT, "seq", "*.json")))}
    json.dump(out, open(os.path.join(OUT, "DIAG_D.json"), "w"), indent=1)
    for f, rec in out["files"].items():
        for name in ("k3", "k2"):
            z, s = rec["reading"][name]["zeros"], rec["reading"][name]["standin"]
            lab = lambda c: "scale-growing" if c["scale_growing"] else "flat" if c["flat"] else "none" if c["none"] else "other"  # noqa: E731
            print(f"{f} {name}: zeros {lab(z)} (τ {z['tau']:+.3f}; null 1–99% [{rec['R_null'][name]['tau_1']:+.3f}, "
                  f"{rec['R_null'][name]['tau_99']:+.3f}]); stand-in {lab(s)} (τ {s['tau']:+.3f})")
        print(f"   halves μ̂: " + ", ".join(f"{h['mu']:.3f} ± {h['mu_se']:.3f}" for h in rec["halves"]))
    for k, c in out["completeness"].items():
        print(f"completeness {k}: zeros {c['n_zeros']} vs θ {c['theta_count']:.2f} (diff {c['diff']:+.2f}) "
              f"{'ok' if c['complete'] else 'OUT OF TOLERANCE'}")
    return out


if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "decode":
        decode(sys.argv[2], sys.argv[3], sys.argv[4])
    elif cmd == "scales":
        res = scales(np.load(sys.argv[2]), int(sys.argv[4]), int(sys.argv[5]) if len(sys.argv) > 5 else None)
        json.dump(res, open(sys.argv[3], "w"), indent=1)
        print(sys.argv[2], f"tau_k3 {res['tau_k3']:+.3f} tau_k2 {res['tau_k2']:+.3f}", flush=True)
    elif cmd == "null":
        null(sys.argv[2], sys.argv[3], int(sys.argv[4]), int(sys.argv[5]))
    elif cmd == "read":
        read()
