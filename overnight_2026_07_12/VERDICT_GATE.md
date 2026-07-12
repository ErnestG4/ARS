# GATE — what do LV and ks_gue actually compute?

git SHA: `48645c541b`   seed: 20260712

## I13_lv
```python
def I13_lv(positions) -> Optional[float]:
    """Lv (Shinomoto 2003): mean over adjacent-ISI pairs of 3((Iᵢ−Iᵢ₊₁)/(Iᵢ+Iᵢ₊₁))². Parameter-free,
    rate-robust local variation; Poisson→1, regular→<1, bursty→>1. Cross-check to I.12_cv2."""
    d = _ordered_intervals(positions)
    if d.size < MIN_N_NNS:
        return None
    a, b = d[:-1], d[1:]
    return float(np.mean(3.0 * ((a - b) / (a + b)) ** 2))
```
**Shinomoto adjacent-pair form: CONFIRMED**

## I5_ks_gue
```python
def I5_ks_gue(s) -> Optional[float]:
    """KS to GUE on the matched plain-NNS object (object (a)). Distinct from
    pvc-11's banked Farey-q-banded ks_gue_med (carry that separately)."""
    s = np.asarray(s, dtype=np.float64)
    return _ks_cdf(s, nns_cdf_gue) if s.size >= MIN_N_NNS else None
```
## canonical_spacings (what ks_gue is fed)
```python
def canonical_spacings(positions: Sequence[float]) -> np.ndarray:
    """The matched spacing array: 2–98% trim + unit-mean renorm of the
    unfolded positions. Identical extractor across substrates."""
    return _trim_spacings(np.asarray(positions, dtype=np.float64))
```
**KS on the spacing multiset (marginal only, no drift correction): CONFIRMED**

## ⚠ A NEW BUG, found because the numeric check CONTRADICTED my algebra

I derived that `ks_gue` must be **exactly** order-invariant (a trim sorts, a unit-mean divides —
both permutation-invariant ⇒ `ks_gue(shuffled) ≡ ks_gue(observed)`). **The measurement said
otherwise** (|Δ| ≈ 1e-3 … 2e-2). The derivation was wrong, and the reason is a bug:

`phase35a/unfold_rotnum.py:70-74`
```python
def spacings(unf):
    u = np.sort(unf); d = np.diff(u)
    d = d[int(0.02 * len(d)):int(0.98 * len(d))]   # <-- POSITIONAL slice of the time-ordered sequence
    m = d.mean()
    return d / m if m > 0 else d
```

**This is a POSITIONAL slice — it drops the first and last 2 % of spacings IN TIME. It is NOT a
"2–98 % tail trim" of the spacing VALUES**, which is what its name and `axes.py:13` both claim.
Same class as `I_rep`'s unreachable *"negative → clustering"* and `phase24/loader.py:49`: a
docstring advertising a capability the code does not have.

Two consequences, and the second is load-bearing:

1. `ks_gue` **is** weakly order-dependent — but only via an **accidental time-crop**, not any
   principled order sensitivity. (So it still cannot be read as an order-domain axis.)
2. **The trim removes NO outlier spacings.** For a **CV = 16** substrate (Allen-HPF) the giant ISIs
   therefore survive, **inflate the unit-mean normaliser**, crush every normalised spacing toward
   zero — and `ks_gue` reads **≈ 0.86** (ζ reads 0.027). **The guard that was supposed to prevent
   exactly this does nothing.** A *third*, independent mechanism for Allen's broken marginal axis.

**Job A therefore computes `ks_gue` BOTH ways** — shipped (positional) and value-trimmed (what it
claims) — so the difference is **measured, not assumed**, and we can see whether Allen's marginal
pathology survives a *correct* trim.

`burst_frac = mean(ISI < 10ms)` remains a pure multiset functional (order-invariant).
LV IS genuinely order-dependent — its shuffle test is the real experiment.
