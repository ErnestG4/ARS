"""Divisor Harmonics v0 -- Addendum A3: token-FREQUENCY control for the numbers result (Will, 2026-10-03).

Hypothesis to exclude: the period-2/4/5/10 excess on 0-99 is a frequency comb -- round numbers (multiples of 5 and 10,
even numbers, powers of 2) are far more common in text, and any activation component that tracks an item's log-frequency
would put peaks at exactly those periods with no divisibility involved.

Steps (sealed in DIVISOR_PREREG.md A3):
  ids    : token ids of the exact item tokens ' 0' .. ' 99' (NeoX tokenizer; local) -> results/divisor/number_token_ids.json
  count  : on spot, over the banked Pile sample (~/llmspec_armb/data/seed1_batches, 3002 batches x 1024 x 2049 uint16
           tokens ~ 6.3e9 tokens; PolyPythias seed-1 order = a uniform shuffle of the Pile): counts of those ids
           -> number_token_counts.json  (numpy only)
  run    : local. For each model: the primary matrix of the numbers concept (primary layers averaged, template mean),
           X (100 x d); covariate c_i = log(count_i + 1), mean-centred; OLS slope beta = X^T c / (c^T c);
           residual X' = X - c beta^T  (removes the rank-1 component along the frequency profile; the quadratic variant
           also removes (c^2 - mean)). Then the SEALED class test (divisor_spectrum.run_concept, unchanged) on X',
           Holm over the same 17 tests with the other concepts' p-values taken from the primary read (unchanged data).
           Prerequisite 'can fire': the class decomposition of the comb profile c itself (fraction of its DFT power in
           d = 2, 4, 5, 10) is reported first; if the comb has no power there, the control is INAPPLICABLE.
Reading (per class d in {2, 4, 5, 10}, primary model, replication beside it):
  SURVIVES      iff Holm still rejects after the linear residualisation;
  VANISHES      iff not rejected AND the smallest detectable f on the residual geometry <= 0.2;
  NOT RESOLVABLE otherwise.
"""
import argparse, json, math, pathlib, sys
import numpy as np
sys.path.insert(0, str(pathlib.Path(__file__).parent))
import divisor_spectrum as S, templates as T

RES = pathlib.Path("results/divisor")


def cmd_ids():
    from transformers import AutoTokenizer
    tok = AutoTokenizer.from_pretrained("EleutherAI/pythia-70m")
    ids = []
    for i in range(100):
        e = tok.encode(" " + str(i)); assert len(e) == 1, (i, e); ids.append(e[0])
    bare = [tok.encode(str(i)) for i in range(100)]
    out = {"item_token_ids": ids, "bare_token_ids": [b[0] if len(b) == 1 else None for b in bare],
           "note": "item tokens are ' N' (space-prefixed) exactly as in the frozen templates"}
    RES.mkdir(parents=True, exist_ok=True); json.dump(out, open(RES / "number_token_ids.json", "w"), indent=1)
    print("ids written", ids[:5], "...")


def cmd_count(ids_json, batch_dir, out_json, max_batches=None):
    """numpy only (spot). Counts every vocab id once (bincount) so the item ids are read off a full table."""
    import glob, time
    ids = json.load(open(ids_json)); items = ids["item_token_ids"]; bare = ids["bare_token_ids"]
    files = sorted(glob.glob(f"{batch_dir}/step*.npy"))[:max_batches]
    tot = np.zeros(65536, np.int64); n_tok = 0; t0 = time.time()
    for k, f in enumerate(files):
        a = np.load(f, mmap_mode="r"); tot += np.bincount(np.asarray(a).ravel(), minlength=65536); n_tok += a.size
        if k % 200 == 0: print(f"{k}/{len(files)} {time.time()-t0:.0f}s", flush=True)
    out = {"n_batches": len(files), "n_tokens": int(n_tok), "item_counts": [int(tot[i]) for i in items],
           "bare_counts": [int(tot[i]) if i is not None else None for i in bare], "source": batch_dir}
    json.dump(out, open(out_json, "w"), indent=1); print("COUNT_DONE", out["n_tokens"], out["item_counts"][:12])


def comb_profile(counts):
    c = np.log(np.asarray(counts, float) + 1.0); c = c - c.mean(); return c


def comb_spectrum(c):
    N = len(c); P = S.power_spectrum(c[:, None]); _, dcl = S.divisor_classes(N)
    tot = P.sum(); return {int(d): float(P[dcl == d].sum() / tot) for d in sorted(set(dcl.tolist()))}, P


def residualise(X, c, quadratic=False):
    cols = [c] if not quadratic else [c, c * c - np.mean(c * c)]
    C = np.stack(cols, 1); beta = np.linalg.lstsq(C, X, rcond=None)[0]
    return X - C @ beta


