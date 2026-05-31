"""
cross_substrate/soc_figure.py — P_comcat_soc.png: the SOC-pair calibrator figure.

Panels:
  (a) NNS of earthquake inter-event times: clustered vs GK-declustered vs Poisson-surrogate,
      against Poisson / GOE / GUE references — recovers known clustering, declustering moves it home.
  (b) Clustering-axis bars (mass<0.3, CV) across: Poisson floor, declustered, clustered-EQ, GOES,
      GOES-max, GOES-min — the calibration ladder.
  (c) One-sided-fitter illustration: Brody q & Berry-Robnik ρ rail at 0 on super-Poisson clustering.
  (d) Directionality gap: pooled-NNS forward≡reversed (max|Δ|≈0) vs Omori after/before ≫1.

Recomputes spacings/declustering from catalogs (cheap-ish; GK once at scale 1). Reads nothing it
can derive directly. Run after comcat_port.py + goes_flares.py have produced the catalogs.
"""
from __future__ import annotations

import os
import sys

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

_HERE = os.path.dirname(os.path.abspath(__file__))
for p in (_HERE, os.path.dirname(_HERE)):
    if p not in sys.path:
        sys.path.insert(0, p)

import comcat_port as CP                                                    # noqa: E402
from axes import canonical_spacings, compute_family_I                      # noqa: E402
from universality import nns_poisson, nns_goe, nns_gue                     # noqa: E402

COORD = os.path.join(_HERE, "coordinates")
FIG = os.path.join(_HERE, "figures", "P_comcat_soc.png")


def _norm_spacings(times):
    s = canonical_spacings(times)
    return s


