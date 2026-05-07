# Citation

If you use `criticality_tool` in research or downstream work, please cite
the codebase and the underlying methods.

## Contact

**combust** &lt;combust@thespot.chat&gt;

## How to cite

Until the accompanying paper is published, please cite this repository
directly.  Suggested BibTeX entry:

```bibtex
@software{criticality_tool_2026,
  author       = {combust},
  title        = {criticality\_tool: A Farey PLL bank for measuring
                  dynamical level statistics of arithmetic signals},
  year         = {2026},
  url          = {https://codeberg.org/combust/criticality_tool},
  note         = {Calibrated against Wigner GUE/GOE/Poisson via analytical
                  passage-time NNS.  Headline result: Riemann ζ zeros'
                  passage-time NNS classifies as Wigner GUE with KS = 0.012
                  at heights ≈ 10^6.}
}
```

## Methods to cite separately

The instrument builds on standard random-matrix-theory results.  If your
work depends on any of them, cite the originals:

- **Wigner surmise** for GOE / GUE level spacing distributions:
  Wigner, E.  (1957).  *Statistical properties of real symmetric matrices
  with many dimensions*.  Canadian Mathematical Congress Proceedings,
  pp. 174–184.
- **GUE conjecture for Riemann zeros**:
  Montgomery, H. L.  (1973).  *The pair correlation of zeros of the zeta
  function*.  Analytic Number Theory, Proc. Sympos. Pure Math., Vol. 24,
  AMS, pp. 181–193.  Numerical evidence: Odlyzko, A. M. (1989).
  *On the distribution of spacings between zeros of the zeta function*.
  Math. Comp. 48, 273–308.
- **Katz–Sarnak symmetry conjectures** for L-function families:
  Katz, N. M. and Sarnak, P. (1999).  *Random Matrices, Frobenius
  Eigenvalues, and Monodromy*.  AMS Colloquium Publications 45.
- **Clauset–Shalizi–Newman power-law MLE**:
  Clauset, A., Shalizi, C. R., and Newman, M. E. J. (2009).
  *Power-law distributions in empirical data*.  SIAM Review 51, 661–703.

## External datasets used in the cross-signal table

If you reproduce the §7 cross-signal results from `RESULTS.md`, cite the
datasets:

- **Odlyzko ζ-zero tables** (zeros1, zeros6):
  Odlyzko, A. M.  *Tables of zeros of the Riemann zeta function*.
  https://www-users.cse.umn.edu/~odlyzko/zeta_tables/
- **PhysioNet EEG Motor Movement / Imagery Database**:
  Schalk, G., McFarland, D. J., Hinterberger, T., Birbaumer, N.,
  Wolpaw, J. R. (2004).  *BCI2000: A General-Purpose Brain-Computer
  Interface (BCI) System*.  IEEE TBME 51 (6) 1034–1043.
  Goldberger AL, Amaral LAN, et al. (2000).  *PhysioBank, PhysioToolkit,
  and PhysioNet: Components of a New Research Resource for Complex
  Physiologic Signals*.  Circulation 101 (23) e215–e220.
  https://physionet.org/content/eegmmidb/1.0.0/
