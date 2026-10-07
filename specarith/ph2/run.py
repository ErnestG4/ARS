"""Phase 2 gate runner (seal PH2_SEAL_2.1 §2–§7). Refuses to read zeros unless the seal JSON exists and its pinned code
and data hashes match (fail closed). `--synthetic` replaces every bin's zeros by CUE_N surrogate heights (N̄⁻¹ of CUE
levels, in the bin's own representation) — the dry run; it never opens a zero file.

  python run.py unfold BIN [--synthetic N]      exact-θ spacings of one bin -> results/run[_synth]/BIN_spacings.npz
  python run.py gates  BIN [--synthetic N]      §4 verdicts + §7 red paths for one bin -> results/run[_synth]/BIN.json
"""
import hashlib
import json
import math
import os
import sys
import time

import numpy as np

import ph2lib as P
import preread as R

HERE = os.path.dirname(os.path.abspath(__file__))
SEAL = os.path.join(HERE, "seals", "PH2_SEAL_2.1.json")
MAIN_DATA = "/home/combust/fmexplorer/criticality_tool/data"
SOURCES = {
    "zeros6": os.path.join(MAIN_DATA, "odlyzko_zeros6.txt"),
    "zeros3": os.path.join(HERE, "data", "odlyzko", "zeros3"),
    "zeros4": os.path.join(HERE, "data", "odlyzko", "zeros4"),
    "zeros5": os.path.join(HERE, "data", "odlyzko", "zeros5"),
}
PLATT_FILES = {"P1": "zeros_2546000.dat", "P2": "zeros_19346000.dat", "P3": "zeros_151646000.dat",
               "P4": "zeros_1119746000.dat", "P5": "zeros_8284946000.dat", "P6": "zeros_30404246000.dat"}
DPS = 45
SENSITIVITY_WINDOWS = (1.8, 2.2)   # A2: reported descriptively beside the sealed S_C = 2.0


def _hash(path, algo):
    h = hashlib.new(algo)
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def check_seal(name):
    """Fail closed: the seal JSON must exist; this bin's data file and the code files must match its pins."""
    if not os.path.exists(SEAL):
        raise SystemExit(f"REFUSED: no seal at {SEAL}; zeros are not read before the seal")
    seal = json.load(open(SEAL))
    for f, h in seal["code_sha256"].items():
        got = _hash(os.path.join(HERE, f), "sha256")
        if got != h:
            raise SystemExit(f"REFUSED: {f} sha256 {got} != sealed {h}")
    kind = next(b[1] for b in R.BINS if b[0] == name)
    if kind == "platt":
        path = os.path.join(HERE, "data", "platt", PLATT_FILES[name])
        got, want = _hash(path, "md5"), seal["data"]["platt_md5"][PLATT_FILES[name]]
    else:
        path = SOURCES[kind]
        got, want = _hash(path, "sha256"), seal["data"]["sha256"][kind]
    if got != want:
        raise SystemExit(f"REFUSED: {path} hash {got} != sealed {want}")
    return seal, path


# ---------------------------------------------------------------- zeros of a bin, as mpf (real) or synthetic
def zeros_of_bin(name, path):
    import mpmath as mp
    _, kind, L0, L1 = next(b for b in R.BINS if b[0] == name)
    with mp.workdps(DPS):
        if kind == "zeros6":
            lo, hi = R.TWO_PI * math.exp(L0), R.TWO_PI * math.exp(L1)
            out = []
            with open(path) as f:
                for line in f:
                    v = float(line)
                    if lo <= v < hi:
                        out.append(mp.mpf(line.strip()))
            return out
        if kind == "platt":
            pairs, first = P.read_platt_file(path)
            return P.platt_to_mpf(pairs, dps=DPS)
        g = P.read_odlyzko_offset_table(path, dps=DPS)
        if len(g) != R.H_COUNT:
            raise SystemExit(f"{path}: {len(g)} zeros, expected {R.H_COUNT}")
        return g


