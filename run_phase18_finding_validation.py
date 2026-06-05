"""
run_phase18_finding_validation.py — Phase 18 Tier 3.

Apply the strengthened (higher-order) induction-on-noise protocol to the
project's existing positive findings.  For each (finding, surrogate) cell:

  1. Load the original event sequence used in the finding.
  2. Compute the joint_q_profile + diagnostic classification.
  3. Generate the surrogate (event-domain).
  4. Compute the surrogate's classification.
  5. Record whether the surrogate produces the same primary quadrant
     (finding does NOT survive — surrogate flags potential artifact) or
     a different one (finding survives).

Findings panel (per SESSION-PLAN Tier 3):

  | finding                         | source           | original class |
  | ζ first 2000 zeros              | §7.ter.7         | TR             |
  | ζ at heights ~10⁶               | §7.ter.21        | TR             |
  | LMFDB EC L-functions            | §7.ter.4         | TR             |
  | Dirichlet L-functions           | §7.ter.3         | TR             |
  | Earthquakes M ≥ 4.5             | §7.ter.4         | BL             |
  | Primes ≤ 10⁶                    | §7.ter.21, .23   | BR_artifact    |
  | Twin primes ≤ 10⁷               | §7.ter.21, .23   | BR_artifact    |

Adamatzky fungi (BL) is omitted from this Tier 3 run because its events
are produced by a multi-channel threshold-spike detector applied to raw
voltage CSVs, requiring a full re-detection pipeline.  The omission is
documented in §7.ter.25 of RESULTS.md as a follow-up.

Stop condition (per spec): if any arithmetic finding fails a surrogate it
was expected to survive, stop and investigate before continuing.

Output:
  data/phase18_finding_validation.parquet
  plots/51_phase18_finding_survival.png
"""
from __future__ import annotations
import os, sys, json, time
from datetime import datetime
import numpy as np
import pandas as pd

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, THIS_DIR)

from arithmetic_toolkit import joint_q_profile, joint_quadrant_diagnostic
from surrogates import (
    phase_randomized_events,           # chirp-driven (continuous proxy + extractor)
    phase_randomized_iei_events,       # IEI-domain (no extractor roundtrip)
    hawkes_matched_events,
    cumulant_matched_events,
)
# Apparatus ops (instrument_confound) folded in as a SECOND arm — see APPARATUS
# block below.  A point process is (substrate ⊗ instrument); the surrogates above
# probe the substrate (destroy structure → does the finding need it?), the
# apparatus arm probes the instrument (dead time / finite efficiency → does the
# finding survive the collection method?).
sys.path.insert(0, os.path.join(THIS_DIR, "cross_substrate"))
import instrument_confound as ic

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

DATA = os.path.join(THIS_DIR, "data")
PLOTS = os.path.join(THIS_DIR, "plots")

# Smaller q_max + event cap to keep total runtime tractable.  joint_q_profile
# at q_max=30, n_events ≤ 10000 ≈ 1–4 s/call; surrogates add ~2–8 s each.
Q_MAX = 30
MIN_EVENTS = 30
N_SEEDS = 3
N_EVENTS_CAP = 8000        # cap events for compute (subsample if larger)


SURROGATE_NAMES = ['phase_randomized', 'hawkes_matched', 'cumulant_matched']

# ─── Apparatus perturbations (the instrument arm) ──────────────────────────
# POLARITY IS OPPOSITE to the surrogate arm. A surrogate "survives" when it
# yields a DIFFERENT class (structure destroyed → finding is real). An apparatus
# perturbation is robust when the class is UNCHANGED (the collection method did
# not manufacture / erase the verdict). Dead time carves a short-range hole
# (fakes repulsion); thinning is finite efficiency (drives toward Poisson). Each
# is applied to the DATA, then the finding is re-classified.
APPARATUS_NAMES = ['deadtime_0.15', 'deadtime_0.30', 'thin_0.10', 'thin_0.25']


# ─── Loaders ──────────────────────────────────────────────────────────────


def _unfold_zeta_zeros(z):
    """Riemann-zeta unfolding: t̃ = (γ / 2π) log(γ / 2πe) + 7/8."""
    z = np.asarray(z, dtype=np.float64)
    return (z / (2 * np.pi)) * np.log(np.maximum(z / (2 * np.pi * np.e), 1.0)) + 7 / 8


