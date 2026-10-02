"""Known answers for the phase-1 runner (pdyn_phase1.py) on its FAKE bank (built from the sealed calibrators; the
real bank cache/armb is never read). Runs the runner three times into --out: (1) full fake run, (2) the identical
command again (resume: every part skipped, words identical), (3) --verdict-only --flip-threshold (red path).

Checks (exit 1 on any failure; the FAILURES line lists them):
 (i)   arm-level P2 word on W2: FAKE_C1 (beta=1 smooth GP) HOLDS; FAKE_B2 (beta=2) FAILS; FAKE_PO (Poisson walk)
       FAILS -- at the fake n (n_k >= 1000 curvature samples per matrix, reported); the witnesses are separated.
 (ii)  FAKE_SHORT (5 checkpoints: n_k < 1000) reads NOT RESOLVABLE on W2.
 (iii) the planted avoided crossing (type O, layer 0, pair 0, t0 = 1500, 2c = 0.1) appears in m3 events of every
       full-length fake arm with |t_min - 1500| <= 5 and |g_min - 0.1| <= 0.01.
 (iv)  C5: every (layer, type) of every arm bit-identical under joint and independent sign flips.
 (v)   P5 and P6 words carry a PROVISIONAL tag; every P2 verdict (arm and per matrix) carries the PROVISIONAL
       (curvature) tag; W3 is DESCRIPTIVE.
 (vi)  resumability: the second run computes 0 parts, resumes all, and all P2/P5 words are identical.
 (vii) the x_step match: every C1/C2 calibrator's measured vrms within 5% of the real window's.
--redpath: run (3) inverts the curvature acceptance region; (i) must then FAIL (FAKE_C1 reads FAILS). Exit 0 iff it does.
Runtime per run is printed (the real-run estimate in the report scales the per-unit time at the real shape).
"""
import sys, time, json, subprocess, argparse
from pathlib import Path
import numpy as np

HERE = Path(__file__).resolve().parent
ap = argparse.ArgumentParser()
ap.add_argument("--redpath", action="store_true")
ap.add_argument("--out", default=None, help="scratch dir for the fake bank + results (default: <scratchpad>/pdyn1/verify)")
ap.add_argument("--workers", type=int, default=6)
ap.add_argument("--fake-n", type=int, default=256)
ap.add_argument("--keep", action="store_true", help="reuse an existing fake run in --out (skip run 1)")
A = ap.parse_args()
RED = A.redpath; fails = []; T0 = time.time()
out = Path(A.out) if A.out else Path("/tmp/claude-1000/-home-combust-fmexplorer-criticality-tool--claude-worktrees-llm-spectra/cb801fdc-4afc-4579-bfa1-385bada159d1/scratchpad/pdyn1/verify")
out.mkdir(parents=True, exist_ok=True)
BASE = [sys.executable, str(HERE / "pdyn_phase1.py"), "--fake", "--fake-n", str(A.fake_n), "--out", str(out), "--workers", str(A.workers)]


def run(extra, label):
    t = time.time()
    r = subprocess.run(BASE + extra, capture_output=True, text=True)
    lines = [l for l in r.stdout.splitlines() if "Warning" not in l]
    print(f"--- run {label}: exit {r.returncode}, {time.time() - t:.0f}s; last lines:")
    for l in lines[-6:]: print("   ", l)
    if r.returncode != 0:
        print(r.stderr[-3000:]); fails.append(f"run {label} exit {r.returncode}")
    return json.load(open(out / "summary.json")), time.time() - t


def words(S):
    return {arm: dict(P2={w: S["arms"][arm]["P2"][w]["word"] for w in S["arms"][arm]["P2"]}, P5={w: S["arms"][arm]["P5"][w]["word"] for w in S["arms"][arm]["P5"]})
            for arm in S["arms"] if S["arms"][arm].get("status") == "OK"}


# ---------------------------------------------------------------- run 1 (full) and run 2 (resume)
if A.keep and (out / "summary.json").exists():
    S1 = json.load(open(out / "summary.json")); t1 = float("nan"); print("--- run 1 reused from", out)