def synthetic_zeros(name, N, n=None, seed=11):
    """CUE_N levels placed at the bin's start height by N̄⁻¹ (mpmath), in the bin's representation (as g0d_chain)."""
    import mpmath as mp
    _, kind, L0, L1 = next(b for b in R.BINS if b[0] == name)
    n_bin, _, _ = R.bin_geometry(name, n_profile=11)
    n = n_bin if n is None else n
    rng = np.random.default_rng(seed)
    x = np.cumsum(P.cue_spacings(N, n // N + 2, rng).ravel()[:n + 1])
    out = []
    with mp.workdps(DPS):
        T0 = R.TWO_PI * mp.exp(mp.mpf(L0))
        base = mp.siegeltheta(T0) / mp.pi + 1
        g = T0
        for xi in x:
            target = base + mp.mpf(float(xi))
            for _ in range(50):
                step = (mp.siegeltheta(g) / mp.pi + 1 - target) / (mp.log(g / (2 * mp.pi)) / (2 * mp.pi))
                g -= step
                if abs(step) < mp.mpf(10) ** -35:
                    break
            out.append(+g)
        digits = R.REPRESENTATION[kind]
        if digits is None:
            eps, t0 = mp.mpf(2) ** -101, mp.floor(out[0])
            out = [t0 + mp.nint((v - t0) / eps) * eps for v in out]
        else:
            q = mp.mpf(10) ** -digits
            out = [mp.nint(v / q) * q for v in out]
    return out


def outdir(synth):
    d = os.path.join(R.RES, "run_synth" if synth else "run")
    os.makedirs(d, exist_ok=True)
    return d


def unfold(name, synth_N=None, synth_n=None):
    t = time.time()
    if synth_N is None:
        _, path = check_seal(name)
        g = zeros_of_bin(name, path)
    else:
        g = synthetic_zeros(name, synth_N, synth_n)
    s = P.unfolded_spacings(g, dps=DPS)
    mid = np.array([float((g[i] + g[i + 1]) / 2) for i in range(len(g) - 1)])
    dg = np.array([float(g[i + 1] - g[i]) for i in range(len(g) - 1)])
    np.savez(os.path.join(outdir(synth_N is not None), f"{name}_spacings.npz"), s=s, mid=mid, dg=dg,
             first=str(g[0]), last=str(g[-1]))
    print(f"{name}: {len(s)} spacings, mean {s.mean():.8f}, {time.time() - t:.0f}s", flush=True)


# ---------------------------------------------------------------- §4 verdicts and §7 red paths for one bin
def _ci_kappa(c_hat, sd_c):
    lo, hi = c_hat - R.Z95 * sd_c, c_hat + R.Z95 * sd_c
    k = lambda c: P.kappa_from_c(c)
    return dict(c=c_hat, c_ci=[lo, hi], kappa=k(c_hat), kappa_ci=[k(hi), k(lo)])   # κ decreasing in c


def gates(name, synth_N=None):
    synth = synth_N is not None
    if synth:   # dry run: the pre-read summary stands in for the seal JSON (allowance = max, A3; sum descriptive)
        srow = {r["bin"]: r for r in json.load(open(os.path.join(R.RES, "summary.json")))["rows"]}[name]
        g0c = {b["bin"]: b for b in json.load(open(os.path.join(R.RES, "g0c.json")))["bins"]}[name]
        srow["prim"]["allowance"] = g0c["allowance_max"]
        srow["prim"]["NOT_RESOLVABLE"] = srow["prim"]["NOT_RESOLVABLE_max"]
        srow["prim"]["allowance_sum_descriptive"] = g0c["allowance_sum"]
        srow["prim"]["NOT_RESOLVABLE_sum_descriptive"] = srow["prim"]["NOT_RESOLVABLE_sum"]
        srow["sec"]["NOT_RESOLVABLE"] = not srow["sec"]["RESOLVABLE_at_floor"]
        srow["prim"]["widened_halfwidth"] = srow["prim"]["widened_halfwidth_max"]
    else:
        srow = {r["bin"]: r for r in json.load(open(SEAL))["bins"]}[name]
    if not synth:
        check_seal(name)
    d = np.load(os.path.join(outdir(synth), f"{name}_spacings.npz"))
    s, mid, dg = d["s"], d["mid"], d["dg"]
    n = len(s)
    L = np.log(mid / R.TWO_PI)
    Neff, ab = R.neff_of_L(L), R.abar_of_L(L)
    Mp, Ms = P.Model(), P.Model(abar_grid=P.SECONDARY_ABAR_GRID)
    Wp, Ws = P.WindowFit(Mp), P.WindowFit(Ms)
    Lb = [f * int(math.ceil(float(np.median(Neff)))) for f in R.BLOCK_FACTORS]
    rng = np.random.default_rng(20261007)
    out = dict(bin=name, synthetic=synth_N, n=n, N_eff_median=float(np.median(Neff)), block_lengths=Lb)
    band = R.MEAN_SPACING_BAND / n
    out["mean_spacing"] = dict(value=float(s.mean()), band=band, ok=bool(abs(s.mean() - 1) <= band))

    def arm_fit(W, abar, spac, Ne, boot=True):
        prep = W.prepare(spac, Ne, abar)
        c, flag = W.fit(prep)
        res = dict(c=c, flag=flag)
        if boot:
            res["boot_sd_c"], res["boot_refit"] = {}, 0
            for Lblk in Lb:
                bs, nref = P.block_bootstrap_c_series(W, prep, c, Lblk, 200, rng)
                res["boot_sd_c"][str(Lblk)] = float(np.std(bs, ddof=1))
                res["boot_refit"] += nref
        return res

    for arm, W, abar in (("prim", Wp, None), ("sec", Ws, ab)):
        f = arm_fit(W, abar, s, Neff)
        sd_cue_c = srow[arm]["sd_c_cue"]                     # G0d's SD of ĉ at this bin's size and N_eff
        sd_c = max(sd_cue_c, max(f["boot_sd_c"].values()))
        ci = _ci_kappa(f["c"], sd_c)
        a = dict(fit=f, sd_c_cue=sd_cue_c, sd_c_used=sd_c, **ci)
        allow = srow["prim"].get("allowance", 0.0) if arm == "prim" else 0.0
        klo, khi = ci["kappa_ci"]
        wlo, whi = klo - allow, (khi + allow if math.isfinite(khi) else math.inf)
        a["kappa_ci_widened"] = [wlo, whi]
        a["power_excludes_inf"] = bool(ci["c_ci"][0] > 0)
        h = srow[arm]["h_bin"]
        a["pinned_h_bin"] = bool(math.isfinite(whi) and wlo >= 1 - h and whi <= 1 + h)
        a["pinned_floor"] = bool(math.isfinite(whi) and wlo >= 1 - R.FLOOR and whi <= 1 + R.FLOOR)
        # NOT RESOLVABLE is decided pre-data (seal JSON): PRIMARY by §4 (widened tolerance cannot exclude N = ∞ or
        # exceeds ±20%); SECONDARY by the same rule on its statistical CI (an interval reaching N = ∞ is no evidence)
        nr = srow[arm]["NOT_RESOLVABLE"]
        # A6(iii): achieved width — an interval that cannot exclude N = ∞ or is wider than ±20% is never PASS/FAIL
        half = (whi - wlo) / 2 if math.isfinite(whi) else math.inf
        pred = srow[arm]["widened_halfwidth"] if arm == "prim" else srow[arm]["ci_halfwidth"]
        a["halfwidth"] = dict(predicted=pred, achieved=half)
        nr_ach = bool(not a["power_excludes_inf"] or half > R.FLOOR)
        a["not_resolvable_achieved"] = nr_ach
        a["G1"] = ("NOT RESOLVABLE" if nr else "NOT RESOLVABLE (achieved)" if nr_ach
                   else ("PASS" if wlo <= 1 <= whi else "FAIL"))
        a["unresolved"] = bool(nr or nr_ach)
        out[arm] = a
    # §7 red paths
    sm = dg * np.log(mid / (R.TWO_PI * math.e)) / R.TWO_PI          # RP-misprint: local density log(E/2πe)/2π
    mis = dict(mean_spacing=float(sm.mean()), mean_ok=bool(abs(sm.mean() - 1) <= band))
    for arm, W, abar in (("prim", Wp, None), ("sec", Ws, ab)):
        f = arm_fit(W, abar, sm, Neff, boot=False)
        lo, hi = out[arm]["kappa_ci_widened"]
        k = P.kappa_from_c(f["c"])
        mis[arm] = dict(c=f["c"], kappa=k, inside_ci=bool(lo <= k <= hi))
    # each arm is scored only where it can fire (pre-data reachability); an unreachable arm is INAPPLICABLE
    mis["arm_mean"] = "FIRED" if not mis["mean_ok"] else "SILENT"
    mis["arm_N_prim"] = ("INAPPLICABLE" if out["prim"]["unresolved"]
                         else ("FIRED" if not mis["prim"]["inside_ci"] else "SILENT"))
    mis["arm_N_sec"] = ("INAPPLICABLE" if out["sec"]["unresolved"]
                        else ("FIRED" if not mis["sec"]["inside_ci"] else "SILENT"))
    live = [mis[k] for k in ("arm_mean", "arm_N_prim", "arm_N_sec") if mis[k] != "INAPPLICABLE"]
    mis["FAILS_as_required"] = bool(live and all(x == "FIRED" for x in live))
    out["rp_misprint"] = mis
    fm = arm_fit(Ws, (1 + ab) / 2, s, Neff, boot=False)
    km = P.kappa_from_c(fm["c"])
    lo, hi = out["sec"]["kappa_ci_widened"]
    reach_mix = bool(srow["rp_mix"]["reachable"] and not out["sec"]["unresolved"])
    out["rp_mix"] = dict(c=fm["c"], kappa=km, shift=km - out["sec"]["kappa"], outside_ci=bool(not (lo <= km <= hi)),
                         reachable=reach_mix,
                         status=("INAPPLICABLE" if not reach_mix
                                 else ("DISTINGUISHED" if not (lo <= km <= hi) else "NOT DISTINGUISHED")))
    out["rp_ninf"] = dict(prim=out["prim"]["power_excludes_inf"], sec=out["sec"]["power_excludes_inf"])
    idx = rng.integers(0, n, n)                                       # RP-shuffle: i.i.d. (s, N_eff) pairs
    fs = arm_fit(Wp, None, s[idx], Neff[idx], boot=False)
    ks = P.kappa_from_c(fs["c"])
    lo, hi = out["prim"]["kappa_ci"]
    out["rp_shuffle"] = dict(kappa=ks, inside_ci=bool(lo <= ks <= hi),
                             status=("INAPPLICABLE" if out["prim"]["unresolved"]
                                     else ("UNCHANGED" if lo <= ks <= hi else "CHANGED")))
    out["rp_lambda"] = "INAPPLICABLE (unreachable, declared)"
    # ---- DESCRIPTIVE (never verdicts): A3's sum-based PRIMARY widening; A2's window sensitivity at 1.8 and 2.2
    p = out["prim"]
    al_sum = srow["prim"]["allowance_sum_descriptive"]
    klo, khi = p["kappa_ci"]
    wlo, whi = klo - al_sum, (khi + al_sum if math.isfinite(khi) else math.inf)
    out["descriptive_prim_sum_allowance"] = dict(
        allowance=al_sum, kappa_ci_widened=[wlo, whi],
        G1="NOT RESOLVABLE" if srow["prim"]["NOT_RESOLVABLE_sum_descriptive"] else ("PASS" if wlo <= 1 <= whi else "FAIL"))
    sens = {}
    for sc in SENSITIVITY_WINDOWS:
        Wp2, Ws2 = P.WindowFit(Mp, sc=sc), P.WindowFit(Ms, sc=sc)
        sens[str(sc)] = {}
        for arm, W, abar in (("prim", Wp2, None), ("sec", Ws2, ab)):
            prep = W.prepare(s, Neff, abar)
            c, flag = W.fit(prep)
            bs, _ = P.block_bootstrap_c_series(W, prep, c, max(Lb), 200, rng)
            sens[str(sc)][arm] = dict(c=c, flag=flag, kappa=P.kappa_from_c(c), boot_sd_c=float(np.std(bs, ddof=1)),
                                      c_range=list(W.c_range(float(np.min(Neff)),
                                                             abars=None if abar is None else (float(ab.min()), float(ab.max())))))
    out["descriptive_window_sensitivity"] = sens
    json.dump(out, open(os.path.join(outdir(synth), f"{name}.json"), "w"), indent=1, default=float)
    print(json.dumps({k: out[k] for k in ("bin", "n", "mean_spacing")}, default=float),
          "prim", out["prim"]["G1"], round(out["prim"]["kappa"], 4), [round(x, 4) for x in out["prim"]["kappa_ci_widened"]],
          "sec", out["sec"]["G1"], round(out["sec"]["kappa"], 4), [round(x, 4) for x in out["sec"]["kappa_ci_widened"]],
          "misprint FAILS", mis["FAILS_as_required"], (mis["arm_mean"], mis["arm_N_prim"], mis["arm_N_sec"]),
          "mix", out["rp_mix"]["status"], "shuffle", out["rp_shuffle"]["status"], flush=True)


if __name__ == "__main__":
    cmd, name = sys.argv[1], sys.argv[2]
    synN = int(sys.argv[sys.argv.index("--synthetic") + 1]) if "--synthetic" in sys.argv else None
    synn = int(sys.argv[sys.argv.index("--n") + 1]) if "--n" in sys.argv else None
    if cmd == "unfold":
        unfold(name, synN, synn)
    elif cmd == "gates":
        gates(name, synN)
