"""Survey arc D3 runner: the measurement.  COMMITTED GENERATOR of
survey/d3_measured.json.  Freeze check first; every threshold from the seal;
verdicts only through verdict_lattice.resolve (rulings-as-code)."""

import hashlib
import json
import sys

import numpy as np

SV = "/home/combust/fmexplorer/criticality_tool/survey"
sys.path.insert(0, SV)

SEAL = json.load(open(f"{SV}/prereg_sealed.json"))


def _blob(path):
    d = open(path, "rb").read()
    return hashlib.sha1(b"blob %d\0" % len(d) + d).hexdigest()


for f, sha in SEAL["code_freeze_blob_shas"].items():
    cur = _blob(f"{SV}/{f}")
    assert cur == sha, (f"FREEZE VIOLATION {f}: {cur[:12]} != {sha[:12]} — "
                        "dated addendum required")

from survey_io import load_cat, load_randoms_split          # noqa: E402
from tiling import build_tiles, tile_points                 # noqa: E402
from estimators import g_ratio, cells_F                     # noqa: E402
from verdict_lattice import tile_class, resolve             # noqa: E402

manifest = json.load(open(f"{SV}/MANIFEST.json"))
kag_ok = json.load(open(f"{SV}/mask_kag_measured.json"))["PASS"]
d2_ok = json.load(open(f"{SV}/d2_gates_measured.json"))["PASS"]
L_LIST = SEAL["scale_ranges"]["sigma2_L_deg"]
b0, b1, db = SEAL["scale_ranges"]["pcf_bins_deg"]
BINS = np.arange(b0, b1 + 1e-9, db)
Z_CLASS = SEAL["lattice"]["Z_CLASS"]

# square-cell pair-distance mass per pcf bin (MC once, unit square, scaled)
rng = np.random.default_rng(7)
_u = rng.uniform(size=(400_000, 4))
_d_unit = np.hypot(_u[:, 0] - _u[:, 2], _u[:, 1] - _u[:, 3])


def q_mass(L):
    d = _d_unit * L
    h, _ = np.histogram(d, bins=BINS)
    return h / len(d)


results = {"seal_cited": f"{SV}/prereg_sealed.json",
           "gates": dict(mask_kag=kag_ok, d2=d2_ok), "slices": {}}

