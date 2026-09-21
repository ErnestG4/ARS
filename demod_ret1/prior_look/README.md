# prior_look/ — a chat-sandbox toy, NOT a sealed generator

`demod_labels_and_ret1_toy.py` (Will, 2026-09-21) and its output were a first look at two inferences in
`DEMODULATION_FINDINGS.md` before any pre-registration existed. It is filed here so the pre-registration
in `../PREREG.md` can disclose it as a prior look. It was hand-tuned (event regularity moved from k_e=6 to 8
to bring the slope into ret-1's range), no single variant matches every ret-1 statistic (R₂(0.1) 4.1 vs
~2.5; 10/20 ms clusters 1.09/1.54 vs 1.24/1.78), and its ~7 Hz ret-1 rate was an inference, not a
measurement (the loader gives median 11.6 Hz, range 4–41 Hz, over the ≥6k-ISI cells). What it shows is
narrower than the toy's docstring claims and is stated in PREREG.md.
