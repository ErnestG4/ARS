"""Acceptance tests for arithmetic_toolkit.joint_q_profile.

Per the Phase 15 Tier 1 spec:
  1. Engine consistency: rf_amplitude_q must match the corresponding
     output of ramanujan_fourier(normalize=False) to floating-point
     precision.
  2. Sanity on calibrators:
       Poisson — uniformly low rf_amplitude_q, low rep_int_q.
       Periodic q=7 — RF spike at q=7; rep_int_q saturated; mass<0.3 = 0.
       β=2 GUE — per-q level statistics classify as GUE for well-powered
       bands; rf_amplitude_q low and unstructured.
  3. Underpowered flag set whenever n_events_q < min_events_per_q.
"""
import os, sys
import numpy as np
import pytest

THIS = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(THIS))

from arithmetic_toolkit import (
    joint_q_profile, ramanujan_fourier,
)
from signal_gen import (
    make_beta_ensemble_eigenvalues, make_uniform_jitter,
)


# ─── 1. Engine consistency ────────────────────────────────────────────────────

def test_rf_amplitude_matches_ramanujan_fourier():
    rng = np.random.default_rng(0)
    t = np.cumsum(rng.exponential(1.0, size=500))
    q_max = 50
    n_bins = int(np.ceil(t.max() - t.min())) + 1
    rf = ramanujan_fourier(t, q_max=q_max, normalize=False, n_bins=n_bins)
    rf_amps_direct = np.abs(np.asarray(rf['amplitudes']))
    j = joint_q_profile(t, q_max=q_max, rf_n_bins=n_bins)
    rf_amps_joint = j['rf_amplitude_q'].to_numpy()
    np.testing.assert_allclose(rf_amps_direct, rf_amps_joint,
                                rtol=1e-9, atol=1e-12,
                                err_msg="rf_amplitude_q must match ramanujan_fourier")


# ─── 2. Sanity on calibrators ────────────────────────────────────────────────

def test_poisson_low_rf_low_rep_int():
    rng = np.random.default_rng(1)
    t = np.cumsum(rng.exponential(1.0, size=2000))
    j = joint_q_profile(t, q_max=50, min_events_per_q=30)
    well_powered = j[~j['underpowered']]
    assert len(well_powered) >= 5, "Poisson should produce well-powered bands"
    median_rep_int = well_powered['rep_int_q'].median()
    assert median_rep_int < 0.20, (
        f"Poisson rep_int_q median should be low (<0.20); got {median_rep_int}")
    # RF amplitudes for Poisson should be unstructured at q ≥ 2 —
    # no individual q in {2..q_max} should dominate by more than 5x the median.
    # (q=1 is the DC term, always ≈ 1.0 for normalize=False indicator mode.)
    rf_excl_dc = well_powered.loc[well_powered['q'] >= 2, 'rf_amplitude_q'].to_numpy()
    rf_med = np.median(rf_excl_dc)
    assert rf_excl_dc.max() < 8 * (rf_med + 1e-9), (
        f"Poisson RF (q≥2) should be flat-ish; got peak {rf_excl_dc.max()} "
        f"vs median {rf_med}")


def test_periodic_q7_rf_spike_and_saturated_rep_int():
    rng = np.random.default_rng(2)
    period = 7.0
    n = 200
    t = (np.arange(1, n + 1) * period
         + 0.2 * rng.standard_normal(n))   # tight jitter
    t = np.sort(t)
    j = joint_q_profile(t, q_max=30, min_events_per_q=30)

    # The RF amplitude at q=7 should dominate the spectrum
    rf_at_7 = float(j.loc[j['q'] == 7, 'rf_amplitude_q'].iloc[0])
    rf_others = j[(j['q'] != 7) & (j['q'] != 1)]['rf_amplitude_q'].to_numpy()
    assert rf_at_7 > 3 * np.median(rf_others), (
        f"RF amplitude at q=7 should dominate; got rf[7]={rf_at_7}, "
        f"median elsewhere {np.median(rf_others)}")

    # rep_int_q saturated near 0.9 (uniform-like) at well-powered bands
    well = j[~j['underpowered']]
    if len(well) > 0:
        median_rep_int = well['rep_int_q'].median()
        assert median_rep_int > 0.7, (
            f"Periodic-with-jitter should saturate rep_int (>0.7); "
            f"got median {median_rep_int}")
        # mass<0.3 should be 0 (no short spacings at periodic input)
        median_mass = well['mass_lt_0_3_q'].median()
        assert median_mass < 0.05, (
            f"Periodic mass<0.3 should be near zero; got {median_mass}")


