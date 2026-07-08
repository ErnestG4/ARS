"""Session K calibrator zoo + S5 zeta GUE control + S3 edge refusal.

Empirical-reference classifier (same estimator+unfolding on all inputs), built
from sampled GUE/GOE/GSE/Poisson. Instrument must: classify each sampled
ensemble to itself, return GUE on Riemann zeta zeros (arithmetic input), and
REFUSE the GKW deterministic decaying spectrum ('not an ensemble')."""
import json, math, os
import numpy as np
import nns_stats as st

RNG = np.random.default_rng(20260708)
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LS = np.linspace(1.0, 15.0, 15)
N = 1500                 # matrix dim; bulk ~1050 levels, matches zeta n=2000 scale

def gen_gue(n=N):
    A = (RNG.standard_normal((n, n)) + 1j * RNG.standard_normal((n, n))) / math.sqrt(2)
    return np.linalg.eigvalsh((A + A.conj().T) / 2)

def gen_goe(n=N):
    A = RNG.standard_normal((n, n))
    return np.linalg.eigvalsh((A + A.T) / 2)

def gen_gse(n=N // 2):
    # 2n x 2n Hermitian self-dual (quaternion) -> Kramers-degenerate; keep one per pair
    A = (RNG.standard_normal((n, n)) + 1j * RNG.standard_normal((n, n)))
    A = (A + A.conj().T) / 2
    B = (RNG.standard_normal((n, n)) + 1j * RNG.standard_normal((n, n)))
    B = (B - B.T) / 2
    H = np.block([[A, B], [-B.conj(), A.conj()]])
    ev = np.linalg.eigvalsh((H + H.conj().T) / 2)
    return ev[::2]                                   # drop Kramers degeneracy

def gen_poisson(m=1050):
    return np.sort(RNG.uniform(0, m, size=m))

REF_GENS = {
    "GUE": lambda: st.unfold_poly(gen_gue()),
    "GOE": lambda: st.unfold_poly(gen_goe()),
    "GSE": lambda: st.unfold_poly(gen_gse()),
    "Poisson": lambda: gen_poisson(),
}

def gkw_spectrum():
    p = os.path.join(os.path.dirname(os.path.abspath(__file__)), "coprimary2_measured.json")
    d = json.load(open(p))
    reprs = d["2a_operator_sanity"]["top6_eigs"]
    return np.array([complex(s.strip("()")).real for s in reprs])

def run():
    print("building empirical reference curves ...")
    refs = st.build_empirical_refs(REF_GENS, LS, n_real=6)
    out = {"refs_sigma2": {k: v["sigma2"].tolist() for k, v in refs.items()},
           "Ls": LS.tolist()}

    # validate: each ensemble classifies to itself (fresh draws), both markers
    for name, gen in REF_GENS.items():
        u = gen()
        r_s2 = st.classify_empirical(u, refs, LS)     # long-range Sigma^2/Delta_3
        r_ns = st.classify_nns(u)                     # short-range NNS
        out[f"selfclass_{name}"] = {"sigma2_verdict": r_s2["verdict"],
                                    "nns_verdict": r_ns["verdict"], "nns_ks": r_ns["ks"]}
        print(f"  self {name:8s} -> Sigma2={r_s2['verdict']:8s} NNS={r_ns['verdict']}")

    # S5 zeta zeros: arithmetic -> GUE (NNS is the robust marker; Sigma^2 saturates)
    zeros = np.load(os.path.join(ROOT, "zeros_2000.npy"))
    t = zeros
    Nsm = (t / (2 * math.pi)) * np.log(t / (2 * math.pi)) - t / (2 * math.pi) + 7.0 / 8.0
    u_zeta = Nsm - Nsm[0]
    r_s2 = st.classify_empirical(u_zeta, refs, LS)
    r_ns = st.classify_nns(u_zeta)
    out["S5_zeta"] = {"nns_verdict": r_ns["verdict"], "nns_ks": r_ns["ks"],
                      "sigma2_verdict_saturated": r_s2["verdict"],
                      "sigma2_curve": r_s2["sigma2"],
                      "note": "NNS=GUE is the control pass; Sigma^2 flattening below GUE is the "
                              "known Berry arithmetic saturation at finite height (a real positive)."}
    print(f"  S5_zeta        -> NNS={r_ns['verdict']} (ks_GUE={r_ns['ks']['GUE']:.3f}); "
          f"Sigma2 saturates -> reads {r_s2['verdict']} (expected Berry saturation)")

    # S3 edge: GKW decaying deterministic spectrum -> REFUSE
    res = st.classify_empirical(gkw_spectrum(), refs, LS)
    out["S3_edge_GKW"] = {"verdict": res["verdict"], "reason": res.get("reason")}
    print(f"  S3_edge_GKW    -> {res['verdict']} ({res.get('reason')})")

    out["INSTRUMENT_VALID"] = bool(
        out["selfclass_GUE"]["nns_verdict"] == "GUE" and
        out["selfclass_GOE"]["nns_verdict"] == "GOE" and
        out["selfclass_GSE"]["nns_verdict"] == "GSE" and
        out["selfclass_Poisson"]["nns_verdict"] == "Poisson" and
        out["selfclass_GUE"]["sigma2_verdict"] == "GUE" and
        out["selfclass_Poisson"]["sigma2_verdict"] == "Poisson" and
        out["S5_zeta"]["nns_verdict"] == "GUE" and
        out["S3_edge_GKW"]["verdict"] == "REFUSE")
    outp = os.path.join(os.path.dirname(os.path.abspath(__file__)), "calibrator_zoo_measured.json")
    json.dump(out, open(outp, "w"), indent=2)
    print("\nINSTRUMENT_VALID:", out["INSTRUMENT_VALID"], "| wrote", outp)
    return out

if __name__ == "__main__":
    run()
