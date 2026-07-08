"""Consolidate Session K: three co-primaries + approach-to-Poisson binning."""
import json, os, math
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
L = lambda f: json.load(open(os.path.join(HERE, f)))

cp2 = L("coprimary2_measured.json")
zoo = L("calibrator_zoo_measured.json")
maass = L("maass_analysis_measured.json")

# approach-to-Poisson: ratio stat in r-bins (odd/even) on the clean 0-599 block
d = np.genfromtxt(os.path.join(HERE, "maass_level1_partial.csv"), delimiter=",", names=True)
r, sym = d["r"], d["symmetry"].astype(int)
def rstat(x):
    x = np.sort(x); s = np.diff(x)
    return np.minimum(s[1:], s[:-1]) / np.maximum(s[1:], s[:-1])
edges = [9, 40, 60, 80, 99]
approach = {}
for s, name in [(0, "odd"), (1, "even")]:
    rs = r[sym == s]; rows = []
    for lo, hi in zip(edges[:-1], edges[1:]):
        m = (rs >= lo) & (rs < hi); rr = rstat(rs[m])
        rows.append({"r_lo": lo, "r_hi": hi, "n": int(m.sum()),
                     "mean_rtilde": float(rr.mean()),
                     "se": float(rr.std(ddof=1) / math.sqrt(len(rr)))})
    approach[name] = rows

summary = {
    "co_primary_2_bridge": {
        "2a_operator": {"lambda_1": cp2["2a_operator_sanity"]["lambda_1"],
                        "lyapunov": cp2["2a_operator_sanity"]["lyapunov_operator"],
                        "levy_const": cp2["2a_operator_sanity"]["levy_const_operator"],
                        "PASS": cp2["2a_operator_sanity"]["PASS_2a"]},
        "2b_theta_ladder": {"max_L_a_err": cp2["2b_bridge"]["max_L_a_err"],
                            "PASS": cp2["2b_bridge"]["PASS_2b"],
                            "ladder_match": {k: v["diff"] for k, v in cp2["2b_bridge"]["ladder_match"].items()}},
        "VERDICT": "banked Session-J theta_inf ladder reproduced from independent spectral route; no conflict"},
    "instrument": {"INSTRUMENT_VALID": zoo["INSTRUMENT_VALID"],
                   "zeta_nns": zoo["S5_zeta"]["nns_verdict"],
                   "S3_edge": zoo["S3_edge_GKW"]["verdict"]},
    "co_primary_1_maass": {
        "completeness": maass["real"]["completeness"],
        "pipeline_valid": maass["synthetic"]["PIPELINE_VALID"],
        "sectors": {k: {"n": v["n_levels"],
                        "mean_rtilde": v["ratio_stat"]["mean_rtilde"],
                        "z_vs_Poisson": v["ratio_stat"]["z_vs"]["Poisson"],
                        "z_vs_GOE": v["ratio_stat"]["z_vs"]["GOE"],
                        "nearest": v["ratio_stat"]["nearest_class"]}
                    for k, v in maass["real"]["sectors"].items()},
        "VERDICT": "arithmetic-Poisson per sector; GOE excluded 7-8 sigma; odd=clean Poisson, "
                   "even=Poisson+mild finite-r residual repulsion"},
    "approach_to_poisson": approach,
    "predictions_resolved": {
        "S1_Maass_arithmetic_Poisson_GOE_excluded": "CONFIRMED (both sectors, desymmetrized)",
        "S5_zeta_GUE": "CONFIRMED (NNS)",
        "S3_edge_REFUSE": "CONFIRMED",
        "S3_theta_inf_bridge": "CONFIRMED (machine precision, 2a+2b)",
        "C_nonarith_Hecke_n5_GOE": "NOT RUN - DATA_ACQUISITION_BLOCKED (Hecke n=5 eigenvalues not on LMFDB); instrument's GOE-detection validated via synthetic + sampled GOE"},
}
json.dump(summary, open(os.path.join(HERE, "SESSION_K_RESULTS.json"), "w"), indent=2, default=str)
print(json.dumps(summary, indent=2, default=str))
