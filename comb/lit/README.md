# comb/lit — third-party sources are NOT redistributed here

The anchor for the comb calibrator's singular series is:

> Kuperberg, Rodgers, Roditty-Gershon, *arXiv:2001.09513* — Ramanujan J. **58** (2022).

The source is cited, not archived. Fetch it from arXiv if you want to check the
derivation; `comb/singular_series.py` names the exact expression to look for
(grep `\mathfrak{S}(\eta):=`), and `comb/prereg_sealed.json` records the anchor
by citation. Nothing in this repository depends on a local copy.

Rationale: this repository is public, and we do not hold redistribution rights
to third-party papers. Local working copies are git-ignored.
