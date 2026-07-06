"""
phase34f/zomega_loader.py — Bianchi-Z[ω] (Q(√−3)) Maass-spectrum loader
+ §D.0a data-availability gate + §D.0b normalization gate, for the
34f-E first-measurement leg.

PHASE34F_BRIEF §B.2 substrate: Maass cusp forms on Γ_K = PSL(2, O_K),
K = Q(√−3), O_K = Z[ω], d_K = −3, acting on ℍ³.  Same eigenvalue
equation as Picard, (Δ + λ)f = 0 with the **3-D convention λ = r² + 1**
(NOT the 2-D SL(2,ℤ) convention λ = 1/4 + r² used in Phase 34e).

ASYMMETRIC-LABEL DISCIPLINE (PHASE34F_BRIEF §E.2 / METHODS §E):
34f-E-Δ is a **FIRST-MEASUREMENT** substrate — unlike Picard/34f-G,
there is NO published empirical anchor (Then 2003 covered Picard only;
no subsequent computational work has surfaced Bianchi-Z[ω] Maass-NNS in
literature accessible from search).  The Sarnak-anomaly extension to
PSL(2,Z[ω]) is a *structural Hecke-algebra prediction*, empirically
unconfirmed.  Pipeline-validation → PIPELINE_VALIDATED_READY_TO_FIRE;
the substantive verdict on data acquisition would be one of
SARNAK_ANOMALY_FIRST_MEASUREMENT_AT_PSL2_Z_OMEGA /
..._WITH_FIELD_SHIFT / NO_ANOMALY_AT_PSL2_Z_OMEGA (PHASE34F_BRIEF
§E.2).  NEVER label this leg a "replication".

§D.0a DATA-AVAILABILITY GATE — FIRES.  No accessible Bianchi-Z[ω] Maass
eigenvalue dataset:
  - LMFDB Bianchi page (PHASE34F_BRIEF §C.2): reCAPTCHA-blocked in
    session; Z[ω] Maass-form cardinality unverified, likely
    insufficient (the Bianchi LMFDB content is primarily Cremona
    holomorphic newforms, NOT Maass forms — §C.2/§C.3).
  - De-novo Hejhal-on-ℍ³ for the order-6 unit group of Z[ω]
    (PHASE34F_BRIEF §C.3): 2–6 weeks from Cremona's bianchi-progs;
    6–12 weeks from scratch.  Multi-week infrastructure cost.
Per the Phase 34e/34f discipline, an underpowered result is NOT
fabricated from unavailable data.  This module defines the schema and
both pre-flight gates so the leg is genuinely ready-to-fire on
acquisition (the gates are exercised on synthetic known-good /
known-bad inputs in the self-test — §7.ter.55: validate the instrument
on known inputs before trusting it on unknown ones).

References:
  - PHASE34F_BRIEF §B.2 (substrate), §C.2/§C.3 (data infrastructure),
    §D.0a/§D.0b (pre-flight gates), §E.2 (verdict labels).
  - Elstrodt-Grunewald-Mennicke (1998), Groups Acting on Hyperbolic
    Space (Bianchi Weyl law + orbifold structure).
"""
from __future__ import annotations

import math
import os
import sys
from dataclasses import dataclass

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, THIS_DIR)

from bianchi_unfolding import bianchi_z_omega_volume

# Field / substrate constants (PHASE34F_BRIEF §B.2).
FIELD = "Q(sqrt(-3))"
RING = "Z[omega]"
D_K = -3
UNIT_GROUP_ORDER = 6           # vs 4 for Z[i] — gives order-2 AND order-3
                               # elliptic fixed points (Picard: order-2 only).
LAMBDA_CONVENTION = "r2+1"     # 3-D Bianchi; NOT the 2-D 1/4+r².
RP_BOUND = 2.0                 # |a(𝔭)| ≤ 2 under Ramanujan-Petersson.


class DataAcquisitionBlocked(RuntimeError):
    """Raised when the §D.0a data-availability gate has fired."""


@dataclass(frozen=True)
class ZOmegaDeltaRecord:
    """One Bianchi-Z[ω] Maass Δ-eigenform spectral parameter."""
    form_id: str
    r_j: float                 # spectral parameter; λ = r_j² + 1.