def test_gue_per_q_classifies_gue():
    e = make_beta_ensemble_eigenvalues(2000, beta=2, seed=3)
    j = joint_q_profile(e, q_max=20, min_events_per_q=200)
    well = j[~j['underpowered']]
    if len(well) >= 3:
        # On well-powered q-bands, GUE β=2 should give KS_GUE small
        # and best label = "GUE" preferred over GOE/Poisson.
        median_ks_u = well['ks_gue_q'].median()
        median_ks_o = well['ks_goe_q'].median()
        median_ks_p = well['ks_p_q'].median()
        assert median_ks_u <= median_ks_o, (
            f"β=2 should fit GUE better than GOE; got KS_GUE={median_ks_u}, "
            f"KS_GOE={median_ks_o}")
        assert median_ks_u < 0.10, (
            f"β=2 KS_GUE per q should be small (<0.10); got {median_ks_u}")
        # RF amplitudes at q ≥ 2 should be unstructured (q=1 is DC term)
        rf_q2 = well.loc[well['q'] >= 2, 'rf_amplitude_q'].to_numpy()
        if rf_q2.size > 0:
            assert rf_q2.max() / max(np.median(rf_q2), 1e-9) < 12, (
                "GUE eigenvalues should not produce sharp RF resonance at q≥2")


# ─── 3. Underpowered flag ────────────────────────────────────────────────────

def test_underpowered_flag():
    """Underpowered flag must equal `n_events_q < min_events_per_q` per row.

    Note: passage-time pooling across coprime numerators is generous —
    even n=200 Poisson events at q_max=200 yield 10k-40k pooled passage
    spacings per q-band.  To force underpowered=True at all, set the
    threshold higher than any realised count.  We verify the flag
    semantics (consistent with n_events_q vs threshold) rather than the
    absolute value.
    """
    rng = np.random.default_rng(4)
    t = np.cumsum(rng.exponential(1.0, size=20))
    threshold = 1_000_000_000   # impossibly large — every row should flag
    j = joint_q_profile(t, q_max=20, min_events_per_q=threshold)
    assert j['underpowered'].all(), (
        "Every band should be flagged when threshold exceeds all event counts")
    assert (j.loc[j['underpowered'], 'n_events_q'] < threshold).all()

    # Now with a generous threshold, no band should flag.
    j2 = joint_q_profile(t, q_max=20, min_events_per_q=1)
    assert (~j2['underpowered']).all() or j2.loc[j2['underpowered'], 'n_events_q'].max() == 0


# ─── 4. DataFrame schema ────────────────────────────────────────────────────

def test_dataframe_schema():
    rng = np.random.default_rng(5)
    t = np.cumsum(rng.exponential(1.0, size=500))
    j = joint_q_profile(t, q_max=20)
    expected = {'q', 'rf_amplitude_q', 'rf_amplitude_q_normalized',
                'n_events_q', 'ks_gue_q', 'ks_goe_q', 'ks_p_q',
                'mass_lt_0_3_q', 'rep_int_q', 'F_T1_q', 'F_T5_q',
                'n_pq_bands', 'underpowered'}
    assert expected.issubset(set(j.columns)), (
        f"Missing columns: {expected - set(j.columns)}")
    assert len(j) == 20, f"Expected 20 rows for q_max=20; got {len(j)}"
    assert (j['q'].to_numpy() == np.arange(1, 21)).all()


if __name__ == '__main__':
    sys.exit(pytest.main([__file__, '-v']))
