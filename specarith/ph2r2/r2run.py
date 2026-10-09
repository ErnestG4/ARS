"""R₂ read (PH2R2_SEAL 1.0): μ̂ per fresh bin for the primary test function, with the §3 CI, verdicts and §4 red paths.

  python r2run.py read BIN        REFUSED unless seals/PH2R2_SEAL_1.0.json exists and pins this code and the Platt file
  python r2run.py roundtrip       Platt encode→decode identity on a synthetic level list (dry-run plumbing check)

The statistic on a level list with window edges (a real bin is one window — its file; a surrogate is a tiling):
  S_f = Σ over ordered pairs within a window, |γ − γ′| ≤ U_MAX δ; prediction (RMT_f, LOT_f) for the same windows;
  μ̂ = (S_f − RMT_f)/LOT_f; CI = μ̂ ± 1.96·max(SD_surrogate, SD_bootstrap,widest over BOOT_LEVELS) (§3, R5);
  verdicts: NOT RESOLVABLE pre-data if power(μ = 0 rejected) < 0.80; NOT RESOLVABLE (achieved) if the achieved CI cannot
  exclude 0 or its half-width exceeds 0.5; else PASS iff 1 ∈ CI. A1 (descriptive): bootstrap SD per block length.
"""
import hashlib
import json
import math
import os
import struct
import sys

import numpy as np

import g0b as G
import r2prep as P

HERE = os.path.dirname(os.path.abspath(__file__))
SEAL = os.path.join(HERE, "seals", "PH2R2_SEAL_1.0.json")
PLATT = {"R1": "zeros_6746000.dat", "R2": "zeros_55046000.dat", "R3": "zeros_412046000.dat",
         "R4": "zeros_3047546000.dat", "R5": "zeros_22522946000.dat"}
EPS101 = 2.0 ** -101


# ---------------------------------------------------------------- Platt I/O (float heights; offsets kept relative)
def read_platt_heights(path):
    """All zeros of a Platt file as float64 heights t0_block + Z·2^-101 (Z exact integer; the float error at 2.25e10 is
    ≤ 4e-6, i.e. ≤ 1.5e-5 of a mean spacing — negligible for pair counts with bumps of width ≥ 0.15 spacings)."""
    out = []
    with open(path, "rb") as f:
        nblocks = struct.unpack("<Q", f.read(8))[0]
        for _ in range(nblocks):
            t0, t1, Nt0, Nt1 = struct.unpack("<ddQQ", f.read(32))
            n = Nt1 - Nt0
            raw = f.read(13 * n)
            Z = 0
            for k in range(n):
                z1, z2, z3 = struct.unpack_from("<QIB", raw, 13 * k)
                Z += (z3 << 96) + (z2 << 64) + z1
                out.append(t0 + Z * EPS101)
    return np.array(out)


def write_platt_heights(path, heights, block_width=100.0):
    """Encode sorted heights in the Platt layout (dyadic Z rounding) — the dry-run round-trip only."""
    h = np.sort(np.asarray(heights, dtype=float))
    edges = np.arange(math.floor(h[0]), h[-1] + block_width, block_width)
    blocks = []
    n_before = 0
    for a, b in zip(edges[:-1], edges[1:]):
        sel = h[(h >= a) & (h < b)]
        blocks.append((a, b, n_before, n_before + len(sel), sel))
        n_before += len(sel)
    with open(path, "wb") as f:
        f.write(struct.pack("<Q", len(blocks)))
        for a, b, n0, n1, sel in blocks:
            f.write(struct.pack("<ddQQ", a, b, n0, n1))
            prev = 0
            for x in sel:
                Z = int(round((x - a) / EPS101))
                d = Z - prev
                prev = Z
                f.write(struct.pack("<QIB", d & ((1 << 64) - 1), (d >> 64) & 0xFFFFFFFF, (d >> 96) & 0xFF))


