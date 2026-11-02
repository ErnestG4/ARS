# SPDX-License-Identifier: AGPL-3.0-or-later
"""FN1 POST-HOC, descriptive (Will 2026-11-02, optional): the sealed §3a segment-noise estimator applied at beta 0.45.

Imports the sealed fn1_read.py unchanged (load, var_stream, constants). Same 8 contiguous prime-order segments per
field; K_seg = round((2*(n//8))^beta); relSD scaled to full N by sqrt(K_seg/K); pooled over the nine fields;
ratio = pooled / sqrt(2/(c K)). Self-check: at beta 0.55 it must reproduce the sealed read's pooled relSD and ratio
exactly (READ1.json). Also reports a linear-detrended relSD per field (descriptive only; not a sealed estimator).
No verdict; nothing here relabels the sealed beta 0.45 FAIL.
"""
import json, math, sys, time
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
    det = r - np.polyval(np.polyfit(x, r, 1), x)
    sc = math.sqrt(Ks / K)
    return dict(K_seg=Ks, R_seg=r.tolist(), relSD_full=float(r.std(ddof=1) / r.mean() * sc),
                relSD_full_detrended=float(det.std(ddof=2) / r.mean() * sc))

pins_json, sealed_read, out = sys.argv[1:4]
t0 = time.time()
pins = json.load(open(pins_json)); arch = pins["archives"]
n = S.Q.n_below(arch["zs2"]["dir"], S.X10); N = 2 * n
K = {b: int(round(N ** b)) for b in (0.55, 0.45)}
per = {b: {} for b in K}
for f in S.FIELDS:
    _, half = S.load(arch[f]["dir"], f, n, arch[f]["manifest_sha256"], keep_half=True)
    for b in K:
        per[b][f] = seg(half, n, K[b], b)
    del half, _
res = {"label": "FN1 POST-HOC descriptive segment noise (sealed estimator at beta 0.45; 0.55 = reproduction check)", "n": n}
sealed = json.load(open(sealed_read))["read_time_noise"]
for b in K:
    pooled = math.sqrt(float(np.mean([per[b][f]["relSD_full"] ** 2 for f in S.FIELDS])))
    pooled_d = math.sqrt(float(np.mean([per[b][f]["relSD_full_detrended"] ** 2 for f in S.FIELDS])))
    model = math.sqrt(2 / (S.C_SE * K[b]))
    res[str(b)] = dict(K=K[b], per_field=per[b], pooled_relSD_full=pooled, noise_ratio_to_sealed_model=pooled / model,
                       pooled_relSD_full_detrended=pooled_d, noise_ratio_detrended=pooled_d / model)
r55 = res["0.55"]
res["reproduces_sealed_055"] = bool(r55["pooled_relSD_full"] == sealed["pooled_relSD_full"]
                                    and r55["noise_ratio_to_sealed_model"] == sealed["noise_ratio_to_sealed_model"])
json.dump(res, open(out, "w"), indent=1, sort_keys=True)
open(out + ".timing", "w").write("wall_s %.1f\n" % (time.time() - t0))
print("done")
