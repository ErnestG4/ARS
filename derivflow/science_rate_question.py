#!/usr/bin/env python3
"""derivflow SEALED SCIENCE PHASE — executes seals/RATE_QUESTION_SEAL.json. No free choices here:
every constant, seed procedure, fit form, selection rule, and adjudication threshold below is a
transcription of the seal (commit 95e1ad3, bound to harness commit 90a1787).

Runs: GUE ensemble (SeedSequence children 48-95, 16 per n ascending), picket-fence single flows,
n=4096 documentation rows (k in {128,256,410}, replicate-0 base curves, outside all fits), then
the sealed adjudication: iid (from track0_ensemble.json, children 0-47) vs GUE at n=4096 —
form ladder {F1 power, F2 exponential, F3 stretched-exp} in log10 space, AICc selection on the
fit window (ensemble mean 1-<rtilde> > 1e-3), shape-parameter z-rule (all < 3: RATE-UNIVERSAL;
any >= 5: RATE-SEED-DEPENDENT; else INCONCLUSIVE + mandatory power statement; form disagreement
=> RATE-SEED-DEPENDENT). Picket-fence: ceiling-invariance clause only. k*(n): descriptive table.
"""
import json, time
import numpy as np
from scipy.linalg import eigvalsh_tridiagonal
from scipy.optimize import curve_fit
from track0_harness import diff_step, bulk_idx, rtilde, sigma2
from free_conv import F_empirical
from track0_iid_scaling import reference_cdf

MASTER_SEED = 20260811
N_SCIENCE = [1024, 2048, 4096]
K_GRID_FIT = [1, 2, 4, 8, 16, 32, 64]
K_GRID_DOC = [128, 256, 410]
R = 16
FIT_WINDOW_MIN = 1e-3
KSTAR_LEVEL = 1e-2
Z_UNIVERSAL, Z_DEPENDENT = 3.0, 5.0
LN10 = np.log(10.0)


def gue_seed(n, rng):
    """Seal §design.seeds.gue: DE beta=2 tridiagonal, full spectrum, /sqrt(n)."""
    diag = rng.normal(0.0, np.sqrt(2.0), n)
    off = np.sqrt(rng.chisquare(2.0 * np.arange(n - 1, 0, -1)))
    ev = eigvalsh_tridiagonal(diag / np.sqrt(2.0), off / np.sqrt(2.0))
    return np.sort(ev) / np.sqrt(n)


def one_flow(seed_roots, n, k_list, label):
    F_seed = F_empirical(seed_roots)
    r = seed_roots.copy()
    rec = {}
    for k in range(1, max(k_list) + 1):
        r = diff_step(r)
        if k not in k_list:
            continue
        m = n - k
        F_at, diag = reference_cdf(F_seed, r, k / n, m)
        u = F_at * m
        du = np.diff(u[bulk_idx(m)])
        u1 = diag["F_at_eps_raw"] * m                 # band arms (scope v1.5.1: raw eps / 2eps)
        u2 = diag["F_at_2eps"] * m
        rec[k] = {"one_minus_rtilde": 1.0 - rtilde(du), "sigma2_8": sigma2(u[bulk_idx(m)], 8),
                  "one_minus_rtilde_epsraw": 1.0 - rtilde(np.diff(u1[bulk_idx(m)])),
                  "one_minus_rtilde_2eps": 1.0 - rtilde(np.diff(u2[bulk_idx(m)]))}
    print(f"  {label} done", flush=True)
    return rec


# ---- sealed fit machinery ----
def f1(logk, la, b):        return la - b * logk                       # power
def f2(k, la, tau):         return la - (k / tau) * np.log10(np.e)    # exponential
def f3(k, la, tau, beta):   return la - ((k / tau) ** beta) * np.log10(np.e)


def fit_ladder(ks, means, sig_means):
    y = np.log10(means)
    sy = sig_means / (means * LN10)
    N = len(ks)
    out = {}
    for name, fn, p0, x in [("F1", f1, [y[0], 1.0], np.log10(ks)),
                            ("F2", f2, [y[0], 5.0], ks),
                            ("F3", f3, [y[0], 5.0, 1.0], ks)]:
        try:
            p, cov = curve_fit(fn, x, y, p0=p0, sigma=sy, absolute_sigma=True, maxfev=20000)
            chi2 = float(np.sum(((y - fn(x, *p)) / sy) ** 2))
            npar = len(p)
            aicc = chi2 + 2 * npar + (2 * npar * (npar + 1) / (N - npar - 1)) if N - npar - 1 > 0 else np.inf
            out[name] = {"params": p.tolist(), "cov": cov.tolist(), "chi2": chi2,
                         "aicc": float(aicc), "dof": N - npar}
        except Exception as e:
            out[name] = {"error": str(e), "aicc": np.inf}
    sel = min(out, key=lambda f: out[f]["aicc"])
    return sel, out