def load_zeta_first(n=2000):
    z = np.loadtxt(os.path.join(DATA, "odlyzko_zeros1.txt"), max_rows=n)
    return _unfold_zeta_zeros(z)


def load_zeta_high(n=4000):
    """ζ-zeros at heights ~10⁶ (Odlyzko archive 6).  Use the unfolding
    that mean-normalises spacings."""
    z = np.loadtxt(os.path.join(DATA, "odlyzko_zeros6.txt"), max_rows=n)
    # These are listed as offsets from a base height; for unfolding we
    # need absolute height.  The first entry is small (offset).  The
    # canonical use in this codebase: just unfold directly and trust that
    # log(γ/2πe) is approximately constant over the local height — so
    # spacings divided by mean spacing yield a unit-mean unfolded sequence.
    sp = np.diff(z)
    sp = sp[sp > 0]
    if sp.size == 0 or sp.mean() <= 0:
        return _unfold_zeta_zeros(z)
    sp_unit = sp / sp.mean()
    out = np.cumsum(np.concatenate([[0.0], sp_unit]))
    return out


def load_lmfdb_pooled(n_max=N_EVENTS_CAP):
    """Pool zeros across all LMFDB EC curves; unfold per-curve by mean
    spacing (each curve's local zero density is treated as constant)."""
    with open(os.path.join(DATA, "lmfdb_zeros.json")) as f:
        rows = json.load(f)
    pooled = []
    for r in rows:
        z = np.asarray(r.get('zeros', []), dtype=np.float64)
        if z.size < 5:
            continue
        sp = np.diff(np.sort(z))
        sp = sp[sp > 0]
        if sp.size == 0 or sp.mean() <= 0:
            continue
        pooled.append(sp / sp.mean())
    if not pooled:
        return np.zeros(0)
    sp_pool = np.concatenate(pooled)
    rng = np.random.default_rng(0)
    rng.shuffle(sp_pool)   # decorrelate per-curve
    if sp_pool.size > n_max:
        sp_pool = sp_pool[:n_max]
    return np.cumsum(np.concatenate([[0.0], sp_pool]))


def load_dirichlet_pooled(n_max=N_EVENTS_CAP):
    with open(os.path.join(DATA, "dirichlet_zeros.json")) as f:
        rows = json.load(f)
    pooled = []
    for r in rows:
        z = np.asarray(r.get('zeros', []), dtype=np.float64)
        if z.size < 5:
            continue
        sp = np.diff(np.sort(z))
        sp = sp[sp > 0]
        if sp.size == 0 or sp.mean() <= 0:
            continue
        pooled.append(sp / sp.mean())
    if not pooled:
        return np.zeros(0)
    sp_pool = np.concatenate(pooled)
    rng = np.random.default_rng(0)
    rng.shuffle(sp_pool)
    if sp_pool.size > n_max:
        sp_pool = sp_pool[:n_max]
    return np.cumsum(np.concatenate([[0.0], sp_pool]))


def load_earthquakes():
    path = os.path.join(DATA, "usgs_M45_5yr.csv")
    times = []
    with open(path) as f:
        header = f.readline().strip().split(',')
        i_t = header.index('time')
        for line in f:
            cols = line.rstrip('\n').split(',')
            try:
                t = datetime.fromisoformat(cols[i_t].replace('Z', '+00:00'))
                times.append(t.timestamp())
            except Exception:
                continue
    times = np.sort(np.asarray(times, dtype=np.float64))
    if times.size > N_EVENTS_CAP:
        # Random-subsample to cap, preserving time order via index sample.
        rng = np.random.default_rng(0)
        idx = np.sort(rng.choice(times.size, size=N_EVENTS_CAP, replace=False))
        times = times[idx]
    # Unfold by mean spacing so unit-mean.
    sp = np.diff(times)
    sp = sp[sp > 0]
    if sp.size == 0 or sp.mean() <= 0:
        return times
    return np.cumsum(np.concatenate([[0.0], sp / sp.mean()]))


def _sieve(N):
    s = np.ones(N + 1, dtype=bool)
    s[:2] = False
    for p in range(2, int(np.sqrt(N)) + 1):
        if s[p]:
            s[p * p::p] = False
    return s


def load_primes(N=1_000_000):
    s = _sieve(N)
    p = np.where(s)[0].astype(np.float64)
    # Prime number theorem unfolding: t / log(t) → unit-mean asymptotically.
    u = p / np.log(np.maximum(p, 2.0))
    if u.size > N_EVENTS_CAP:
        u = u[:N_EVENTS_CAP]
    return u


