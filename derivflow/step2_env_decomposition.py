#!/usr/bin/env python3
"""ROADMAP Step 2 — environment-conditioned decomposition of the iid stretch.

EXPLORATORY AND UNSEALED unless the prize clause fires (roadmap Step 2). Everything in this
header is PINNED 2026-08-11 (night) BEFORE any per-bin curve was seen, and BEFORE the v1.5.1
campaign's corrected aggregate curves were seen — committed while the campaign was mid-run.

QUESTION: does the iid seed's stretched relaxation decompose into narrower per-environment
exponentials when conditioned on initial local gap environment?

PINNED RULES (the binning-rule pre-commitment the roadmap requires):

1. Environment variable (per root, per step): root j of p^(k) descends from the seed through an
   interlacing ancestry cone of seed roots [j, j+k]. E_j(k) = (x0_{j+k} - x0_j)/k — the
   cone-average seed gap. Deterministic given the seed; no tuning knob.
2. Bins: QUINTILES of E_j(k) among bulk-window roots, quintile edges computed per (replicate, k).
   Five bins, equal population by construction. No other binning will be tried before the ladder
   outcome is filed (a second rule would be a second chance).
3. Per-bin readout: for root j (interior of bulk window), r_j = min/max of its two adjacent
   UNFOLDED gaps (v1.5.1 corrected reference, Richardson primary). Per-bin per-k value:
   1 - mean(r_j) over bin members; ensemble mean over the 16 seal-protocol iid replicates
   (SeedSequence children 32..47, n = 4096); sigma from replicate spread / sqrt(16).
4. k-grid: {1, 2, 4, 8, 16, 32, 64} (the sealed fit grid). Fit window per bin: k with
   per-bin mean > 1e-3 (same rule as the seal).
5. Per-bin fits: the sealed ladder {F1, F2, F3} with AICc, unchanged machinery
   (science_rate_question.fit_ladder). Interpretation ladder, PRE-COMMITTED:
   - SUPPORTED: AICc selects F2 (exponential) in >= 4 of 5 bins AND the fitted tau_b is
     strictly monotone across the five bin quintiles. (Direction NOT pinned — monotonicity is
     the claim; which direction is a finding.)
   - NOT SUPPORTED: AICc selects F3 with beta < 0.9 in >= 3 of 5 bins (the stretch survives
     conditioning — heterogeneity is not (only) initial-environment).
   - MIXED otherwise: filed as MIXED, no richer-form work proceeds from it.
   - Consistency witness (reported, not adjudicating): the population-weighted sum of the five
     fitted per-bin curves overlaid on the aggregate curve.
6. THE PRIZE CLAUSE (only if SUPPORTED): the derived prediction — for ANY seed class the
   relaxation form is the rate-mixture functional of its gap law — becomes SEALABLE. Per the
   roadmap: the new seal is committed BEFORE any mixture prediction is computed for another
   seed class (picket-fence curves are banked-never-fitted; GUE's gap law is known).

Cost: 16 flows to k = 64 at n = 4096 with per-root tracking + corrected references per k.
"""
import json, time
import numpy as np
from track0_harness import diff_step, bulk_idx
from free_conv import F_empirical
from track0_iid_scaling import reference_cdf
from science_rate_question import fit_ladder

N = 4096
K_GRID = [1, 2, 4, 8, 16, 32, 64]
R = 16
NBINS = 5
FIT_WINDOW_MIN = 1e-3
MASTER_SEED = 20260811          # seal RNG protocol; children 32..47 are the n=4096 iid replicates


def per_root_ratios(u):
    """r_j = min/max of the two unfolded gaps adjacent to interior root j; index aligned to u[1:-1]."""
    du = np.diff(u)
    return np.minimum(du[:-1], du[1:]) / np.maximum(du[:-1], du[1:])


