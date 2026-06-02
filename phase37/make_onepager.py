"""Render a one-page PDF summary of the CRCNS spectral-statistics findings (matplotlib, no external deps)."""
import textwrap
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

OUT = "/home/combust/fmexplorer/criticality_tool/phase37/CRCNS_SUMMARY_1PAGE.pdf"
LEFT = 0.07; WIDTH_CHARS = 108

fig = plt.figure(figsize=(8.5, 11)); fig.patch.set_facecolor("white")
def T(x, y, s, size=9.5, weight="normal", color="black", mono=False, italic=False):
    fig.text(x, y, s, fontsize=size, fontweight=weight, color=color, va="top", ha="left",
             family=("monospace" if mono else "sans-serif"),
             style=("italic" if italic else "normal"))

y = 0.965
T(LEFT, y, "Spectral statistics of spike trains across three CRCNS datasets", size=15, weight="bold"); y -= 0.028
T(LEFT, y, "Exploratory cross-dataset analysis, 2026-06  ·  fresh re-derivation, firing-rate + burst controlled, bootstrap 95% CIs",
  size=8.5, italic=True, color="#444444"); y -= 0.032

def para(txt, size=9.3, gap=0.0125, lead=0.0, width=WIDTH_CHARS):
    global y
    y -= lead
    for ln in txt.split("\n"):
        for w in (textwrap.wrap(ln, width=width) or [""]):
            T(LEFT, y, w, size=size); y -= gap

def head(txt):
    global y
    y -= 0.006
    T(LEFT, y, txt, size=10.5, weight="bold", color="#1a3e6e"); y -= 0.019

head("What we measure")
para("For each unit we characterise the inter-spike-interval (ISI) spacing distribution against random-matrix "
     "spectral classes. ks_gue = KS distance of the unit-mean-normalised ISI spacings from the GUE Wigner "
     "surmise: LOW = rigid / level-repulsive (sub-Poisson), HIGH = far from GUE (Poisson or clustered). CV2 "
     "(Holt 1996) is a rate-robust local-irregularity measure: ~1 Poisson, <1 regular, >1 bursty/clustered.")

head("Selectivity ↔ spectral class  (does functional tuning predict ISI structure?)")
# table
rows = [
    ("Dataset (preparation)", "Selectivity test", "Spearman ρ (controlled)"),
    ("macaque V1 — pvc-11 (Kohn)", "OSI ↔ ks_gue", "+0.72   (n=210, rate-ctrl)"),
    ("rat hippocampus — hc-3 (Buzsáki)", "spatial-info ↔ ks_gue", "+0.37  [0.29, 0.46]  rate-strat."),
    ("mouse retina — ret-1", "RF-SNR ↔ ks_gue", "+0.05   uninformative*"),
    ("mouse V1 — Allen (non-CRCNS ref.)", "OSI ↔ ks_gue", "−0.22  (sign reversal)"),
]
col_x = [LEFT, LEFT + 0.34, LEFT + 0.60]
y -= 0.004
for i, r in enumerate(rows):
    wt = "bold" if i == 0 else "normal"
    for cx, cell in zip(col_x, r):
        T(cx, y, cell, size=9.0, weight=wt, mono=True)
    y -= 0.0165
    if i == 0:
        T(LEFT, y + 0.004, "─" * 96, size=7, mono=True, color="#999999"); y -= 0.006
y -= 0.004
para("Positive = more selective cells have ISI spacings farther from GUE (more clustered). All values control "
     "firing rate and burst fraction; hc-3 also rate-stratified within quartiles (raw +0.69 → partial +0.47 "
     "→ stratified +0.37) and is rate-modulated (stronger at high rate). Macaque V1 and rat hippocampus "
     "AGREE in direction; the lone reversal is mouse V1.  *retina: RF-SNR is a noisy proxy for tuning quality "
     "(wrong resolution) — uninformative as specified, NOT a negative result; the test is a motion/DS axis.", size=9.0)

head("Local irregularity (CV2): a sensory → hippocampal clustering gradient")
para("Hippocampus is genuinely fast-clustering with a within-structure gradient CA3 1.25 > EC 1.10 > DG 1.02 "
     "(recurrent CA3 burst-prone → sparse dentate near Poisson). Retina CV2 ≈ 1.08; mouse V1 ≈ 1.0 "
     "(Poisson point). CV2 (vs the global ISI CV) separates genuine bursting from slow rate-drift / recording-"
     "epoch structure.", size=9.0)

head("Headline")
para("In both CRCNS datasets with a matched tuning axis — macaque V1 (orientation) and rat hippocampus "
     "(spatial information) — functional selectivity predicts spectral class in the SAME direction: more "
     "selective cells are more temporally clustered (farther from GUE), robust to firing-rate and burst control. "
     "The one sign reversal is mouse V1, suggesting a species/preparation-systematic effect rather than a "
     "cortex-vs-hippocampus one.", size=9.3)

head("Caveats")
para("• ks_gue is rate-sensitive at finite spike counts — all correlations are rate-controlled; naive "
     "uncontrolled values are larger and should not be used.\n"
     "• Burst fraction co-varies with ks_gue by construction (intrinsic); the reported links are the "
     "EXTRINSIC selectivity effect AFTER burst control — not merely 'place/selective cells burst.'\n"
     "• DG is underpowered (n=16). • Exploratory analyses of public CRCNS data, not peer-reviewed.\n"
     "• Datasets: CRCNS pvc-11 (Kohn), hc-3 (Mizuseki/Buzsáki), ret-1; reference mouse-V1 = Allen "
     "Neuropixels. Reproducible scripts + per-cell tables available on request. (Confirm exact dataset "
     "citations before publication.)", size=8.6)

with PdfPages(OUT) as pdf:
    pdf.savefig(fig, facecolor="white")
plt.close(fig)
print("wrote", OUT)
