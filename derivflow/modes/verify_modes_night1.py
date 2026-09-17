"""Checker for derivflow/modes Night 1 (auto-discovered by verify_all.py as verify_*.py).

Re-derives every banked verdict from the committed artifacts, checks the seal-order property
for this arc's (seal, output) pairs with the same --full-history logic verify_seal_order.py
uses (that file is read-only for this arc; the pairs are listed here and proposed there), and
RED-PATHS the two witnesses the BRIEF requires to be able to fire:

  R1  gate ML must FAIL on a solver that finds the root of sum_j sign(x-r_j)|x-r_j|^-1.2 = 0
      per gap (the wrong exponent). That solver exists ONLY here.
  R2  the M6 interlacing witness must FIRE when one root is moved outside its Rolle bracket.

Missing artifacts (a stage not yet run) are reported as SKIP rows, never FAIL — a permanently
red row for a benign reason trains the reader to ignore red rows.
"""
import json
import os
import subprocess
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import modes_common as M                             # noqa: E402

bad, skipped, rows = [], [], []


def art(name):
    p = os.path.join(HERE, name)
    return json.load(open(p)) if os.path.exists(p) else None


def check(cond, msg):
    rows.append((bool(cond), msg))
    if not cond:
        bad.append(msg)


# ---- seal order (same logic as verify_seal_order.first_commit) ----
def first_commit(path):
    r = subprocess.run(["git", "log", "--full-history", "--format=%H %ct", "--diff-filter=A", "--", path],
                       cwd=M.ROOT, capture_output=True, text=True)
    lines = [l for l in r.stdout.strip().splitlines() if l.strip()]
    if not lines:
        return None
    h, t = lines[-1].split()
    return h, int(t)


OUTPUTS = ["ml_gain_gate_4096.json", "ml_gain_gate_16384.json", "mt_transfer.json",
           "m3_gue_4096.json", "m3_iid_1024.json", "m3_gue_1024.json", "m3_iid_2048.json", "m3_gue_2048.json"]
seal_c = first_commit("derivflow/modes/seal_night1.json")
for o in OUTPUTS:
    oc = first_commit(f"derivflow/modes/{o}")
    if oc is None or seal_c is None:
        skipped.append(f"seal-order {o}: UNTRACKED (not yet committed)")
        continue
    v = "DECLARED" if oc[0] == seal_c[0] else ("SEALED" if seal_c[1] < oc[1] else "INVERTED")
    check(v != "INVERTED", f"seal order {o}: {v}")

# ---- M0 smoke / M3 cells ----
for name in ["m0_smoke.json"] + [f"m3_{c}_{n}.json" for c in ("iid", "gue") for n in (1024, 2048, 4096, 16384)]:
    a = art(name)
    if a is None:
        skipped.append(f"{name}: not present"); continue
    check(a["reproduction"]["REPRODUCED"], f"{name}: PROD arms + k* reproduce the banked artifact")
    check(a["interlacing"]["holds"], f"{name}: interlacing D_k <= k/n at every k (max ratio {a['interlacing']['max_D_n_over_k']:.4f})")
    ks = a["k_grid"]
    for arm, s in a["arms"].items():
        cur = np.array(s["per_replicate"])
        check(np.allclose(cur.mean(axis=0), s["mean"], rtol=0, atol=1e-15), f"{name} {arm}: banked mean = mean of banked replicates")
        ki = M.kstar_interp(ks, s["mean"])
        check((ki is None and s["kstar_interp"]["value"] is None) or abs(ki - s["kstar_interp"]["value"]) < 1e-12,
              f"{name} {arm}: k*_interp re-derives ({ki})")
        pt = M.p_tail(ks, s["mean"], s["p_tail"]["k_range"][0], s["p_tail"]["k_range"][1])
        check((pt is None and s["p_tail"]["value"] is None) or abs(pt[0] - s["p_tail"]["value"]) < 1e-12,
              f"{name} {arm}: p_tail re-derives")
        check(s["kstar_fit"]["err_covariance"] is None or s["kstar_fit"]["err_bootstrap"] is not None,
              f"{name} {arm}: both error models present")
    npz = os.path.join(M.ROOT, a["roots_npz"])
    if os.path.exists(npz):
        check(M.sha256_of(npz) == a["roots_npz_sha256"], f"{name}: roots npz sha256 matches")
    else:
        skipped.append(f"{name}: roots npz absent locally")

