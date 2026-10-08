"""Phase 6.1 tests T1–T4 (PH6_SEAL 6.1 §3–§6 with amendments A1–A3), on a level list t_1 < t_2 < … (T1-rescaled).

  python tests61.py nulls ID TOP OUT NPROC   GUE/Poisson null bands for T3 at the configuration rule_config(0, TOP) (6.0 §3,
                                            §6.2, §7: 100 + 100 calibration draws, seeds as the 6.0 pre-read)
  python tests61.py known OUT NPROC          known-answer dry run: the zeros (first 3·10⁴), a GUE null and a picket fence
                                            mapped onto ζ's smooth count — the only spectra this mode ever reads
  python tests61.py read ID                  a candidate — REFUSED unless seals/PH6_SEAL_6.1.json exists and pins this code

Declared here (not fixed by the seal text; flagged to Will before the seal):
  CRYSTAL_RTILDE = 0.9   integrable crystal ⇔ ⟨r̃⟩ ≥ 0.9 (GSE band tops at 0.677, picket = 1); decides T4 INAPPLICABLE and T2
                         FAIL ("crystal") before either is read
  BOOT_BLOCK, BOOT_B     moving-block bootstrap of the ratio sequence for T2's SDs: blocks of 100 ratios, 2,000 replicates
"""
import hashlib
import json
import math
import os
import sys
from multiprocessing import Pool

import numpy as np

import ph6lib as L
import preread as PR

HERE = os.path.dirname(os.path.abspath(__file__))
ZEROS6 = "/home/combust/fmexplorer/criticality_tool/data/odlyzko_zeros6.txt"
ZEROS6_SHA256 = "2ef7b752c2f17405222e670a61098250c8e4e09047f823f41e2b41a7b378e7c6"
BANDS61 = os.path.join(HERE, "results", "preread61", "bands61.json")
TAU1 = 0.02                       # D3: max(5·SD_blocks, 0.02), SD_blocks = 4.6e-4 on the zeros (preread61)
CRYSTAL_RTILDE = 0.9
BOOT_BLOCK, BOOT_B = 100, 2000
SEP_T4 = 3.0                      # A3: nearest class separated from the second-nearest by ≥ 3 SD units
SEED = 20261008


# ---------------------------------------------------------------- shared
def ratios(t):
    s = np.diff(np.sort(t))
    return np.minimum(s[:-1], s[1:]) / np.maximum(s[:-1], s[1:])


def boot_sd_mean(x, rng, block=BOOT_BLOCK, B=BOOT_B):
    n = len(x)
    nb = int(math.ceil(n / block))
    cs = np.concatenate([[0.0], np.cumsum(x)])
    starts = rng.integers(0, n - block + 1, (B, nb))
    sums = (cs[starts + block] - cs[starts]).sum(axis=1)
    return float(np.std(sums / (nb * block), ddof=1))


def zeros_in(t_lo, t_hi):
    if hashlib.sha256(open(ZEROS6, "rb").read()).hexdigest() != ZEROS6_SHA256:
        raise SystemExit("REFUSED: zeros6 sha256")
    z = np.loadtxt(ZEROS6)
    return z[(z >= t_lo) & (z <= t_hi)]


# ---------------------------------------------------------------- T1
def t1(t):
    import mpmath as mp
    mp.mp.dps = 30
    nbar = np.array([float(mp.siegeltheta(x) / mp.pi + 1) for x in t])
    n = np.arange(1, len(t) + 1)
    delta = (n - 0.5) - nbar
    slope = float(np.polyfit(np.log(t), delta, 1)[0])
    dbar = float(delta.mean())
    fails = [k for k, v in (("constant", abs(dbar) > TAU1), ("slope", abs(slope) > TAU1)) if v]
    return dict(verdict="PASS" if not fails else "FAIL", attribution=fails, delta_bar=dbar, slope=slope, tau1=TAU1,
                n=int(len(t)), t_range=[float(t[0]), float(t[-1])])


