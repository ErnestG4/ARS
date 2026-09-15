"""Check that every number in the LaTeX paper traces to a committed source.

The .tex is a TRANSCRIPTION of PROSE.md (plus NOTE.md's appendices), and a
transcription's characteristic failure is silent: a digit changes, or a line is
dropped, and nothing downstream notices because prose has no arithmetic to
re-derive.  So this checker treats the numerals themselves as the checkable
content.

What it protects, in order:

  1. NO INVENTED NUMBER.  Every numeral in the body of paper.tex must occur in
     PROSE.md or NOTE.md, or be RE-DERIVED HERE from a committed artifact.  The
     .tex adds one footnote and one parenthetical that postdate the prose draft
     (the correlated-error study); those numbers are recomputed from
     zbeta_correlated_error.json at check time rather than allowlisted as
     strings, so editing the artifact breaks this row.
  2. NO DROPPED NUMBER.  Every numeral in PROSE.md must appear in paper.tex,
     except tokens listed with a reason below -- draft management, and the
     citations dropped when section 5 was de-linked from the glass literature.
     This is the arm that catches a paragraph lost in conversion.
  3. STRUCTURE.  Every PROSE section heading has a sectioning command in the
     .tex, and every \\includegraphics target exists on disk.

What it does NOT check: that each number is attached to the same QUANTITY in
both documents.  Numerals are compared as a multiset of strings, so a
transposition between two sentences passes.  That is a real gap and is stated
rather than papered over; the defence against it is that both documents are
read by a human before submission.

Formatting numerals (font sizes, margins, figure widths) are excluded by
stripping the preamble and \\includegraphics options -- they are typography, not
claims, and allowlisting them individually would slowly become a place to hide
a real number.
"""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
DFLOW = os.path.dirname(HERE)
bad = []

tex_raw = open(os.path.join(HERE, "paper.tex")).read()
prose = open(os.path.join(HERE, "PROSE.md")).read()
note = open(os.path.join(HERE, "NOTE.md")).read()

# --- body only: the preamble is typography, not claims -----------------------
if "\\begin{document}" not in tex_raw:
    bad.append("paper.tex has no \\begin{document}")
    tex_body = tex_raw
else:
    tex_body = tex_raw.split("\\begin{document}", 1)[1]

NUM = re.compile(r"\d+(?:\.\d+)?(?:e-?\d+)?")


def numerals(text):
    text = re.sub(r"\\includegraphics\[[^\]]*\]", " \\\\includegraphics ", text)
    text = re.sub(r"\\[a-zA-Z]+\*?", " ", text)
    for ch in "{}$":
        text = text.replace(ch, " ")
    return set(NUM.findall(text))


# --- numbers the .tex adds, re-derived from the artifact ---------------------
sys.path.insert(0, DFLOW)
import numpy as _np                                                   # noqa: E402
from science_rate_question import (f3 as _f3, fit_ladder as _ladder,   # noqa: E402
                                   LN10 as _LN10, FIT_WINDOW_MIN as _FWM)

# --- Stage 3c window surface: every numeral in the paper's window-disclosure
# paragraph is READ from the artifact, never typed. Added 2026-09-14 with that
# paragraph; the standing rule this arc paid five times to learn.
s3c = json.load(open(os.path.join(DFLOW, "stage3c_window_surface_alln.json")))
w3c = set()
for nn, v in s3c["per_n"].items():
    w3c |= {"%.4f" % v["sep_min"], "%.4f" % v["sep_max"],
            "%.1f" % (v["spread"] * 100), "%.2f" % v["zb_min"],
            "%.2f" % v["zb_max"], "%.1f" % v["swing"],
            "%.2f" % v["sealed_zbeta"], "%d" % round(v["pct"] * 100)}
w3c |= {"%d" % (len(s3c["k_lo"]) * len(s3c["upper_rules"])),
        "%d" % max(s3c["k_lo"]), "%d" % len(s3c["ns"])}

# --- Stage 3d: the bootstrap correction to the percentile claim. Same rule --
# every numeral READ from the artifact, so the correction footnote cannot drift
# from the measurement that motivated it.
s3d = json.load(open(os.path.join(DFLOW, "stage3d_error_model.json")))
for nn, v in s3d["per_n"].items():
    w3c |= {"%.2f" % v["pct_boot"], "%.1f" % v["swing_boot"],
            "%.2f" % v["sealed_boot"], "%.2f" % v["swing_cov"],
            "%.2f" % (v["sealed_cov"] / v["sealed_boot"])}

