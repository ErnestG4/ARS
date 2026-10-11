"""Probe (no statistics): PARI complex-character zeros on [-T, T], conjugate symmetry, and E11 quadratic-twist cost."""
import math
import time

import cypari2

pari = cypari2.Pari()
pari.allocatemem(2 * 10 ** 9)
pari("default(realprecision, 38)")
print("PARI", pari("version()"))
q, k = 101, 7
G = f"znstar({q},1)"
T = 8 * 2 * math.pi / math.log(q)
print("conductor of chi_k:", pari(f"znconreyconductor({G},[{k}])"))
zp = sorted(float(x) for x in pari(f"lfunzeros(lfuncreate([{G}, [{k}]]), [-{T:.6f}, {T:.6f}], 64)"))
zc = sorted(float(x) for x in pari(f"lfunzeros(lfuncreate([{G}, [{q - 1 - k}]]), [-{T:.6f}, {T:.6f}], 64)"))
print("n zeros on [-T,T]:", len(zp), "first:", zp[:4], "...", zp[-3:])
print("conjugate = negated zeros:", len(zp) == len(zc) and max(abs(a + b) for a, b in zip(zp, zc[::-1])))
for d in (5, 1009, 40009, 399989):
    t0 = time.time()
    E = f"elltwist(ellinit([0,-1,1,0,0]), {d})"
    N = int(pari(f"ellglobalred({E})[1]"))
    eps = int(pari(f"ellrootno({E})"))
    T = 8 * math.pi / math.log(math.sqrt(N) / (2 * math.pi))
    z = pari(f"lfunzeros(lfuncreate({E}), {T:.6f}, 64)")
    print("d", d, "N", N, "eps", eps, "nz", len(z), "%.1f s" % (time.time() - t0), flush=True)
