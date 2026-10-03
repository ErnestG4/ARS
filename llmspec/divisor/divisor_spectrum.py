"""Divisor Harmonics v0 -- CPU analysis (brief §5.2-§6). numpy only (runs on spot, which has no scipy/torch).

Per concept (sealed choices in DIVISOR_PREREG.md):
  1. layers = middle third of the blocks (resid_post), averaged; template average per item; mean-centre over items.
  2. P(n) = sum over model dims of |DFT along items|^2 folded onto n = 1..N//2 (Parseval; basis-free).
  3. Lorentzian null, exponential kernel exp(-|dx|/sigma) on the lattice (domain [-1,1), spacing 2/N, q = exp(-2/(sigma N))):
       periodic:  L(n) = s * (1 - q^2) / (1 - 2 q cos(2 pi n/N) + q^2)                     (brief §5.4; Corollary 2 on the lattice)
       open:      L(n) = s * (1/N) sum_{m=-(N-1)}^{N-1} (N - |m|) q^|m| cos(2 pi n m/N)    (exact periodogram expectation
                  of the same kernel on an open segment -- the DFT-basis statement of Proposition 3)
     fit: 1-D grid over sigma (801 log-spaced values in [10^-2.5, 10^2.5], domain units), closed-form scale, least squares
     in log power (= relative weighting).
  4. divisor classes: polygon vertex count / period dcl = N / gcd(n, N); class statistic E_d = sum_{n in d} (P(n) - L(n)),
     z_d = (E_d - mean_null) / sd_null, one-sided p from the parametric bootstrap.
  5. nulls: (a) item-shuffle (cycle gate: lag-1 autocorrelation of the item sequence, rho1 = sum_i <x_i, x_{i+1}> /
     sum_i |x_i|^2, circular for periodic BC, open otherwise; the fundamental fraction f1 is descriptive); (b) parametric
     Lorentzian bootstrap:
     Gaussian Fourier coefficients with variance L_hat(n), k_eff random dims (k_eff = participation ratio of the data),
     plus isotropic noise matched to the template-averaging variance; the SAME fit and statistics on every draw.
  6. gates: weekdays (prime) residual-whiteness; nouns (shuffled) cycle gate must be NULL; Holm over the primary tests.
  7. power: planted class excess (fraction f of the fitted Lorentzian power) through the same generator, detected against
     the unplanted null threshold; smallest f with power >= 0.8 reported per class (NOT RESOLVABLE if none).
"""
import argparse, json, math, pathlib, sys, time
import numpy as np
sys.path.insert(0, str(pathlib.Path(__file__).parent))
import templates as T

SIG_GRID = np.logspace(-2.5, 2.5, 801)   # sigma in units of the domain [-1,1) (period 2)
_SHAPES = {}