SHAPE_IDX = {"F1": [1], "F2": [1], "F3": [1, 2]}   # b | tau | tau,beta (amplitude excluded)


def kstar(form, params, cov, rng):
    """k where fitted curve crosses KSTAR_LEVEL, CI via 1000 MVN parameter draws."""
    def solve(p):
        la = p[0]; y0 = np.log10(KSTAR_LEVEL)
        if form == "F1":
            return 10 ** ((la - y0) / p[1])
        if form == "F2":
            return p[1] * (la - y0) / np.log10(np.e)
        return p[1] * ((la - y0) / np.log10(np.e)) ** (1.0 / p[2])
    k0 = solve(params)
    draws = rng.multivariate_normal(params, cov, 1000)
    ks = [solve(d) for d in draws if solve(d) > 0]
    return float(k0), float(np.std(ks))


def run():
    t0 = time.time()
    children = np.random.SeedSequence(MASTER_SEED).spawn(96)
    art = {"executes": "seals/RATE_QUESTION_SEAL.json (commit 95e1ad3)", "gue": {}, "picket": {},
           "doc_rows": {}, "fits": {}, "kstar_table": {}, "adjudication": {}}

    for ni, n in enumerate(N_SCIENCE):
        reps = []
        for i in range(R):
            rng = np.random.default_rng(children[48 + ni * R + i])
            reps.append(one_flow(gue_seed(n, rng), n, K_GRID_FIT, f"GUE n={n} rep={i}"))
        art["gue"][str(n)] = {str(k): {
            "values": [r[k]["one_minus_rtilde"] for r in reps],
            "mean": float(np.mean([r[k]["one_minus_rtilde"] for r in reps])),
            "std": float(np.std([r[k]["one_minus_rtilde"] for r in reps], ddof=1)),
            "sigma_mean": float(np.std([r[k]["one_minus_rtilde"] for r in reps], ddof=1) / np.sqrt(R)),
            "mean_epsraw": float(np.mean([r[k]["one_minus_rtilde_epsraw"] for r in reps])),
            "sigma_mean_epsraw": float(np.std([r[k]["one_minus_rtilde_epsraw"] for r in reps], ddof=1) / np.sqrt(R)),
            "mean_2eps": float(np.mean([r[k]["one_minus_rtilde_2eps"] for r in reps])),
            "sigma_mean_2eps": float(np.std([r[k]["one_minus_rtilde_2eps"] for r in reps], ddof=1) / np.sqrt(R)),
            "sigma2_8_mean": float(np.mean([r[k]["sigma2_8"] for r in reps]))} for k in K_GRID_FIT}

    for n in N_SCIENCE:
        pf = np.linspace(-1.0, 1.0, n)
        art["picket"][str(n)] = {str(k): v for k, v in
                                 one_flow(pf, n, K_GRID_FIT, f"picket n={n}").items()}

    n = 4096
    for label, seed in [("iid", np.sort(np.random.default_rng(children[32]).uniform(-1, 1, n))),
                        ("gue", gue_seed(n, np.random.default_rng(children[80])))]:
        art["doc_rows"][label] = {str(k): v for k, v in
                                  one_flow(seed, n, K_GRID_DOC, f"doc {label}").items()}

    # ---- sealed adjudication (v1.5: run at eps AND 2eps; band invariance has teeth) ----
    iid = json.load(open("derivflow/track0_ensemble.json"))["ensembles"]
    rng_ci = np.random.default_rng(12345)
    for band, mkey, skey in [("primary", "mean", "sigma_mean"),
                             ("eps", "mean_epsraw", "sigma_mean_epsraw"),
                             ("2eps", "mean_2eps", "sigma_mean_2eps")]:
        for seed_class, data in [("iid", {nn: iid[nn] for nn in iid}), ("gue", art["gue"])]:
            art["fits"].setdefault(band, {})[seed_class] = {}
            for nn in map(str, N_SCIENCE):
                ks = [k for k in K_GRID_FIT if data[nn][str(k)][mkey] > FIT_WINDOW_MIN]
                means = np.array([data[nn][str(k)][mkey] for k in ks])
                sm = np.array([data[nn][str(k)][skey] for k in ks])
                sel, fits = fit_ladder(np.array(ks, dtype=float), means, sm)
                art["fits"][band][seed_class][nn] = {"fit_window_k": ks, "selected": sel, "ladder": fits}
                if band == "primary" and "params" in fits[sel]:
                    k0, kerr = kstar(sel, np.array(fits[sel]["params"]), np.array(fits[sel]["cov"]), rng_ci)
                    art["kstar_table"].setdefault(seed_class, {})[nn] = {"kstar": k0, "err": kerr, "form": sel}

    fi, fg = art["fits"]["primary"]["iid"]["4096"], art["fits"]["primary"]["gue"]["4096"]
    adj = {"n_adjudicated": 4096, "iid_form": fi["selected"], "gue_form": fg["selected"],
           "band_forms": {b: {sc: art["fits"][b][sc]["4096"]["selected"] for sc in ("iid", "gue")}
                          for b in ("primary", "eps", "2eps")}}
    # v1.5.1 strengthened clause: selection must agree across {primary, raw-eps, raw-2eps} per seed
    band_invariant = all(len({art["fits"][b][sc]["4096"]["selected"] for b in ("primary", "eps", "2eps")}) == 1
                         for sc in ("iid", "gue"))
    adj["band_invariant"] = band_invariant
    if not band_invariant:
        adj["verdict"] = "INCONCLUSIVE-ON-INSTRUMENT-GROUNDS"
        adj["basis"] = ("form selection not invariant across {primary, eps, 2eps} "
                        f"(scope v1.5.1 band clause): {adj['band_forms']}")
    elif fi["selected"] != fg["selected"]:
        adj["verdict"] = "RATE-SEED-DEPENDENT"
        adj["basis"] = "form disagreement (seal adjudication clause), invariant under the v1.5.1 band"
    else:
        form = fi["selected"]
        pi, ci = np.array(fi["ladder"][form]["params"]), np.array(fi["ladder"][form]["cov"])
        pg, cg = np.array(fg["ladder"][form]["params"]), np.array(fg["ladder"][form]["cov"])
        zs = {}
        for idx in SHAPE_IDX[form]:
            zs[f"param{idx}"] = float(abs(pi[idx] - pg[idx]) / np.sqrt(ci[idx][idx] + cg[idx][idx]))
        adj["shape_z"] = zs
        zmax = max(zs.values())
        if zmax < Z_UNIVERSAL:
            adj["verdict"] = "RATE-UNIVERSAL"
        elif zmax >= Z_DEPENDENT:
            adj["verdict"] = "RATE-SEED-DEPENDENT"
        else:
            adj["verdict"] = "INCONCLUSIVE"
            adj["power_statement"] = ("achieved shape-parameter sigma implies resolvable separation "
                                      f"~{3*np.sqrt(max(ci[i][i]+cg[i][i] for i in SHAPE_IDX[form])):.3g} "
                                      "at 3-sigma; measured separation falls in the 3-5 sigma band")
    pf_ok = all(v["one_minus_rtilde"] < FIT_WINDOW_MIN
                for nn in art["picket"] for v in art["picket"][nn].values())
    adj["picket_fence_ceiling_invariant"] = bool(pf_ok)
    art["adjudication"] = adj
    art["runtime_s"] = round(time.time() - t0, 1)
    with open("derivflow/science_rate_question.json", "w") as f:
        json.dump(art, f, indent=1)
    print(f"\nVERDICT: {adj['verdict']}  (picket ceiling-invariant: {pf_ok})")
    print(f"forms: iid={adj['iid_form']} gue={adj['gue_form']}" +
          (f"  shape z: {adj.get('shape_z')}" if "shape_z" in adj else ""))
    for sc in art["kstar_table"]:
        for nn, v in art["kstar_table"][sc].items():
            print(f"k*({sc}, n={nn}) = {v['kstar']:.2f} ± {v['err']:.2f}  [{v['form']}]")
    print(f"runtime {art['runtime_s']}s -> derivflow/science_rate_question.json")


if __name__ == "__main__":
    run()
