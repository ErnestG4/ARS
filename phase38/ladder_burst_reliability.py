"""
Phase 38 on the ladder — split-half reliability of the per-unit BURST statistic,
per substrate, then regress rho_burst against ladder position.

Protocol replicated from the Allen Phase 38 run (build_ledger.py):
  - per-unit statistic split into 5 equal-time windows; odd {0,2,4} vs even {1,3};
    Spearman-Brown corrected  rho = 2r/(1+r), rank-robust (Spearman r).
  - burst_frac = mean(ISI < 10 ms)   (repo convention, allen_hpf.py:81)
  - gate: tau = 0.20; for a POSITIVE correlation r_obs, attenuation gives
    r_obs <= sqrt(rho_burst * rho_ksgue), rho_ksgue ~ 0.978 (Phase 38), so the
    minimum rho_burst consistent with r_obs is ~ R2_obs. verdictable if measured
    rho_burst comfortably exceeds R2_obs (real structure, not attenuation-limited).

Ladder (burst<->ks_gue, banked): hc-3 +0.78 > ret-1 +0.53 > 000638 +0.44 > V1 +0.25 > HPF ~0.

Diagnostic (the point): does rho_burst RISE with the ladder r (reliability gradient in a
biological costume) or stay FLAT while r varies (ordering survives as biology)? Also
regress rho_burst vs mean firing rate (the mechanical confound the user flagged).
"""
import os, sys, glob
import numpy as np
from scipy.stats import spearmanr

N_WIN = 5
BURST_ISI = 0.010
HC3_FS = 20000.0


def burst_frac(spikes):
    if spikes.size < 3:
        return np.nan
    isi = np.diff(np.sort(spikes))
    return float(np.mean(isi < BURST_ISI))


def split_half_windows(spikes, t0, t1):
    """burst_frac in each of 5 equal-time windows. Returns 5-vector (nan if <10 spikes)."""
    edges = np.linspace(t0, t1, N_WIN + 1)
    out = []
    for w in range(N_WIN):
        seg = spikes[(spikes >= edges[w]) & (spikes < edges[w + 1])]
        out.append(burst_frac(seg) if seg.size >= 10 else np.nan)
    return np.array(out)


def rho_split_half(M):
    """M: (n_cells, 5) per-window burst_frac. rank-robust Spearman-Brown of odd vs even."""
    ok = ~np.isnan(M).any(1)
    M = M[ok]
    if len(M) < 15:
        return np.nan, len(M)
    odd = M[:, ::2].mean(1)
    even = M[:, 1::2].mean(1)
    r = spearmanr(odd, even).statistic
    return (2 * r / (1 + r) if r > 0 else 0.0), len(M)


# ---------- hc-3 (Neuroscope .res/.clu) ----------
def load_hc3_units(session_leaf):
    """Yield per-unit spike times (s) for single units (clu >= 2) across electrode groups."""
    base = os.path.basename(session_leaf)
    units = []
    for res_path in sorted(glob.glob(os.path.join(session_leaf, f"{base}.res.*"))):
        grp = res_path.rsplit(".", 1)[1]
        clu_path = os.path.join(session_leaf, f"{base}.clu.{grp}")
        if not os.path.exists(clu_path):
            continue
        res = np.loadtxt(res_path, dtype=np.int64)
        clu = np.loadtxt(clu_path, dtype=np.int64)
        if clu.size < 2:
            continue
        clu = clu[1:]  # first line = n_clusters
        if clu.size != res.size:
            continue
        t = res / HC3_FS
        for c in np.unique(clu):
            if c >= 2:  # 0=artifact, 1=noise/MUA
                units.append(t[clu == c])
    return units


def run_hc3(sessions, tag):
    rows = []
    rates = []
    for leaf in sessions:
        for spk in load_hc3_units(leaf):
            spk = np.sort(spk)
            if spk.size < 50:
                continue
            t0, t1 = spk[0], spk[-1]
            if t1 - t0 < 60:
                continue
            rows.append(split_half_windows(spk, t0, t1))
            rates.append(spk.size / (t1 - t0))
    M = np.array(rows)
    rho, n = rho_split_half(M)
    return rho, n, np.array(rates)


if __name__ == "__main__":
    SESS = os.path.expandvars("$HOME/fmexplorer/crcns_cache/sessions")
    # EC (Mizuseki entorhinal) sessions = the +0.78 anchor
    ec_tops = [d for d in sorted(os.listdir(SESS)) if d.startswith(("ec013", "ec016"))]
    leaves = []
    for top in ec_tops[:8]:
        p = os.path.join(SESS, top)
        for leaf in sorted(glob.glob(os.path.join(p, "*"))):
            if glob.glob(os.path.join(leaf, "*.res.*")):
                leaves.append(leaf)
    print(f"hc-3 EC: {len(leaves)} session-leaves found")
    rho, n, rates = run_hc3(leaves, "hc-3 EC")
    print(f"\nhc-3 EC (ladder r=+0.78, R2_obs=0.61):")
    print(f"  n_units={n}  split-half rho_burst = {rho:.4f}")
    print(f"  mean firing rate: median={np.median(rates):.2f} Hz  (rate<->reliability confound check)")
    print(f"  gate: rho_burst {'>' if rho > 0.61 else '<='} R2_obs=0.61  -> "
          f"{'verdictable (headroom)' if rho > 0.61 else 'RELIABILITY-LIMITED at this rung'}")