# --- the (tau, beta) degeneracy on the shortest window, COMPUTED not trusted.
# The paper quotes corr(tau,beta) = 0.999 on seven points; that number came from
# a diagnostic on 2026-09-15 and is banked nowhere, so the checker refits the
# cell and derives it. If the correlation ever drops below what the paper
# claims, the paper is wrong and the row says so.
from scipy.optimize import curve_fit as _cf                            # noqa: E402
_s3 = json.load(open(os.path.join(DFLOW, "stage3_commensurable_window.json")))
_KA = _np.array(_s3["k_grid"], float)
_worst_corr = 1.0
for _sc in ("iid", "gue"):
    _c = _np.array(_s3["per_replicate_curves"][_sc])
    _mu, _sg = _c.mean(axis=0), _c.std(axis=0, ddof=1) / _np.sqrt(16)
    _w = (_KA >= 5) & (_KA <= 11)
    _y, _sy = _np.log10(_mu[_w]), _sg[_w] / (_mu[_w] * _LN10)
    _best = None
    for _t in (2.0, 5.0, 10.0, 30.0):
        for _b in (0.5, 0.75, 1.0):
            try:
                _p, _cov = _cf(_f3, _KA[_w], _y, p0=[_y[0], _t, _b], sigma=_sy,
                               absolute_sigma=True,
                               bounds=([-_np.inf, 1e-3, 0.05], [_np.inf, 1e4, 3.0]),
                               maxfev=20000)
                _c2 = float(_np.sum(((_y - _f3(_KA[_w], *_p)) / _sy) ** 2))
                if _np.isfinite(_c2) and (_best is None or _c2 < _best[0]):
                    _best = (_c2, _p, _cov)
            except Exception:
                pass
    _r = abs(_best[2][1, 2] / _np.sqrt(_best[2][1, 1] * _best[2][2, 2]))
    _worst_corr = min(_worst_corr, _r)
w3c |= {"%.3f" % _worst_corr}

# --- the sealed-window degeneracy and the fork threshold, DERIVED. The paper
# now says corr(tau,beta) is 0.994 on the sealed window and the fork's
# threshold is 0.95; both come from code, not from a number I typed here.
sys.path.insert(0, os.path.dirname(DFLOW))
from errormodel import degeneracy_of as _deg                       # noqa: E402
import importlib.util as _ilu                                      # noqa: E402
_spec = _ilu.spec_from_file_location(
    "_ve", os.path.join(os.path.dirname(DFLOW), "verify_errormodel.py"))
_thr = None
for _line in open(_spec.origin):
    if _line.startswith("DEGENERACY_THRESHOLD"):
        _thr = float(_line.split("=")[1].split("#")[0])
w3c |= {"%.2f" % _thr}
_sealed_corr = 1.0
_sealed_by_class = {}
for _sc in ("iid", "gue"):
    _c = _np.array(_s3["per_replicate_curves"][_sc])
    _mu, _sg = _c.mean(axis=0), _c.std(axis=0, ddof=1) / _np.sqrt(16)
    _w = _mu > _FWM
    _y, _sy = _np.log10(_mu[_w]), _sg[_w] / (_mu[_w] * _LN10)
    _best = None
    for _t in (2.0, 5.0, 10.0, 30.0):
        for _b in (0.5, 0.75, 1.0):
            try:
                _p, _cov = _cf(_f3, _KA[_w], _y, p0=[_y[0], _t, _b], sigma=_sy,
                               absolute_sigma=True,
                               bounds=([-_np.inf, 1e-3, 0.05], [_np.inf, 1e4, 3.0]),
                               maxfev=20000)
                _c2 = float(_np.sum(((_y - _f3(_KA[_w], *_p)) / _sy) ** 2))
                if _np.isfinite(_c2) and (_best is None or _c2 < _best[0]):
                    _best = (_c2, _p, _cov)
            except Exception:
                pass
    _sealed_by_class[_sc] = _deg(_best[2])
    _sealed_corr = min(_sealed_corr, _sealed_by_class[_sc])
