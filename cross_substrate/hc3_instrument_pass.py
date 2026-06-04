"""
cross_substrate/hc3_instrument_pass.py — first real-substrate lensing-ledger pass
for instrument_confound.py, on CRCNS hc-3 pyramidal units.

Per unit: bracket the dead-time apparatus between a TIGHT null (hardware/sorter
refractory ~2 ms) and a WIDE null (empirical P0.5-ISI floor, rel_err widened to
0.5) — the empirical floor over-absorbs biological refractoriness, so the bracket
records a ZONE (SUBSTRATE_ROBUST / INDETERMINATE / APPARATUS_EXPLAINS), not a
binary. Plus thinning sweep + method-perturbation + the low-efficiency-Poisson
caveat. Matched-n nulls (contiguous segment cap, NOT decimation — decimation would
Poissonize the bursts) so residual z honestly reflects sample size.

Run: hc3_instrument_pass.py --session <dir> --region CA3 --celltype p [--workers N]
"""
from __future__ import annotations

import argparse
import glob
import json
import os
import sys
import time
import xml.etree.ElementTree as ET
from concurrent.futures import ProcessPoolExecutor
from dataclasses import asdict
from datetime import date

import numpy as np
import pandas as pd

_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)

import instrument_confound as ic

CACHE = os.path.expanduser("~/fmexplorer/crcns_cache")
META = os.path.join(CACHE, "docs/hc3-metadata-tables/hc3-cell.csv")
COORD = os.path.join(_HERE, "coordinates")
CAP = 5000              # contiguous-segment spike cap (matched empirical+null n)
N_SEEDS = 16
HW_REFRACTORY_S = 0.002  # hardware/sorter absolute refractory (tight-null τ)

_CTYPE = {"p": "excitatory", "i": "inhibitory", "n": "unclassified"}


def _coarse(r):
    r = str(r)
    return "EC" if r.startswith("EC") else (r if r in ("CA1", "CA3", "DG") else "other")


def load_cellmap():
    c = pd.read_csv(META, header=None)
    c.columns = ["id", "topdir", "animal", "ele", "clu", "region", "nexc", "ninh",
                 "exc", "inh", "excd", "inhd", "fr", "tfr", "type"]
    m = {}
    for _, r in c.iterrows():
        m[(r["topdir"], int(r["ele"]), int(r["clu"]))] = (
            _coarse(r["region"]), _CTYPE.get(str(r["type"]), "unclassified"))
    return m


def _read_ints(p):
    with open(p) as fh:
        return np.array(fh.read().split(), dtype=np.int64)


def parse_units(sdir, topdir, session, cellmap):
    xmls = glob.glob(os.path.join(sdir, "*.xml"))
    sr = 20000.0
    if xmls:
        t = ET.parse(xmls[0]).getroot().findtext(".//acquisitionSystem/samplingRate")
        sr = float(t) if t else 20000.0
    units, tmax = [], 0.0
    for resf in sorted(glob.glob(os.path.join(sdir, "*.res.*"))):
        N = int(resf.rsplit(".", 1)[1])
        cluf = resf.replace(".res.", ".clu.")
        if not os.path.exists(cluf):
            continue
        res, clu = _read_ints(resf), _read_ints(cluf)
        clu = clu[1:] if clu.size == res.size + 1 else (clu[1:] if clu.size > res.size else clu)
        if res.size == 0:
            continue
        tmax = max(tmax, res.max() / sr)
        for cc in np.unique(clu):
            if cc < 2:
                continue
            spk = np.sort(res[clu == cc]) / sr
            reg, ct = cellmap.get((topdir, N, int(cc)), ("other", "unclassified"))
            units.append({"ele": N, "clu": int(cc), "region": reg, "celltype": ct, "spk": spk})
    return units, tmax, sr


