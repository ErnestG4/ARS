"""
cross_substrate/comcat_port.py — USGS ComCat earthquake catalog as an ARS calibrator-zoo substrate.

Near-ground-truth: earthquakes are strongly clustered (ETAS / Omori-Utsu). The question is not "are
quakes clustered" but whether the ARS fingerprint RECOVERS it, WHERE it lands on GUE↔Poisson, and HOW
FAR declustering moves it (the calibration: direction of motion known a priori).

  G1  clustered read   — fingerprint (Family I) of the full catalog event-time sequence + clustering
                         readout (mass<τ, CV) + rate-matched Poisson surrogate floor.
  G2  declustered read — Gardner-Knopoff windowing (+ window-scale sensitivity ×0.5/×2 robustness).
                         Fingerprint should move TOWARD Poisson. Quantify displacement.
  G3  single-fault     — a regional box; if characteristic-quake recurrence gave level-repulsion would
                         the fingerprint see it? N-LIMITED -> no-false-positive regime at best. Flagged.
  G4  directionality   — (a) pooled-NNS forward ≡ reversed (band-invariance, §7.ter.10), shown numerically;
                         (b) ordering-sensitive irreversibility (spacing-increment skew + lagged-product
                         asymmetry, vs shuffled surrogate); (c) magnitude-conditioned Omori rate asymmetry
                         (rate after a mainshock ≫ before). The GAP = directionality NNS is blind to.

One-sided-fitter caveat: Brody q ∈ [0,1] and Berry-Robnik ρ ∈ [0,1] span only Poisson→GOE; they are
blind to super-Poisson clustering and rail at 0. Clustering is read on the Poisson-EXCESS side.

Usage: python3 comcat_port.py --csv coordinates/comcat/global_m45.csv [--fault-csv ...]
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timezone

import numpy as np

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_HERE)
for p in (_HERE, _ROOT):
    if p not in sys.path:
        sys.path.insert(0, p)

from axes import compute_family_I, compute_family_II, canonical_spacings  # noqa: E402
from universality import nns_cdf_poisson, nns_cdf_gue, nns_cdf_goe         # noqa: E402

R_EARTH = 6371.0
DAY = 86400.0


# ── catalog I/O ───────────────────────────────────────────────────────────────
def load_catalog(path):
    """Return dict of arrays sorted by time: t (s, unix), mag, lat, lon, depth."""
    t, mag, lat, lon, dep = [], [], [], [], []
    with open(path) as f:
        header = f.readline().rstrip("\n").split(",")
        ix = {k: header.index(k) for k in ("time", "mag", "latitude", "longitude")}
        idep = header.index("depth") if "depth" in header else None
        for line in f:
            c = line.rstrip("\n").split(",")
            try:
                ts = datetime.fromisoformat(c[ix["time"]].replace("Z", "+00:00")).timestamp()
                m = float(c[ix["mag"]]) if c[ix["mag"]] else np.nan
                la = float(c[ix["latitude"]]); lo = float(c[ix["longitude"]])
            except Exception:                         # noqa: BLE001
                continue
            t.append(ts); mag.append(m); lat.append(la); lon.append(lo)
            dep.append(float(c[idep]) if idep is not None and c[idep] else np.nan)
    t = np.asarray(t); order = np.argsort(t)
    return dict(t=t[order], mag=np.asarray(mag)[order],
                lat=np.asarray(lat)[order], lon=np.asarray(lon)[order],
                depth=np.asarray(dep)[order])


# ── fingerprint + clustering readout ──────────────────────────────────────────
def local_rate_unfold(times, W=51):
    """Inhomogeneous-Poisson null: normalize each inter-event time by the LOCAL event rate
    (sliding W-event window), removing the smooth rate envelope. Under inhomogeneous Poisson the
    result → unit-rate exponential (mass<0.3≈0.26, CV≈1); residual clustering above that floor is
    GENUINE memory/triggering, not the rate envelope. Returns unit-mean locally-normalized spacings.

    This is the right null for rate-nonstationary SOC substrates (solar-cycle flare modulation,
    network-growth seismicity): a homogeneous-Poisson surrogate would mistake the envelope for
    clustering (ars-rate-dependence lesson / within-substrate-before-pooled)."""
    t = np.sort(np.asarray(times, float)); n = t.size
    if n < W + 2:
        return None
    h = W // 2
    lam = np.empty(n - 1)
    for i in range(n - 1):
        a = max(0, i - h); b = min(n - 1, i + h)
        span = t[b] - t[a]
        lam[i] = (b - a) / span if span > 0 else np.nan
    s = np.diff(t) * lam
    s = s[np.isfinite(s) & (s > 0)]
    return s / s.mean() if s.size else None


def clustering_from_spacings(s):
    """Poisson-excess-side readout from a ready spacing array (e.g. local-rate-unfolded), NO re-diff."""
    s = np.asarray(s, float); s = s[np.isfinite(s) & (s > 0)]
    if s.size < 20:
        return None
    s = s / s.mean()
    return dict(
        n_spacings=int(s.size),
        mass_lt_0p1=float((s < 0.1).mean()),
        mass_lt_0p3=float((s < 0.3).mean()),
        mass_lt_1=float((s < 1.0).mean()),
        cv=float(np.std(s) / np.mean(s)),
        max_over_mean=float(s.max()),
    )


def clustering_readout(times):
    """Poisson-excess-side readout (where clustering lives; one-sided fitters can't see it).
    Takes POSITIONS/event-times (diffs internally). For an already-computed spacing array
    (e.g. local_rate_unfold output) use clustering_from_spacings to avoid a double-diff."""
    s = canonical_spacings(times)
    if s.size < 20:
        return None
    return dict(
        n_spacings=int(s.size),
        mass_lt_0p1=float((s < 0.1).mean()),
        mass_lt_0p3=float((s < 0.3).mean()),
        mass_lt_1=float((s < 1.0).mean()),
        cv=float(np.std(s) / np.mean(s)),             # CV>1 ⇒ super-Poisson (Poisson CV=1)
        max_over_mean=float(s.max()),
    )


def fingerprint(times, with_longrange=True):
    fp = {"family_I": compute_family_I(times),
          "clustering": clustering_readout(times)}
    su = local_rate_unfold(np.asarray(times, float), W=51)
    fp["local_rate_unfolded"] = clustering_from_spacings(su) if su is not None else None
    if with_longrange:
        fp["family_II"] = compute_family_II(times)
    return fp


def poisson_surrogate(times, n_rep=10, seed=0):
    """Rate-matched HOMOGENEOUS Poisson floor: n events uniform on [t0,t1]."""
    rng = np.random.default_rng(seed)
    t0, t1, n = float(times.min()), float(times.max()), times.size
    keys = ("I.5_ks_gue", "I.7_ks_poisson", "I.4_w1_poisson", "I.1_w1_clock")
    acc = {k: [] for k in keys}
    mass = []
    for r in range(n_rep):
        ts = np.sort(rng.uniform(t0, t1, n))
        fi = compute_family_I(ts)
        for k in keys:
            if fi.get(k) is not None:
                acc[k].append(fi[k])
        cr = clustering_readout(ts)
        if cr:
            mass.append(cr["mass_lt_0p3"])
    return {f"{k}_med": (float(np.median(acc[k])) if acc[k] else None) for k in keys} | \
           {"mass_lt_0p3_med": (float(np.median(mass)) if mass else None)}


# ── Gardner-Knopoff declustering ──────────────────────────────────────────────
def _gk_windows(mag):
    """GK (1974) interaction windows: distance L (km), time T (days)."""
    L = 10.0 ** (0.1238 * mag + 0.983)
    T = np.where(mag >= 6.5,
                 10.0 ** (0.032 * mag + 2.7389),
                 10.0 ** (0.5409 * mag - 0.547))
    return L, T


def _sphere_xyz(lat, lon):
    la, lo = np.radians(lat), np.radians(lon)
    cl = np.cos(la)
    return np.column_stack([R_EARTH * cl * np.cos(lo),
                            R_EARTH * cl * np.sin(lo),
                            R_EARTH * np.sin(la)])


def gardner_knopoff(cat, time_scale=1.0):
    """Return boolean mask of INDEPENDENT events (mainshocks + isolated).
    Magnitude-descending nucleus sweep with a spatial KD-tree; an event within the space-time
    window of a larger (already-)nucleus is flagged dependent (fore- and aftershocks). time_scale
    multiplies the GK time window (sensitivity knob)."""
    from scipy.spatial import cKDTree
    t, mag, lat, lon = cat["t"], cat["mag"], cat["lat"], cat["lon"]
    n = t.size
    m = np.where(np.isfinite(mag), mag, np.nanmin(mag[np.isfinite(mag)]) if np.isfinite(mag).any() else 0.0)
    L, T = _gk_windows(m)
    T = T * time_scale * DAY                          # → seconds
    xyz = _sphere_xyz(lat, lon)
    tree = cKDTree(xyz)
    dependent = np.zeros(n, dtype=bool)
    order = np.argsort(-m)                            # largest magnitude first
    for i in order:
        if dependent[i]:
            continue                                  # already inside a larger cluster
        chord = 2 * R_EARTH * np.sin(min(L[i] / (2 * R_EARTH), np.pi / 2))
        cand = tree.query_ball_point(xyz[i], chord)
        for j in cand:
            if j == i or dependent[j]:
                continue
            if m[j] < m[i] and abs(t[j] - t[i]) <= T[i]:
                dependent[j] = True
    return ~dependent


# ── G4 directionality ─────────────────────────────────────────────────────────
def irreversibility(times, n_surr=20, seed=1):
    """Ordering-sensitive time-reversal asymmetry on the inter-event-time series.
    Reversible ⇒ stats ≈ 0. Surrogate = shuffled inter-event times (destroys order)."""
    tau = np.diff(np.sort(times))
    tau = tau[tau > 0]
    if tau.size < 100:
        return None
    d = np.diff(tau)                                   # spacing increments
    def skew(x):
        x = x - x.mean(); s = x.std()
        return float((x ** 3).mean() / s ** 3) if s > 0 else 0.0
    def lagprod(x):                                    # E[x_i^2 x_{i+1}] - E[x_i x_{i+1}^2]
        a, b = x[:-1], x[1:]
        num = float((a ** 2 * b).mean() - (a * b ** 2).mean())
        return num / (x.std() ** 3 + 1e-300)
    real = dict(incr_skew=skew(d), lagprod_asym=lagprod(tau))
    rng = np.random.default_rng(seed)
    sk, lp = [], []
    for _ in range(n_surr):
        ts = rng.permutation(tau)
        sk.append(skew(np.diff(ts))); lp.append(lagprod(ts))
    real["incr_skew_surr_med"] = float(np.median(sk))
    real["incr_skew_surr_sd"] = float(np.std(sk))
    real["lagprod_surr_med"] = float(np.median(lp))
    real["lagprod_surr_sd"] = float(np.std(lp))
    real["incr_skew_z"] = (real["incr_skew"] - real["incr_skew_surr_med"]) / (real["incr_skew_surr_sd"] + 1e-300)
    real["lagprod_z"] = (real["lagprod_asym"] - real["lagprod_surr_med"]) / (real["lagprod_surr_sd"] + 1e-300)
    return real


def pooled_nns_reversal_invariance(times):
    """Band-invariance check: fingerprint of {t} vs time-reversed {T_max - t}. Should be identical."""
    fwd = compute_family_I(times)
    rev = compute_family_I((times.max() - times)[::-1])
    keys = [k for k in fwd if fwd[k] is not None and rev.get(k) is not None]
    maxdiff = max(abs(fwd[k] - rev[k]) for k in keys) if keys else None
    return dict(max_abs_diff=float(maxdiff) if maxdiff is not None else None,
                forward=fwd, reversed=rev)


def omori_asymmetry(cat, main_min_mag=6.0, lag_days=30.0, radius_km=100.0, max_main=300):
    """Magnitude-conditioned causal asymmetry: stacked event rate AFTER vs BEFORE mainshocks.
    Omori ⇒ after ≫ before (the time arrow NNS cannot see)."""
    from scipy.spatial import cKDTree
    t, mag, lat, lon = cat["t"], cat["mag"], cat["lat"], cat["lon"]
    mains = np.where(np.isfinite(mag) & (mag >= main_min_mag))[0]
    if mains.size == 0:
        return None
    if mains.size > max_main:
        mains = mains[np.linspace(0, mains.size - 1, max_main).astype(int)]
    xyz = _sphere_xyz(lat, lon)
    tree = cKDTree(xyz)
    chord = 2 * R_EARTH * np.sin(min(radius_km / (2 * R_EARTH), np.pi / 2))
    lag = lag_days * DAY
    before_tot = after_tot = 0
    for i in mains:
        cand = tree.query_ball_point(xyz[i], chord)
        for j in cand:
            if j == i:
                continue
            dt = t[j] - t[i]
            if -lag <= dt < 0:
                before_tot += 1
            elif 0 < dt <= lag:
                after_tot += 1
    return dict(n_mainshocks=int(mains.size), main_min_mag=main_min_mag,
                lag_days=lag_days, radius_km=radius_km,
                n_before=int(before_tot), n_after=int(after_tot),
                after_over_before=(after_tot / before_tot) if before_tot else None)


# ── driver ────────────────────────────────────────────────────────────────────
def describe(cat, tag):
    t = cat["t"]; yr = (t.max() - t.min()) / (365.25 * DAY)
    mfin = cat["mag"][np.isfinite(cat["mag"])]
    print(f"[{tag}] n={t.size}  span={yr:.1f}yr  rate={t.size/yr:.0f}/yr  "
          f"M[{mfin.min():.1f},{mfin.max():.1f}]" if mfin.size else f"[{tag}] n={t.size}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv", required=True)
    ap.add_argument("--fault-csv", default=None, help="single-fault/region catalog for G3")
    ap.add_argument("--out", default=os.path.join(_HERE, "coordinates", "comcat-fingerprint.jsonl"))
    ap.add_argument("--main-min-mag", type=float, default=6.0)
    a = ap.parse_args()

    cat = load_catalog(a.csv)
    describe(cat, "full")
    rec = {"source": os.path.basename(a.csv), "n_events": int(cat["t"].size)}

    # G1 — clustered read
    print("=== G1 clustered fingerprint ===")
    rec["G1_clustered"] = fingerprint(cat["t"])
    rec["G1_poisson_surrogate"] = poisson_surrogate(cat["t"])
    cr = rec["G1_clustered"]["clustering"]; fi = rec["G1_clustered"]["family_I"]
    sur = rec["G1_poisson_surrogate"]
    print(f"  ks_gue={fi['I.5_ks_gue']:.3f} ks_poisson={fi['I.7_ks_poisson']:.3f} "
          f"brody_q={fi['I.8_brody_q']} BR_rho={fi['I.9_berry_robnik_rho']}")
    print(f"  CLUSTERING mass<0.3={cr['mass_lt_0p3']:.3f} (Poisson-surr {sur['mass_lt_0p3_med']:.3f}) "
          f"CV={cr['cv']:.2f} (Poisson≈1)")
    unf = rec["G1_clustered"].get("local_rate_unfolded")
    if unf:
        print(f"  CLUSTERING (local-rate unfolded) mass<0.3={unf['mass_lt_0p3']:.3f} CV={unf['cv']:.2f} "
              f"(inhom-Poisson floor ~0.26/1.0; residual = genuine triggering)")

    # G2 — declustered read + window-scale sensitivity
    print("=== G2 Gardner-Knopoff declustered ===")
    rec["G2_decluster"] = {}
    for scale in (0.5, 1.0, 2.0):
        keep = gardner_knopoff(cat, time_scale=scale)
        td = cat["t"][keep]
        fpd = fingerprint(td, with_longrange=(scale == 1.0))
        rec["G2_decluster"][f"scale_{scale}"] = {
            "n_kept": int(keep.sum()), "frac_kept": float(keep.mean()), **fpd}
        cd = fpd["clustering"]; fd = fpd["family_I"]
        print(f"  scale×{scale}: kept {keep.sum()} ({keep.mean()*100:.0f}%)  "
              f"ks_poisson={fd['I.7_ks_poisson']:.3f}  mass<0.3={cd['mass_lt_0p3']:.3f}  CV={cd['cv']:.2f}")

    # G3 — single-fault (N-limited)
    if a.fault_csv:
        print("=== G3 single-fault (N-LIMITED; no-false-positive regime at best) ===")
        fcat = load_catalog(a.fault_csv)
        describe(fcat, "fault")
        rec["G3_single_fault"] = {"source": os.path.basename(a.fault_csv),
                                  "n_events": int(fcat["t"].size),
                                  "N_LIMITED_FLAG": "no-false-positive regime at best",
                                  **fingerprint(fcat["t"], with_longrange=False),
                                  "poisson_surrogate": poisson_surrogate(fcat["t"])}
        ff = rec["G3_single_fault"]["family_I"]
        print(f"  ks_gue={ff['I.5_ks_gue']} ks_poisson={ff['I.7_ks_poisson']} "
              f"(repulsion would need GUE/GOE-side + surrogate; N={fcat['t'].size})")

    # G4 — directionality
    print("=== G4 directionality (pooled-NNS arrow-blindness vs Omori) ===")
    rec["G4_reversal_invariance"] = pooled_nns_reversal_invariance(cat["t"])
    rec["G4_irreversibility"] = irreversibility(cat["t"])
    rec["G4_omori"] = omori_asymmetry(cat, main_min_mag=a.main_min_mag)
    inv = rec["G4_reversal_invariance"]; irr = rec["G4_irreversibility"]; om = rec["G4_omori"]
    print(f"  pooled-NNS forward≡reversed: max|Δ|={inv['max_abs_diff']:.2e} (≈0 ⇒ arrow-blind)")
    if irr:
        print(f"  irreversibility: incr_skew z={irr['incr_skew_z']:+.1f}  lagprod z={irr['lagprod_z']:+.1f}")
    if om and om["after_over_before"]:
        print(f"  Omori after/before={om['after_over_before']:.1f}× "
              f"(n_main={om['n_mainshocks']}, ±{om['lag_days']:.0f}d, {om['radius_km']:.0f}km)")
    print("  → spacing engine reads clustering strongly, arrow not at all; the gap is the directionality.")

    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    with open(a.out, "a") as f:
        f.write(json.dumps(rec, default=str) + "\n")
    print(f"[banked] {a.out}")


if __name__ == "__main__":
    main()
