"""
Phase 17 Tier 4 — Real-signal σ̂ recovery on principled BR_artifact signals.

Apply the validated recover_uniform_jitter_sigma estimator to:
  - primes ≤ 10⁶ (joint_q_profile re-computed from the sieve)
  - twin primes ≤ 10⁷ (re-computed)
  - LLM residual_norm_peaks for Qwen 2.5 3B (cached cascade re-run)
  - ζ first 2000 (TR class, control — should flag out-of-domain)
  - Synthetic uniform_jitter at σ ∈ {0.10, 0.15, 0.20} (controls)
  - Optional slot-based candidates: tokenization rhythm,
    quantized periodic, regular grid + jitter

Compares σ̂ across signals to test:
  - Whether the LLM and primes occupy the same region of BR_artifact
  - Whether σ̂ is architecture-invariant for LLMs
  - Whether slot-based candidates land at the same σ̂ (if so, BR_artifact
    is a generic property of slot-based-with-bounded-jitter generative
    processes; if not, the LLM/primes coincidence is informative)

Output:
  data/phase17_real_signal_recovery.parquet
  plots/49b_phase17_real_signal_sigma_distribution.png
"""
import os, sys, json, time
import numpy as np
import pandas as pd

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, THIS_DIR)
from arithmetic_toolkit import joint_q_profile
from field_generator import generate
from bulk_recovery import recover_uniform_jitter_sigma
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

DATA = os.path.join(THIS_DIR, "data")
PLOTS = os.path.join(THIS_DIR, "plots")
N_TARGET = 1000
Q_MAX = 30
MIN_EVENTS = 30


# ─── Load functions ──────────────────────────────────────────────────────────

def _subsample(t, n=N_TARGET):
    if t.size <= n: return t
    step = t.size // n
    return t[::max(1, step)][:n]


def load_primes(N=10**6):
    sieve = np.ones(N + 1, dtype=bool); sieve[:2] = False
    for p in range(2, int(N**0.5) + 1):
        if sieve[p]: sieve[p*p::p] = False
    primes = np.where(sieve)[0].astype(np.float64)
    unfolded = primes / np.log(np.maximum(primes, 2.0))
    return _subsample(unfolded)


def load_twin_primes(N=10**7):
    sieve = np.ones(N + 1, dtype=bool); sieve[:2] = False
    for p in range(2, int(N**0.5) + 1):
        if sieve[p]: sieve[p*p::p] = False
    primes = np.where(sieve)[0]
    diffs = np.diff(primes)
    twins = primes[:-1][diffs == 2].astype(np.float64)
    unfolded = twins / np.log(np.maximum(twins, 2.0))
    return _subsample(unfolded)


def load_zeta_first():
    z = np.loadtxt(os.path.join(DATA, "odlyzko_zeros6.txt"), max_rows=N_TARGET)
    return (z / (2*np.pi)) * np.log(np.maximum(z / (2*np.pi*np.e), 1.0)) + 7/8


def gen_uniform_control(sigma, seed=0):
    return generate('uniform_jitter', dict(sigma=sigma),
                     n_events=N_TARGET, seed=seed)


def gen_tokenization_rhythm(seed=0):
    """Slot-based candidate: token-boundary positions from running random
    text through a tokenizer (no model run)."""
    try:
        from transformers import AutoTokenizer
    except ImportError:
        return None
    rng = np.random.default_rng(seed)
    # Random word sequence — vary lengths to break trivial periodicity
    words = ('apple banana cherry delta echo fragment glade horizon iguana '
              'junction kestrel lattice meridian nebula octave plume quartet '
              'ridge sapphire trellis umbrella vortex wisteria xenon yarrow '
              'zenith arc beacon catalyst draft ember firmament gale halo '
              'isotope joist knell lobe morass nexus orbit prism quill rune '
              'satchel timbre understory veneer waft xylophone yam zircon').split()
    text = ' '.join(rng.choice(words, size=2000, replace=True))
    tok = AutoTokenizer.from_pretrained("Qwen/Qwen2.5-3B", trust_remote_code=True)
    enc = tok(text, return_offsets_mapping=True, return_tensors='np')
    if 'offset_mapping' in enc:
        offsets = enc['offset_mapping'][0]
        # event = end of each token (character position)
        token_ends = offsets[:, 1].astype(np.float64)
        # Filter out zero-length tokens
        token_ends = token_ends[np.diff(np.concatenate([[0], token_ends])) > 0]
        return _subsample(token_ends)
    return None


def gen_quantized_periodic(seed=0):
    """Slot-based candidate: events at integer positions with discretization
    noise — the cleanest 'regular grid + jitter' instance."""
    rng = np.random.default_rng(seed)
    base = np.arange(1, N_TARGET + 1, dtype=np.float64)
    return np.sort(base + 0.10 * rng.standard_normal(N_TARGET))