def load_twin_primes(N=10_000_000):
    s = _sieve(N)
    p = np.where(s)[0].astype(np.float64)
    diffs = np.diff(p)
    twin_lo = p[:-1][diffs == 2]
    u = twin_lo / np.log(np.maximum(twin_lo, 2.0)) ** 2  # twin-prime unfold
    # Mean-normalise.
    sp = np.diff(u)
    sp = sp[sp > 0]
    if sp.size == 0 or sp.mean() <= 0:
        return u
    out = np.cumsum(np.concatenate([[0.0], sp / sp.mean()]))
    if out.size > N_EVENTS_CAP:
        out = out[:N_EVENTS_CAP]
    return out


# ─── Findings panel ───────────────────────────────────────────────────────


# NNS-MARGINAL RELABEL (Phase-18 STOP CONDITION resolution): the TR verdict is an
# NNS statistic = a property of the MARGINAL spacing distribution. Marginal-
# PRESERVING surrogates (phase_randomized_iei, cumulant_matched) reproduce it BY
# CONSTRUCTION, so they are EXPECTED to be caught, not to survive — only the
# marginal-DESTROYING surrogate (hawkes_matched, which clusters) is expected to flip
# an NNS verdict. The 'GUE class' claim is NOT carried here; it is carried by the
# long-range statistic (Σ²/Δ₃) in longrange_discriminator.py, which the marginal-
# preserving surrogates cannot fake. On NNS alone the earned claim is
# 'marginal spacing matches GUE'.
FINDINGS = [
    dict(name='zeta_first_2000',      source='§7.ter.7',
         expected='TR',
         expected_survives=['hawkes_matched'],
         loader=lambda: load_zeta_first(n=2000)),
    dict(name='zeta_high_height',     source='§7.ter.21',
         expected='TR',
         expected_survives=['hawkes_matched'],
         loader=lambda: load_zeta_high(n=4000)),
    dict(name='lmfdb_ec_pooled',      source='§7.ter.4',
         expected='TR',
         expected_survives=['hawkes_matched'],
         loader=load_lmfdb_pooled),
    dict(name='dirichlet_pooled',     source='§7.ter.3',
         expected='TR',
         expected_survives=['hawkes_matched'],
         loader=load_dirichlet_pooled),
    dict(name='earthquakes_M45',      source='§7.ter.4',
         expected='BL',
         # Earthquakes are Hawkes-like (ETAS).  hawkes_matched is the
         # surrogate that should reproduce the BL classification (expected
         # catch — not a problem, the discipline working).
         expected_survives=['phase_randomized', 'cumulant_matched'],
         loader=load_earthquakes),
    dict(name='primes_1e6',           source='§7.ter.21, .23',
         expected='BR_artifact',
         expected_survives=['phase_randomized', 'hawkes_matched',
                              'cumulant_matched'],
         loader=lambda: load_primes(1_000_000)),
    dict(name='twin_primes_1e7',      source='§7.ter.21, .23',
         expected='BR_artifact',
         expected_survives=['phase_randomized', 'hawkes_matched',
                              'cumulant_matched'],
         loader=lambda: load_twin_primes(10_000_000)),
]


# ─── Classification ───────────────────────────────────────────────────────


def primary_quadrant(events):
    if events.size < MIN_EVENTS:
        return 'underpowered', float('nan'), float('nan'), int(events.size)
    j = joint_q_profile(events, q_max=Q_MAX, min_events_per_q=MIN_EVENTS)
    qd = joint_quadrant_diagnostic(j)
    well = qd[~qd['underpowered']]
    if not len(well):
        return 'underpowered', float('nan'), float('nan'), int(events.size)
    counts = well['quadrant'].value_counts()
    primary = str(counts.idxmax())
    rep_med = float(well['rep_int_q'].median())
    ks_med = float(well['ks_gue_q'].median())
    return primary, rep_med, ks_med, int(events.size)


# ─── Surrogate dispatch ───────────────────────────────────────────────────