else:
    S1, t1 = run([], "1 (full fake)")
S2, t2 = run([], "2 (resume)")
print(f"(vi) resume: computed_parts {S2['computed_parts']} skipped_parts {S2['skipped_parts']} (run 1: computed {S1['computed_parts']})")
if S2["computed_parts"] != 0 or S2["skipped_parts"] != S1["computed_parts"] + S1["skipped_parts"]: fails.append(f"(vi) resume recomputed {S2['computed_parts']} parts")
if words(S1) != words(S2): fails.append("(vi) words differ between run 1 and the resumed run")

# ---------------------------------------------------------------- (i) / (ii)
W = words(S1)
exp = {"FAKE_C1": "HOLDS", "FAKE_B2": "FAILS", "FAKE_PO": "FAILS", "FAKE_SHORT": "NOT RESOLVABLE"}
for arm, e in exp.items():
    got = W.get(arm, {}).get("P2", {}).get("W2", "ABSENT")
    v = S1["arms"][arm]["P2"]["W2"]
    extra = f" components {{{', '.join(f'{c}:{d['word']}' for c, d in v.get('components', {}).items())}}}" if v.get("components") else f" reason: {v.get('reason')}"
    print(f"({'ii' if arm == 'FAKE_SHORT' else 'i'}) {arm}: P2 W2 = {got} (expected {e}); matrices {v.get('n_matrices')} holds {v.get('n_holds')} fails {v.get('n_fails')} NR {v.get('n_not_resolvable')}{extra}")
    if got != e: fails.append(f"({'ii' if arm == 'FAKE_SHORT' else 'i'}) {arm} P2 W2 {got} != {e}")
m2 = json.load(open(out / "FAKE_C1" / "m2.json"))
nk = [v["n_k"] for v in m2["verdict_p2"]["W2"].values()]; nks = [v["n_k"] for v in json.load(open(out / "FAKE_SHORT" / "m2.json"))["verdict_p2"]["W2"].values()]
print(f"    n_k per matrix: FAKE_C1 W2 {sorted(set(nk))}; FAKE_SHORT W2 {sorted(set(nks))} (threshold 1000)")
seps = [(v["components"]["curvature"]["z_c1_b2"], v["components"]["curvature"]["z_c1_po"]) for v in m2["verdict_p2"]["W2"].values() if v.get("components")]
print(f"    witness separation (seed z, C1:beta2 / C1:Poisson) over FAKE_C1 matrices: min {min(s[0] for s in seps):.1f} / {min(s[1] for s in seps):.1f}")
Sm = [(v["components"]["curvature"]["S"], np.mean(v["components"]["curvature"]["S_c1"]), np.mean(v["components"]["curvature"]["S_b2"]), np.mean(v["components"]["curvature"]["S_po"])) for v in m2["verdict_p2"]["W2"].values() if v.get("components")]
print(f"    median|k| W2 (real / C1 / beta2 / Poisson), matrix means: {np.round(np.mean(Sm, axis=0), 3)}")

# ---------------------------------------------------------------- (iii) planted crossing
for arm in ("FAKE_C1", "FAKE_B2", "FAKE_PO"):
    m3 = json.load(open(out / arm / "m3.json"))
    ev = [e for e in m3["events"] if e["type"] == "O" and e["layer"] == 0 and e["pair"] == 0]
    print(f"(iii) {arm}: planted-crossing events on (L0, O, pair 0): {[(round(e['t_min'], 1), round(e['g_min'], 4), e['ambiguous']) for e in ev]} (truth t0 1500, 2c 0.1)")
    if len(ev) != 1 or abs(ev[0]["t_min"] - 1500) > 5 or abs(ev[0]["g_min"] - 0.1) > 0.01: fails.append(f"(iii) {arm} planted crossing {ev}")

# ---------------------------------------------------------------- (iv) C5
for arm in W:
    c5 = S1["arms"][arm]["controls"]["C5_all_bit_identical"]
    print(f"(iv) {arm}: C5 all bit-identical = {c5}")
    if c5 is not True: fails.append(f"(iv) {arm} C5 {c5}")