def run_model(tag, counts, B, Bs, draws, rng, quadratic=False, log=print):
    z = np.load(RES / "acts" / f"{tag}.npz", allow_pickle=False); L = int(z["layers"])
    X = z["numbers_last"].astype(np.float64)[S.primary_layers(L)].mean(0)          # (T, N, d)
    c = comb_profile(counts)
    # residualise the template-averaged matrix (the sealed statistic reads the template mean; the noise estimate uses the
    # per-template spread, so residualise every template with the SAME beta fitted on the mean)
    Xbar = X.mean(0); C = np.stack([c] if not quadratic else [c, c * c - np.mean(c * c)], 1)
    beta = np.linalg.lstsq(C, Xbar - Xbar.mean(0), rcond=None)[0]
    Xres = X - (C @ beta)[None]
    nt = len(S.primary_tests())
    r = S.run_concept(f"numbers|{tag}|resid{'Q' if quadratic else ''}", Xres, "open", B, Bs, rng, [0.02, 0.05, 0.1, 0.2, 0.4, 0.8], draws, nt, log=log)
    # how much of X did the covariate explain, and the correlation of each class's leading harmonic with c
    expl = float(np.linalg.norm(C @ beta) ** 2 / np.linalg.norm(Xbar - Xbar.mean(0)) ** 2)
    return r, expl


def cmd_run(counts_json, tags, B, Bs, draws, seed):
    counts = json.load(open(counts_json))["item_counts"]; c = comb_profile(counts)
    frac, Pc = comb_spectrum(c); rng = np.random.default_rng(seed)
    out = {"counts_source": counts_json, "comb_class_power_fraction": frac, "comb_P": Pc.tolist(),
           "can_fire": sum(frac.get(d, 0) for d in (2, 4, 5, 10)) > 0.10, "models": {}}
    print("comb profile: class power fractions", {d: round(v, 3) for d, v in frac.items()}, "can_fire:", out["can_fire"])
    for tag in tags:
        prim = json.load(open(RES / f"{tag}_last_primary.json"))
        m = {"before": {str(d): {"z": prim["concepts"]["numbers"]["z"][str(d)], "p": prim["concepts"]["numbers"]["p"][str(d)],
                                 "R": prim["concepts"]["numbers"]["R"][str(d)], "holm": prim["holm"][f"numbers:d{d}"]["reject"]} for d in (2, 4, 5, 10)}}
        for variant, quad in (("linear", False), ("quadratic", True)):
            r, expl = run_model(tag, counts, B, Bs, draws, rng, quadratic=quad)
            tests = {k: v["p"] for k, v in prim["holm"].items() if not k.startswith("numbers:")}
            for d in r["classes"]:
                if 1 < d < 100: tests[f"numbers:d{d}"] = r["p"][d]
            H = S.holm(tests); words = {}
            for d in (2, 4, 5, 10):
                rej = H[f"numbers:d{d}"][2]; sf = r["smallest_f"][str(d)]
                words[str(d)] = "SURVIVES" if rej else ("VANISHES" if (sf is not None and sf <= 0.2) else "NOT RESOLVABLE")
            m[variant] = {"explained_fraction": expl, "z": {str(d): r["z"][d] for d in (2, 4, 5, 10)}, "p": {str(d): r["p"][d] for d in (2, 4, 5, 10)},
                          "R": {str(d): r["R"][d] for d in (2, 4, 5, 10)}, "holm_reject": {str(d): H[f"numbers:d{d}"][2] for d in (2, 4, 5, 10)},
                          "p_adj": {str(d): H[f"numbers:d{d}"][1] for d in (2, 4, 5, 10)}, "smallest_f": {str(d): r["smallest_f"][str(d)] for d in (2, 4, 5, 10)},
                          "words": words, "sigma": r["sigma"], "k_eff": r["k_eff"], "cycle_p": r["cycle_p"], "white_p": r["white_p"], "full": r}
            print(f"  {tag} {variant}: explained {expl:.3f}; words {words}; z {{ {', '.join(f'{d}: {r['z'][d]:.1f}' for d in (2,4,5,10))} }}")
        out["models"][tag] = m
    fp = RES / "numbers_freq_control.json"; json.dump(out, open(fp, "w"), indent=1)
    print("WROTE", fp, "FREQ_CONTROL_DONE")


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("cmd", choices=["ids", "count", "run"])
    ap.add_argument("--ids", default=str(RES / "number_token_ids.json")); ap.add_argument("--batch-dir", default="/home/combust/llmspec_armb/data/seed1_batches")
    ap.add_argument("--counts", default=str(RES / "number_token_counts.json")); ap.add_argument("--max-batches", type=int, default=None)
    ap.add_argument("--tags", default="pythia-1.4b,pythia-410m,pythia-70m"); ap.add_argument("--B", type=int, default=4000)
    ap.add_argument("--B-shuffle", type=int, default=10000); ap.add_argument("--power-draws", type=int, default=200); ap.add_argument("--seed", type=int, default=20261003)
    a = ap.parse_args()
    if a.cmd == "ids": cmd_ids()
    elif a.cmd == "count": cmd_count(a.ids, a.batch_dir, a.counts, a.max_batches)
    else: cmd_run(a.counts, a.tags.split(","), a.B, a.B_shuffle, a.power_draws, a.seed)


if __name__ == "__main__":
    main()
