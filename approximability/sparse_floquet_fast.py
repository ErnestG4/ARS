"""Speedup wrapper for the CERTIFIED cyclic-tridiagonal inertia core (sparse_floquet.py).
The recurrence LOGIC is unchanged — only JIT-compiled (numba @njit) and parallelized (prange) across the
2q INDEPENDENT per-eigenvalue bisections. The LDL recurrence stays sequential WITHIN one eval (that axis is
genuinely un-vectorizable); we parallelize ACROSS the independent evals. Completeness stays Sylvester-rigorous
(inertia(lo)==0 and inertia(hi)==q asserted per sector). Must reproduce the serial core on the overlap.
"""
import numpy as np
from numba import njit, prange

@njit(cache=True)
def inertia_nb(V, E, corner):
    """# eigenvalues of H(corner) strictly below E — JIT of the certified inertia_cyclic (identical recurrence)."""
    q=V.shape[0]; TINY=1e-300
    a0=V[0]-E
    dprev=a0 if a0!=0.0 else TINY
    neg=1 if dprev<0.0 else 0
    sigprev=corner; ssum=sigprev*sigprev/dprev
    for i in range(1,q-1):
        d=(V[i]-E)-1.0/dprev
        if d==0.0: d=TINY
        if d<0.0: neg+=1
        add=1.0 if i==q-2 else 0.0
        sig=add-sigprev/dprev
        ssum+=sig*sig/d
        dprev=d; sigprev=sig
    dlast=(V[q-1]-E)-ssum
    if dlast<0.0: neg+=1
    return neg

@njit(cache=True)
def kth_eig(V, corner, i, lo, hi, tol):
    """i-th eigenvalue (0-indexed asc) = sup{E: inertia(E)<=i}, by bisection on the certified inertia."""
    a=lo; b=hi
    for _ in range(200):
        if b-a<=tol: break
        m=0.5*(a+b)
        if inertia_nb(V,m,corner)<=i: a=m
        else: b=m
    return 0.5*(a+b)

@njit(parallel=True, cache=True)
def all_eigs_nb(V, corner, lo, hi, tol):
    q=V.shape[0]; out=np.empty(q)
    for i in prange(q):
        out[i]=kth_eig(V,corner,float(i),lo,hi,tol)   # i passed as float for signature stability
    return out

def bands_W_fast(V, tol=1e-13):
    """Total bandwidth W + band count via both BCs, parallel+JIT. count_eq_q is Sylvester-rigorous."""
    V=np.ascontiguousarray(V, dtype=np.float64)
    lo=-2.5; hi=float(V.max())+2.5; q=len(V)
    # completeness gate (Sylvester): all q eigenvalues bracketed in [lo,hi], per sector
    for c in (1.0,-1.0):
        assert inertia_nb(V,lo,c)==0, "lo not below spectrum"
        assert inertia_nb(V,hi,c)==q, f"hi does not bracket all q (sector {c})"
    ep=np.sort(all_eigs_nb(V, 1.0, lo, hi, tol))
    ea=np.sort(all_eigs_nb(V,-1.0, lo, hi, tol))
    edges=np.sort(np.concatenate([ep,ea]))
    widths=edges[1::2]-edges[0::2]
    return float(widths.sum()), len(widths), ep, ea