def gen_llm_residual_norm_peaks(seed=0):
    """LLM control — full forward pass + residual-norm peak extraction.
    Slow (model load); only one cell to keep Tier 4 runtime bounded."""
    try:
        from llm_cascade import extract_cascade, NATURAL_TEXT
        from llm_extractors import extract_residual_norm_peaks
    except Exception as e:
        print(f"  (LLM data unavailable: {e})")
        return None
    cascade = extract_cascade(NATURAL_TEXT, model_name="Qwen/Qwen2.5-3B",
                               max_seq_len=1024, compute_attention=False)
    return extract_residual_norm_peaks(cascade)


# ─── Real-signal panel ───────────────────────────────────────────────────────

PANEL = [
    ('zeta_first_2000',         'control_TR',          load_zeta_first),
    ('synthetic_uniform_0.10',  'synthetic_control',   lambda: gen_uniform_control(0.10, seed=0)),
    ('synthetic_uniform_0.15',  'synthetic_control',   lambda: gen_uniform_control(0.15, seed=0)),
    ('synthetic_uniform_0.20',  'synthetic_control',   lambda: gen_uniform_control(0.20, seed=0)),
    ('primes_le_10^6',          'arithmetic',          load_primes),
    ('twin_primes_le_10^7',     'arithmetic',          load_twin_primes),
    ('llm_residual_norm_peaks', 'llm',                 gen_llm_residual_norm_peaks),
    ('tokenization_rhythm',     'slot_based_candidate',gen_tokenization_rhythm),
    ('quantized_periodic',      'slot_based_candidate',gen_quantized_periodic),
]

# Truth values for synthetic controls (None if unknown / not applicable)
TRUTH = {
    'synthetic_uniform_0.10': 0.10,
    'synthetic_uniform_0.15': 0.15,
    'synthetic_uniform_0.20': 0.20,
}