def apply_surrogate(events, name, rng):
    if name == 'phase_randomized':
        # Tier 3 inputs are point processes by construction (zeros, primes,
        # earthquake event catalog) — there is no continuous-signal +
        # extractor in the data-generating process.  Use the IEI-domain
        # phase randomisation to avoid contaminating the surrogate with
        # the find_peaks autocorrelation rhythm (§7.ter.19) that the
        # chirp-driven variant introduces when applied to such inputs.
        return phase_randomized_iei_events(events, rng=rng)
    if name == 'hawkes_matched':
        return hawkes_matched_events(events, rng=rng)
    if name == 'cumulant_matched':
        return cumulant_matched_events(events, rng=rng)
    raise ValueError(name)


def apply_apparatus(events, name, rng):
    """Apply a collection-method perturbation to the DATA (dead time as a
    fraction of the mean ISI; thinning as Bernoulli retention). The verdict is
    apparatus-robust iff the re-classified quadrant is UNCHANGED."""
    m = ic.mean_isi(events)
    if not np.isfinite(m) or m <= 0:
        return np.asarray(events, dtype=np.float64)
    if name == 'deadtime_0.15':
        return ic.apply_deadtime(events, 0.15 * m)
    if name == 'deadtime_0.30':
        return ic.apply_deadtime(events, 0.30 * m)
    if name == 'thin_0.10':
        return ic.random_thin(events, 0.90, rng)
    if name == 'thin_0.25':
        return ic.random_thin(events, 0.75, rng)
    raise ValueError(name)


# ─── Main loop ────────────────────────────────────────────────────────────


