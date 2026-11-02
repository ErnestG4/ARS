# SPDX-License-Identifier: AGPL-3.0-or-later
"""FN1 stage-2 design input (POST HOC on stage-1, seen data; TOOLKIT §9.I: read-only inputs, scratch-only output):
the sealed §3a segment estimator, raw and per-field linear-detrended, on the stage-1 rows [0, n10) at
beta 0.40, 0.45, 0.55. Checks: the 0.55 raw values must reproduce the sealed read exactly, and 0.45 must reproduce
lead/SEGNOISE_B045.json exactly. Used only to state stage-2 power for the secondaries (Will: power from their own
slopes) before sealing.   python fn1_segnoise_betas.py PINS SEALED_READ1 PRIOR_B045 OUT_REL
"""
import math, os, sys, time
_H = os.path.dirname(os.path.abspath(__file__))
sys.path[:0] = [os.path.join(_H, ".."), os.path.join(_H, "..", "..")]   # fn1_read (fn1/), safeio (specarith/ locally, fn1/ on spot)
import safeio
safeio.enforce()
import numpy as np
import fn1_read as S

def seg(half, n, K, beta):
    ns = n // S.M_SEG
    Ks = int(round((2 * ns) ** beta))
    r = []
    for i in range(S.M_SEG):
        s = half[i * ns:(i + 1) * ns]
        t = np.concatenate([s, np.mod(1.0 - s, 1.0)]); t.sort()
        r.append(float(S.Q.var_stream(t, Ks) / (2 * ns / Ks)))
    r = np.array(r); x = np.arange(len(r))
    fit = np.polyfit(x, r, 1); det = r - np.polyval(fit, x)
    sc = math.sqrt(Ks / K)
    return dict(K_seg=Ks, R_seg=r.tolist(), relSD_full=float(r.std(ddof=1) / r.mean() * sc),
                relSD_full_detrended=float(det.std(ddof=2) / r.mean() * sc),
                drift_total_rel=float(fit[0] * (S.M_SEG - 1) / r.mean()))

pins_json, sealed, prior, out_rel = sys.argv[1:5]
t0 = time.time()
pins = safeio.read_json(pins_json); arch = pins["archives"]
n = S.Q.n_below(arch["zs2"]["dir"], S.X10); N = 2 * n
BET = (0.55, 0.45, 0.40)
K = {b: int(round(N ** b)) for b in BET}
per = {b: {} for b in BET}
for f in S.FIELDS:
    _, half = S.load(arch[f]["dir"], f, n, arch[f]["manifest_sha256"], keep_half=True)
    for b in BET:
        per[b][f] = seg(half, n, K[b], b)
    del half, _
res = {"label": "FN1 stage-2 design input: stage-1 segment noise at beta 0.40/0.45/0.55 (seen data)", "n": n}
for b in BET:
    pooled = math.sqrt(float(np.mean([per[b][f]["relSD_full"] ** 2 for f in S.FIELDS])))
    pooled_d = math.sqrt(float(np.mean([per[b][f]["relSD_full_detrended"] ** 2 for f in S.FIELDS])))
    model = math.sqrt(2 / (S.C_SE * K[b]))
    drift = [per[b][f]["drift_total_rel"] for f in S.FIELDS]
    res[str(b)] = dict(K=K[b], per_field=per[b], pooled_relSD_full=pooled, noise_ratio=pooled / model,
                       pooled_relSD_full_detrended=pooled_d, noise_ratio_detrended=pooled_d / model,
                       drift_total_rel_mean=float(np.mean(drift)), drift_total_rel_acrossfield_SD=float(np.std(drift, ddof=1)))
sr = safeio.read_json(sealed)["read_time_noise"]; pr = safeio.read_json(prior)
res["check_055_reproduces_sealed"] = bool(res["0.55"]["pooled_relSD_full"] == sr["pooled_relSD_full"])
res["check_045_reproduces_prior"] = bool(res["0.45"]["pooled_relSD_full"] == pr["0.45"]["pooled_relSD_full"]
                                         and res["0.45"]["pooled_relSD_full_detrended"] == pr["0.45"]["pooled_relSD_full_detrended"])
p = safeio.write_json(safeio.scratch(out_rel), res)
print("done", p, round(time.time() - t0, 1))
