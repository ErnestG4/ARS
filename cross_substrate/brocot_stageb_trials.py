"""STAGE B TRIALS: a blinded, runnable listening session.

Builds the trial bank the sealed protocol specifies, blinded, plus the response
sheet a listener fills in. Produces NO result -- it is apparatus.

BLINDING, AND WHY IT MATTERS MORE THAN USUAL HERE
---------------------------------------------------
The most likely listener is the person who knows the hypothesis, which is the
weakest position anyone can listen from: the masking model predicts silence on
six of seven merge ratios, and knowing that is enough to hear silence. Three
defences, all mechanical rather than dispositional:

  1. TRIAL FILES CARRY NO RATIO. Each is `trial_0001.wav` and nothing else. The
     mapping from trial to ratio, and the position of the odd interval, live in
     a key file the listener does not open.
  2. TRIALS ARE INTERLEAVED. Merge and beat trials are shuffled together, so a
     listener cannot tell which arm they are in -- which matters because the
     beat arm is the gate and knowing you are being gated changes effort.
  3. THE ODD POSITION IS UNIFORM AND SEEDED. Each trial's odd interval is 1, 2
     or 3 with equal probability, so a positional response bias shows up as
     chance rather than as signal.

What blinding cannot fix is n = 1. A single informed listener can establish that
a difference IS audible (B3, B1) far more cheaply than that one is NOT (B2), so
read a positive result from small n and treat a null as provisional until the
listener count is stated. That asymmetry is in the analysis cell, not left to
the reader.

USAGE
    python3 cross_substrate/brocot_stageb_trials.py          # build the bank
    -> stageb_trials/trial_0001.wav ...   listen, one at a time
    -> stageb_trials/responses.csv        write 1, 2 or 3 in the `odd` column
    then: python3 cross_substrate/brocot_stageb_score.py     # scores the seal
"""
import csv
import json
import os
import sys
from fractions import Fraction

import numpy as np
from scipy.io import wavfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)
from redpath import redpath                                       # noqa: E402

SEED = 20260826
TRIALS_PER_RATIO = 10
GAP_S = 0.4
SRC = os.path.join(HERE, "stageb_stimuli")
OUT = os.path.join(HERE, "stageb_trials")
PROTO = json.load(open(os.path.join(HERE, "brocot_stageb_protocol.json")))

os.makedirs(OUT, exist_ok=True)
by = {}
for m in PROTO["manifest"]:
    by.setdefault((m["arm"], m["ratio"]), {})[m["cents"]] = m["file"]

rng = np.random.default_rng(SEED)
plan = []
for (arm, ratio), files in sorted(by.items()):
    if 0.0 not in files or PROTO["detune_cents"] not in files:
        continue
    for _ in range(TRIALS_PER_RATIO):
        plan.append(dict(arm=arm, ratio=ratio,
                         exact=files[0.0], twin=files[PROTO["detune_cents"]]))
rng.shuffle(plan)

sr = PROTO["sr"]
gap = np.zeros(int(GAP_S * sr), np.int16)
key = []
for i, t in enumerate(plan, 1):
    odd = int(rng.integers(1, 4))
    _, ex = wavfile.read(os.path.join(SRC, t["exact"]))
    _, tw = wavfile.read(os.path.join(SRC, t["twin"]))
    seq = [tw if k == odd else ex for k in (1, 2, 3)]
    audio = np.concatenate([seq[0], gap, seq[1], gap, seq[2]])
    name = f"trial_{i:04d}.wav"
    wavfile.write(os.path.join(OUT, name), sr, audio)
    key.append(dict(trial=i, file=name, arm=t["arm"], ratio=t["ratio"], odd=odd))

with open(os.path.join(OUT, "responses.csv"), "w", newline="") as fh:
    w = csv.writer(fh)
    w.writerow(["trial", "file", "odd"])
    for k in key:
        w.writerow([k["trial"], k["file"], ""])

json.dump(dict(seed=SEED, trials_per_ratio=TRIALS_PER_RATIO, gap_s=GAP_S,
               n_trials=len(key), key=key),
          open(os.path.join(OUT, "KEY_do_not_open.json"), "w"), indent=1)

n_merge = sum(1 for k in key if k["arm"] == "merge")
n_beat = sum(1 for k in key if k["arm"] == "beat")
print(f"built {len(key)} blinded trials -> {os.path.relpath(OUT, ROOT)}/")
print(f"   {n_merge} merge (the prediction)   {n_beat} beat (the gate), interleaved")
print(f"   each trial: 3 intervals, one is the {PROTO['detune_cents']:.0f}-cent "
      f"twin, {GAP_S:.1f} s gaps")
print(f"\n   open listen.html in a browser (keys 1/2/3, r replay, s skip),")
print(f"   or play trial_NNNN.wav and write 1/2/3 in responses.csv `odd`")
print(f"   the key is in KEY_do_not_open.json — the name is the whole protocol")
print(f"\n   partial data is fine: the scorer reports per-arm n and refuses to "
      f"read\n   a merge null that has not cleared its gate.")

with redpath("blinded trials built", expect_min=100) as rp:
    rp.observed(len(key))