def divisor_classes(N):
    """n -> dcl = N/gcd(n,N) for n = 1..N//2; nontrivial classes are 1 < dcl < N."""
    n = np.arange(1, N // 2 + 1)
    return n, np.array([N // math.gcd(int(k), N) for k in n])

def lorentz_shape(N, sigma, boundary):
    n = np.arange(1, N // 2 + 1)
    q = math.exp(-2.0 / (sigma * N))
    if boundary == "periodic":
        return (1 - q * q) / (1 - 2 * q * np.cos(2 * np.pi * n / N) + q * q)
    m = np.arange(-(N - 1), N)
    w = (N - np.abs(m)) * q ** np.abs(m)
    return (np.cos(2 * np.pi * np.outer(n, m) / N) @ w) / N

def shape_grid(N, boundary):
    key = (N, boundary)
    if key not in _SHAPES:
        _SHAPES[key] = np.log(np.maximum(np.array([lorentz_shape(N, s, boundary) for s in SIG_GRID]), 1e-300))
    return _SHAPES[key]

def fit_lorentz(P, N, boundary):
    """LS in log power over the sigma grid; returns (sigma, scale, L_hat)."""
    lp = np.log(np.maximum(P, 1e-300)); LS = shape_grid(N, boundary)
    D = lp[None, :] - LS; c = D.mean(1); r = np.sum((D - c[:, None]) ** 2, 1); i = int(np.argmin(r))
    return float(SIG_GRID[i]), math.exp(c[i]), np.exp(c[i] + LS[i])

def power_spectrum(X):
    """X: (N, d) item x dims, mean-centred over items. Returns P(n), n = 1..N//2, Parseval-folded."""
    N = X.shape[0]
    pw = np.sum(np.abs(np.fft.fft(X, axis=0) / N) ** 2, axis=1)
    P = np.empty(N // 2)
    for k in range(1, N // 2 + 1):
        P[k - 1] = pw[k] + (pw[N - k] if k != N - k else 0.0)
    return P

def lag1(X, boundary):
    """Lag-1 autocorrelation of the item sequence (circular for periodic BC). Permutation-exact cycle statistic."""
    num = np.sum(X[:-1] * X[1:]) + (np.sum(X[-1] * X[0]) if boundary == "periodic" else 0.0)
    return float(num / np.sum(X * X))

def class_stats(P, Lhat, dcl):
    cls = sorted(set(dcl.tolist()))
    E = {c: float(np.sum((P - Lhat)[dcl == c])) for c in cls}
    R = {c: float(np.sum((P - Lhat)[dcl == c]) / np.sum(Lhat[dcl == c])) for c in cls}
    return E, R

def synth(N, d, k_eff, Lhat, noise_var, rng, plant=None):
    """One parametric-bootstrap draw: Gaussian Fourier coefficients (variance Lhat(n) summed over k_eff dims) in a random
    k_eff-dim subspace of R^d, plus isotropic noise. plant = (dcl, class, f): add f * sum(Lhat) power to that class."""
    Lp = Lhat.copy()
    if plant is not None:
        dcl, c, f = plant; idx = dcl == c
        Lp[idx] += f * np.sum(Lhat) / idx.sum()
    F = np.zeros((N, k_eff), complex)
    for k in range(1, N // 2 + 1):
        v = Lp[k - 1]
        if k == N - k:                                      # Nyquist, real
            F[k] = rng.normal(size=k_eff) * math.sqrt(v / k_eff)
        else:
            z = (rng.normal(size=k_eff) + 1j * rng.normal(size=k_eff)) * math.sqrt(v / (4 * k_eff))
            F[k] = z; F[N - k] = np.conj(z)
    Xk = np.real(np.fft.ifft(F, axis=0)) * N                # (N, k_eff); E[P(n)] = Lp(n)
    Q, _ = np.linalg.qr(rng.normal(size=(d, k_eff)))
    X = Xk @ Q.T + rng.normal(size=(N, d)) * math.sqrt(noise_var)
    return X - X.mean(0)

def analyse_matrix(X, N, boundary):
    P = power_spectrum(X); sg, s, Lhat = fit_lorentz(P, N, boundary)
    n, dcl = divisor_classes(N); E, R = class_stats(P, Lhat, dcl)
    return dict(P=P, sigma=sg, scale=s, Lhat=Lhat, dcl=dcl, E=E, R=R, f1=float(P[0] / P.sum()), rho1=lag1(X, boundary),
                resid_max=float(np.max(np.abs(np.log(P) - np.log(Lhat)))))

def primary_layers(L):
    lo, hi = L // 3, (2 * L) // 3                             # blocks lo..hi-1 (resid_post) = hidden_states lo+1..hi
    return list(range(lo + 1, hi + 1))

def run_concept(name, Xall, boundary, B, B_shuffle, rng, power_grid, power_draws, n_tests=17, log=print):
    """Xall: (T, N, d) at the primary layers already averaged. Returns the result dict (JSON-able)."""
    Tn, N, d = Xall.shape
    Xbar = Xall.mean(0); Xc = Xbar - Xbar.mean(0)
    noise_var = float(np.mean(Xall.var(0, ddof=1)) / Tn) if Tn > 1 else 0.0   # template-averaging noise per element
    sv = np.linalg.svd(Xc, compute_uv=False); k_eff = int(np.ceil((sv ** 2).sum() ** 2 / np.sum(sv ** 4)))
    real = analyse_matrix(Xc, N, boundary); dcl = real["dcl"]; cls = sorted(set(dcl.tolist()))
    # item-shuffle null (cycle gate): lag-1 autocorrelation under permutations of the item order
    rho_sh = np.array([lag1(Xc[rng.permutation(N)], boundary) for _ in range(B_shuffle)])
    cycle_p = float((np.sum(rho_sh >= real["rho1"]) + 1) / (B_shuffle + 1))
    tot = real["P"].sum()
    f1_sh = np.array([power_spectrum(Xc[rng.permutation(N)])[0] / tot for _ in range(min(B_shuffle, 1000))])
    f1_p = float((np.sum(f1_sh >= real["f1"]) + 1) / (len(f1_sh) + 1))
    # parametric Lorentzian bootstrap
    En = {c: np.empty(B) for c in cls}; rmax = np.empty(B); sig_b = np.empty(B)
    for b in range(B):
        r = analyse_matrix(synth(N, d, k_eff, real["Lhat"], noise_var, rng), N, boundary)
        for c in cls: En[c][b] = r["E"][c]
        rmax[b] = r["resid_max"]; sig_b[b] = r["sigma"]
    z = {c: float((real["E"][c] - En[c].mean()) / (En[c].std(ddof=1) + 1e-300)) for c in cls}
    p = {c: float((np.sum(En[c] >= real["E"][c]) + 1) / (B + 1)) for c in cls}
    white_p = float((np.sum(rmax >= real["resid_max"]) + 1) / (B + 1))
    # power against the unplanted null threshold: per-class 0.05 and the Holm first-step level 0.05/n_tests
    power, smallest = {}, {}
    for c in cls:
        thr95 = np.quantile(En[c], 0.95); thr_h = np.quantile(En[c], 1 - 0.05 / max(1, n_tests))
        power[c] = {}
        for f in power_grid:
            det = det_h = 0
            for _ in range(power_draws):
                r = analyse_matrix(synth(N, d, k_eff, real["Lhat"], noise_var, rng, plant=(dcl, c, f)), N, boundary)
                det += r["E"][c] > thr95; det_h += r["E"][c] > thr_h
            power[c][f] = (det / power_draws, det_h / power_draws)
        smallest[c] = next((f for f in power_grid if power[c][f][1] >= 0.8), None)
    log(f"  {name:9s} N={N} d={d} k_eff={k_eff} sigma={real['sigma']:.3f} rho1={real['rho1']:.3f} cycle_p={cycle_p:.4f} "
        f"white_p={white_p:.3f} z={ {c: round(v, 2) for c, v in z.items()} } smallest_f={smallest}")
    return dict(N=N, d=d, T=Tn, k_eff=k_eff, noise_var=noise_var, boundary=boundary, P=real["P"].tolist(),
                Lhat=real["Lhat"].tolist(), sigma=real["sigma"], scale=real["scale"], dcl=dcl.tolist(),
                classes=cls, E=real["E"], R=real["R"], z=z, p=p, rho1=real["rho1"], cycle_p=cycle_p, f1=real["f1"], f1_p=f1_p,
                rho1_shuffle_q99=float(np.quantile(rho_sh, 0.99)),
                resid_max=real["resid_max"], white_p=white_p, sigma_boot=[float(np.quantile(sig_b, q)) for q in (0.05, 0.5, 0.95)],
                power={str(c): {str(f): v for f, v in power[c].items()} for c in cls}, smallest_f={str(c): smallest[c] for c in cls},
                B=B, B_shuffle=B_shuffle, n_tests_for_holm_power=n_tests)

def holm(pdict, alpha=0.05):
    """pdict: {key: p}. Returns {key: (p, adjusted_p, reject)}."""
    items = sorted(pdict.items(), key=lambda kv: kv[1]); m = len(items); out = {}; running = 0.0; stop = False
    for i, (k, pv) in enumerate(items):
        adj = min(1.0, max(running, (m - i) * pv)); running = adj
        rej = (not stop) and adj <= alpha
        if not rej: stop = True
        out[k] = (pv, adj, bool(rej))
    return out

def primary_tests():
    """(concept, class) pairs tested in the primary model: composite concepts, nontrivial classes 1 < dcl < N."""
    out = []
    for name, (items, tps, N, bc, role) in T.CONCEPTS.items():
        if role != "composite": continue
        _, dcl = divisor_classes(N)
        out += [(name, c) for c in sorted(set(dcl.tolist())) if 1 < c < N]
    return out

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("acts"); ap.add_argument("--out", default=None); ap.add_argument("--B", type=int, default=4000)
    ap.add_argument("--B-shuffle", type=int, default=10000); ap.add_argument("--power-draws", type=int, default=200)
    ap.add_argument("--read", default="last", choices=["last", "first"]); ap.add_argument("--seed", type=int, default=20261003)
    ap.add_argument("--layers", default="primary", help="'primary' (middle third) or 'all' (per-layer descriptive)")
    ap.add_argument("--power-grid", default="0.02,0.05,0.1,0.2,0.4,0.8")
    a = ap.parse_args()
    rng = np.random.default_rng(a.seed); grid = [float(x) for x in a.power_grid.split(",")]
    z = np.load(a.acts, allow_pickle=False); L = int(z["layers"]); tag = str(z["tag"]); nt = len(primary_tests())
    out = {"tag": tag, "model": str(z["model"]), "layers": L, "read": a.read, "primary_layers_hidden_idx": primary_layers(L),
           "concepts": {}, "n_tests": nt, "time": time.strftime("%Y-%m-%dT%H:%M:%S")}
    print(f"{tag}: L={L} primary hidden-state indices {primary_layers(L)} read={a.read} primary tests={nt}")
    for name, (items, tps, N, bc, role) in T.CONCEPTS.items():
        key = f"{name}_{a.read}"
        if key not in z.files:
            if a.read == "first": continue
            raise KeyError(key)
        X = z[key].astype(np.float64)                              # (L+1, T, N, d)
        bnd = "periodic" if bc == "periodic" else "open"
        if a.layers == "primary":
            out["concepts"][name] = run_concept(name, X[primary_layers(L)].mean(0), bnd, a.B, a.B_shuffle, rng, grid,
                                                a.power_draws, nt)
        else:
            out["concepts"][name] = {"per_layer": {}}
            for li in range(1, L + 1):
                out["concepts"][name]["per_layer"][li] = run_concept(f"{name}@{li}", X[li], bnd, max(200, a.B // 10),
                                                                     max(500, a.B_shuffle // 10), rng, [], 0, nt)
        out["concepts"][name]["role"] = role
    if a.layers == "primary" and a.read == "last":          # Holm + gates only for the sealed primary read (A2: the
        tests = {f"{n}:d{c}": out["concepts"][n]["p"][c] for n, c in primary_tests()}   # first-token column is hours-only)
        out["holm"] = {k: {"p": v[0], "p_adj": v[1], "reject": v[2]} for k, v in holm(tests).items()}
        wd, nn = out["concepts"]["weekdays"], out["concepts"]["nouns"]
        g = {"weekdays_white_p": wd["white_p"], "weekdays_pass": wd["white_p"] > 0.01,
             "nouns_cycle_p": nn["cycle_p"], "nouns_pass": nn["cycle_p"] > 0.01,
             "nouns_min_class_p": min(nn["p"].values()), "nouns_class_pass": min(nn["p"].values()) > 0.01 / len(nn["p"])}
        g["all_pass"] = bool(g["weekdays_pass"] and g["nouns_pass"] and g["nouns_class_pass"])
        out["gates"] = g
        print("HOLM:", {k: (round(v["p"], 4), v["reject"]) for k, v in out["holm"].items()})
        print("GATES:", g)
    fp = a.out or str(pathlib.Path(a.acts).with_suffix("")).replace("/acts/", "/") + f"_{a.read}_{a.layers}.json"
    pathlib.Path(fp).parent.mkdir(parents=True, exist_ok=True)
    json.dump(out, open(fp, "w"), indent=1, default=lambda o: o.tolist() if hasattr(o, "tolist") else str(o))
    print(f"WROTE {fp}  SPECTRUM_DONE {tag}")

if __name__ == "__main__":
    main()
