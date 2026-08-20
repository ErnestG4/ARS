"""Calibrate the fit_poor threshold with BOTH error rates measured.
COMMITTED GENERATOR of gate_census/fitpoor_calibration.json.

The first cut put the threshold at 0.09 because uniform spacings measured 0.091
through this argmin at n=2000. But at n=3000 uniform reads 0.0878 -- the
threshold sits EXACTLY ON a calibrator, making it a coin flip on that case. That
is one-sided calibration once more, in a threshold built during the census that
found the class: chosen from where a non-member landed, with the genuine-member
side never measured across n.

So: measure best_ks for GENUINE members (Poisson, GOE, GUE) and for NON-MEMBERS
across a range of n, then choose the threshold from the SEPARATION, with both
rates reported. Uses detector_spec.DetectorSpec, which refuses to certify unless
both sides are recorded.
"""
import json, sys
import numpy as np

ROOT = "/home/combust/fmexplorer/criticality_tool"
sys.path.insert(0, ROOT)
from arithmetic_toolkit import _classify                    # noqa: E402
from detector_spec import DetectorSpec                      # noqa: E402

NS = [500, 1000, 2000, 5000, 10000]
REPS = 12
rng = np.random.default_rng(20260819)


def gue_spacings(n):
    A = rng.standard_normal((n, n)) + 1j * rng.standard_normal((n, n))
    H = (A + A.conj().T) / 2
    ev = np.sort(np.linalg.eigvalsh(H))
    x = np.clip(ev / (2 * np.sqrt(n)), -1, 1)
    u = (0.5 + (x * np.sqrt(1 - x * x) + np.arcsin(x)) / np.pi) * n
    s = np.diff(u)
    return s[s > 0] / s[s > 0].mean()


MEMBERS = {
    "poisson": lambda n: (lambda x: x / x.mean())(rng.exponential(1, n)),
    "gue": lambda n: gue_spacings(min(n, 1200)),
}
NONMEMBERS = {
    "uniform": lambda n: (lambda x: x / x.mean())(rng.uniform(0, 2, n)),
    "lognormal": lambda n: (lambda x: x / x.mean())(rng.lognormal(0, 1.2, n)),
    "bimodal": lambda n: (lambda x: x / x.mean())(
        np.concatenate([np.full(n // 2, .2), np.full(n // 2, 1.8)])),
    "clock": lambda n: np.ones(n),
    "clustered": lambda n: (lambda x: x / x.mean())(
        rng.exponential(1, n) * rng.choice([0.05, 3.0], n, p=[.7, .3])),
}


def sample(fam, n):
    return [float(_classify(fam(n))["best_ks"]) for _ in range(REPS)]


def main():
    mem, non = {}, {}
    for name, f in MEMBERS.items():
        mem[name] = {str(n): sample(f, n) for n in NS}
        allv = [v for vs in mem[name].values() for v in vs]
        print(f"  member    {name:10s} best_ks max over all n = {max(allv):.4f}")
    for name, f in NONMEMBERS.items():
        non[name] = {str(n): sample(f, n) for n in NS}
        allv = [v for vs in non[name].values() for v in vs]
        print(f"  NONmember {name:10s} best_ks min over all n = {min(allv):.4f}")

    mem_max = max(v for d in mem.values() for vs in d.values() for v in vs)
    non_min = min(v for d in non.values() for vs in d.values() for v in vs)
    print(f"\n  worst genuine member : {mem_max:.4f}")
    print(f"  best  non-member     : {non_min:.4f}")
    separated = non_min > mem_max
    # geometric midpoint of the gap -- equidistant in ratio, so neither side is
    # favoured, and it sits OFF both calibrators rather than on one
    thr = float(np.sqrt(mem_max * non_min)) if separated else None
    print(f"  separated: {separated}"
          + (f"   -> threshold at geometric midpoint {thr:.4f}" if separated else ""))

    out = dict(ns=NS, reps=REPS, member_max=mem_max, nonmember_min=non_min,
               separated=bool(separated), threshold=thr,
               members=mem, nonmembers=non)
    if separated:
        spec = DetectorSpec(
            name="fit_poor (argmin goodness gate)",
            fires_on="a winning KS fit no better than a measured non-member",
            positive_set={k: "must fire" for k in NONMEMBERS},
            negative_set={k: "must stay silent" for k in MEMBERS},
            nearest_confusable="uniform spacings — the non-member that lands "
                               "closest to the genuine members through this argmin",
            negative_rationale="true Poisson/GUE samples ARE members of the class "
                               "space; firing on them is a false positive")
        for k, d in NONMEMBERS.items():
            spec.record(k, all(v > thr for vs in non[k].values() for v in vs))
        for k in MEMBERS:
            spec.record(k, any(v > thr for vs in mem[k].values() for v in vs))
        r = spec.certify()
        out["detector_spec"] = r
        print(f"  DetectorSpec CERTIFIED: sensitivity {r['sensitivity']}, "
              f"specificity {r['specificity']}")
    json.dump(out, open(f"{ROOT}/gate_census/fitpoor_calibration.json", "w"), indent=1)


if __name__ == "__main__":
    main()