@dataclass(frozen=True)
class ZOmegaHeckeRecord:
    """One Hecke eigenvalue at a prime ideal of Z[ω] (Sato-Tate, 34f-E-H)."""
    form_id: str
    prime_ideal_norm: int      # N(𝔭); split N=p (p≡1 mod 3), inert N=p².
    hecke_eigenvalue: float    # RP-normalized a(𝔭) ∈ [-RP_BOUND, RP_BOUND].


def data_availability_gate() -> dict:
    """§D.0a — fires for 34f-E (no accessible Z[ω] Maass dataset).

    Returns a structured FIRED report with the acquisition paths and
    their cost flags (PHASE34F_BRIEF §C.2/§C.3).  Mirrors the 34f-G
    §D.0a discipline (PHASE34F_FINDINGS §A) for the FIRST-MEASUREMENT
    substrate.
    """
    return dict(
        gate="§D.0a data-availability (34f-E Bianchi-Z[ω])",
        status="FIRED",
        substrate_role="FIRST_MEASUREMENT",   # asymmetric-label discipline
        reason="No accessible Bianchi-Z[ω] Maass eigenvalue dataset.",
        acquisition_paths=[
            dict(path="LMFDB Bianchi page (Q(√−3))",
                 cost="reCAPTCHA-blocked in session; primarily Cremona "
                      "holomorphic newforms, Maass cardinality unverified "
                      "and likely insufficient (§C.2)"),
            dict(path="De-novo Hejhal-on-ℍ³ from Cremona bianchi-progs",
                 cost="2–6 weeks implementation (§C.3)"),
            dict(path="De-novo Hejhal-on-ℍ³ from scratch / Strömberg "
                      "PSAGE / Lemurell algorithms",
                 cost="6–12 weeks implementation (§C.3)"),
        ],
        substantive_verdict="DATA_ACQUISITION_BLOCKED",
        note="Underpowered results are NOT fabricated from unavailable "
             "data (Phase 34e/34f discipline). Pipeline is "
             "ready-to-fire on acquisition; gates are synthetic-validated.",
    )


def normalization_gate(r=None, hecke=None,
                        lam_convention: str = LAMBDA_CONVENTION,
                        volume: float | None = None) -> dict:
    """§D.0b — normalization / convention gate (PHASE34F_BRIEF §D.0b).

    Validates, for whatever subset of (r, hecke) is supplied:
      - spectral-parameter convention is the 3-D λ = r² + 1, NOT the
        2-D λ = 1/4 + r² (a carried-over 2-D convention is the canonical
        contamination bug — caught here, not downstream);
      - r values are real and positive (Maass cusp-form spectral
        parameters);
      - Hecke eigenvalues obey the Ramanujan-Petersson bound
        |a(𝔭)| ≤ 2;
      - the unfolding volume is the substrate-correct pinned
        Bianchi-Z[ω] value (bianchi_z_omega_volume()), NOT the Picard
        volume — the §F.3 / §7.ter.55 substrate-correct-constant check.

    Returns a checks dict; raises AssertionError on any failure (the
    highest-priority debug trigger per §D.0b).
    """
    import numpy as np

    if volume is None:
        volume = bianchi_z_omega_volume()
    z_omega_vol = bianchi_z_omega_volume()

    checks: dict[str, bool] = {}
    checks["lambda_convention_is_3d"] = (lam_convention == "r2+1")
    # A 2-D convention slipping through is the canonical contamination.
    checks["not_2d_convention"] = (lam_convention != "1/4+r2")
    checks["volume_is_substrate_correct"] = (
        abs(volume - z_omega_vol) < 1e-9
    )

    if r is not None:
        r = np.asarray(r, dtype=np.float64)
        checks["r_real_finite"] = bool(np.all(np.isfinite(r)))
        checks["r_positive"] = bool(np.all(r > 0))
        # λ = r²+1 ⇒ λ ≥ 1 for real r; a 1/4+r² dataset fed as r²+1
        # would not violate this, so the convention flag above is the
        # real guard — this is a coarse sanity rail only.
        checks["lambda_ge_1_under_r2p1"] = bool(np.all(r ** 2 + 1.0 >= 1.0))

    if hecke is not None:
        hecke = np.asarray(hecke, dtype=np.float64)
        checks["hecke_finite"] = bool(np.all(np.isfinite(hecke)))
        checks["hecke_within_RP_bound"] = bool(
            np.all(np.abs(hecke) <= RP_BOUND + 1e-9)
        )

    for name, ok in checks.items():
        assert ok, (
            f"§D.0b normalization_gate FAILED: {name} "
            f"(highest-priority debug trigger per PHASE34F_BRIEF §D.0b)"
        )
    return dict(passed=True, checks=checks,
                volume_used=float(volume),
                z_omega_volume=float(z_omega_vol),
                lambda_convention=lam_convention)