def main():
    t_start = time.time()
    print("=" * 110)
    print("Phase 17 Tier 4 — real-signal σ̂ recovery")
    print("=" * 110)
    rows = []
    for name, family, loader in PANEL:
        t0 = time.time()
        try:
            t_k = loader()
        except Exception as e:
            print(f"  {name:<32}  loader failed: {type(e).__name__}: {e}")
            continue
        if t_k is None or len(t_k) < 50:
            print(f"  {name:<32}  insufficient (n={len(t_k) if t_k is not None else 'None'})")
            rows.append(dict(signal=name, family=family, n=0,
                              sigma_hat=np.nan, ci_lo=np.nan, ci_hi=np.nan,
                              flagged=True, error='insufficient'))
            continue
        j = joint_q_profile(t_k, q_max=Q_MAX, min_events_per_q=MIN_EVENTS)
        sigma_hat, (lo, hi), flagged = recover_uniform_jitter_sigma(j)
        truth = TRUTH.get(name)
        truth_str = f" (truth={truth})" if truth is not None else ""
        elapsed = time.time() - t0
        print(f"  {name:<32}  family={family:<22}  n={len(t_k):>5}  "
              f"σ̂={sigma_hat:.3f}  CI=[{lo:.3f}, {hi:.3f}]  "
              f"flagged={flagged}{truth_str}  ⏱ {elapsed:.0f}s")
        rows.append(dict(signal=name, family=family, n=int(len(t_k)),
                          sigma_hat=sigma_hat, ci_lo=lo, ci_hi=hi,
                          ci_width=hi - lo, flagged=bool(flagged),
                          truth=truth))

    df = pd.DataFrame(rows)
    df.to_parquet(os.path.join(DATA, "phase17_real_signal_recovery.parquet"))
    print(f"\n  → data/phase17_real_signal_recovery.parquet ({len(df)} rows)")

    # ─── Acceptance check ──────────────────────────────────────────────────
    print("\n" + "=" * 110)
    print("ACCEPTANCE CHECK")
    print("=" * 110)
    # 1. ζ control
    z = df[df['signal'] == 'zeta_first_2000']
    if len(z) > 0:
        z_row = z.iloc[0]
        z_sigma = z_row['sigma_hat']
        z_flag = z_row['flagged']
        print(f"  ζ control: σ̂={z_sigma:.3f}, flagged={z_flag}  → "
              f"{'✓ correctly out-of-domain' if z_flag or z_sigma > 0.25 else '✗ spurious confident σ̂'}")
    # 2. Synthetic controls
    print("  Synthetic uniform controls:")
    for sig, truth_val in TRUTH.items():
        row = df[df['signal'] == sig]
        if len(row) == 0: continue
        sig_hat = row['sigma_hat'].iloc[0]
        err = abs(sig_hat - truth_val)
        mark = '✓' if err <= 0.02 else '✗'
        print(f"    {sig:<32}  σ̂={sig_hat:.3f} vs truth {truth_val}  "
              f"|err|={err:.3f}  {mark}")
    # 3. Primes-vs-LLM σ̂ comparison
    print("  Primes-vs-LLM σ̂ comparison:")
    for sig in ('primes_le_10^6', 'twin_primes_le_10^7',
                 'llm_residual_norm_peaks'):
        row = df[df['signal'] == sig]
        if len(row) == 0: continue
        sig_hat = row['sigma_hat'].iloc[0]
        lo = row['ci_lo'].iloc[0]; hi = row['ci_hi'].iloc[0]
        print(f"    {sig:<32}  σ̂={sig_hat:.3f}  CI=[{lo:.3f}, {hi:.3f}]")
    # 4. Slot-based candidates
    print("  Slot-based candidates:")
    for sig in ('tokenization_rhythm', 'quantized_periodic'):
        row = df[df['signal'] == sig]
        if len(row) == 0: continue
        sig_hat = row['sigma_hat'].iloc[0]
        lo = row['ci_lo'].iloc[0]; hi = row['ci_hi'].iloc[0]
        print(f"    {sig:<32}  σ̂={sig_hat:.3f}  CI=[{lo:.3f}, {hi:.3f}]")

    # ─── Forest plot ────────────────────────────────────────────────────────
    valid = df.dropna(subset=['sigma_hat']).copy()
    if len(valid) > 0:
        order = ['zeta_first_2000',
                  'synthetic_uniform_0.10', 'synthetic_uniform_0.15',
                  'synthetic_uniform_0.20',
                  'primes_le_10^6', 'twin_primes_le_10^7',
                  'llm_residual_norm_peaks',
                  'tokenization_rhythm', 'quantized_periodic']
        valid['order_key'] = valid['signal'].apply(
            lambda s: order.index(s) if s in order else 99)
        valid = valid.sort_values('order_key').reset_index(drop=True)

        fig, ax = plt.subplots(figsize=(9, 6))
        family_colors = {
            'control_TR': '#1f77b4', 'synthetic_control': '#2ca02c',
            'arithmetic': '#d62728', 'llm': '#9467bd',
            'slot_based_candidate': '#ff7f0e',
        }
        ys = np.arange(len(valid))
        colors = [family_colors.get(f, '#777777') for f in valid['family']]
        sigma_hats = valid['sigma_hat'].to_numpy()
        ci_lo = valid['ci_lo'].to_numpy(); ci_hi = valid['ci_hi'].to_numpy()
        ax.errorbar(sigma_hats, ys, xerr=[sigma_hats - ci_lo, ci_hi - sigma_hats],
                    fmt='o', ecolor='gray', capsize=3, markersize=7,
                    markeredgecolor='black', markerfacecolor='white')
        for y, (sh, ci_l, ci_h, fam) in enumerate(zip(sigma_hats, ci_lo, ci_hi,
                                                          valid['family'])):
            ax.scatter([sh], [y], c=family_colors.get(fam, '#777777'),
                       s=80, zorder=3, edgecolors='black', linewidths=1)
        # Truth markers for synthetic controls
        for _, r in valid.iterrows():
            if pd.notna(r.get('truth')):
                y = list(valid['signal']).index(r['signal'])
                ax.scatter([r['truth']], [y], marker='|', c='black',
                            s=300, lw=2, zorder=4)
        ax.set_yticks(ys)
        ax.set_yticklabels(valid['signal'], fontsize=9)
        ax.set_xlabel('σ̂  (uniform_jitter parameter)')
        ax.set_xlim(-0.05, 0.6)
        ax.axvline(0.0, color='gray', ls=':', lw=0.8)
        ax.grid(True, axis='x', alpha=0.3)
        # Family legend
        from matplotlib.patches import Patch
        legend_handles = [Patch(facecolor=c, label=f) for f, c in family_colors.items()]
        ax.legend(handles=legend_handles, fontsize=8, loc='upper right')
        ax.set_title('Phase 17 Tier 4 — σ̂ ± 95% CI per real signal '
                      '(black bar = ground truth; controls only)')
        fig.tight_layout()
        fig.savefig(os.path.join(PLOTS, "49b_phase17_real_signal_sigma_distribution.png"),
                    dpi=120)
        plt.close(fig)
        print(f"\n  → plots/49b_phase17_real_signal_sigma_distribution.png")

    print(f"\nTotal time: {time.time() - t_start:.0f}s")


if __name__ == '__main__':
    main()