for sname, (zlo, zhi) in SEAL["slices"].items():
    print(f"=== slice {sname} {zlo}-{zhi} ===", flush=True)
    data = load_cat("LRG_NGC_clustering.dat.fits", zlo, zhi)
    nulls = load_randoms_split("null_half", zlo, zhi, manifest)
    kagr = load_randoms_split("kag_half", zlo, zhi, manifest)
    null_per_deg2 = nulls["w"].sum() / 3464.9234532477117
    tiles = build_tiles(nulls["ra"], nulls["dec"], nulls["w"], null_per_deg2)
    gm = data["w"].mean()
    srow = dict(n_data=int(len(data["w"])), tiles={})
    tile_calls, excluded = {}, []
    for t in tiles:
        xy_d, w_d = tile_points(data, t)
        if len(xy_d) < 500:
            excluded.append(dict(tile=(t["ra0"], t["dec0"]), why="n<500"))
            continue
        if abs(w_d.mean() / gm - 1.0) > 0.05:      # sealed weight budget
            excluded.append(dict(tile=(t["ra0"], t["dec0"]), why="weight"))
            continue
        xy_r, w_r = tile_points(nulls, t)
        ext = (xy_r[:, 0].min(), xy_r[:, 0].max(),
               xy_r[:, 1].min(), xy_r[:, 1].max())
        g = g_ratio(xy_d, w_d, xy_r, w_r, BINS)
        Fs, zs = [], []
        for L in L_LIST:
            out = cells_F(xy_d, w_d, xy_r, w_r, L, ext)
            Fs.append(out)
            zs.append((out["F"] - 1.0) / out["sigma_F"])
        call = tile_class(zs, Z_CLASS)
        key = f"{t['ra0']:.0f},{t['dec0']:.0f}"
        tile_calls[key] = call
        # descriptive Sigma2-from-pcf + obstruction envelope, per sealed L
        pcf_rows = []
        for L, out in zip(L_LIST, Fs):
            q = q_mass(L)
            gm1 = np.nan_to_num(g["g"] - 1.0)
            F_pcf = 1.0 + out["mean_E"] * float((gm1 * q).sum())
            sig_int = out["mean_E"] * float(np.sqrt(
                ((q / np.sqrt(np.maximum(g["DD_eff"], 1.0)))**2).sum()))
            pcf_rows.append(dict(L=L, F_pcf=float(F_pcf),
                                 sigma_int=float(sig_int)))
        srow["tiles"][key] = dict(
            call=call, n_d=int(len(xy_d)),
            F=[dict(L=f["L"], F=f["F"], sigma=f["sigma_F"],
                    n_cells=f["n_cells"]) for f in Fs],
            g=g["g"].tolist(), g_centers=g["centers"].tolist(),
            DD_eff=np.nan_to_num(g["DD_eff"]).tolist(),
            K_ratio=np.nan_to_num(g["K_ratio"]).tolist(),
            pcf_route=pcf_rows)
        print(f"  {key}: n={len(xy_d)} call={call} "
              f"F={['%.2f' % f['F'] for f in Fs]}", flush=True)
    srow["excluded"] = excluded

    # pooled per-L F with tile-scatter errors (tiles = independent axis)
    pool = {}
    for i, L in enumerate(L_LIST):
        vals = np.array([v["F"][i]["F"] for v in srow["tiles"].values()])
        pool[str(L)] = dict(mean=float(vals.mean()),
                            se=float(vals.std(ddof=1) / np.sqrt(len(vals))),
                            n_tiles=int(len(vals)))
    srow["pooled_F"] = pool
    # exponent: weighted LS of log(F-1) vs log L; drift = fit chi2 (1 dof)
    x = np.log(np.array(L_LIST))
    y = np.array([pool[str(L)]["mean"] - 1.0 for L in L_LIST])
    sy = np.array([pool[str(L)]["se"] for L in L_LIST])
    m = y > 0
    if m.sum() == 3:
        ylog, sylog = np.log(y), sy / y
        w = 1.0 / sylog**2
        A = np.vstack([x, np.ones_like(x)]).T
        C = np.linalg.inv(A.T @ (A * w[:, None]))
        beta = C @ A.T @ (w * ylog)
        resid = ylog - A @ beta
        chi2 = float((w * resid**2).sum())
        slope, slope_err = float(beta[0]), float(np.sqrt(C[0, 0]))
    else:
        slope, slope_err, chi2 = float("nan"), float("nan"), 0.0
    srow["exponent"] = dict(slope=slope, err=slope_err, drift_chi2=chi2,
                            note="slope of log(F-1) vs log L; F-1 ~ L^slope")

    # obstruction check per sealed envelope (pooled across tiles per L)
    obstruction = False
    for i, L in enumerate(L_LIST):
        fc = pool[str(L)]["mean"]
        fp = np.mean([v["pcf_route"][i]["F_pcf"]
                      for v in srow["tiles"].values()])
        se = np.hypot(pool[str(L)]["se"],
                      np.mean([v["pcf_route"][i]["sigma_int"]
                               for v in srow["tiles"].values()]))
        srow.setdefault("route_compare", []).append(
            dict(L=L, F_cells=float(fc), F_pcf=float(fp), se=float(se),
                 excess=float(abs(fc - fp) / se)))
    # class calls of the two routes: both super-Poissonian? then no
    # obstruction regardless of amplitude mismatch within envelope logic
    exc = max(r["excess"] for r in srow["route_compare"])
    routes_disagree = any((r["F_pcf"] - 1.0) * (r["F_cells"] - 1.0) < 0
                          for r in srow["route_compare"])
    obstruction = bool(routes_disagree and exc > 3.0)

    sub_fired = any(c == "SUB_FLAG" for c in tile_calls.values())
    hold_cleared = False
    if sub_fired:
        print("  §0.1 SURPRISE CLAUSE FIRED — hold state; audit is next "
              "action, no banking", flush=True)
    power_ok = (len(tile_calls) >= 20 and
                all(sum(v["F"][i]["n_cells"] for v in srow["tiles"].values())
                    >= 500 for i in range(len(L_LIST))))
    verdict = resolve(sname, gates_green=bool(kag_ok and d2_ok),
                      power_ok=power_ok, tile_calls=tile_calls,
                      sub_fired=sub_fired, hold_cleared=hold_cleared,
                      drift_chi2=chi2, obstruction_excess=obstruction,
                      seal=SEAL["lattice"])
    srow["verdict"] = verdict
    print(f"slice {sname}: VERDICT {verdict['primary']} "
          f"flags={verdict['flags']} | {verdict['detail']} | "
          f"slope={slope:.3f}±{slope_err:.3f} chi2={chi2:.2f}", flush=True)
    results["slices"][sname] = srow

json.dump(results, open(f"{SV}/d3_measured.json", "w"), indent=1)
print("D3 DONE", flush=True)
