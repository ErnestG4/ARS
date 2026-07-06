"""
cross_substrate/goes_flares.py — GOES soft X-ray solar flares as the second SOC substrate (G5).

Pairs with ComCat earthquakes: two self-organised-criticality systems (one tectonic, one solar) asked
the same clustering-vs-quasiperiodic question. Solar flares have power-law waiting times and a live
Poisson-vs-memory debate; the solar cycle is a second within-substrate knob (solar MAX → clustered,
solar MIN → more Poisson). Flare peak times are the point process; GOES class is the magnitude mark.

Source: HEK (Heliophysics Events Knowledgebase) GOES/SWPC flare list — open, no registration.
  https://www.lmsal.com/hek/her?cmd=search&type=column&event_type=fl&frm_name=SWPC&...  (paged JSON)
Reuses the earthquake fingerprint / clustering / irreversibility machinery from comcat_port.

Usage:
  python3 goes_flares.py --fetch --start 1996-01-01 --end 2025-01-01     # download to coordinates/goes-flares.jsonl
  python3 goes_flares.py --analyze                                       # fingerprint + solar-cycle split
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time as _time
import urllib.parse
import urllib.request
from datetime import datetime, timedelta, timezone

import numpy as np

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_HERE)
for p in (_HERE, _ROOT):
    if p not in sys.path:
        sys.path.insert(0, p)

from axes import compute_family_I, compute_family_II                       # noqa: E402
import comcat_port as CP                                                    # reuse machinery  # noqa: E402

RAW = os.path.join(_HERE, "coordinates", "goes-flares.jsonl")
HEK = "https://www.lmsal.com/hek/her?"
DAY = 86400.0


# ── fetch (paged, sequential) ─────────────────────────────────────────────────
def _get(url, retries=5):
    last = None
    for k in range(retries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "ars-goes/1.0"})
            with urllib.request.urlopen(req, timeout=120) as r:
                return r.read()
        except Exception as e:                         # noqa: BLE001
            last = e; _time.sleep(2.0 * (k + 1))
    raise RuntimeError(f"GET failed: {url}\n  {last}")


def _goes_class_to_flux(cls):
    """'M5.0' -> 5e-5 W/m². Returns nan if unparseable."""
    if not cls:
        return np.nan
    cls = cls.strip().upper()
    mult = {"A": 1e-8, "B": 1e-7, "C": 1e-6, "M": 1e-5, "X": 1e-4}
    if cls[0] not in mult:
        return np.nan
    try:
        return mult[cls[0]] * float(cls[1:] or "1")
    except ValueError:
        return np.nan


# HEK aggregates many feature-recognition methods (FRMs) — the SAME physical flare appears from
# multiple FRMs, dominated by the "Flare Detective - Trigger Module" auto-trigger (~2000/month vs the
# canonical NOAA "SWPC" list's ~170/month). Critically, the frm_name= QUERY param does NOT filter
# server-side (returns all FRMs regardless), so apparent "strong clustering" in a naive pull is mostly
# duplicate-flare contamination (~29% of inter-event gaps <60s). We filter to a single FRM CLIENT-SIDE.
# The canonical clean list is "SWPC" (NOAA SWPC human-vetted GOES flare events). This is the solar
# analogue of the seismic Mc completeness gate. (See COMCAT_SOC_FINDINGS §G5 dedup note.)
CLEAN_FRM = "SWPC"


def fetch(start, end, frm=CLEAN_FRM):
    """Page HEK month-by-month, keep only the canonical single-FRM flare list (client-side filter,
    since the frm_name query param does not actually filter), one JSON record per unique peaktime."""
    os.makedirs(os.path.dirname(RAW), exist_ok=True)
    a = datetime.fromisoformat(start).replace(tzinfo=timezone.utc)
    end = datetime.fromisoformat(end).replace(tzinfo=timezone.utc)
    n_total = 0
    seen = set()
    with open(RAW, "w") as out:
        while a < end:
            b = (a.replace(day=28) + timedelta(days=8)).replace(day=1)  # next month start
            b = min(b, end)
            p = {"cmd": "search", "type": "column", "event_type": "fl",
                 "event_coordsys": "helioprojective",
                 "x1": "-1200", "x2": "1200", "y1": "-1200", "y2": "1200",
                 "event_starttime": a.strftime("%Y-%m-%dT00:00:00"),
                 "event_endtime": b.strftime("%Y-%m-%dT00:00:00"),
                 "result_limit": "20000", "cosec": "2", "return":
                 "event_peaktime,fl_goescls,fl_peakflux,frm_name"}
            url = HEK + urllib.parse.urlencode(p)
            try:
                js = json.loads(_get(url).decode("utf-8", "replace"))
            except Exception as e:                     # noqa: BLE001
                sys.stderr.write(f"  parse fail {a:%Y-%m}: {e}\n"); a = b; continue
            res = js.get("result", [])
            kept = 0
            for r in res:
                if r.get("frm_name") != frm:           # CLIENT-SIDE single-FRM filter (dedup FRMs)
                    continue
                pk = r.get("event_peaktime") or ""
                cls = r.get("fl_goescls") or ""
                if not pk or pk in seen:
                    continue
                seen.add(pk)
                try:
                    ts = datetime.fromisoformat(pk.replace("Z", "+00:00")
                                                .replace(" ", "T")).replace(
                        tzinfo=timezone.utc).timestamp()
                except Exception:                      # noqa: BLE001
                    continue
                out.write(json.dumps({"t": ts, "cls": cls,
                                      "flux": _goes_class_to_flux(cls)}) + "\n")
                n_total += 1; kept += 1
            print(f"  {a:%Y-%m}: {len(res)} all-FRM -> {kept} {frm} (total {n_total})")
            a = b
    print(f"[done] {n_total} {frm} flares -> {RAW}")


def load():
    t, flux, cls = [], [], []
    with open(RAW) as f:
        for line in f:
            r = json.loads(line)
            t.append(r["t"]); flux.append(r.get("flux", np.nan)); cls.append(r.get("cls", ""))
    t = np.asarray(t); o = np.argsort(t)
    return dict(t=t[o], flux=np.asarray(flux)[o], cls=np.asarray(cls)[o])


# ── analysis ──────────────────────────────────────────────────────────────────
def _phase_split(t):
    """Data-driven solar-cycle split: annual flare counts; top-tercile years = MAX, bottom = MIN."""
    yrs = np.array([datetime.fromtimestamp(x, tz=timezone.utc).year for x in t])
    uy, cnt = np.unique(yrs, return_counts=True)
    rate = dict(zip(uy.tolist(), cnt.tolist()))
    hi = np.quantile(list(rate.values()), 2 / 3)
    lo = np.quantile(list(rate.values()), 1 / 3)
    max_yrs = {y for y, c in rate.items() if c >= hi}
    min_yrs = {y for y, c in rate.items() if c <= lo}
    return (np.array([y in max_yrs for y in yrs]),
            np.array([y in min_yrs for y in yrs]),
            {"rate_per_year": rate, "max_years": sorted(max_yrs), "min_years": sorted(min_yrs)})


def analyze():
    cat = load()
    t = cat["t"]
    yr = (t.max() - t.min()) / (365.25 * DAY)
    print(f"[goes] n={t.size} span={yr:.1f}yr rate={t.size/yr:.0f}/yr")
    rec = {"substrate": "goes-flares", "n": int(t.size), "span_years": float(yr)}

    print("=== full fingerprint ===")
    su = CP.local_rate_unfold(t, W=51)
    unf = CP.clustering_from_spacings(su) if su is not None else None
    rec["full"] = {"family_I": compute_family_I(t),
                   "family_II": compute_family_II(t),
                   "clustering": CP.clustering_readout(t),
                   "poisson_surrogate": CP.poisson_surrogate(t),
                   "local_rate_unfolded": unf,
                   "irreversibility": CP.irreversibility(t)}
    fi = rec["full"]["family_I"]; cr = rec["full"]["clustering"]; sur = rec["full"]["poisson_surrogate"]
    print(f"  ks_gue={fi['I.5_ks_gue']:.3f} ks_poisson={fi['I.7_ks_poisson']:.3f} "
          f"brody_q={fi['I.8_brody_q']} BR_rho={fi['I.9_berry_robnik_rho']}")
    print(f"  CLUSTERING (homogeneous) mass<0.3={cr['mass_lt_0p3']:.3f} "
          f"(Poisson-surr {sur['mass_lt_0p3_med']:.3f}) CV={cr['cv']:.2f}")
    if unf:
        print(f"  CLUSTERING (local-rate unfolded) mass<0.3={unf['mass_lt_0p3']:.3f} CV={unf['cv']:.2f} "
              f"-> {'GENUINE memory above inhom-Poisson floor (~0.26/1.0)' if unf['cv']>1.1 else 'collapses to Poisson: was rate envelope'}")

    print("=== solar-cycle knob (MAX vs MIN years) ===")
    is_max, is_min, info = _phase_split(t)
    rec["cycle_split"] = {"info": info}
    for name, msk in (("max", is_max), ("min", is_min)):
        tt = t[msk]
        if tt.size < 50:
            print(f"  {name}: n={tt.size} insufficient"); continue
        # local-rate unfold WITHIN the phase removes both the cycle envelope and the
        # pooling-across-disjoint-years gap artifact (raw CV is meaningless across year-sets).
        su = CP.local_rate_unfold(tt, W=51)
        unf = CP.clustering_from_spacings(su) if su is not None else None
        fp = {"n": int(tt.size), "family_I": compute_family_I(tt),
              "clustering_homogeneous": CP.clustering_readout(tt),
              "clustering_local_rate_unfolded": unf}
        rec["cycle_split"][name] = fp
        if unf:
            print(f"  {name} (n={tt.size}): UNFOLDED mass<0.3={unf['mass_lt_0p3']:.3f} CV={unf['cv']:.2f} "
                  f"(homogeneous CV={fp['clustering_homogeneous']['cv']:.1f} = pooling artifact, ignore)")
    print("  → genuine-memory comparison is on the UNFOLDED readout (homogeneous CV is a "
          "pooling-across-disjoint-cycle-years artifact). Expectation: MAX ≥ MIN residual memory.")

    out = os.path.join(_HERE, "coordinates", "goes-fingerprint.jsonl")
    with open(out, "a") as f:
        f.write(json.dumps(rec, default=str) + "\n")
    print(f"[banked] {out}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--fetch", action="store_true")
    ap.add_argument("--analyze", action="store_true")
    ap.add_argument("--start", default="1996-01-01")
    ap.add_argument("--end", default="2025-01-01")
    a = ap.parse_args()
    if a.fetch:
        fetch(a.start, a.end)
    if a.analyze:
        analyze()
    if not (a.fetch or a.analyze):
        ap.error("need --fetch and/or --analyze")


if __name__ == "__main__":
    main()