# ---------------------------------------------------------------- (v) PROVISIONAL tags
for arm in W:
    S = S1["arms"][arm]
    for w in S["P5"]:
        if not any("PROVISIONAL" in t for t in S["P5"][w]["tags"]): fails.append(f"(v) {arm} P5 {w} lacks PROVISIONAL")
        if not any("PROVISIONAL" in t for t in S["P6"][w]["tags"]): fails.append(f"(v) {arm} P6 {w} lacks PROVISIONAL")
        if not any("PROVISIONAL" in t for t in S["P2"][w]["tags"]): fails.append(f"(v) {arm} P2 {w} lacks PROVISIONAL (curvature)")
    m2a = json.load(open(out / arm / "m2.json"))
    for w, d in m2a["verdict_p2"].items():
        for key, v in d.items():
            if not any("PROVISIONAL" in t for t in v["tags"]): fails.append(f"(v) {arm} {w} {key} per-matrix P2 lacks PROVISIONAL")
            if v.get("components") and not v["components"]["curvature"].get("PROVISIONAL"): fails.append(f"(v) {arm} {w} {key} curvature not PROVISIONAL")
    if S.get("W3") != "DESCRIPTIVE" or not str(S["P2"].get("W3", {}).get("word", "DESCRIPTIVE")).startswith("DESCRIPTIVE"): fails.append(f"(v) {arm} W3 not DESCRIPTIVE: {S.get('W3')} {S['P2'].get('W3', {}).get('word')}")
    print(f"(v) {arm}: P5 tags {S['P5']['W2']['tags']}; P6 tags {S['P6']['W2']['tags']}; P2 tags {S['P2']['W2']['tags']}; W3 {S.get('W3')}; "
          f"P5 W2 {S['P5']['W2']['word']} (n={S['P5']['W2']['n_events']}), P6 W2 {S['P6']['W2']['word']} (n={S['P6']['W2']['n_events']})")

# ---------------------------------------------------------------- (vii) matching
for arm in ("FAKE_C1", "FAKE_B2", "FAKE_PO"):
    ctl = json.load(open(out / arm / "controls.json"))
    ratios = [s["match"]["vrms_measured"] / s["match"]["v_target"] for k in ctl["per_matrix"] for w in ctl["per_matrix"][k] for fam in ("c1", "b2", "po")
              for s in ctl["per_matrix"][k][w].get("families", {}).get(fam, []) if s.get("status") == "OK"]
    print(f"(vii) {arm}: calibrator vrms / real vrms over {len(ratios)} draws: min {min(ratios):.3f} max {max(ratios):.3f}; C3 collapsed frac {ctl['C3_collapsed_frac']}; "
          f"C4 spectrum fp32 ratio median {ctl['C4_spectrum_ratio_median']:.1e}; C4 matrix fp32 ratio median {ctl['C4_matrix_fp32_ratio_median']:.1e}")
    if max(abs(r - 1) for r in ratios) > 0.05: fails.append(f"(vii) {arm} vrms mismatch up to {max(abs(r - 1) for r in ratios):.3f}")

# ---------------------------------------------------------------- red path
if RED:
    S3, t3 = run(["--verdict-only", "--flip-threshold"], "3 (RED: --flip-threshold)")
    got = S3["arms"]["FAKE_C1"]["P2"]["W2"]["word"]
    print(f"(RED) FAKE_C1 P2 W2 with the curvature acceptance inverted = {got} (check (i) requires HOLDS); flip recorded: {S3['flip_threshold']}")
    if got != "HOLDS": fails.append("(i) FAKE_C1 P2 W2 FAILS under the flipped threshold")
    # restore the un-flipped verdicts in the output dir
    run(["--verdict-only"], "4 (restore)")

print(f"runtime {time.time() - T0:.0f}s (run 1 {t1:.0f}s, resume {t2:.0f}s)")
print(("REDPATH failures: " if RED else "FAILURES: ") + str(fails or "none"))
red_fired = any(f.startswith("(i) FAKE_C1") for f in fails)
sys.exit((0 if red_fired else 1) if RED else (1 if fails else 0))