def run():
    t0 = time.time()
    children = np.random.SeedSequence(MASTER_SEED).spawn(96)
    acc = {k: [[] for _ in range(NBINS)] for k in K_GRID}   # per-k, per-bin, per-replicate means
    agg = {k: [] for k in K_GRID}
    for i in range(R):
        seed = np.sort(np.random.default_rng(children[32 + i]).uniform(-1.0, 1.0, N))
        F_seed = F_empirical(seed)
        r = seed.copy()
        for k in range(1, K_GRID[-1] + 1):
            r = diff_step(r)
            if k not in K_GRID:
                continue
            m = N - k
            F_at, _ = reference_cdf(F_seed, r, k / N, m)
            u = F_at * m
            bi = bulk_idx(m)
            lo, hi = bi.start, bi.stop
            ratios = per_root_ratios(u)                     # aligned to roots 1..m-2
            j_idx = np.arange(max(lo, 1), min(hi, m - 1))   # interior bulk roots
            rj = ratios[j_idx - 1]
            E = (seed[j_idx + k] - seed[j_idx]) / k         # ancestry-cone mean seed gap
            edges = np.quantile(E, np.linspace(0, 1, NBINS + 1))
            edges[0] -= 1e-12; edges[-1] += 1e-12
            which = np.digitize(E, edges) - 1
            for b in range(NBINS):
                sel = which == b
                acc[k][b].append(1.0 - float(np.mean(rj[sel])))
            agg[k].append(1.0 - float(np.mean(rj)))
        print(f"  rep {i} done", flush=True)

    out = {"step": "ROADMAP Step 2 (exploratory, unsealed)", "pinned_header": "see file header",
           "per_bin": {}, "aggregate": {}, "fits": {}, "ladder_outcome": None}
    for k in K_GRID:
        out["aggregate"][str(k)] = {"mean": float(np.mean(agg[k])),
                                    "sigma_mean": float(np.std(agg[k], ddof=1) / np.sqrt(R))}
        out["per_bin"][str(k)] = [{"mean": float(np.mean(acc[k][b])),
                                   "sigma_mean": float(np.std(acc[k][b], ddof=1) / np.sqrt(R))}
                                  for b in range(NBINS)]
    sel_forms, taus, betas = [], [], []
    for b in range(NBINS):
        ks = [k for k in K_GRID if out["per_bin"][str(k)][b]["mean"] > FIT_WINDOW_MIN]
        means = np.array([out["per_bin"][str(k)][b]["mean"] for k in ks])
        sm = np.array([out["per_bin"][str(k)][b]["sigma_mean"] for k in ks])
        sel, fits = fit_ladder(np.array(ks, dtype=float), means, sm)
        out["fits"][f"bin{b}"] = {"fit_window_k": ks, "selected": sel, "ladder": fits}
        sel_forms.append(sel)
        p = fits[sel].get("params")
        taus.append(p[1] if sel in ("F2", "F3") and p else None)
        betas.append(p[2] if sel == "F3" and p else None)
    n_f2 = sum(1 for f in sel_forms if f == "F2")
    n_f3_stretch = sum(1 for f, be in zip(sel_forms, betas) if f == "F3" and be is not None and be < 0.9)
    tau_ok = all(t is not None for t in taus) and \
        (all(taus[b] < taus[b + 1] for b in range(NBINS - 1)) or
         all(taus[b] > taus[b + 1] for b in range(NBINS - 1)))
    if n_f2 >= 4 and tau_ok:
        out["ladder_outcome"] = "SUPPORTED"
    elif n_f3_stretch >= 3:
        out["ladder_outcome"] = "NOT_SUPPORTED"
    else:
        out["ladder_outcome"] = "MIXED"
    out["selected_forms"] = sel_forms
    out["taus"] = taus
    out["betas"] = betas
    out["runtime_s"] = round(time.time() - t0, 1)
    with open("derivflow/step2_env_decomposition.json", "w") as f:
        json.dump(out, f, indent=1)
    print(f"\nLADDER OUTCOME: {out['ladder_outcome']}")
    print("forms per bin:", sel_forms)
    print("taus:", [None if t is None else round(t, 3) for t in taus])
    print(f"runtime {out['runtime_s']}s")
    return out["ladder_outcome"]


if __name__ == "__main__":
    run()