# ---------------------------------------------------------------- T2 (A3) and the crystal criterion
def t2(t, rng):
    r = ratios(t)
    rc = float(r.mean())
    out = dict(rtilde=rc, crystal=bool(rc >= CRYSTAL_RTILDE))
    bands = json.load(open(BANDS61))["bands"]
    g = bands["GUE"]
    out["GUE_band_descriptive"] = dict(band=g["band"], z=(rc - g["mean"]) / g["sd"], W=json.load(open(BANDS61))["W"])
    if out["crystal"]:
        out.update(verdict="FAIL", attribution="integrable crystal (⟨r̃⟩ ≥ %.1f)" % CRYSTAL_RTILDE)
        return out
    z = zeros_in(t[0], t[-1])
    rz = ratios(z)
    sd_c, sd_z = boot_sd_mean(r, rng), boot_sd_mean(rz, rng)
    tol = 3 * math.sqrt(sd_c ** 2 + sd_z ** 2)
    out.update(rtilde_zeros=float(rz.mean()), n_zeros=int(len(z)), sd_cand=sd_c, sd_zeros=sd_z, tol=tol,
               diff=rc - float(rz.mean()), verdict="PASS" if abs(rc - float(rz.mean())) <= tol else "FAIL")
    return out


# ---------------------------------------------------------------- T4 (A3)
def t4(t2res):
    if t2res["crystal"]:
        return dict(verdict="INAPPLICABLE", reason="integrable crystal")
    bands = json.load(open(BANDS61))["bands"]
    v = t2res["rtilde"]
    d = sorted((abs(v - b["mean"]) / b["sd"], k) for k, b in bands.items())
    sep = d[1][0] - d[0][0]
    cls = d[0][1] if sep >= SEP_T4 else "ambiguous"
    return dict(verdict=cls if cls != "ambiguous" else "NOT RESOLVABLE", nearest=d[0][1], distances={k: x for x, k in d},
                separation=sep)


# ---------------------------------------------------------------- T3 (6.0 instrument)
def t3(t, band, top):
    cfg = L.rule_config(0.0, top)
    lev = t[t <= top]
    taus = L.local_grid(cfg)
    S, M = L.zero_sums(cfg, lev, taus, exact=True)
    sm = L.rhs_dirichlet(cfg, taus, 1, None, 0)["smooth"]
    c = L.readout(cfg, taus, (S + M - sm) / cfg.norm)
    v, det = L.t3_verdict(c, L.weights("zeta"), band)
    return dict(verdict=v, details=det, config=dict(T0=cfg.T0, sigma=cfg.sigma, E_hi=cfg.E_hi))


def null_band(top, nproc, n=100):
    cfg = L.rule_config(0.0, top)
    cfgd = dict(T0=cfg.T0, sigma=cfg.sigma, E_lo=cfg.E_lo, E_hi=cfg.E_hi)
    jobs = [("gue", PR.CALIB_SEEDS["gue"] + i, cfgd, "zeta") for i in range(n)]
    with Pool(nproc) as pool:
        res = pool.map(PR._one_draw, jobs, chunksize=1)
    taus = L.local_grid(cfg)
    sm = L.rhs_dirichlet(cfg, taus, 1, None, 0)["smooth"]
    cs = np.array([L.readout(cfg, taus, (r[2] - sm) / cfg.norm) for r in res])
    B, s = L.band(cs, PR.ALPHA)
    return B, dict(config=cfgd, n_draws=n, B_log2=float(B[0]), B_log90=float(B[-1]))


def run_all(t, band, top, rng):
    a = t1(t)
    b = t2(t, rng)
    c = t3(t, band, top)
    d = t4(b)
    return dict(T1=a, T2=b, T3=c, T4=d, tuple=[a["verdict"], b["verdict"], c["verdict"], d["verdict"]])


# ---------------------------------------------------------------- known-answer dry run
def cue_block_positions(n_total, block, rng):
    """Unfolded GUE-statistics positions with exactly uniform density: concatenated CUE_block eigenphases (Haar,
    Mezzadri), x = b·block + block·θ/2π, so the expected count of x below X is X (no unfolding error)."""
    xs = []
    for b in range(int(math.ceil(n_total / block))):
        Z = (rng.standard_normal((block, block)) + 1j * rng.standard_normal((block, block))) / math.sqrt(2)
        Q, R = np.linalg.qr(Z)
        Q = Q * (np.diagonal(R) / np.abs(np.diagonal(R)))[None, :]
        th = np.sort(np.mod(np.angle(np.linalg.eigvals(Q)), 2 * math.pi))
        xs.append(b * block + block * th / (2 * math.pi))
    return np.concatenate(xs)[:n_total]


