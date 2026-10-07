# CC Brief — ARS Spectral–Arithmetic Programme, Phase 6: H = xp and prime spectroscopy (v1)

> Filed verbatim from Will's paste, 2026-10-07. Will's decisions on this brief (same day) are in
> `PH6_DECISIONS_2026-10-07.md` and take precedence where they differ from the text below.

**v1 changes:**
- G0's known answer is Landau's formula.
- New section 6.3, Hamiltonian descent, which runs only after G0–G4 pass.

Part of the spectral–arithmetic programme (brief v1). All of its standing rules apply:
- seal before reading;
- red paths, witnesses must fail;
- FAIL-as-sealed with attribution;
- primary sources or UNVERIFIED;
- check which slot owns each fact;
- CPU on spot;
- nothing is pushed or published without Will.

**Read before starting:** brief v1 §0, which lists the existing ARS work (Session K's Maass data, the comb arc, arsrh Phase 1, Look arc Task B).

## Aim

Test candidate "Riemann Hamiltonians" built on Berry–Keating's H = xp against three properties of the zeta zeros:
1. the smooth zero count;
2. local GUE statistics, including the finite-height corrections from Phase 2;
3. **prime spectroscopy:** the primes appearing as spikes in the Fourier transform of the spectrum.

Property 3 is the decisive one. No proposal is known to reproduce it.

**Expected outcome:** every candidate fails property 3, with that failure documented by a calibrated instrument. That is a legitimate and useful result.

## Background — known answers (fetch and file each primary source before sealing)

- **The explicit formula (Riemann–von Mangoldt / Weil).** For a smooth test function, the sum over zeros of h(γ) equals a smooth term minus a sum over prime powers of (log p / p^{k/2}) · ĝ(k log p). So the Fourier transform of the *fluctuating* part of the zero density has spikes at τ = k·log p, with amplitude ∝ log p / p^{k/2}.
   - **The overall sign is part of the known answer.** Its mismatch with Gutzwiller's formula is the sign puzzle; record the sign convention explicitly.
- **The Selberg trace formula,** for the modular surface. The Maass spectrum's Fourier transform has spikes at the lengths of closed geodesics, ℓ = 2·log λ, where λ is the larger eigenvalue of a primitive hyperbolic class (the R^n L^n family gives the metallic lengths). Elliptic and cusp terms add known smooth contributions.
- **Berry–Keating (1999):** cutting off phase space at x, p ≥ √(2π) gives a cell count matching the smooth N(T) up to its constant term (1 against 7/8).
- **Dilation on an interval (derivation, to verify).** The operator (xp + px)/2 on [l, L], with boundary condition ψ(L) = e^{iθ}ψ(l), has eigenfunctions x^{−1/2+iE}, so the spacing E·log(L/l) = θ + 2πn is *exactly equal*. That is a picket fence: the bare xp regularisation is a crystal. Verify this derivation before using it as a calibrator.
- **Literature candidates.** Fetch, file and state exact definitions for each:
   - Sierra & Townsend (2008, the Landau-level xp);
   - Sierra's x(p + ℓ_p²/p);
   - Bender, Brody & Müller (2017, PRL), the non-Hermitian construction. **Record the published disputes** (e.g. Bellissard's comment) next to it.
   - Connes's absorption interpretation goes in the background only.

## 6.0 — Prime spectroscopy instrument and gates (seal first)

**Statistic.** S(τ) = Σ_k w(γ_k) · e^{iτγ_k} on the unfolded fluctuations, with these sealed in advance:
- the window w (for example a Gaussian taper over the height range);
- the τ grid, over [0.5, 4.5];
- the peak-detection rule;
- the amplitude-fit rule.

The resolution is about 2π / (height span): fine enough to separate log 2, log 3, log 4, log 5, log 7, log 8, log 9.

**The precise G0 known answer is Landau's formula (1911; fetch the primary source):** Σ over 0 < γ ≤ T of x^{iγ} = −(T/2π)·Λ(x)/√x + O(log T), for fixed x > 1. Here Λ(x) = log p if x = p^k, and 0 otherwise. So at τ = log x there are negative spikes at x = 2, 3, 4, 5, 7, 8, 9, 11, …, with heights ∝ log p/√x, and no spike at 6, 10, 12, … (non-prime-powers). Data: Odlyzko's tables, fetched on Will's machine.

**Gates. Every one passes before any candidate is read.**
- **G0, zeta zeros (known answer).** Use Odlyzko's low-height table (first ~10⁵ zeros), hashed. Spikes appear at k·log p for every p^k ≤ declared bound, with amplitude ratios matching log p / p^{k/2} within sealed tolerance. Both the sign and the k = 2 harmonics are checked.
- **G1, the Maass spectrum (second arithmetic positive).** Use Session K's LMFDB lists, sym0 and sym1, run separately per the desymmetrisation gate. Spikes appear at the closed-geodesic lengths 2·log λ (metallic R^n L^n and the others, enumerated from SL(2,ℤ) hyperbolic classes), within tolerance.
- **G2, Dirichlet L-function zeros (a witness on the weights).** Use a real character mod q.
   - The spikes must carry χ(p)-dependent signs, so the instrument has to read arithmetic *weights* and not just positions.
   - The mod-4 character gives sign flips between p ≡ 1 and p ≡ 3 (mod 4).
   - Compute the zeros with PARI if no stored table exists.
- **G3, nulls that must stay silent.** GUE/CUE spectra of matched size and Poisson spectra must show no spikes above the sealed band at any log p.
- **G4, the picket fence.** The interval-dilation spectrum (equally spaced) gives one spike family at its own period and nothing at log p.

## 6.1 — Candidates

For each candidate:
- compute ≥ 10⁴ levels where the construction allows it;
- record the regularisation parameters and the basis size;
- run a convergence check in the basis size, so that a spectrum which hasn't converged is never read.

Then apply four tests:
- **T1, smooth count.** After the declared energy rescaling, does N(E) match Riemann–von Mangoldt, including the constant term?
- **T2, local statistics.** ARS ⟨r̃⟩ (primary), plus NNS, Σ² and Δ₃. Read them as one witness, per Task B. Compare against GUE and against the zeros' finite-height CUE(N_eff) from Phase 2.
- **T3, prime spectroscopy.** Spikes at k·log p with the explicit-formula amplitudes and sign.
- **T4, symmetry class.** β from the ARS classifier. The time-reversal-breaking candidates should read β = 2.

**Verdict per candidate:** a 4-tuple of PASS / FAIL / NOT RESOLVABLE, one entry per test. **No "Riemann Hamiltonian" language unless all four pass**, and even then only "candidate passes the instrument", never anything about RH.

## 6.2 — Exploratory (no verdicts)

- **Deformation scan.** Vary the regularisation parameter of each literature candidate and track how T2 and T3 move. In particular, look for any parameter region where log p spikes begin to form.
- **Weight mapping.** For any candidate showing spikes anywhere, map spike position against log of the nearest prime power, and amplitude against the explicit-formula weight.


## 6.3 — Hamiltonian descent (runs only after G0–G4 pass)

**Idea.** Start from a candidate family H(θ) and slide θ downhill on a loss built from the ARS tests. Eigenvalue gradients come from Hellmann–Feynman: dE/dθ = ⟨ψ|∂H/∂θ|ψ⟩, or from autograd through `eigh`. Run on the GPU, with matrices of a few thousand rows.

**The trap, and the design that avoids it.** Any finite list of numbers is the spectrum of *some* Hermitian matrix: a diagonal one, or a Jacobi matrix from an inverse-eigenvalue construction. Matching zeros directly therefore proves nothing.

**Required constraints (seal all four):**
1. **A constrained family.** Few parameters (declare the count), a quantisation of a classical flow of xp type, and defined independently of the matrix size N. Check convergence in N for every reported result.
2. **Train on primes, test on zeros.**
   - The loss uses only the smooth count (T1) plus prime spectroscopy (T3): spike positions at k·log p and explicit-formula amplitude and sign.
   - **No individual zero heights ever enter the loss.**
   - Zeros are held-out data: after training, compare the candidate's levels with Odlyzko zeros over a declared height range, with a sealed tolerance and a null (GUE draws matched to the density).
3. **Smooth spectral losses only.** Compare spectral transforms and smoothed densities, never ordered eigenvalue lists. Avoided crossings make ordered lists jump.
4. **A null for the descent itself.** Run the same descent on shuffled-prime targets, with spikes placed at log m for random non-prime-powers m. If the family fits fake primes as well as real ones, any fit to the real primes is flexibility, not structure.

**Verdicts:**
- FITS-PRIMES-AND-PREDICTS-ZEROS: never expected; report with full audit if seen.
- FITS-PRIMES-ONLY.
- FITS-NOTHING.
- FLEXIBLE: fits fake primes equally well.

Any positive verdict needs independent replication by a second implementation before it's written up, and even then the claim is "the instrument cannot reject the candidate", never anything about RH.

**Exploratory.** Record the path through parameter space. Watching where spikes start to form along a deformation is informative even if the descent ends with FITS-NOTHING.

## Outputs

- PH6_FINDINGS.md: the gate table, plus the candidate × test verdict matrix.
- Plots: S(τ) for the zeros, Maass, Dirichlet, the nulls, the picket fence, and each candidate, all on the same axes.
- An Open leads section.

## Order and cost

The work is CPU only, minutes to hours: the zeros are tables and the candidate diagonalisations are moderate.

1. Seal the 6.0 rules.
2. Run G0 → G4.
3. Run the 6.1 candidates.
4. Run the 6.2 exploration.
5. Run 6.3 Hamiltonian descent, sealed first; GPU.