w3c |= {"%.3f" % v for v in _sealed_by_class.values()}
w3c |= {"%.3f" % _sealed_corr, "%.3f" % max(_worst_corr, _sealed_corr)}
if _sealed_corr < _thr:
    raise SystemExit(f"the sealed-window degeneracy reads {_sealed_corr:.3f}, below "
                     f"the fork threshold {_thr} — the paper's 'not separately "
                     "identified at any window' claim is stale")
if _worst_corr < 0.99:
    raise SystemExit(f"the (tau,beta) degeneracy the paper quotes as 0.999 now "
                     f"reads {_worst_corr:.3f} — the paper's claim is stale")

# --- the iid sealed-window residuals and the AICc margins, DERIVED not typed.
_bank = json.load(open(os.path.join(DFLOW, "science_dense_grid.json")))
_c = _bank["data"]["iid"]["4096"]
_ks = sorted((int(k) for k in _c), key=int)
_m = _np.array([_c[str(k)]["mean"] for k in _ks])
_sg = _np.array([_c[str(k)]["sigma_mean"] for k in _ks])
_w = _m > _FWM
_r = ((_np.log10(_m[_w]) - _f3(_np.array(_ks, float)[_w],
                               *_bank["adjudication"]["shape_params"]["iid"]))
      / (_sg[_w] / (_m[_w] * _LN10)))
w3c |= {"%.2f" % abs(v) for v in _r[:3]}
_mg, _cells = [], 0
for _n in (1024, 2048, 4096):
    for _sc in ("iid", "gue"):
        _cc = _bank["data"][_sc][str(_n)]
        _kk = sorted((int(k) for k in _cc), key=int)
        _mm = _np.array([_cc[str(k)]["mean"] for k in _kk])
        _ss = _np.array([_cc[str(k)]["sigma_mean"] for k in _kk])
        for _keep in (_mm > _FWM, _np.array(_kk) <= 11, _np.array(_kk) <= 16,
                      _np.array(_kk) <= 8):
            if _keep.sum() < 5:
                continue
            _sel, _f = _ladder(_np.array(_kk, float)[_keep], _mm[_keep], _ss[_keep])
            if _sel != "F3":
                raise SystemExit(f"F3 is no longer AICc-best at {_sc} n={_n}: "
                                 f"selected {_sel} — the paper's footnote is stale")
            _a = {k_: v_["aicc"] for k_, v_ in _f.items()
                  if _np.isfinite(v_.get("aicc", _np.inf))}
            _mg.append(min(v_ for k_, v_ in _a.items() if k_ != "F3") - _a["F3"])
            _cells += 1
# both the rounded and one-decimal forms, because prose quotes whichever reads
# better and the checker must not force the prose to a format.
w3c |= {"%.1f" % min(_mg), "%.1f" % max(_mg), "%d" % round(min(_mg)),
        "%d" % round(max(_mg)), "%d" % _cells}

z = json.load(open(os.path.join(DFLOW, "zbeta_correlated_error.json")))
gls = z["z"]["gls_sweep"]
c4 = z["bars"]["max |z_gls - z_boot| / z_boot over the shrinkage sweep"]
n80 = z["bars"]["recovered-vs-banked mismatches (80 numbers)"]
derived = {
    "%.2f" % z["z"]["bootstrap"],            # 8.24, footnote in section 4
    "%.2f" % min(gls),                       # 9.97   \
    "%.2f" % max(gls),                       # 11.12  / the GLS sweep's range
    "%.2f" % z["z"]["sealed_recomputed"],    # 9.31
    "%.3f" % z["ratios"]["gue"],             # 0.735  tightens
    "%.3f" % z["ratios"]["iid"],             # 1.363  loosens
    "%d" % n80["ceiling"],                   # 80 numbers recovered
    "%d" % round(c4["value"] * 100),         # 35% disagreement
    "%d" % round(c4["thresh"] * 100),        # against the 25% ceiling
}
if n80["value"] != 0:
    bad.append("the recovery premise no longer reads 0 mismatches; the "
               "footnote's 'reproduced the banked artifact exactly' is stale")
if c4["met"]:
    bad.append("C4 now reads MET; the .tex footnote says the stability bar was "
               "MISSED, so one of the two is wrong")