def roundtrip():
    rng = np.random.default_rng(1)
    h = np.sort(6_746_000.0 + np.cumsum(rng.exponential(0.45, 20_000)))
    p = os.path.join(HERE, "results", "roundtrip_platt.dat")
    os.makedirs(os.path.dirname(p), exist_ok=True)
    write_platt_heights(p, h)
    back = read_platt_heights(p)
    err = float(np.max(np.abs(back - h)))
    os.remove(p)
    out = dict(n=len(h), max_abs_err=err, PASS=bool(len(back) == len(h) and err < 1e-8))
    print(json.dumps(out))
    return out


# ---------------------------------------------------------------- the statistic for a level list with window edges
def mu_hat(levels, edges, name, u, w, kernel_dir, sd_surrogate, rng):
    g = P.geometry(name)
    K = G.CachedKernel(G.kernel_path(kernel_dir, name))
    wr = np.load(G.kernel_path(kernel_dir, name))["wr"]
    cs = []
    for a, b in zip(edges[:-1], edges[1:]):
        t = levels[(levels >= a) & (levels < b)]
        cs.append(G.contributions(t, u, w, g["delta"]))
    c = np.concatenate(cs)
    S = float(c.sum())
    rmt, lot = G.predict_tiling(K, wr, list(edges), u, w, g["delta"])
    mu = (S - rmt) / lot
    bsd = {str(bl): G.boot_sd_sum(c, bl, rng) / abs(lot) for bl in G.BOOT_LEVELS}
    sd = max([sd_surrogate] + list(bsd.values()))
    half = 1.959964 * sd
    return dict(n=int(len(levels)), S=S, RMT=rmt, LOT=lot, mu=mu, sd_surrogate=sd_surrogate, boot_sd=bsd,
                sd_used=sd, ci=[mu - half, mu + half], halfwidth=half,
                A1_growth=[bsd[str(b)] / bsd[str(G.BOOT_LEVELS[0])] for b in G.BOOT_LEVELS])


def verdict(m, resolvable):
    if not resolvable:
        return "NOT RESOLVABLE"
    lo, hi = m["ci"]
    if lo <= 0 <= hi or m["halfwidth"] > 0.5:
        return "NOT RESOLVABLE (achieved)"
    return "PASS" if lo <= 1 <= hi else "FAIL"


def read(name):
    if not os.path.exists(SEAL):
        raise SystemExit("REFUSED: no PH2R2_SEAL_1.0.json — fresh zeros are not decoded before the seal")
    seal = json.load(open(SEAL))
    for f, h in seal["code_sha256"].items():
        if hashlib.sha256(open(os.path.join(HERE, f), "rb").read()).hexdigest() != h:
            raise SystemExit(f"REFUSED: {f} differs from the sealed code")
    path = os.path.join(HERE, "data", "platt", PLATT[name])
    if hashlib.md5(open(path, "rb").read()).hexdigest() != seal["platt_md5"][PLATT[name]]:
        raise SystemExit(f"REFUSED: {path} md5 differs from the pin")
    b = seal["bins"][name]
    u, w = seal["primary"]
    levels = read_platt_heights(path)
    g = P.geometry(name)
    edges = np.array([g["t0"], g["t1"]])
    rng = np.random.default_rng(seal["seed"])
    m = mu_hat(levels, edges, name, u, w, os.path.join(HERE, seal["kernel_dir"]), b["sd_surrogate"], rng)
    m["verdict"] = verdict(m, b["resolvable"])
    m["power_arm_mu0_excluded"] = bool(not (m["ci"][0] <= 0 <= m["ci"][1]))
    os.makedirs(os.path.join(HERE, "results", "read"), exist_ok=True)
    json.dump(m, open(os.path.join(HERE, "results", "read", f"{name}.json"), "w"), indent=1, default=float)
    print(name, m["verdict"], round(m["mu"], 4), [round(x, 4) for x in m["ci"]], flush=True)


if __name__ == "__main__":
    {"read": lambda: read(sys.argv[2]), "roundtrip": roundtrip}[sys.argv[1]]()
