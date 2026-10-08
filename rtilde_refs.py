"""Reference values of the mean gap ratio ⟨r̃⟩ = ⟨min(s_n, s_{n+1}) / max(s_n, s_{n+1})⟩ — one shared, sourced table.

Source: Y. Y. Atas, E. Bogomolny, O. Giraud, G. Roux, "Distribution of the ratio of consecutive level spacings in
random matrix ensembles", Phys. Rev. Lett. 110 (2013) 084101, arXiv:1212.5611, Table I (read from the arXiv LaTeX source,
sha256 of the e-print f211c8ba…dc7f537, 2026-10-08):
  - row ⟨r̃⟩_W: the 3×3 Wigner-like SURMISE, exact closed forms;
  - row ⟨r̃⟩_fit: LARGE-N values from their numerics, 0.5307(1), 0.5996(1), 0.6744(1); Poisson is exact (2 ln 2 − 1).

Use LARGE_N as the reference/label for real spectra (Will, Phase 6.1 D4, 2026-10-08). The surmise differs from large N
by 0.004–0.005 (GOE), 0.003 (GUE), 0.002 (GSE) — about 2 standard errors at 3·10⁴ levels. At finite sizes, verdict bands
should come from matched-size draws, with these constants as labels only.
"""
import math

SURMISE = {
    "Poisson": 2 * math.log(2) - 1,                          # 0.386294
    "GOE": 4 - 2 * math.sqrt(3),                             # 0.535898
    "GUE": 2 * math.sqrt(3) / math.pi - 0.5,                 # 0.602658
    "GSE": 32 / 15 * math.sqrt(3) / math.pi - 0.5,           # 0.676168
}

LARGE_N = {
    "Poisson": 2 * math.log(2) - 1,                          # exact
    "GOE": 0.5307,                                           # Atas et al. 2013 Table I, ±0.0001
    "GUE": 0.5996,
    "GSE": 0.6744,
}