def known(out, nproc):
    """Known answers and red paths for T1–T4 (no candidate read). Spectra, all mapped onto ζ's smooth count N̄ (exact θ):
      zeros            the first 3·10⁴ zeros                                     expected (PASS, PASS, PASS, GUE)
      cue_null         GUE statistics, exact density: N̄(t_n) = x_n (CUE blocks)  T1 PASS, T2 FAIL, T3 FAIL, T4 GUE
      picket           N̄(t_n) = n − ½ exactly (smooth, crystal)                  T1 PASS, T2 FAIL, T3 FAIL, T4 INAPPLICABLE
      rp_t1_constant   picket with N̄(t_n) = n − ½ − ⅛ (the 1-vs-7/8 constant)    T1 FAIL (constant)
      rp_t1_density    picket with N̄(t_n) = (n − ½)/1.02 (2% density error)      T1 FAIL
    The T3 band (GUE nulls at G0-c's configuration, 6.0 machinery) is cached in OUT/band61_known.npy."""
    rng = np.random.default_rng(SEED)
    z = zeros_in(0, 1e9)[:30_000]
    top = float(z[-1])
    bp = os.path.join(out, "band61_known.npy")
    if os.path.exists(bp):
        band, binfo = np.load(bp), json.load(open(bp.replace(".npy", ".json")))
    else:
        band, binfo = null_band(top, nproc)
        os.makedirs(out, exist_ok=True)
        np.save(bp, band)
        json.dump(binfo, open(bp.replace(".npy", ".json"), "w"), indent=1)
    nb = lambda x: L.nbar_zeta(x)
    inv = lambda x: L.invert_nbar(nb, x, 7.0, top * 1.05 + 100)
    n = np.arange(1, 30_001)
    spectra = {
        "zeros": z,
        "cue_null": inv(cue_block_positions(30_000, 1000, np.random.default_rng(SEED + 1))),
        "picket": inv(n - 0.5),
        "rp_t1_constant": inv(n - 0.5 - 0.125),
        "rp_t1_density": inv((n - 0.5) / 1.02),
    }
    res = dict(band=binfo)
    for k, t in spectra.items():
        t = np.sort(t[(t > 0) & (t <= top)])
        res[k] = run_all(t, band, top, rng)
        print(k, res[k]["tuple"], "T1 attribution", res[k]["T1"]["attribution"], flush=True)
    os.makedirs(out, exist_ok=True)
    json.dump(res, open(os.path.join(out, "tests61_known.json"), "w"), indent=1, default=float)


SEAL61 = os.path.join(HERE, "seals", "PH6_SEAL_6.1.json")


def _sha(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()


def read(ident):
    """Read one candidate under the 6.1 seal: every pinned hash (code, inputs, levels, band) is checked before the level
    file is opened; candidates the seal marks INAPPLICABLE / NOT RESOLVABLE pre-read are not opened at all."""
    if not os.path.exists(SEAL61):
        raise SystemExit("REFUSED: no PH6_SEAL_6.1.json — candidates are not read before the 6.1 seal")
    seal = json.load(open(SEAL61))
    for f, h in list(seal["code_sha256"].items()) + list(seal["inputs_sha256"].items()):
        if _sha(os.path.join(HERE, f)) != h:
            raise SystemExit(f"REFUSED: {f} differs from the sealed file")
    c = seal["candidates"][ident]
    out = dict(id=ident)
    if c.get("pre_verdict"):
        out.update(tuple=[c["pre_verdict"]] * 4, reason=c["reason"])
    else:
        lev_path = os.path.join(HERE, c["levels"])
        if _sha(lev_path) != c["levels_sha256"]:
            raise SystemExit(f"REFUSED: {c['levels']} differs from the sealed level file")
        band_path = os.path.join(HERE, c["band"])
        if _sha(band_path) != c["band_sha256"]:
            raise SystemExit(f"REFUSED: {c['band']} differs from the sealed band")
        t = np.sort(np.load(lev_path))
        t = t[t > 0]
        out.update(run_all(t, np.load(band_path), c["config_top"], np.random.default_rng(SEED)))
    os.makedirs(os.path.join(HERE, "results", "read61"), exist_ok=True)
    json.dump(out, open(os.path.join(HERE, "results", "read61", f"{ident}.json"), "w"), indent=1, default=float)
    print(ident, out["tuple"], flush=True)


if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "known":
        known(sys.argv[2], int(sys.argv[3]))
    elif cmd == "nulls":
        ident, top, out, nproc = sys.argv[2], float(sys.argv[3]), sys.argv[4], int(sys.argv[5])
        B, info = null_band(top, nproc)
        os.makedirs(out, exist_ok=True)
        np.save(os.path.join(out, f"band61_{ident}.npy"), B)
        json.dump(info, open(os.path.join(out, f"band61_{ident}.json"), "w"), indent=1)
        print(ident, info, flush=True)
    elif cmd == "read":
        read(sys.argv[2])