# --- numerals PROSE carries that the paper deliberately does not --------------
# Two classes, each entry named with its reason.  This list is the ONLY way a
# numeral may go missing, so adding to it is a deliberate, reviewable act; a
# conversion that silently dropped a paragraph would still fail the row.
DRAFT_ONLY = {
    "1.0": "the prose draft's own version marker (v1.0)",
    "19": "the draft header's target submission date, 2026-08-19, now past",
}
# 2026-09-09, on Will's instruction to "back off of any claims of linkage and
# only point out facts": section 5 no longer places this system's stretched
# exponential inside the glass-relaxation literature's open question, so the
# bibliographic numerals of the works cited ONLY to make that linkage are gone
# with it.  The measurements they sat beside are all still in the paper -- what
# was removed is the claim of kinship, not a result.
DELINKED = {
    "51": "Ediger, Annu. Rev. Phys. Chem. 51", "2000": "Ediger, year",
    "99": "Ediger, page",
    # "14" was Richert's volume number. It re-entered the paper on 2026-09-14 as
    # part of that date in the window-disclosure footnote, so the exclusion is
    # retired rather than the date being reworded to dodge a checker.
    "2002": "Richert, year", "703": "Richert, page R703",
    "243": "Sillescu, J. Non-Cryst. Solids 243", "1999": "Sillescu, year",
    "81": "Sillescu, page", "93": "Widmer-Cooper et al., PRL 93",
    "2004": "Widmer-Cooper et al., year",
    "135701": "Widmer-Cooper et al., article number",
    "2011.00579": "arXiv preprint on KWW origins",
}
EXCLUDED = {**DRAFT_ONLY, **DELINKED}

tex_nums = numerals(tex_body)
src_nums = numerals(prose) | numerals(note)

invented = sorted(tex_nums - src_nums - derived - w3c, key=lambda s: (len(s), s))
if invented:
    bad.append("numerals in paper.tex with no source and no derivation: "
               + ", ".join(invented))

dropped = sorted(numerals(prose) - tex_nums - set(EXCLUDED),
                 key=lambda s: (len(s), s))
if dropped:
    bad.append("numerals in PROSE.md missing from paper.tex: "
               + ", ".join(dropped))

for tok, why in EXCLUDED.items():
    if tok in tex_nums and tok not in w3c:
        bad.append(f"{tok!r} is in paper.tex but was excluded as {why}")

# --- structure ---------------------------------------------------------------
heads = re.findall(r"^#{2,3} (.+)$", prose, re.M)
tex_heads = re.findall(r"\\(?:section|subsection)\*?\{([^}]*)\}", tex_body)
tex_heads_l = [h.lower() for h in tex_heads] + (
    ["abstract"] if "\\begin{abstract}" in tex_body else [])
for h in heads:
    key = re.sub(r"^(?:\d+\.|Appendix [A-Z]\s*[-—]?)\s*", "", h).strip().lower()
    if not any(key in t for t in tex_heads_l):
        bad.append(f"PROSE heading {h!r} has no matching section in paper.tex")

figs = re.findall(r"\\includegraphics\[[^\]]*\]\{([^}]*)\}", tex_body)
if not figs:
    bad.append("no \\includegraphics in paper.tex — the figures were dropped")
for f in figs:
    if not os.path.exists(os.path.join(HERE, f)):
        bad.append(f"figure {f} does not exist")

print(f"  numerals: {len(tex_nums)} in the paper, "
      f"{len(tex_nums & src_nums)} traced to PROSE/NOTE, "
      f"{len(tex_nums & derived)} re-derived from zbeta_correlated_error.json")
print(f"  sections: {len(heads)} PROSE headings, {len(tex_heads)} in the .tex; "
      f"figures: {len(figs)} included, all present")
print(f"  the C4 miss the footnote reports still reads MISSED at "
      f"{c4['value']:.4f} vs {c4['thresh']}")

if bad:
    print("VERIFY_PAPER_NUMBERS: FAIL")
    for b in bad:
        print("  *", b)
    sys.exit(1)
print("VERIFY_PAPER_NUMBERS: PASS — no invented numeral, no dropped numeral, "
      "every section and figure carried over")