def load_zomega_eigenvalues(path: str | None = None):
    """Load Bianchi-Z[ω] Maass Δ-eigenvalues.

    The §D.0a gate fires (no accessible dataset).  On acquisition, this
    parses the source into List[ZOmegaDeltaRecord], runs
    normalization_gate(), and returns the r_j array ready for
    bianchi_unfolding.unfold_bianchi_3d(r, bianchi_z_omega_volume()).
    Format is source-dependent (LMFDB export, Cremona bianchi-progs
    output, or de-novo Hejhal-on-ℍ³ dump) and is wired on acquisition.
    """
    gate = data_availability_gate()
    raise DataAcquisitionBlocked(
        f"{gate['gate']}: {gate['status']} — {gate['reason']} "
        f"Substantive 34f-E = {gate['substantive_verdict']}. "
        f"Pipeline ready-to-fire on acquisition (paths: "
        f"{[p['path'] for p in gate['acquisition_paths']]})."
    )


def _self_test() -> dict:
    """Exercise both gates on synthetic known-good / known-bad inputs.

    §7.ter.55 discipline: validate the instrument on known inputs
    before trusting it on unknown ones.  The §D.0b gate must PASS on a
    plausible 3-D Z[ω] spectrum and substrate-correct volume, and must
    FAIL on (a) a 2-D-convention contamination and (b) the Picard
    volume substituted for the Z[ω] volume.
    """
    import numpy as np
    from bianchi_unfolding import picard_volume

    rng = np.random.default_rng(0)
    # Plausible Z[ω] spectrum: positive r with a 3-D Weyl-like growth.
    r_good = np.sort(rng.uniform(1.0, 80.0, size=500))
    hecke_good = np.clip(rng.normal(0.0, 0.8, size=500), -2.0, 2.0)

    # (1) known-good: gate PASSES.
    g_ok = normalization_gate(r=r_good, hecke=hecke_good,
                              lam_convention="r2+1",
                              volume=bianchi_z_omega_volume())
    assert g_ok["passed"]

    # (2) known-bad A: 2-D convention contamination → gate FAILS.
    bad_conv_caught = False
    try:
        normalization_gate(r=r_good, lam_convention="1/4+r2")
    except AssertionError:
        bad_conv_caught = True
    assert bad_conv_caught, "2-D-convention contamination NOT caught"

    # (3) known-bad B: Picard volume substituted → gate FAILS.
    bad_vol_caught = False
    try:
        normalization_gate(r=r_good, volume=picard_volume())
    except AssertionError:
        bad_vol_caught = True
    assert bad_vol_caught, "wrong-substrate volume NOT caught"

    # (4) known-bad C: Hecke eigenvalue outside RP bound → gate FAILS.
    rp_caught = False
    try:
        normalization_gate(hecke=np.array([0.1, 2.7, -0.5]))
    except AssertionError:
        rp_caught = True
    assert rp_caught, "RP-bound violation NOT caught"

    # (5) §D.0a data-availability gate FIRES; loader raises.
    da = data_availability_gate()
    assert da["status"] == "FIRED"
    assert da["substrate_role"] == "FIRST_MEASUREMENT"
    loader_blocked = False
    try:
        load_zomega_eigenvalues()
    except DataAcquisitionBlocked:
        loader_blocked = True
    assert loader_blocked, "loader did not raise DataAcquisitionBlocked"

    return dict(
        normalization_gate_known_good=g_ok["checks"],
        caught_2d_convention=bad_conv_caught,
        caught_wrong_volume=bad_vol_caught,
        caught_rp_violation=rp_caught,
        data_availability_gate=da,
        all_self_test_checks_pass=True,
    )


__all__ = [
    "FIELD", "RING", "D_K", "UNIT_GROUP_ORDER", "LAMBDA_CONVENTION",
    "RP_BOUND",
    "DataAcquisitionBlocked",
    "ZOmegaDeltaRecord", "ZOmegaHeckeRecord",
    "data_availability_gate", "normalization_gate",
    "load_zomega_eigenvalues",
]


if __name__ == "__main__":
    import json
    print(json.dumps(_self_test(), indent=2, default=float))
    print("zomega_loader self-test: ALL CHECKS PASS")
