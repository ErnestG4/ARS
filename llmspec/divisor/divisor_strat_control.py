"""Divisor Harmonics v0 -- Amendment A4 (v2, Will 2026-10-03): STRATIFIED-PERMUTATION frequency null for the numbers result.
CONFIRMATION RUN: designed after A3's descriptive result was seen (residualising log-frequency changed no z-score).

Null hypothesis H0_freq: an item's activation depends on its corpus frequency (any function of it) plus noise, and on
nothing about the number beyond that. Under H0_freq, items of matched corpus count are exchangeable, so permuting items
ONLY WITHIN frequency strata (bins of matched count) yields a valid null that carries the full frequency comb, linear or
not. If the observed divisor-class excess is extreme against that null, frequency does not explain it.

Procedure (per model; primary numbers matrix exactly as the primary read: blocks L/3..2L/3-1 averaged, template mean):
  strata : S = 10 bins of 10 items by rank of count (' 0'..' 99' counts, results/divisor/number_token_counts.json);
           the within-stratum count range is reported (how well matched "matched" is).
  stat   : the SEALED class statistic E_d = sum_{n in d} (P(n) - L_hat(n)) with L_hat the OBSERVED Lorentzian fit
           (divisor_spectrum.analyse_matrix, unchanged), held FIXED across permutations: a permutation destroys the
           translation-symmetry structure the fit models, so re-fitting per permutation biases E_d (verifier, 10-03).
  null   : B_strat = 10 000 within-stratum permutations of the item order; p_d = (#{E_d^perm >= E_d} + 1) / (B + 1),
           one-sided, for d in {2, 4, 5, 10}; Holm over these four. Also reported: the UNSTRATIFIED permutation p (the
           ordinary item shuffle) and a coarse-strata column (S = 5 bins of 20) as sensitivity.
Words per class: SURVIVES iff Holm rejects against the stratified null; VANISHES iff p_strat > 0.05 AND the unstratified
  shuffle rejects (the excess exists but is explained by frequency); NOT RESOLVABLE otherwise (e.g. the stratified null is
  too narrow/wide to say; reported with the null's spread).
Can-fire (verifier): a synthetic non-linear frequency feature (activation = Lorentzian + v (x) g(count), g = comb part of
  the count profile) must read VANISHES; a genuine class plant independent of frequency must read SURVIVES.
"""
import argparse, json, pathlib, sys
import numpy as np
sys.path.insert(0, str(pathlib.Path(__file__).parent))
import divisor_spectrum as S

RES = pathlib.Path("results/divisor")


def strata(counts, n_bins):
    order = np.argsort(np.asarray(counts, float))[::-1]          # descending count
    lab = np.empty(len(counts), int); size = len(counts) // n_bins
    for b in range(n_bins):
        lab[order[b * size:(b + 1) * size]] = b
    rng_ = {b: (int(min(np.asarray(counts)[lab == b])), int(max(np.asarray(counts)[lab == b]))) for b in range(n_bins)}
    return lab, rng_


def strat_perm(lab, rng):
    perm = np.arange(len(lab))
    for b in np.unique(lab):
        idx = np.where(lab == b)[0]; perm[idx] = idx[rng.permutation(len(idx))]
    return perm


def class_E(X, N, boundary):
    r = S.analyse_matrix(X, N, boundary); return r["E"], r


def class_E_fixed(X, Lhat, dcl):
    """Class excess against a FIXED baseline (the observed fit): a permutation destroys the translation-symmetry
    structure the Lorentzian models, so re-fitting per permutation biases E_d (verifier 10-03); the baseline is held."""
    P = S.power_spectrum(X); E, _ = S.class_stats(P, Lhat, dcl); return E


def test_matrix(Xc, counts, B, rng, n_bins=10, classes=(2, 4, 5, 10), boundary="open", log=print):
    N = Xc.shape[0]; lab, cr = strata(counts, n_bins)
    E_obs, r_obs = class_E(Xc, N, boundary); Lhat, dcl = r_obs["Lhat"], r_obs["dcl"]
    Es = {c: np.empty(B) for c in classes}; Eu = {c: np.empty(B) for c in classes}
    for b in range(B):
        E = class_E_fixed(Xc[strat_perm(lab, rng)], Lhat, dcl)
        for c in classes: Es[c][b] = E[c]
        E = class_E_fixed(Xc[rng.permutation(N)], Lhat, dcl)
        for c in classes: Eu[c][b] = E[c]
    p_s = {c: float((np.sum(Es[c] >= E_obs[c]) + 1) / (B + 1)) for c in classes}
    p_u = {c: float((np.sum(Eu[c] >= E_obs[c]) + 1) / (B + 1)) for c in classes}
    z_s = {c: float((E_obs[c] - Es[c].mean()) / (Es[c].std(ddof=1) + 1e-300)) for c in classes}
    H = S.holm({f"d{c}": p_s[c] for c in classes})
    words = {}
    for c in classes:
        rej = H[f"d{c}"][2]
        words[c] = "SURVIVES" if rej else ("VANISHES" if (p_s[c] > 0.05 and p_u[c] < 0.05 / len(classes)) else "NOT RESOLVABLE")
    log(f"    strata={n_bins}: p_strat={ {c: round(v, 4) for c, v in p_s.items()} } p_unstrat={ {c: round(v, 4) for c, v in p_u.items()} } "
        f"z_strat={ {c: round(v, 1) for c, v in z_s.items()} } words={words}")
    return dict(n_bins=n_bins, strata_count_range=cr, E_obs={c: E_obs[c] for c in classes}, p_strat=p_s, p_unstrat=p_u,
                z_strat=z_s, holm={k: {"p": v[0], "p_adj": v[1], "reject": v[2]} for k, v in H.items()}, words=words,
                null_mean={c: float(Es[c].mean()) for c in classes}, null_sd={c: float(Es[c].std(ddof=1)) for c in classes},
                sigma=r_obs["sigma"], B=B)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--counts", default=str(RES / "number_token_counts.json")); ap.add_argument("--tags", default="pythia-1.4b,pythia-410m,pythia-70m")
    ap.add_argument("--B", type=int, default=10000); ap.add_argument("--seed", type=int, default=20261003)
    a = ap.parse_args(); rng = np.random.default_rng(a.seed)
    counts = json.load(open(a.counts))["item_counts"]
    out = {"doc": "A4 v2 stratified-permutation frequency null (CONFIRMATION RUN, designed after A3's descriptive read)", "models": {}}
    for tag in a.tags.split(","):
        z = np.load(RES / "acts" / f"{tag}.npz", allow_pickle=False); L = int(z["layers"])
        X = z["numbers_last"].astype(np.float64)[S.primary_layers(L)].mean(0).mean(0); Xc = X - X.mean(0)
        print(f"== {tag}")
        out["models"][tag] = {"primary_10bins": test_matrix(Xc, counts, a.B, rng, 10),
                              "sensitivity_5bins": test_matrix(Xc, counts, max(2000, a.B // 5), rng, 5)}
    fp = RES / "numbers_strat_control.json"; json.dump(out, open(fp, "w"), indent=1, default=float)
    print("WROTE", fp, "STRAT_CONTROL_DONE")


if __name__ == "__main__":
    main()
