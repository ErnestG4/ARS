"""Route (a) Phase 2 bins check (fortieth/forty-first/forty-third rounds): DESCRIPTIVE pipeline/SE check on seen data only,
after the rule and calibration were committed (397fe1f3) and before the seal. It does not enter the verdict.

For each Phase 2 Platt bin P1–P6 (already read and sealed in Phase 2; md5 pins from ph2/make_seal_json.PLATT_MD5):
  pipeline  decode through the read's own path (route_a_read.spacings_from_platt) and compare the float64 spacings
            bit for bit with Phase 2's cached unfolded spacings (sha256 of the array, taken on spot from
            ph2/results/run/P*_spacings.npz, 2026-10-07);
  fit       route_a_read.fit_file with the F3 template nearest in ℓ (the prediction exists only at the F3 heights, so
            μ̂ here is NOT a measurement of μ: the template's height differs from the bin's); bootstrap SE at the
            declared block lengths against the template file's CUE spread SD scaled to the bin's size by √(n_F3/n_bin);
            the GoF χ² beside the template's T_f; the per-bin residuals (O − E)/√E.
No F3 file is opened.

  python route_a_ph2bins.py BIN PLATT_PATH OUT.json
"""
import hashlib
import json
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import route_a_read as RR  # noqa: E402

PLATT = {"P1": ("zeros_2546000.dat", "5642999b13dc52270064a055b1b6b15f",
                "8ff4946cad2f8f1fecdb682e768ee6868ba5427cefb027704c143a82ad6614fc", 2_546_000, 4_646_000),
         "P2": ("zeros_19346000.dat", "24dedbc917f3a006690026dd7cda930b",
                "0e8cbea7e97d2e34365d9a8531b2f8d5130f283c11fd14d3b8d07fa62da3571d", 19_346_000, 21_446_000),
         "P3": ("zeros_151646000.dat", "242ca86d1691d1a93623b2f8ce2cbf33",
                "4258f2c03033d82e335235740c6535e708ca72d4c271bdf369d1f117a41b7b2a", 151_646_000, 153_746_000),
         "P4": ("zeros_1119746000.dat", "8d01c4c244daf4751f3c251de53008af",
                "2158ee19b6bb5c1e0766b060b1b8a8325c209c908da076cd2a0c38a5680c365d", 1_119_746_000, 1_121_846_000),
         "P5": ("zeros_8284946000.dat", "8adc69731784c1958ca60d67686e98b4",
                "7cf82040edb7c563aee94e3bca9b324d68cf4de94d543b6200f77703496a3dcc", 8_284_946_000, 8_287_046_000),
         "P6": ("zeros_30404246000.dat", "95f2c89b2b4572e5529cd25a79e9def8",
                "d8313498439463734c73aa38d4806c6f8fda3774a2f03c50b037a2cbd989fa08", 30_404_246_000, 30_406_346_000)}


def md5(path):
    h = hashlib.md5()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main(b, path, out):
    name, want_md5, want_sha, t0, t1 = PLATT[b]
    if os.path.basename(path) != name:
        raise SystemExit(f"REFUSED: {path} is not {b}'s file {name}")
    got = md5(path)
    if got != want_md5:
        raise SystemExit(f"REFUSED: {path} md5 {got} != pinned {want_md5}")
    s = np.ascontiguousarray(RR.spacings_from_platt(path), dtype=np.float64)
    sha = hashlib.sha256(s.tobytes()).hexdigest()
    pred = json.load(open(RR.PRED))
    cal = RR.calib()
    _, nf = RR.weights()
    ell = math.log(0.5 * (t0 + t1) / (2 * math.pi))
    tf = min(RR.F3, key=lambda f: abs(pred["files"][f]["ell_mean"] - ell))
    fit = RR.MuFit.for_file(tf, pred)
    rng = np.random.default_rng([20261014, int(b[1])])
    r = RR.fit_file(fit, s, rng, RR.BLOCK_LENS)
    z, edges = fit.gof_detail(s, r["mu"])
    c = cal["files"][tf]
    sd_scaled = c["sd"] * math.sqrt(nf[tf] / len(s))
    res = dict(bin=b, file=name, md5=got, n_spacings=int(len(s)), mean_spacing=float(s.mean()), sha256_spacings=sha,
               pipeline_bit_exact=bool(sha == want_sha), ell_bin=ell, template=tf,
               ell_template=pred["files"][tf]["ell_mean"], fit=r, mu_minus_template_bias=r["mu"] - c["bias"],
               cue_sd_template=c["sd"], cue_sd_scaled=sd_scaled,
               se_over_scaled_sd={k: v / sd_scaled for k, v in r["se"].items()},
               chi2_threshold_template=c["T"], gof_residuals=z.tolist(), gof_edges=edges.tolist())
    json.dump(res, open(out, "w"), indent=1)
    print(f"{b}: n {len(s)}  bit-exact vs Phase 2 {res['pipeline_bit_exact']}  template {tf} (ℓ {ell:.3f} vs "
          f"{res['ell_template']:.3f})  μ̂ {r['mu']:+.4f}  SE " + " ".join(f"{k}:{v:.4f}" for k, v in r["se"].items())
          + f"  scaled CUE SD {sd_scaled:.4f}  χ² {r['chi2']:.1f} (T {c['T']:.1f})  max|z| {np.max(np.abs(z)):.2f}",
          flush=True)
    return 0 if res["pipeline_bit_exact"] else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1], sys.argv[2], sys.argv[3]))