def _unit_record(arg):
    spk, meta = arg
    full = np.sort(np.asarray(spk, dtype=np.float64))
    n_raw = full.size
    # contamination (additive apparatus) computed on the FULL cluster — RPV is a
    # whole-cluster isolation property, not a windowed one. The one apparatus
    # direction that can FAKE clustering.
    contam = ic.refractory_violation_rate(full, HW_REFRACTORY_S)
    contam["flag"] = ic.contamination_flag(contam.get("rpv"))
    # contiguous segment (preserve burst structure; NEVER decimate)
    spk = full[:CAP] if full.size > CAP else full
    n = spk.size
    m = ic.mean_isi(spk)
    if not np.isfinite(m) or m <= 0 or n < 200:
        return None
    floor = ic.estimate_deadtime_floor(spk, pct=0.5, rel_err=0.5)
    tau_wide = floor["tau_frac"]
    if tau_wide is None or tau_wide <= 0:
        return None
    tau_tight = HW_REFRACTORY_S / m
    if tau_tight >= tau_wide:                     # keep tight strictly below wide
        tau_tight = 0.5 * tau_wide
    br = ic.apparatus_bracket(spk, tau_tight, tau_wide,
                              rel_err_tight=0.2, rel_err_wide=0.5, n_seeds=N_SEEDS)
    axes_raw = ic.axis_values(spk)
    thin = ic.thin_sweep(spk)
    prov = ic.Provenance(
        substrate=f"hc3-{meta['region']}", dataset_id=meta["dataset_id"],
        n_events=n, sampling_rate_hz=meta["sr"],
        dead_time=floor.get("floor_abs"), dead_time_rel_err=0.5,
        refractory=HW_REFRACTORY_S, obs_window=float(spk[-1] - spk[0]),
        sort_label="neuroscope/klusters", notes=meta["notes"])
    rec = dict(
        provenance=asdict(prov), n_raw=n_raw,
        celltype=meta["celltype"], ele=meta["ele"], clu=meta["clu"],
        axes_raw=axes_raw,
        tau_tight_frac=tau_tight, tau_wide_frac=tau_wide,
        bracket={a: {"zone": br[a]["zone"], "z_vs_tight": round(br[a]["z_vs_tight"], 2),
                     "z_vs_wide": round(br[a]["z_vs_wide"], 2)} for a in br},
        thinning_flags={a: thin[a]["flag"] for a in thin},
        contamination=contam,
        computed_date=date.today().isoformat())
    return rec


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--session", required=True, help="session dir containing *.res.*")
    ap.add_argument("--region", default="CA3")
    ap.add_argument("--celltype", default="p", choices=["p", "i", "n"])
    ap.add_argument("--workers", type=int, default=10)
    ap.add_argument("--max-units", type=int, default=0, help="0 = all")
    a = ap.parse_args()

    sdir = a.session
    parts = sdir.rstrip("/").split("/")
    topdir, session = parts[-2], parts[-1]
    cellmap = load_cellmap()
    units, tmax, sr = parse_units(sdir, topdir, session, cellmap)
    want_ct = _CTYPE[a.celltype]
    sel = [u for u in units if u["region"] == a.region and u["celltype"] == want_ct
           and u["spk"].size >= 200]
    if a.max_units:
        sel = sel[:a.max_units]
    print(f"hc-3 instrument pass — {session} {a.region} {want_ct}: "
          f"{len(sel)} units (of {len(units)} total), session {tmax:.0f}s, sr={sr:.0f}")
    if not sel:
        print("no units"); return

    args = [(u["spk"], {"region": a.region, "celltype": want_ct, "ele": u["ele"],
                        "clu": u["clu"], "sr": sr,
                        "dataset_id": f"{session}_{a.region}_e{u['ele']}c{u['clu']}",
                        "notes": f"CRCNS hc-3 {topdir}/{session}; Neuroscope; "
                                 f"hw-refractory {HW_REFRACTORY_S*1e3:.0f}ms tight, "
                                 f"P0.5-ISI-floor wide"})
            for u in sel]

    t0 = time.perf_counter()
    recs = []
    with ProcessPoolExecutor(max_workers=a.workers) as ex:
        for r in ex.map(_unit_record, args):
            if r is not None:
                recs.append(r)
    dt = time.perf_counter() - t0

    ledger = os.path.join(COORD, f"instrument_lensing_ledger_hc3_{a.region}_{a.celltype}.jsonl")
    with open(ledger, "w") as f:
        for r in recs:
            f.write(json.dumps(r) + "\n")

    # ── summary: zone distribution per axis (the headline) ──
    print(f"\n{len(recs)} units processed in {dt/60:.1f} min → {os.path.basename(ledger)}")
    axes = ic.AXES
    print("\nZONE DISTRIBUTION (per axis, across units):")
    print(f"  {'axis':14s} {'SUBSTRATE':>10s} {'INDETERM':>9s} {'APPARATUS':>10s} {'NULL':>5s}")
    for ax in axes:
        zc = {"SUBSTRATE_ROBUST": 0, "INDETERMINATE": 0, "APPARATUS_EXPLAINS": 0, "NULL": 0}
        for r in recs:
            z = r["bracket"].get(ax, {}).get("zone")
            if z in zc:
                zc[z] += 1
        print(f"  {ax:14s} {zc['SUBSTRATE_ROBUST']:>10d} {zc['INDETERMINATE']:>9d} "
              f"{zc['APPARATUS_EXPLAINS']:>10d} {zc['NULL']:>5d}")
    # residual z (vs WIDE null) on the clustering axis — the power readout
    for ax in ("I.11_mass03", "I.10_cv", "I.5_ks_gue"):
        zs = [r["bracket"][ax]["z_vs_wide"] for r in recs if ax in r["bracket"]]
        if zs:
            zs = np.asarray(zs)
            print(f"\n  {ax} residual z vs WIDE null: "
                  f"median={np.median(zs):.1f} IQR=[{np.percentile(zs,25):.1f},"
                  f"{np.percentile(zs,75):.1f}]  (frac z>2.5: {np.mean(zs>2.5):.2f})")
    # ── contamination cross-tab: the additive apparatus that FAKES clustering ──
    # Of the units that read SUBSTRATE_ROBUST on clustering (mass03), how many are
    # merge suspects? Those verdicts are contamination, not substrate.
    clus_robust = [r for r in recs
                   if r["bracket"].get("I.11_mass03", {}).get("zone") == "SUBSTRATE_ROBUST"]
    cc = {"CLEAN": 0, "MARGINAL": 0, "MERGE_SUSPECT": 0, "UNKNOWN": 0}
    for r in clus_robust:
        cc[r["contamination"].get("flag", "UNKNOWN")] += 1
    print(f"\nCONTAMINATION (additive apparatus — the only one that fakes clustering):")
    print(f"  refractory-violation threshold = {HW_REFRACTORY_S*1e3:.0f} ms")
    print(f"  of {len(clus_robust)} clustering-SUBSTRATE_ROBUST units: "
          f"CLEAN={cc['CLEAN']} MARGINAL={cc['MARGINAL']} MERGE_SUSPECT={cc['MERGE_SUSPECT']}")
    rpvs = [r["contamination"]["rpv"] for r in recs if r["contamination"].get("rpv") is not None]
    if rpvs:
        rpvs = np.asarray(rpvs)
        print(f"  RPV across units: median={np.median(rpvs)*100:.2f}%  max={rpvs.max()*100:.2f}%")
    suspects = [r for r in clus_robust if r["contamination"].get("flag") == "MERGE_SUSPECT"]
    if suspects:
        print(f"  MERGE_SUSPECT units (clustering verdict is contamination, not substrate):")
        for r in suspects:
            print(f"    e{r['ele']}c{r['clu']}: RPV={r['contamination']['rpv']*100:.2f}% "
                  f"n_raw={r['n_raw']}")
    print("\nNote: efficiency not estimated for hc-3 (no ground-truth detection model) → "
          "Poisson-ambiguity caveat not applied; thinning flags recorded per unit.")


if __name__ == "__main__":
    main()
