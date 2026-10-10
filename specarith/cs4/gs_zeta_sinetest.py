"""gs_zeta's quadratures (I₃ product rule 40 × 42; in-pair 20 nodes on [0, 2.4]; short midpoint grid × χ; long
trapezoid grid × (1 − χ) on the non-oscillating pieces) run on the sine kernel, against gs_unitary's direct v(b)
(b = 100, 300, 1000; known answer: the sine-kernel step's results)."""
import math

import numpy as np

import gs_unitary as G
import gs_zeta as Z

DIRECT = {100: 0.11995580, 300: 0.11371976, 1000: 0.11153607}
a, wa, e, we = Z.i3_nodes()
A_, E_ = a[:, None], e[None, :]
p, q, s = np.sinc(A_), np.sinc(E_), np.sinc(E_ - A_)
R3 = 1 - p * p - q * q - s * s + 2 * p * q * s
WW = np.outer(wa * G.F(a), we * G.F(e))
rho2 = 1 - np.sinc(Z.DN) ** 2
I2 = 2 * float(np.sum(Z.DW * Z.FD ** 2 * rho2))
rs = Z.short_grid()
rl = Z.long_grid()
rl = rl[rl <= 4.8 * 1000 + 1]
model = G.SineLimit()
short, long_ = np.zeros(3), np.zeros(3)
B = (100, 300, 1000)
for (i, j) in Z.PAIRS:
    d1, d2 = Z.DN[i], Z.DN[j]
    full = G.det4(d1, d2, rs) - (1 - np.sinc(d1) ** 2) * (1 - np.sinc(d2) ** 2)
    non, _ = G.nonosc_np(model, np.array(d1), np.array(d2), rl)
    wgt = 4 * Z.DW[i] * Z.FD[i] * Z.DW[j] * Z.FD[j] * (1 if i == j else 2)
    for k, b in enumerate(B):
        short[k] += wgt * 2 * Z.DR_S * np.sum(G.chi(rs) * Z.gb(rs, b) * full)
        long_[k] += wgt * 2 * Z.DR_L * np.sum((1 - G.chi(rl)) * Z.gb(rl, b) * non.real)
for k, b in enumerate(B):
    I3 = float(np.sum(WW * R3 * np.exp(-math.pi * (E_ - A_) ** 2 / (8 * b * b))))
    v = math.sqrt(2) * I2 + 2 * math.sqrt(2) * I3 + (short[k] + long_[k]) / math.sqrt(2)
    print("b=%5d  gs_zeta quadratures v %.8f  direct %.8f  rel %.1e   (I3 %.10f vs gs_unitary %.10f)"
          % (b, v, DIRECT[b], v / DIRECT[b] - 1, I3, G.I3(b)))
