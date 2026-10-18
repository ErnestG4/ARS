"""Near-resonant (off-diagonal) prime-triple contribution to the third moment of
DeltaS = S(t+h) - S(t), averaged over t in a window of width H (our derivation).

Model: S(t) ~ -(1/pi) sum_n Lambda(n) sin(t log n) / (sqrt(n) log n), n <= X.
DeltaS(tau) = sum_n b_n cos(tau log n), tau = t + h/2,
b_n = -(2/pi) Lambda(n)/(sqrt(n) log n) * sin(h log n / 2).
(DeltaS)^3 -> (1/4) sum_{n1,n2,n3} b1 b2 b3 [cos(tau(l1+l2-l3)) + 2 perms + cos(tau(l1+l2+l3))].
Window average of cos(omega tau + phi) over width H = cos(omega Tc + phi) sinc(omega H/2).
Random-phase model: RMS^2 over window centres = sum_omega (c_omega sinc)^2 / 2.
numpy only.
"""
import numpy as np, time, sys

PI = np.pi
TRAP = getattr(np, "trapezoid", None) or np.trapz
H = 2.1e6
L = 3.0
ELLS = [15.6, 17.5, 19.75, 21.25]          # log(t/2pi) of the four files
PMAX = 21_000_000                           # sieve limit for exact enumeration
ME = 20_000_000                             # m = n1 n2 enumerated exactly up to here
J = 24                                      # nearest prime powers on each side of m


def sieve(n):
    s = np.ones(n + 1, dtype=bool); s[:2] = False
    for i in range(2, int(n ** 0.5) + 1):
        if s[i]:
            s[i * i::i] = False
    return np.nonzero(s)[0]


def sinc(x):
    return np.sinc(x / PI)                  # sin(x)/x


t0 = time.time()
P = sieve(PMAX)
print(f"primes <= {PMAX}: {len(P)}  ({time.time()-t0:.1f}s)")

# prime-power list (k = 1, 2) with log p, k
sq = P[P * P <= PMAX]
NV = np.concatenate([P, sq * sq]).astype(np.int64)
KV = np.concatenate([np.ones(len(P)), 2 * np.ones(len(sq))])
LP = np.concatenate([np.log(P), np.log(sq)])
o = np.argsort(NV); NV, KV, LP = NV[o], KV[o], LP[o]


def amp(h, lp, k):
    """b_{p^k} = -(2/pi) sin(h k log p / 2) / (k p^{k/2})"""
    return -(2 / PI) * np.sin(h * k * lp / 2) / (k * np.exp(k * lp / 2))


def exact_resonance(h, X):
    """sum over (p^a, p^b, p^{a+b}) triples: weight 3/4 (a=b) or 6/4 (a!=b)."""
    tot = 0.0; parts = {}
    lp = np.log(P[P <= 10**6]).astype(float)
    for a in range(1, 6):
        for b in range(a, 6):
            if a + b > 8:
                continue
            w = 0.75 if a == b else 1.5
            m = (a + b) * lp <= np.log(X)
            v = w * np.sum((amp(h, lp, a) * amp(h, lp, b) * amp(h, lp, a + b))[m])
            parts[(a, b)] = v; tot += v
    return tot, parts


def diag_var(h, X):
    """sum_n b_n^2 / 2 over prime powers n <= X: model Var(DeltaS) (diagonal)."""
    lp = np.log(P.astype(float)); s = 0.0
    for k in (1, 2, 3, 4):
        m = k * lp <= np.log(X)
        s += 0.5 * np.sum(amp(h, lp[m], k) ** 2)
    if X > PMAX:   # primes in (PMAX, X] by PNT density: sum b^2 ~ int (4/pi^2) sin^2(hu/2)/u du
        u = np.linspace(np.log(PMAX), np.log(X), 200001)
        f = (4 / PI**2) * np.sin(h * u / 2) ** 2 / u
        s += 0.5 * TRAP(f, u)
    return s


