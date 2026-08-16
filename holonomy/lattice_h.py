"""Holonomy pilot verdict lattice (brief §3) — rulings-as-code shared module.

resolve_pair returns dict(primary, measurement, flags, basis) where:
  primary      the pair's headline verdict
  measurement  the measurement-layer sub-verdict (recorded even when the
               census forces ORDER_RULING_REQUIRED — the census ground and
               the measured ground are different facts, both banked)
Ruling-basis vocabulary (§4): RULED_CORRECT, RULED_CORRECT_BY_TRANSFER,
RULED_CONSISTENT.
"""

MEAS = ("COMMUTES", "COMMUTATOR_MEASURED", "POINT_CHECK_CLEAN",
        "UNDERPOWERED", "NONCOMMUTING_UNPREDICTED")


def resolve_pair(*, kind, both_orders_live, materiality_clean,
                 fp_all_within_tol=None, law_agrees=None, powered=True,
                 mean_within_ksem=None, sign_ok=None, envelope_ok=None):
    """kind: 'dialed' | 'stochastic_point' | 'deterministic_point'.
    Args by kind (others must be None / default):
      dialed:              fp_all_within_tol, law_agrees, powered
      stochastic_point:    mean_within_ksem, sign_ok, powered
      deterministic_point: envelope_ok  (cannot be UNDERPOWERED — A1 scoping)
    """
    flags = []
    # measurement layer
    if kind == "dialed":
        if not powered:
            meas = "UNDERPOWERED"
        elif fp_all_within_tol:
            meas = "COMMUTES"
        elif law_agrees:
            meas = "COMMUTATOR_MEASURED"
        else:
            meas = "NONCOMMUTING_UNPREDICTED"   # law disagrees -> ruling req.
    elif kind == "stochastic_point":
        if sign_ok is False:
            flags.append("HALT_PLUMBING_SIGN")  # A3: audit before holonomy
        if not powered:
            meas = "UNDERPOWERED"
        elif mean_within_ksem and sign_ok:
            meas = "POINT_CHECK_CLEAN"
        else:
            meas = "NONCOMMUTING_UNPREDICTED" if not mean_within_ksem \
                else "UNDERPOWERED"
    elif kind == "deterministic_point":
        meas = "POINT_CHECK_CLEAN" if envelope_ok else \
            "NONCOMMUTING_UNPREDICTED"
    else:
        raise ValueError(kind)

    # primary layer (§3 ORDER_RULING_REQUIRED triggers)
    ruling_needed = (both_orders_live
                     or not materiality_clean
                     or meas == "NONCOMMUTING_UNPREDICTED")
    if both_orders_live:
        flags.append("CENSUS_BOTH_ORDERS")
    if not materiality_clean:
        flags.append("MATERIAL_MARGIN")
    primary = "ORDER_RULING_REQUIRED" if ruling_needed else meas
    return dict(primary=primary, measurement=meas, flags=flags)
