"""
cross_substrate/harvest.py — Phase 2a: harvest already-banked NNS metrics
across all measured substrates into landscape coordinate records.

NO recompute. Reads existing phase result artifacts (parquet / JSON) and
maps banked fields onto labelled landscape axes, per viewpoints.md §6.

INSTRUMENT LABELLING (carry-viewpoints-annotate-validity)
---------------------------------------------------------
Every banked `ks_gue_med` here is the ARS Farey-q-banded statistic
(joint_q_profile), NOT AM's plain unfolded-NNS W1δ. It is banked as
axis `I.5q_ks_gue_med` (q-banded label), mutually comparable ACROSS these
substrates but NOT comparable to AM's I.1/I.5 (object (a)). The matched
object-(a) axes (I.1 W1δ, I.2–I.4, I.6, I.8/I.9, II.*) are listed as
applicable-but-not-yet-computed (they are Phase 2b recompute).

`rep_med` (ARS repulsion-integral median) is carried as `ARS.rep_med`.
Per-substrate `extraction_method` records the exact leg so comparison
validity is annotatable downstream.

Output: cross_substrate/coordinates/{substrate}.jsonl
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from datetime import date

import numpy as np
import pandas as pd

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_HERE)
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from cross_substrate.axes import compute_family_III_from_rf  # noqa: E402

OUT_DIR = os.path.join(_HERE, "coordinates")
os.makedirs(OUT_DIR, exist_ok=True)
TODAY = date.today().isoformat()

# Object-(a) matched axes that exist for these substrates only after 2b recompute
MATCHED_NOT_YET = [
    "I.1_w1_clock", "I.2_w1_gue", "I.3_w1_goe", "I.4_w1_poisson",
    "I.5_ks_gue", "I.6_ks_clock", "I.7_ks_poisson", "I.8_brody_q",
    "I.9_berry_robnik_rho", "II.1_sigma2_L", "II.2_delta3_L",
]

_COMMIT_CACHE: dict[str, str] = {}


def _commit_of(relpath: str) -> str | None:
    if relpath in _COMMIT_CACHE:
        return _COMMIT_CACHE[relpath]
    try:
        h = subprocess.check_output(
            ["git", "log", "-1", "--format=%h", "--", relpath],
            cwd=_ROOT, stderr=subprocess.DEVNULL).decode().strip()
    except Exception:
        h = None
    _COMMIT_CACHE[relpath] = h or None
    return h or None


def _mtime_of(relpath: str) -> str | None:
    p = os.path.join(_ROOT, relpath)
    if not os.path.exists(p):
        return None
    return date.fromtimestamp(os.path.getmtime(p)).isoformat()


def _f(x):
    """Banked-float coercion: NaN/None → None (not-a-measurement)."""
    if x is None:
        return None
    try:
        v = float(x)
    except (TypeError, ValueError):
        return None
    return None if not np.isfinite(v) else v


def make_record(substrate, cell_id, axes, extraction_method, source_artifact,
                non_applicable=None, applicable_not_yet=None, audit=None,
                meta=None):
    return {
        "substrate": substrate,
        "cell_id": cell_id,
        "axes_computed": axes,
        "applicable_axes_not_yet_computed":
            list(applicable_not_yet if applicable_not_yet is not None
                 else MATCHED_NOT_YET),
        "non_applicable_axes": list(non_applicable or []),
        "extraction_method": extraction_method,
        "extraction_audit": audit or {},
        "source_artifact": source_artifact,
        "source_commit": _commit_of(source_artifact),  # null: data/ is gitignored
        "source_mtime": _mtime_of(source_artifact),
        "computed_date": TODAY,
        **({"meta": meta} if meta else {}),
    }


def _rf_axes(rf_amp_per_q):
    """Family III from a banked rf_amp_per_q vector, or {} if absent."""
    if rf_amp_per_q is None or len(rf_amp_per_q) < 7:
        return {}
    return {k: v for k, v in compute_family_III_from_rf(rf_amp_per_q).items()}


def _qbanded_axes(row_like, ks_key="ks_gue_med", rep_key="rep_med",
                  n_well_key="n_well", rf_key="rf_amp_per_q"):
    ksv = _f(row_like.get(ks_key))
    n_well = row_like.get(n_well_key)
    axes = {
        "I.5q_ks_gue_med": ksv,
        "ARS.rep_med": _f(row_like.get(rep_key)),
    }
    if ksv is None:
        axes["_I.5q_na_reason"] = f"underpowered (n_well={n_well})"
    rf = row_like.get(rf_key)
    axes.update(_rf_axes(rf if rf is not None else None))
    return axes


QBAND_METHOD = ("ARS joint_q_profile (Farey q-banded ks vs GUE), "
                "unfold_unit_mean, JPF_CAP=1500")


# ── adapters ─────────────────────────────────────────────────────────────────
def harvest_pvc11():
    src = "data/phase22a_results/h1_classifications.parquet"
    df = pd.read_parquet(os.path.join(_ROOT, src))
    recs = []
    for _, r in df.iterrows():
        d = r.to_dict()
        cell = f"{d['recording']}/{d['unit_id']}/{d['condition']}"
        recs.append(make_record(
            "pvc-11", cell, _qbanded_axes(d), QBAND_METHOD, src,
            non_applicable=["V.1_lyapunov", "V.2_correlation_dim"],
            audit={"n_events_in": int(d["n_events_in"]),
                   "n_events_used": int(d["n_events_used"]),
                   "n_well": int(d["n_well"]), "subset": d["subset"],
                   "primary_quadrant": d["primary"]},
            meta={"monkey": int(d["monkey"]), "subset": d["subset"]}))
    return "pvc-11", recs


def harvest_allen():
    src = "data/phase28_results/analysis1_per_cluster_real.parquet"
    df = pd.read_parquet(os.path.join(_ROOT, src))
    recs = []
    for _, r in df.iterrows():
        d = r.to_dict()
        cell = f"{d['session_id']}/{d['bin']}/anchor{d['anchor_unit']}"
        recs.append(make_record(
            "allen-np", cell, _qbanded_axes(d), QBAND_METHOD, src,
            non_applicable=["V.1_lyapunov", "V.2_correlation_dim"],
            audit={"n_events": int(d["n_events"]), "n_well": int(d["n_well"]),
                   "n_members": int(d["n_members"]), "bin": d["bin"],
                   "primary_quadrant": d["primary"],
                   "total_dur_sec": _f(d["total_dur_sec"])},
            meta={"session_id": int(d["session_id"]), "spatial_bin": d["bin"]}))
    return "allen-np", recs


def harvest_kuramoto():
    recs = []
    src_o = "data/phase30_results/analysis1_per_oscillator_real.parquet"
    df = pd.read_parquet(os.path.join(_ROOT, src_o))
    for _, r in df.iterrows():
        d = r.to_dict()
        cell = f"K{d['K_factor']:.3f}/seed{d['seed']}/N{d['N']}/osc{d['i']}"
        recs.append(make_record(
            "kuramoto", cell, _qbanded_axes(d),
            QBAND_METHOD + " on oscillator phase-crossing events", src_o,
            audit={"n_events": int(d["n_events"]), "n_well": int(d["n_well"]),
                   "rate": _f(d["rate"]), "omega_i": _f(d["omega_i"]),
                   "primary_quadrant": d["primary"]},
            meta={"K": _f(d["K"]), "K_factor": _f(d["K_factor"]),
                  "level": "oscillator"}))
    src_a = "data/phase30_results/analysis1_aggregate.parquet"
    dfa = pd.read_parquet(os.path.join(_ROOT, src_a))
    for _, r in dfa.iterrows():
        d = r.to_dict()
        cell = f"K{d['K_factor']:.3f}/seed{d['seed']}/N{d['N']}/agg"
        axes = {"I.5q_ks_gue_med": _f(d["agg_ks_med"]),
                "ARS.rep_med": _f(d["agg_rep_med"])}
        axes.update(_rf_axes(d.get("agg_rf_amp_per_q")))
        recs.append(make_record(
            "kuramoto", cell, axes,
            QBAND_METHOD + " aggregate over oscillators", src_a,
            audit={"n_events_total": int(d["n_events_total"]),
                   "agg_n_well": int(d["agg_n_well"]),
                   "order_param_mean": _f(d["order_param_mean"]),
                   "primary_quadrant": d["agg_primary"]},
            meta={"K": _f(d["K"]), "K_factor": _f(d["K_factor"]),
                  "level": "aggregate"}))
    return "kuramoto", recs


def harvest_pulsar():
    src = "data/phase33a_results/pilot_direct_stats.parquet"
    df = pd.read_parquet(os.path.join(_ROOT, src))
    recs = []
    for _, r in df.iterrows():
        d = r.to_dict()
        cell = f"{d['pulsar']}/{d['mode']}"
        axes = {
            "I.5q_ks_gue_med": _f(d["ks_gue_med"]),
            "ARS.rep_med": _f(d["rep_med"]),
            "I.7_ks_poisson_direct": _f(d["ks_poisson"]),
            "aux.cv": _f(d["cv"]), "aux.mass_lt_0p3": _f(d["mass_lt_0p3"]),
            "aux.z_ks_gue": _f(d.get("z_ks_gue")),
            "aux.z_rep": _f(d.get("z_rep")),
        }
        recs.append(make_record(
            "pulsar-nanograv", cell, axes,
            "ARS classify, DIRECT mode (raw_toas) — NOT q-banded; "
            "cross-domain STRUCTURAL_MISMATCH bounded (phase33a)", src,
            non_applicable=["V.1_lyapunov", "V.2_correlation_dim"],
            audit={"n_events": int(d["n_events"]),
                   "duration_yr": _f(d["duration_yr"]),
                   "surrogate_z_ks_gue": _f(d.get("z_ks_gue"))},
            meta={"mode": d["mode"]}))
    return "pulsar-nanograv", recs


def _arith_record(substrate, cell, sub, src, method, meta=None):
    axes = {"I.5q_ks_gue_med": _f(sub.get("ks_gue_med")),
            "ARS.rep_med": _f(sub.get("rep_med"))}
    if axes["I.5q_ks_gue_med"] is None:
        axes["_I.5q_na_reason"] = f"n_well={sub.get('n_well')}"
    return make_record(
        substrate, cell, axes, method, src,
        non_applicable=["V.1_lyapunov", "V.2_correlation_dim"],
        audit={"n_events_used": sub.get("n_events_used"),
               "n_well": sub.get("n_well"),
               "primary_quadrant": sub.get("primary")},
        meta=meta)


def harvest_arithmetic():
    ARITH_METHOD = ("ARS joint_q_profile (Farey q-banded ks vs GUE) on "
                    "arithmetic point process")
    out = {}  # substrate -> recs
    # 34a Mertens, 34b Liouville: top-level segment dicts
    for src, substrate in [("data/phase34a_results/nns_classify.json", "mertens"),
                           ("data/phase34b_results/nns_classify.json", "liouville")]:
        p = os.path.join(_ROOT, src)
        if not os.path.exists(p):
            continue
        d = json.load(open(p))
        recs = []
        for key, seg in d.items():
            if isinstance(seg, dict) and "ks_gue_med" in seg:
                recs.append(_arith_record(substrate, key, seg, src,
                                          ARITH_METHOD,
                                          meta={"segment": seg.get("label", key)}))
        out[substrate] = recs
    # 34c zeta/Dirichlet/EC L: panels[*].nns_reproduction
    src = "data/phase34c_results/surveys.json"
    p = os.path.join(_ROOT, src)
    if os.path.exists(p):
        d = json.load(open(p))
        recs = []
        for panel, pd_ in d.get("panels", {}).items():
            nns = pd_.get("nns_reproduction") if isinstance(pd_, dict) else None
            if isinstance(nns, dict) and "ks_gue_med" in nns:
                recs.append(_arith_record("L-zeros", panel, nns, src,
                                          ARITH_METHOD,
                                          meta={"panel": panel}))
        out["L-zeros"] = recs
    # 34d Gaussian + Eisenstein primes: panels[*].nns_full
    for src, substrate in [
            ("data/phase34d_results/gaussian_prepilot_ars.json", "gaussian-primes"),
            ("data/phase34d_results/eisenstein_substantive_ars.json", "eisenstein-primes")]:
        p = os.path.join(_ROOT, src)
        if not os.path.exists(p):
            continue
        d = json.load(open(p))
        recs = []
        for panel, pd_ in d.get("panels", {}).items():
            if not isinstance(pd_, dict):
                continue
            nns = pd_.get("nns_full") or pd_.get("nns_reproduction")
            if isinstance(nns, dict) and "ks_gue_med" in nns:
                recs.append(_arith_record(substrate, panel, nns, src,
                                          ARITH_METHOD, meta={"panel": panel}))
        if recs:
            out[substrate] = recs
    # 34e Maass Gamma0(N): results[level_*].full_n_classification + BR rho
    src = "data/phase34e_results/nns_classification.json"
    p = os.path.join(_ROOT, src)
    if os.path.exists(p):
        d = json.load(open(p))
        br_path = os.path.join(_ROOT, "data/phase34e_results/berry_robnik.json")
        br = json.load(open(br_path)) if os.path.exists(br_path) else {}
        br_res = br.get("results", {})
        recs = []
        for lvl_key, seg in d.get("results", {}).items():
            cls = seg.get("full_n_classification") if isinstance(seg, dict) else None
            if not (isinstance(cls, dict) and "ks_gue_med" in cls):
                continue
            rec = _arith_record("maass-gamma0", lvl_key, cls, src,
                                ARITH_METHOD, meta={"level": seg.get("level")})
            brk = br_res.get(lvl_key)
            if isinstance(brk, dict) and "rho_mle" in brk:
                rec["axes_computed"]["I.9_berry_robnik_rho"] = _f(brk["rho_mle"])
                if "I.9_berry_robnik_rho" in rec["applicable_axes_not_yet_computed"]:
                    rec["applicable_axes_not_yet_computed"].remove("I.9_berry_robnik_rho")
                rec["extraction_audit"]["br_source"] = \
                    "data/phase34e_results/berry_robnik.json"
                rec["extraction_audit"]["I.9_note"] = (
                    "BR rho on plain unfolded Maass NNS (object-(a)-style); "
                    "matched to AM I.9. I.5q remains q-banded.")
            recs.append(rec)
        out["maass-gamma0"] = recs
    return out


def write_jsonl(substrate, recs):
    path = os.path.join(OUT_DIR, f"{substrate}.jsonl")
    with open(path, "w") as f:
        for r in recs:
            f.write(json.dumps(r) + "\n")
    return path, len(recs)


def main():
    print("=" * 76)
    print("PHASE 2a — harvest banked NNS metrics across substrates")
    print("=" * 76)
    written = {}
    for fn in (harvest_pvc11, harvest_allen, harvest_kuramoto, harvest_pulsar):
        sub, recs = fn()
        path, n = write_jsonl(sub, recs)
        n_meas = sum(1 for r in recs if r["axes_computed"].get("I.5q_ks_gue_med") is not None)
        written[sub] = (n, n_meas)
        print(f"  {sub:18s} {n:5d} cells  ({n_meas} with I.5q measured)  → {os.path.basename(path)}")
    for sub, recs in harvest_arithmetic().items():
        path, n = write_jsonl(sub, recs)
        n_meas = sum(1 for r in recs if r["axes_computed"].get("I.5q_ks_gue_med") is not None)
        written[sub] = (n, n_meas)
        print(f"  {sub:18s} {n:5d} cells  ({n_meas} with I.5q measured)  → {os.path.basename(path)}")
    total = sum(v[0] for v in written.values())
    print(f"\n  {len(written)} substrates, {total} total coordinate records")
    print(f"  → {OUT_DIR}")


if __name__ == "__main__":
    main()