def enum_triples(h, Mmax, Hw, bands):
    """Exact enumeration: n1 <= n2 prime powers (k<=2), m = n1 n2 <= Mmax,
    n3 = the J nearest prime powers to m on each side (n3 != m).
    Returns variance contributions binned by |omega| H."""
    acc = np.zeros(len(bands) + 1)
    b_all = amp(h, LP, KV)
    nmax = int(np.searchsorted(NV, int(np.sqrt(Mmax)), side='right'))
    for i in range(nmax):
        n1 = NV[i]
        jhi = int(np.searchsorted(NV, Mmax // n1, side='right'))
        if jhi <= i:
            continue
        idx2 = np.arange(i, jhi)
        m = n1 * NV[idx2]
        c = np.where(idx2 == i, 0.75, 1.5)
        w12 = c * b_all[i] * b_all[idx2]
        pos = np.searchsorted(NV, m)
        offs = np.concatenate([np.arange(-J, 0), np.arange(0, J)])
        k3 = pos[:, None] + offs[None, :]
        k3 = np.clip(k3, 0, len(NV) - 1)
        n3 = NV[k3]
        valid = n3 != m[:, None]
        om = np.log1p((m[:, None] - n3) / n3.astype(float))
        w = w12[:, None] * b_all[k3] * sinc(om * Hw / 2)
        contrib = np.where(valid, 0.5 * w * w, 0.0)
        xb = np.abs(om) * Hw
        bi = np.searchsorted(bands, xb)
        acc += np.bincount(bi.ravel(), weights=contrib.ravel(), minlength=len(bands) + 1)
    return acc


def density_part(h, Mlo, Mhi, Hw, P1=10**5):
    """m in (Mlo, Mhi]: inner n3-sum by PNT density (sinc^2 integrated exactly):
    per unordered pair (n1<n2): (9/4)(1/2) b1^2 b2^2 * 8 sin^2(h log m/2)/(pi Hw log m).
    n1 exact primes <= P1, n2 by density; n1 > P1 both by density."""
    if Mhi <= Mlo:
        return 0.0
    lMlo, lMhi = np.log(Mlo), np.log(Mhi)
    def inner(u1, b1sq):                      # integrate over u2 >= u1, u1+u2 in (lMlo, lMhi]
        lo = max(u1, lMlo - u1); hi = lMhi - u1
        if hi <= lo:
            return 0.0
        u2 = np.linspace(lo, hi, max(2001, int((hi - lo) / 0.005)))
        f = (4 / PI**2) * np.sin(h * u2 / 2) ** 2 / u2 \
            * 8 * np.sin(h * (u1 + u2) / 2) ** 2 / (PI * Hw * (u1 + u2))
        return (9 / 8) * b1sq * TRAP(f, u2)
    tot = 0.0
    for p in P[P <= P1]:
        u1 = np.log(p)
        tot += inner(u1, amp(h, u1, 1) ** 2)
    # n1 > P1, density
    u1max = lMhi / 2
    if u1max > np.log(P1):
        u1g = np.linspace(np.log(P1), u1max, 400)
        vals = [inner(u1, 1.0) * (4 / PI**2) * np.sin(h * u1 / 2) ** 2 / u1 for u1 in u1g]
        tot += TRAP(vals, u1g)
    return tot


def pair_var_kappa2(h, X, Hw):
    """kappa2 analogue: unordered pairs n1 != n2 (primes), coefficient b1 b2 on
    cos(tau(l1-l2)); variance sum (b1 b2 sinc)^2/2. Exact for p <= min(X,PMAX),
    density for p in (PMAX, X]."""
    Pm = P[P <= min(X, PMAX)].astype(float)
    b = amp(h, np.log(Pm), 1)
    tot = 0.0
    for d in range(1, 4 * J):
        om = np.log(Pm[d:] / Pm[:-d])
        tot += np.sum(0.5 * (b[d:] * b[:-d] * sinc(om * Hw / 2)) ** 2)
    if X > PMAX:   # per p: (1/2) b_p^2 * sum_q b_q^2 sinc^2 ~ (1/2) b_p^2 (4/pi^2) s^2 (1/log p)(2 pi /Hw) ; /2 unordered
        u = np.linspace(np.log(PMAX), np.log(X), 20001)
        f = (4 / PI**2) * np.sin(h * u / 2) ** 2 / u * 0.5 * (4 / PI**2) * np.sin(h * u / 2) ** 2 \
            * (2 * PI / Hw) / u * 0.5
        tot += TRAP(f, u)
    return tot


bands = np.array([1.0, PI, 10.0, 100.0])
print("\n=== per height: h, X=T/2pi, diag Var(DeltaS), exact-resonance E3 ===")
for ell in ELLS:
    h = 2 * PI * L / ell; X = np.exp(ell)
    e3, parts = exact_resonance(h, X)
    print(f"ell={ell:5.2f} h={h:.4f} X={X:.3e}  Var_diag={diag_var(h, X):.4f}  "
          f"E3_exact={e3:+.5f}  (p,p,p^2)={parts[(1,1)]:+.5f}  (p,p^2,p^3)={parts[(1,2)]:+.5f}")

print("\n=== near-resonant triple RMS (random phase), H = %.2e ===" % H)
for ell in ELLS:
    h = 2 * PI * L / ell; X = np.exp(ell)
    t1 = time.time()
    Mx = min(X, ME)
    acc = enum_triples(h, Mx, H, bands)
    dens_in = density_part(h, Mx, X, H) if X > Mx else 0.0
    dens_x2 = density_part(h, max(Mx, X), X**2, H)
    dens_inf = density_part(h, max(Mx, X), 1e40, H)
    dens_chk = density_part(h, 1e6, Mx, H)           # density approx on the enumerated range (check)
    acc_chk = enum_triples(h, Mx, H, bands) if False else None
    var_cut = acc.sum() + dens_in
    print(f"ell={ell:5.2f}: enum m<={Mx:.2e}: var={acc.sum():.3e}  bands|w|H<1,<pi,<10,<100,>100: "
          + " ".join(f"{v:.2e}" for v in acc)
          + f"\n           density m in ({Mx:.1e},{X:.1e}]: {dens_in:.3e};  density check on (1e6,{Mx:.1e}]: {dens_chk:.3e}"
          + f"\n           RMS(cut X=T/2pi) = {np.sqrt(var_cut):.2e};  +extra to X^2: {dens_x2:.2e} -> RMS {np.sqrt(var_cut+dens_x2):.2e};"
          + f"  no cutoff: RMS {np.sqrt(var_cut+dens_inf):.2e}   ({time.time()-t1:.0f}s)")
    sys.stdout.flush()

print("\n=== scaling with window width (ell=19.75, cutoff X=T/2pi) ===")
ell = 19.75; h = 2 * PI * L / ell; X = np.exp(ell)
for Hw in [2.1e4, 2.1e5, 2.1e6, 2.1e7]:
    acc = enum_triples(h, min(X, ME), Hw, bands)
    v = acc.sum() + density_part(h, min(X, ME), X, Hw)
    print(f"H={Hw:.1e}: RMS={np.sqrt(v):.3e}  RMS*sqrt(H)={np.sqrt(v*Hw):.3f}")

print("\n=== kappa2 analogue (pairs p1 != p2), H=2.1e6 ===")
for ell in ELLS:
    h = 2 * PI * L / ell; X = np.exp(ell)
    v = pair_var_kappa2(h, X, H)
    vinf = pair_var_kappa2(h, X**2, H)
    print(f"ell={ell:5.2f}: RMS(kappa2 offsets, cut X)={np.sqrt(v):.2e}; cut X^2: {np.sqrt(vinf):.2e}")
print(f"total {time.time()-t0:.0f}s")
