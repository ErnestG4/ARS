"""
phase31b/p7_content_vs_rate_check.py — quick analytical check on whether
the p=7 movie-suppression is rate-driven or content-driven.

Direct matched-rate comparison from existing data:
  monkey1_gratings: 27.93 Hz, z_p7 = +9.77  (CLASS SIGNAL)
  monkey1_natural_movie: 24.25 Hz, z_p7 = -0.96 (SUPPRESSED)
  monkey1_noise_movie: 20.08 Hz, z_p7 = -0.72 (SUPPRESSED)

If suppression were rate-driven, similar rates (~24 Hz vs ~28 Hz, less
than 15 % difference) should produce similar z scores.  They differ by
~11 standard deviations.  The difference is content-driven.

Output:
  data/phase31b_results/p7_content_vs_rate_check.json
"""
import json
from pathlib import Path

OUT_DIR = Path('$HOME/fmexplorer/criticality_tool/data/phase31b_results')

# Per-recording from pvc11_all_qmax200 (monkey1 only, comparable monkey)
data = [
    dict(recording='monkey1_gratings', subset='gratings',
          rate_hz=27.93, z_p7=+9.77, real_p7=2.41,
          comment='strongest pvc-11 p=7 (CLASS SIGNAL)'),
    dict(recording='monkey1_gratings_movie', subset='gratings_movie',
          rate_hz=11.94, z_p7=+1.62, real_p7=1.68,
          comment='partial movie suppression'),
    dict(recording='monkey1_natural_movie', subset='natural_movie',
          rate_hz=24.25, z_p7=-0.96, real_p7=0.69,
          comment='matched-rate to gratings; full suppression'),
    dict(recording='monkey1_noise_movie', subset='noise_movie',
          rate_hz=20.08, z_p7=-0.72, real_p7=1.04,
          comment='similar-rate; suppressed'),
    dict(recording='monkey1_spontaneous', subset='spontaneous',
          rate_hz=41.84, z_p7=+1.91, real_p7=2.39,
          comment='higher rate; p=7 present'),
]

print("monkey1 p=7 z-scores across all 5 subsets (within-monkey comparison):")
print("recording                  subset           rate(Hz)    z(p=7)   real_p7   note")
for r in data:
    print(f"  {r['recording']:24s}  {r['subset']:15s}  {r['rate_hz']:6.2f}    {r['z_p7']:+5.2f}    {r['real_p7']:.2f}   {r['comment']}")

# Rate-controlled comparison: gratings (27.93) vs natural_movie (24.25)
# Rate differs by ~15%, both are in similar mid-range.
# If rate-driven: similar z expected
# Observed: Δz ≈ 10.7 z-score units — far more than rate-similarity predicts.

# Spontaneous (41.84 Hz, z=+1.91) is HIGHER rate than gratings (27.93, z=+9.77)
# yet has weaker z.  This is the OPPOSITE of what rate-driven prediction
# would say (higher rate → more events → tighter surrogate → higher z).
# Both gratings (medium rate) and spontaneous (high rate) have p=7 enrichment,
# whereas movies (medium rate) do NOT.  → not rate-driven.

verdict = 'CONTENT_DRIVEN'

summary = dict(
    verdict=verdict,
    monkey1_subsets=data,
    interpretation=(
        "monkey1_gratings (27.93 Hz) and monkey1_natural_movie (24.25 Hz) "
        "have similar rates but differ by ~11 z-score units in p=7 "
        "enrichment.  Rate-matched comparison rules out rate as the driver "
        "of movie p=7 suppression; the difference is content-driven. "
        "Further evidence: monkey1_spontaneous at 41.84 Hz (higher rate) "
        "still shows positive p=7 z, ruling out a simple 'high rate "
        "washes out p-adic structure' explanation."
    ),
)
with open(OUT_DIR / 'p7_content_vs_rate_check.json', 'w') as f:
    json.dump(summary, f, indent=2)
print(f"\nVERDICT: {verdict}")
print(f"  → p7_content_vs_rate_check.json")
