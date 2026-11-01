# Bridge kit A4: what ARS needs from the bundle format to ingest fabric streams as calibrators

Brief: Will, 2026-10-31 (Part A4). This is input to the shared spec (Part C), not a change to it: changes go through
the spec. Ingestion code would live in this repo (criticality_tool / specarith), never in ARSv2.

## Must have (ARS refuses a bundle without these)

1. **An exact time base.** `t` as int64 ticks, with `tick_hz` (or the exact rational tick period) in the manifest, not
   float seconds.
   - Calibrator statistics such as spacings, number variance and rates must be recomputable bit for bit.
   - Float timestamps lose the integer structure that the L3 cell guarantees.
2. **The known answer as exact objects, not floats.**
   - A slope as an exact algebraic number: minimal polynomial plus an isolating interval, or a rational p/q.
   - The continued fraction as integers, with preperiod and period for quadratic irrationals; the Stern–Brocot path as
     a string.
   - Expected class: Sturmian / Christoffel / non-Sturmian / Poisson / periodic.
   - Expected p(n) as a rule, for example n + 1.
   - ARS gates compare against these exactly (Part C5).
3. **The averaging class and rate, where known**, as named fields: elliptic N^(−1) / chaotic N^(−½) / the smoothness s
   and dimension d. This is what lets a fabric family serve as a §9.G calibrator: a planted-rate witness with a known
   exponent.
4. **The witness role per bundle**: must-pass / must-fail / descriptive. For must-fail, also name the alternative it
   embodies (for example "random word, same density"). A must-fail without a named alternative can't show which
   confound it excludes (TOOLKIT §9: one null, one confound).
5. **Provenance and hashes:** generator repo and commit, bitstream sha, golden-model sha, config, seed, and the sha256
   of every file.
   - For sealed use, the bundle's manifest sha256 must be stampable (OpenTimestamps) before any ARS statistic is
     computed from it, so sealed-fresh fabric data follows the same seal → stamp → attest → read order.
6. **Schema version, refused if unknown** (already in C1).

## Should have

- **A seeded regeneration recipe** (generator, seed, length), so ARS can regenerate a slice and compare it bit for bit.
  This is a cheap integrity check without trusting the bundle.
- **Word encoding stated completely:** bit order, length in letters, and the letter mapping (1 = slip). A CRC over the
  unpacked letters as well as over the file.
- **Bulk format:** `.npy` or parquet with int64 columns. CSV is too slow at 10⁹ events.
- **A stated "unseen" status** for bundles meant as fresh data: no statistic computed by the producing session. ARS
  records who has seen what, as in its seal discipline.
- **Licence:** `ars-bridge` is AGPL-3.0-or-later, as specified. Any third-party permissive code inside it keeps its
  own notice.

## What ARS would do with them first

- Run the C5 gates on ingest.
- Then use the exact-rate families (B2's hardware Sturmian/Christoffel words at chosen slopes, and coupled variants at
  known gain) as planted-rate witnesses for §9.G. These are calibrators whose averaging exponent is known by
  construction, which is what the GEO1 SE problem lacked.

## Amendment (Will, 2026-10-31: fabric update)

**Dictionary.**
- *Survives:* run length ↔ partial quotient.
- *Withdrawn:* the ε^(−½) edge law. The exponent depends on the shape of the phase detector's peak: T ∝ ε^(−(1−1/ν)).
  The XOR cell gives a log law, and pulse detectors give ε⁻¹.
- *Restricted:* "parabolic ↔ saddle-node" holds only for smooth detectors.
- *Consequence:* any ARS use of the edge law must carry the detector's ν. A manifest field for the PD shape (ν, or the
  class smooth / XOR / pulse) is therefore needed, alongside the averaging class in item 3.

**Hardware words are rational** (32-bit NCO). The manifest carries:
- the exact p/q (density of 1s);
- the intercept;
- the irrational target;
- the agreement length L.

**Ingest change.** "Sturmian" means **Sturmian to length L**. The class checks (p(n) = n + 1, balance) are applied for
n ≤ L only. The known answer is the exact Christoffel / mechanical word of slope p/q with that intercept. Agreement with
the irrational target's word is asserted only up to L.
- A bundle claiming more than L is refused.
- A must-pass "Sturmian" witness is scored on [1, L].
- Past L, the word is periodic with period q, which is the expected answer there.

**words.py** (the seed of `ars-bridge` C2): ARS owns it and fabric imports it. It gets a fresh review on arrival. It has
not arrived yet.
