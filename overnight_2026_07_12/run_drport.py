#!/usr/bin/env python3
"""dr-port (DANDI 000638) — the 7th substrate. Streamed over HTTP-range.

SCOPE, PRE-COMMITTED:
  dr-port EXTENDS THE COUPLING RANGE and TESTS THE DISSOCIATION.
  IT DOES NOT RESURRECT THE LADDER. The fine-grained ordering swapped under the cell-cap
  (a nuisance parameter); a 7th substrate does not stabilise an object that moves under one.
  If the ordering comes back looking clean, THAT IS THE MOMENT TO RE-PERTURB THE CELL-CAP,
  NOT TO BELIEVE IT.

Writes VERDICT_DRPORT.md EVEN ON FAILURE. A silent null is the most dangerous object here.
"""
import os, sys, json, time, traceback
import numpy as np
from scipy import stats

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
for p in (HERE, ROOT, os.path.join(ROOT, "cross_substrate")):
    sys.path.insert(0, p)

import run_overnight as R

SEED = 20260712
MIN_SPIKES = 400
MAX_CELLS = 300
BLOCK = 16 * 1024 * 1024          # 16MB block — banked lesson for multi-GB range reads


def irep(isi):
    return R.irep_unclipped(np.cumsum(isi / isi.mean())) if isi.size >= 50 else np.nan


def logcv(isi):
    return float(np.std(np.log(isi))) if isi.size >= 50 else np.nan


def gsh(x):
    x = x[x > 0]
    s = np.log(x.mean()) - np.log(x).mean()
    return (3 - s + np.sqrt((s - 3) ** 2 + 24 * s)) / (12 * s) if s > 0 else np.nan


def halves(spk, nb=20):
    e = np.linspace(spk.min(), spk.max(), nb + 1)
    i = np.digitize(spk, e) - 1
    return spk[(i % 2) == 0], spk[(i % 2) == 1]


def stream_cells():
    """Per-unit spike trains from DANDI 000638, over HTTP range."""
    import json as _j, urllib.request as _u
    from nwb_remote import open_dandi_asset
    api = ("https://api.dandiarchive.org/api/dandisets/000638/versions/draft/"
           "assets/?page_size=100")
    assets = _j.load(_u.urlopen(api, timeout=60))["results"]
    print(f"  {len(assets)} assets", flush=True)
    n_yield = 0
    for a in assets:
        aid, size, path = a["asset_id"], a["size"], a["path"]
        print(f"  opening {path} ({size/1e9:.1f} GB)…", flush=True)
        try:
            h = open_dandi_asset("000638", aid, size=size, block_size=BLOCK)
        except TypeError:
            h = open_dandi_asset("000638", aid, size=size)
        except Exception as e:
            print(f"    SKIP (open failed): {type(e).__name__}: {e}", flush=True)
            continue
        try:
            with h:
                if "units" not in h:
                    print("    SKIP: no units table", flush=True)
                    continue
                sti = h["units/spike_times_index"][:]
                st = h["units/spike_times"]
                print(f"    {len(sti)} units", flush=True)
                for r in range(len(sti)):
                    lo = 0 if r == 0 else int(sti[r - 1])
                    hi = int(sti[r])
                    if hi - lo < MIN_SPIKES:
                        continue
                    spk = np.sort(np.asarray(st[lo:hi], dtype=np.float64))
                    yield (f"dr/{path}/{r}", spk)
                    n_yield += 1
                    if n_yield >= MAX_CELLS:
                        return
        except Exception as e:
            print(f"    SKIP (read failed): {type(e).__name__}: {e}", flush=True)
            continue