def main(global_csv, goes_jsonl=None):
    cat = CP.load_catalog(global_csv)
    t = cat["t"]
    s_clu = _norm_spacings(t)
    keep = CP.gardner_knopoff(cat, time_scale=1.0)
    s_dec = _norm_spacings(t[keep])
    rng = np.random.default_rng(0)
    s_poi = _norm_spacings(np.sort(rng.uniform(t.min(), t.max(), t.size)))

    fi_clu = compute_family_I(t)
    fi_dec = compute_family_I(t[keep])
    cr_clu = CP.clustering_readout(t); cr_dec = CP.clustering_readout(t[keep])
    cr_poi = CP.clustering_readout(np.sort(rng.uniform(t.min(), t.max(), t.size)))
    inv = CP.pooled_nns_reversal_invariance(t)
    om = CP.omori_asymmetry(cat, main_min_mag=6.0)

    goes = None
    if goes_jsonl and os.path.exists(goes_jsonl):
        import goes_flares as GF
        goes = GF.load()

    fig, ax = plt.subplots(2, 3, figsize=(18, 9))
    grid = np.linspace(0.01, 4, 300); be = np.linspace(0, 4, 41)

    # (a) NNS distributions
    a = ax[0, 0]
    a.hist(s_clu, be, density=True, alpha=0.5, color="C3", label=f"clustered (mass<.3={cr_clu['mass_lt_0p3']:.2f})")
    a.hist(s_dec, be, density=True, alpha=0.5, color="C0", label=f"GK-declustered ({cr_dec['mass_lt_0p3']:.2f})")
    a.plot(grid, nns_poisson(grid), "g--", lw=1.4, label="Poisson")
    a.plot(grid, nns_goe(grid), "C2-", lw=1.0, label="GOE")
    a.plot(grid, nns_gue(grid), "r-", lw=1.4, label="GUE")
    a.set_xlim(0, 4); a.set_ylim(0, 2.0); a.set_xlabel("s (unit-mean inter-event)"); a.set_ylabel("P(s)")
    a.set_title("(a) earthquakes: recover clustering, declustering moves it home")
    a.legend(fontsize=7)

    # (b) clustering ladder
    b = ax[0, 1]
    labels = ["Poisson\nfloor", "GK-\ndeclustered", "clustered\nEQ"]
    mass = [cr_poi["mass_lt_0p3"], cr_dec["mass_lt_0p3"], cr_clu["mass_lt_0p3"]]
    cvs = [cr_poi["cv"], cr_dec["cv"], cr_clu["cv"]]
    if goes is not None:
        cg = CP.clustering_readout(goes["t"])
        su_g = CP.local_rate_unfold(goes["t"], W=51)
        cgu = CP.clustering_from_spacings(su_g) if su_g is not None else cg
        labels += ["GOES\n(homog.)", "GOES\n(unfolded)"]
        mass += [cg["mass_lt_0p3"], cgu["mass_lt_0p3"]]
        cvs += [cg["cv"], cgu["cv"]]
    x = np.arange(len(labels))
    b.bar(x - 0.2, mass, 0.4, color="C3", label="mass<0.3")
    b.axhline(cr_poi["mass_lt_0p3"], color="g", ls="--", lw=1, label="Poisson mass<0.3")
    b2 = b.twinx(); b2.plot(x + 0.2, cvs, "ks-", label="CV (right)")
    b2.axhline(1.0, color="gray", ls=":", lw=1)
    b.set_xticks(x); b.set_xticklabels(labels, fontsize=8); b.set_ylabel("mass<0.3")
    b2.set_ylabel("CV  (Poisson=1)")
    b.set_title("(b) clustering-axis calibration ladder"); b.legend(fontsize=7, loc="upper left")

    # (c) one-sided fitters
    c = ax[1, 0]
    names = ["Brody q", "Berry-Robnik ρ", "ks_gue", "ks_poisson"]
    clu_v = [fi_clu["I.8_brody_q"], fi_clu["I.9_berry_robnik_rho"], fi_clu["I.5_ks_gue"], fi_clu["I.7_ks_poisson"]]
    dec_v = [fi_dec["I.8_brody_q"], fi_dec["I.9_berry_robnik_rho"], fi_dec["I.5_ks_gue"], fi_dec["I.7_ks_poisson"]]
    xx = np.arange(len(names))
    c.bar(xx - 0.2, clu_v, 0.4, color="C3", label="clustered")
    c.bar(xx + 0.2, dec_v, 0.4, color="C0", label="declustered")
    c.set_xticks(xx); c.set_xticklabels(names, fontsize=8)
    c.set_title("(c) Brody q / BR ρ rail at 0: blind to super-Poisson clustering")
    c.legend(fontsize=8)
    c.annotate("repulsion fitters\nsaturate at Poisson", (0.5, 0.05), fontsize=8, color="C3")

    # (e) GOES unfold CV vs bandwidth, against the MEASURED no-memory synthetic floor (not CV=1).
    # The real no-memory floor dips sub-Poisson at small W, so CV<1 there is the estimator artifact,
    # not regularity; only the UPWARD divergence from synth-A (large W) is real clustering.
    e = ax[0, 2]
    if goes is not None:
        Ws = [5, 7, 11, 15, 21, 31, 51, 101, 201, 501]
        cvs_g = [(lambda su: CP.clustering_from_spacings(su)["cv"] if su is not None else np.nan)(
            CP.local_rate_unfold(goes["t"], W)) for W in Ws]
        # measured no-memory synthetic floor (from soc_synthetic_validate process A)
        synthA_W = [5, 7, 11, 15, 21, 31, 51, 101]
        synthA_cv = [0.776, 0.847, 0.906, 0.932, 0.953, 0.970, 0.984, 0.993]
        e.plot(Ws, cvs_g, "o-", color="C1", lw=1.9, label="GOES SWPC (clean)")
        e.plot(synthA_W, synthA_cv, "s--", color="0.4", lw=1.3, ms=4,
               label="no-memory synthetic (unfold floor)")
        e.axhline(1.0, color="g", ls=":", lw=1.0, alpha=0.7)
        e.axvline(18, color="C3", ls="-", lw=1.0, alpha=0.6)
        e.annotate("CV=1 crossover\nW≈18 ev ≈ 1.5 d\n(active-region lifetime)", (18, 1.55),
                   fontsize=6.5, color="C3", ha="center")
        e.annotate("small-W CV<1 = ARTIFACT\n(GOES≈synth floor)", (6, 0.66), fontsize=6.5, color="0.3")
        e.annotate("REAL clustering\n(GOES > floor)", (120, 1.25), fontsize=6.5, color="C1")
        e.set_xscale("log"); e.set_xlabel("unfold window W (events)")
        e.set_ylabel("unfolded CV"); e.set_ylim(0.6, 2.0)
        e.set_title("(e) solar flares: REAL multi-day clustering\n(sub-day 'regularity' = unfold+deadtime artifact)")
        e.legend(fontsize=6.5, loc="upper left"); e.grid(True, alpha=0.3)
    else:
        e.axis("off"); e.set_title("(e) GOES — no data")

    # (d) directionality gap
    d = ax[1, 1]
    d.axis("off")
    om_ratio = om["after_over_before"] if om and om["after_over_before"] else float("nan")
    txt = (
        "(d)  DIRECTIONALITY GAP\n\n"
        f"pooled-NNS forward ≡ reversed:\n   max|Δ(fingerprint)| = {inv['max_abs_diff']:.2e}\n"
        "   → the spacing engine is arrow-BLIND (§7.ter.10)\n\n"
        f"clustering it DOES see:  mass<0.3 = {cr_clu['mass_lt_0p3']:.2f}  (Poisson {cr_poi['mass_lt_0p3']:.2f})\n\n"
        f"Omori after/before rate ratio = {om_ratio:.1f}×\n"
        f"   (n_main={om['n_mainshocks'] if om else 0}, ±{om['lag_days'] if om else 0:.0f}d, "
        f"{om['radius_km'] if om else 0:.0f}km)\n"
        "   → the time arrow, which NNS cannot read\n\n"
        "GAP = strong clustering + zero arrow (NNS)\n"
        "     vs strong arrow (Omori). Directionality\n"
        "     lives in observables the engine discards."
    )
    d.text(0.02, 0.98, txt, va="top", ha="left", fontsize=10, family="monospace")

    # (f) solar-cycle knob: residual (unfolded) clustering, MAX vs MIN years
    f = ax[1, 2]
    if goes is not None:
        from datetime import datetime, timezone
        tt = goes["t"]
        yrs = np.array([datetime.fromtimestamp(x, tz=timezone.utc).year for x in tt])
        uy, cnt = np.unique(yrs, return_counts=True); rate = dict(zip(uy.tolist(), cnt.tolist()))
        hi = np.quantile(list(rate.values()), 2/3); lo = np.quantile(list(rate.values()), 1/3)
        maxy = {y for y, c in rate.items() if c >= hi}; miny = {y for y, c in rate.items() if c <= lo}
        bars = []
        for nm, sel in (("solar MAX", maxy), ("solar MIN", miny)):
            sub = tt[np.array([y in sel for y in yrs])]
            su = CP.local_rate_unfold(np.sort(sub), 51)
            cc = CP.clustering_from_spacings(su) if su is not None else None
            bars.append((nm, cc["cv"] if cc else np.nan, sub.size))
        f.bar([b[0] for b in bars], [b[1] for b in bars], color=["C3", "C0"], width=0.5)
        f.axhline(1.0, color="g", ls="--", lw=1.2, label="floor")
        for i, b in enumerate(bars):
            f.text(i, b[1] + 0.03, f"CV={b[1]:.2f}\nn={b[2]}", ha="center", fontsize=8)
        f.set_ylabel("unfolded CV (W51)"); f.set_ylim(0, 2.6)
        f.set_title("(f) cycle knob: MIN MORE clustered than MAX\n(opposite naive; survives window-confound)")
        f.legend(fontsize=7)
    else:
        f.axis("off"); f.set_title("(f) GOES — no data")

    fig.suptitle(f"SOC pair — ComCat earthquakes (n={t.size}) + GOES SWPC flares: clustering, timescale, directionality", fontsize=13)
    fig.tight_layout(rect=[0, 0, 1, 0.97])
    os.makedirs(os.path.dirname(FIG), exist_ok=True)
    fig.savefig(FIG, dpi=120); plt.close(fig)
    print(f"[fig] {FIG}")


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv", default=os.path.join(COORD, "comcat", "global_m45.csv"))
    ap.add_argument("--goes", default=os.path.join(COORD, "goes-flares.jsonl"))
    a = ap.parse_args()
    main(a.csv, a.goes)
