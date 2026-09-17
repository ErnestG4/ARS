"""ring/ — rotational dynamics / attractor geometry arc (build plan v5, this dir).

TORCH IS OPTIONAL AND GUARDED. The venv already carries torch 2.11+cu130 and
cupy 14 (v4 of the plan thought torch was absent; it was not). The rule is not
"torch is not installed" but "no verification file may need it": every checker
runs on numpy, and `verify_ring.py` proves the guard by importing this package
in a subprocess with `sys.modules['torch'] = None`. The network sims take a
`backend` argument; numpy is the default and the only one the board exercises.
"""
try:                                  # guarded on purpose — see docstring
    import torch as _torch            # noqa: F401
    HAVE_TORCH = True
except Exception:                     # ImportError, or a broken CUDA runtime
    _torch = None
    HAVE_TORCH = False

torch = _torch
__all__ = ["HAVE_TORCH", "torch"]
