"""Sparse (O(q)-memory) Floquet band solver for the Sturmian operator — NEW module, dense engine untouched.

Correctness core = a CERTIFIED cyclic-tridiagonal INERTIA (Sturm) count: exact number of eigenvalues below E
via LDL pivot signs of (H−EI), O(q) memory, guaranteed complete by Sylvester's law of inertia. This makes
count_eq_q rigorous. Band edges (periodic corner=+1, antiperiodic corner=−1) found by inertia-guided bisection;
W = Σ band widths from the sorted 2q edges (same pairing as the certified dense engine, edges[1::2]−edges[0::2]).

STATUS: certified against the dense engine on the OVERLAP (small q). Does NOT reach π depths 6–8 in-session:
the inertia recurrence is O(q) PER EVAL and un-vectorizable across its own sequential dimension, so full
extraction is O(q²) with no JIT (numba/cython absent) → ~107 min at q₆=66317, ~28 h at q₈. Compute-bound,
NOT RAM-bound (this fixes the banked 'RAM wall' framing). The future run needs a compiled inner loop.
"""
import numpy as np

def inertia_cyclic(V, E, corner):
    """# eigenvalues of H(corner) strictly below E. H = tridiag(V; offdiag 1) + corner at (0,q-1),(q-1,0)."""
    q=len(V); a=V-E; TINY=1e-300
    dprev=a[0] if a[0]!=0 else TINY
    neg=1 if dprev<0 else 0
    sigprev=float(corner); ssum=sigprev*sigprev/dprev
    for i in range(1,q-1):
        d=a[i]-1.0/dprev
        if d==0: d=TINY
        if d<0: neg+=1
        add=1.0 if i==q-2 else 0.0
        sig=add - sigprev/dprev
        ssum+=sig*sig/d
        dprev=d; sigprev=sig
    dlast=a[q-1]-ssum
    if dlast<0: neg+=1
    return neg

def eigs_by_inertia(V, corner, lo, hi, tol=1e-12):
    """All q eigenvalues of H(corner) in [lo,hi] via stebz-style inertia bisection. Complete by construction."""
    q=len(V)
    nlo=inertia_cyclic(V,lo,corner); nhi=inertia_cyclic(V,hi,corner)
    out=[]; stack=[(lo,hi,nlo,nhi)]
    while stack:
        a,b,na,nb=stack.pop()
        k=nb-na
        if k<=0: continue
        if b-a<tol:
            for _ in range(k): out.append(0.5*(a+b))    # k eigenvalues (near-degenerate cluster) at midpoint
            continue
        m=0.5*(a+b); nm=inertia_cyclic(V,m,corner)
        if nm>na: stack.append((a,m,na,nm))
        if nb>nm: stack.append((m,b,nm,nb))
    return np.sort(np.array(out))

def bands_W(V, lo=None, hi=None, tol=1e-12):
    """Total bandwidth W and band count via the two BCs. count_eq_q enforced by the inertia oracle."""
    if lo is None: lo=-2.5
    if hi is None: hi=float(V.max())+2.5
    ep=eigs_by_inertia(V,+1.0,lo,hi,tol)
    ea=eigs_by_inertia(V,-1.0,lo,hi,tol)
    q=len(V)
    assert len(ep)==q, f"count_eq_q FAIL periodic: {len(ep)}!={q}"
    assert len(ea)==q, f"count_eq_q FAIL antiperiodic: {len(ea)}!={q}"
    edges=np.sort(np.concatenate([ep,ea]))
    widths=edges[1::2]-edges[0::2]
    return float(widths.sum()), len(widths)