def main():
    rows = []
    apparatus_rows = []
    t_start = time.time()
    print("=" * 100)
    print(f"Phase 18 Tier 3 — finding validation across {len(FINDINGS)} "
          f"findings × {len(SURROGATE_NAMES)} surrogates × {N_SEEDS} seeds")
    print("=" * 100)

    unexpected_catches = []   # halt log

    for finding in FINDINGS:
        name = finding['name']
        try:
            t_load = time.time()
            events = finding['loader']()
            print(f"\n  {name}: loaded {events.size:,} events in "
                  f"{time.time() - t_load:.1f}s")
        except Exception as e:
            print(f"  {name}: load FAILED: {e}")
            continue

        if events.size < MIN_EVENTS:
            print(f"  {name}: too few events ({events.size}); skipping")
            continue

        # Original classification (deterministic — no seed).
        t_orig = time.time()
        orig_q, orig_rep, orig_ks, orig_n = primary_quadrant(events)
        print(f"  ORIGINAL  n={orig_n:,}  rep_med={orig_rep:.3f}  "
              f"ks_gue_med={orig_ks:.3f}  → {orig_q}  "
              f"(expected {finding['expected']})  ⏱ {time.time() - t_orig:.1f}s")

        for surr in SURROGATE_NAMES:
            for seed in range(N_SEEDS):
                t_s = time.time()
                rng = np.random.default_rng(seed * 1000 + abs(hash(surr)) % 50000)
                try:
                    surr_events = apply_surrogate(events, surr, rng)
                except Exception as e:
                    print(f"    {surr:<20} seed={seed}: surrogate FAILED: {e}")
                    rows.append(dict(
                        finding=name, source=finding['source'],
                        seed=seed, surrogate=surr,
                        orig_quadrant=orig_q, orig_rep=orig_rep,
                        orig_ks_gue=orig_ks, orig_n=orig_n,
                        expected=finding['expected'],
                        expected_survives=(surr in finding['expected_survives']),
                        surr_quadrant='error', surr_rep=float('nan'),
                        surr_ks_gue=float('nan'), surr_n=0,
                        survives=False))
                    continue

                surr_q, surr_rep, surr_ks, surr_n = primary_quadrant(surr_events)
                # SURVIVES = surrogate produces a DIFFERENT classification.
                if surr_q == 'underpowered' or orig_q == 'underpowered':
                    survives = False
                else:
                    survives = (surr_q != orig_q)

                expected_to_survive = (surr in finding['expected_survives'])
                # Stop condition: arithmetic finding (zeta/lmfdb/dirichlet/
                # primes/twin_primes) failed a surrogate it was expected to
                # survive.
                arith_findings = {'zeta_first_2000', 'zeta_high_height',
                                  'lmfdb_ec_pooled', 'dirichlet_pooled',
                                  'primes_1e6', 'twin_primes_1e7'}
                is_arith = name in arith_findings
                unexpected = expected_to_survive and (not survives) and is_arith

                if unexpected:
                    unexpected_catches.append(
                        f"{name}/{surr}/seed={seed}: orig={orig_q}, surr={surr_q}")

                rows.append(dict(
                    finding=name, source=finding['source'],
                    seed=seed, surrogate=surr,
                    orig_quadrant=orig_q, orig_rep=orig_rep,
                    orig_ks_gue=orig_ks, orig_n=orig_n,
                    expected=finding['expected'],
                    expected_survives=expected_to_survive,
                    surr_quadrant=surr_q, surr_rep=surr_rep,
                    surr_ks_gue=surr_ks, surr_n=surr_n,
                    survives=bool(survives)))
                tag = 'SURVIVES' if survives else 'CAUGHT'
                exp = '(expected)' if (expected_to_survive == survives) else \
                      '(UNEXPECTED catch — investigate)' if unexpected else \
                      '(expected catch — Hawkes/cumulant agreement is fine)'
                print(f"    {surr:<20} seed={seed}  surr n={surr_n:,}  "
                      f"rep={surr_rep:.3f}  ks={surr_ks:.3f}  "
                      f"→ {surr_q:<12} {tag:<9} {exp}  "
                      f"⏱ {time.time() - t_s:.1f}s")

        # ── Apparatus arm (the instrument): dead time + thinning on the DATA ──
        # robust = quadrant UNCHANGED (collection method did not fake/erase it).
        for appn in APPARATUS_NAMES:
            for seed in range(N_SEEDS):
                t_a = time.time()
                rng = np.random.default_rng(seed * 1000 + abs(hash(appn)) % 50000)
                try:
                    app_events = apply_apparatus(events, appn, rng)
                    app_q, app_rep, app_ks, app_n = primary_quadrant(app_events)
                except Exception as e:
                    print(f"    {appn:<20} seed={seed}: apparatus FAILED: {e}")
                    continue
                stable = (app_q != 'underpowered' and orig_q != 'underpowered'
                          and app_q == orig_q)
                apparatus_rows.append(dict(
                    finding=name, source=finding['source'], seed=seed,
                    apparatus=appn, kind='deadtime' if appn.startswith('deadtime')
                    else 'thinning',
                    orig_quadrant=orig_q, orig_rep=orig_rep, orig_ks_gue=orig_ks,
                    orig_n=orig_n, app_quadrant=app_q, app_rep=app_rep,
                    app_ks_gue=app_ks, app_n=app_n, apparatus_robust=bool(stable)))
                tag = 'ROBUST' if stable else 'MOVED'
                print(f"    {appn:<20} seed={seed}  app n={app_n:,}  "
                      f"rep={app_rep:.3f}  ks={app_ks:.3f}  "
                      f"→ {app_q:<12} {tag:<7} "
                      f"⏱ {time.time() - t_a:.1f}s")

    df = pd.DataFrame(rows)
    out_path = os.path.join(DATA, 'phase18_finding_validation.parquet')
    df.to_parquet(out_path)
    print(f"\n  → {out_path}  ({len(df)} rows)")

    # ── Aggregate ───────────────────────────────────────────────────────
    agg = (df.groupby(['finding', 'surrogate'])
             .agg(survival_rate=('survives', 'mean'),
                  n_seeds=('survives', 'count'),
                  expected_survives=('expected_survives', 'first'),
                  orig_quadrant=('orig_quadrant', 'first'),
                  surr_q_mode=('surr_quadrant',
                               lambda x: x.value_counts().index[0]))
             .reset_index())
    print()
    print("=" * 100)
    print("Survival matrix (finding × surrogate):  fraction of seeds where the "
          "surrogate yielded a different classification (= finding survives)")
    print("=" * 100)
    pivot = agg.pivot(index='finding', columns='surrogate',
                       values='survival_rate')
    print(pivot.to_string(float_format=lambda v: f"{v:.2f}"))

    # Print expected-survival map.
    print()
    print("Expected-survival reference (• = expected to survive):")
    exp_pivot = agg.pivot(index='finding', columns='surrogate',
                            values='expected_survives')
    print(exp_pivot.to_string())

    # ── Plot ────────────────────────────────────────────────────────────
    fig, ax = plt.subplots(figsize=(8.5, 5.5))
    ordered = [f['name'] for f in FINDINGS]
    pivot_arr = pivot.reindex(index=ordered, columns=SURROGATE_NAMES)
    im = ax.imshow(pivot_arr.values, aspect='auto', cmap='RdYlGn',
                    vmin=0, vmax=1)
    ax.set_xticks(np.arange(len(SURROGATE_NAMES)))
    ax.set_xticklabels(SURROGATE_NAMES, rotation=20, ha='right')
    ax.set_yticks(np.arange(len(ordered)))
    ax.set_yticklabels(ordered)
    for i in range(pivot_arr.shape[0]):
        for j in range(pivot_arr.shape[1]):
            v = pivot_arr.values[i, j]
            txt = f"{v:.2f}" if not np.isnan(v) else '—'
            # Mark expected catches with a dot.
            f = FINDINGS[i]
            surr = SURROGATE_NAMES[j]
            if surr not in f['expected_survives']:
                txt += '\n(exp catch)'
            ax.text(j, i, txt, ha='center', va='center', fontsize=8,
                     color='black' if 0.3 < v < 0.7 else 'white')
    cbar = fig.colorbar(im, ax=ax)
    cbar.set_label('survival rate (fraction of seeds where surrogate '
                    '\nproduced a different classification)')
    ax.set_title('Phase 18 Tier 3 — Finding survival matrix\n'
                  '(green = finding survives surrogate; red = surrogate '
                  'reproduces the classification)')
    plt.tight_layout()
    out_png = os.path.join(PLOTS, '51_phase18_finding_survival.png')
    plt.savefig(out_png, dpi=130)
    plt.close()
    print(f"\n  → {out_png}")

    # ── Apparatus-robustness arm (the instrument) ───────────────────────
    if apparatus_rows:
        adf = pd.DataFrame(apparatus_rows)
        a_out = os.path.join(DATA, 'phase18_apparatus_robustness.parquet')
        adf.to_parquet(a_out)
        a_agg = (adf.groupby(['finding', 'apparatus'])
                    .agg(robust_rate=('apparatus_robust', 'mean'),
                         orig_quadrant=('orig_quadrant', 'first'),
                         app_q_mode=('app_quadrant',
                                     lambda x: x.value_counts().index[0]))
                    .reset_index())
        print()
        print("=" * 100)
        print("APPARATUS-ROBUSTNESS matrix (finding × perturbation):  fraction of "
              "seeds where the QUADRANT IS UNCHANGED")
        print("  (POLARITY OPPOSITE to the surrogate matrix: here HIGH = robust = "
              "collection method did not fake/erase the verdict)")
        print("=" * 100)
        a_pivot = a_agg.pivot(index='finding', columns='apparatus',
                              values='robust_rate').reindex(columns=APPARATUS_NAMES)
        print(a_pivot.to_string(float_format=lambda v: f"{v:.2f}"))
        # Per-finding apparatus verdict.
        print()
        print("Apparatus verdict per finding "
              "(dead time fakes repulsion; thinning fakes Poisson):")
        for f in FINDINGS:
            nm = f['name']
            sub = adf[adf.finding == nm]
            if sub.empty:
                continue
            dt = sub[sub.kind == 'deadtime']['apparatus_robust'].mean()
            th = sub[sub.kind == 'thinning']['apparatus_robust'].mean()
            flags = []
            if dt < 0.5:
                flags.append('DEADTIME_SENSITIVE')
            if th < 0.5:
                flags.append('THINNING/EFFICIENCY_SENSITIVE')
            verdict = 'APPARATUS_ROBUST' if not flags else ' + '.join(flags)
            print(f"  {nm:<20} deadtime_robust={dt:.2f}  thinning_robust={th:.2f}"
                  f"  → {verdict}")
        print(f"\n  → {a_out}  ({len(adf)} rows)")
        print("  Bound: apparatus-robust = stable under the manipulations run, "
              "NOT 'the territory'.")

    # ── Stop condition ──────────────────────────────────────────────────
    if unexpected_catches:
        print()
        print("=" * 100)
        print("STOP CONDITION TRIGGERED — unexpected catches on arithmetic findings:")
        print("=" * 100)
        for line in unexpected_catches:
            print(f"  {line}")
        print()
        print("Per the SESSION-PLAN ground rules, this requires investigation "
              "before proceeding to Tier 4.  See Tier 3 Acceptance #4: "
              "'Unexpected catches are findings.  If an arithmetic-side "
              "classification fails a surrogate, this needs investigation.'")
    else:
        print()
        print("No unexpected catches — all arithmetic findings survived their "
              "expected surrogates.  Tier 4 (writeup) unblocked.")

    print(f"\n  total time: {time.time() - t_start:.1f}s")


if __name__ == '__main__':
    main()