# ---- gate ML ----
for n in (4096, 16384):
    a = art(f"ml_gain_gate_{n}.json")
    if a is None:
        skipped.append(f"ml_gain_gate_{n}.json: not present"); continue
    dom = [c for c in a["cells"] if c["in_pass_domain"] and c["assessable"]]
    fails = [c for c in dom if c["rel_err"] > 1e-3]
    verdict = "PASS" if (not fails and a["known_answers_pass"] and dom) else "FAIL"
    check(verdict == a["GATE_ML"], f"ml n={n}: GATE_ML re-derives as {verdict} ({len(fails)} fails / {len(dom)} assessable)")
    for c in a["cells"][:50]:
        check(abs(c["gain_pred"] - (1 - c["qw"] / np.pi) ** c["k"]) < 1e-15, f"ml n={n}: gain_pred formula (qw={c['qw']},k={c['k']})")
    check(a["interlacing"]["holds"], f"ml n={n}: interlacing holds on every flow")

# ---- gate MT ----
a = art("mt_transfer.json")
if a is None:
    skipped.append("mt_transfer.json: not present")
else:
    fails = 0; n_in = 0
    for r in a["rows"]:
        if 0.1 <= r["qw"] <= 0.5:
            for arm in ("PROD_PRIMARY", "PROD_BW1", "PROD_BW2"):
                n_in += 1
                x = r["arms"][arm]
                Tp = 1 - x["B"] * np.exp(r["k"] * (-np.log(1 - r["qw"] / np.pi) - r["qw"] / np.pi))
                check(abs(Tp - x["T_pred"]) < 1e-12, f"mt: T_pred formula qw={r['qw']} k={r['k']} {arm}")
                if abs(complex(x["T_re"], x["T_im"]) - Tp) > 0.1:
                    fails += 1
    check(("PASS" if fails == 0 else "FAIL") == a["GATE_MT"], f"mt: GATE_MT re-derives ({fails} fails / {n_in})")

# ---- R1: red path for gate ML — the wrong-exponent solver must FAIL ----
def bad_step(r, p=1.2):
    a, b = r[:-1], r[1:]
    lo, hi = a.copy(), b.copy()
    for _ in range(40):
        mid = 0.5 * (lo + hi)
        d = mid[:, None] - r[None, :]
        s = np.sum(np.sign(d) * np.abs(d) ** (-p), axis=1)
        neg = s < 0
        hi = np.where(neg, mid, hi); lo = np.where(neg, lo, mid)
    return 0.5 * (lo + hi)


from ml_gain_gate import project        # noqa: E402
n, qw, A = 512, 0.5, 1e-5   # k<=2 at qw=0.5: the sealed recipe itself passes here (3e-4) at every n
lat, wav = M.seed_lattice(n), M.seed_lattice_wave(n, qw, A, 0.3)
worst_bad, worst_good = 0.0, 0.0
for k in range(1, 3):
    lat, wav = bad_step(lat), bad_step(wav)
    worst_bad = max(worst_bad, project(wav - lat, lat, n, k, qw, A)["rel_err"])
lat, wav = M.seed_lattice(n), M.seed_lattice_wave(n, qw, A, 0.3)
for k in range(1, 3):
    lat, wav = M.diff_step(lat), M.diff_step(wav)
    worst_good = max(worst_good, project(wav - lat, lat, n, k, qw, A)["rel_err"])
check(worst_bad > 1e-3, f"R1 red path: exponent-1.2 solver FAILS gate ML (rel_err {worst_bad:.3e} > 1e-3)")
check(worst_good <= 1e-3, f"R1 control: the certified solver passes at n=512 (rel_err {worst_good:.3e})")

# ---- R2: red path for M6 — a root moved outside its bracket must fire under k/n ----
s = M.seed_iid_uniform(M.seal_children()[32], 64)
r = M.diff_step(s)
D_ok = M.interlacing_D(s, r)
rr = r.copy(); rr[5] = 0.5 * (s[7] + s[8]); rr = np.sort(rr)
D_bad = M.interlacing_D(s, rr)
check(D_ok <= 1 / 64 + 1e-15, f"R2 control: genuine k=1 flow within k/n (D={D_ok:.5f})")
check(D_bad > 1 / 64, f"R2 red path: moved root FIRES the sharp bound (D={D_bad:.5f} > {1/64:.5f})")
check(D_bad <= 2 / 63, f"R2 note: the BRIEF's 2k/(n-k) would NOT fire on it (D={D_bad:.5f} <= {2/63:.5f})")

# ---- board ----
for ok, msg in rows:
    print(f"  {'ok ' if ok else 'BAD'} {msg}")
for m in skipped:
    print(f"  SKIP {m}")
print(f"\n{sum(1 for r in rows if r[0])} ok, {len(bad)} bad, {len(skipped)} skipped")
if bad:
    print("VERIFY_MODES_NIGHT1: FAIL")
    sys.exit(1)
print("VERIFY_MODES_NIGHT1: PASS")