def main():
    t0 = time.time()
    rng = np.random.default_rng(SEED + 99)
    I, S, C, G, ai, bi, ac, bc = [], [], [], [], [], [], [], []
    n_seen = n_used = 0
    try:
        for cid, spk in stream_cells():
            n_seen += 1
            isi = np.diff(spk)
            isi = isi[isi > 0]
            if isi.size < MIN_SPIKES:
                continue
            o = irep(isi)
            sh = np.mean([irep(rng.permutation(isi)) for _ in range(8)])
            c, g = logcv(isi), gsh(isi)
            A, B = halves(spk)
            if A.size < 150 or B.size < 150:
                continue
            ia, ib = np.diff(np.sort(A)), np.diff(np.sort(B))
            ia, ib = ia[ia > 0], ib[ib > 0]
            va, vb = irep(ia), irep(ib)
            la, lb = logcv(ia), logcv(ib)
            if any(np.isnan(x) for x in (o, sh, c, g, va, vb, la, lb)):
                continue
            I.append(o); S.append(sh); C.append(c); G.append(g)
            ai.append(va); bi.append(vb); ac.append(la); bc.append(lb)
            n_used += 1
            if n_used % 25 == 0:
                print(f"    {n_used} cells done ({time.time()-t0:.0f}s)", flush=True)
    except Exception:
        R.write("VERDICT_DRPORT.md", "# dr-port — **STREAM FAILED**\n\n"
                "**This is a FAILURE, not a null.**\n\n"
                f"n_seen={n_seen}  n_used={n_used}\n\n```\n{traceback.format_exc()}\n```\n")
        return

    if n_used < 30:
        R.write("VERDICT_DRPORT.md",
                f"# dr-port — **INSUFFICIENT CELLS**\n\n**A FAILURE, not a null.**\n\n"
                f"n_seen (cells streamed) = **{n_seen}**\nn_used (passed filters) = **{n_used}**\n\n"
                "Denominator reported per the negative-space audit: an unlogged exclusion is an absence.\n")
        return

    sb = lambda r: 2 * r / (1 + r)
    rho_i = sb(stats.spearmanr(ai, bi)[0])
    rho_c = sb(stats.spearmanr(ac, bc)[0])
    coup = stats.spearmanr(C, I)[0]
    gcoup = stats.spearmanr(G, I)[0]
    dis = coup / np.sqrt(max(rho_i, 1e-9) * max(rho_c, 1e-9))
    sl, ic, r, p, se = stats.linregress(np.asarray(S), np.asarray(I))
    res = dict(n_seen=n_seen, n_used=n_used, med_irep=float(np.median(I)),
               rho_i=float(rho_i), rho_c=float(rho_c), coup=float(coup),
               coup_dis=float(dis), gcoup=float(gcoup), R2_marginal=float(r ** 2),
               secs=time.time() - t0)
    json.dump(res, open(os.path.join(HERE, "drport.json"), "w"), indent=1)

    L = ["# dr-port (DANDI 000638) — THE 7th SUBSTRATE", "",
         "**SCOPE, PRE-COMMITTED BEFORE THE RUN:** dr-port **extends the coupling range** and **tests the",
         "dissociation**. **IT DOES NOT RESURRECT THE LADDER.** The fine-grained ordering swapped under the",
         "cell-cap — a nuisance parameter. A 7th substrate does not stabilise an object that moves under one.",
         "**If the ordering comes back looking clean, that is the moment to RE-PERTURB THE CELL-CAP, not to",
         "believe it.**", "",
         f"Streamed over HTTP-range. **n_seen = {n_seen} · n_used = {n_used}** "
         f"({time.time()-t0:.0f}s).", "",
         "| quantity | value |", "|---|---|",
         f"| clustering (median unclipped `I_rep`) | **{np.median(I):+.3f}** |",
         f"| split-half ρ(I_rep) | **{rho_i:+.3f}** |",
         f"| split-half ρ(logCV) | **{rho_c:+.3f}** |",
         f"| **coupling** ρ(log-ISI CV, I_rep) | **{coup:+.3f}** |",
         f"| coupling ρ(gamma-k, I_rep) | **{gcoup:+.3f}** |",
         f"| **coupling, disattenuated** | **{dis:+.3f}** |",
         f"| R²_marginal (variance decomposition) | **{r**2:.3f}** |", "",
         "## Reference (n=6, from `ladder_n6.json`)", "",
         "| substrate | clustering | ρ(I) | coupling | R²_marg |", "|---|---|---|---|---|",
         "| ibl-port | −0.236 | 0.988 | **−0.694** | 0.794 |",
         "| hc3-port | −1.962 | 0.913 | **−0.604** | 0.705 |",
         "| buzsaki | −2.389 | 0.903 | **−0.482** | 0.582 |",
         "| allen-hpf | −8.306 | 0.598 | **−0.429** | 0.574 |",
         "| ret1 | −0.309 | 0.970 | **−0.187** | 0.656 |",
         "| pvc-11 | −0.863 | 0.954 | **+0.076** | 0.761 |",
         f"| **dr-port** | **{np.median(I):+.3f}** | **{rho_i:.3f}** | **{coup:+.3f}** | **{r**2:.3f}** |", "",
         "**Read it against the DISSOCIATION (clustering ⊥ coupling), not against the ordering.**"]
    R.write("VERDICT_DRPORT.md", "\n".join(L))
    print("\n".join(L[-12:]))


if __name__ == "__main__":
    main()
