"""
phase34f_cohh/bianchi_data_loader.py — cohomological-H data layer.

Source (per §3, verified): JohnCremona/bianchi-data GitHub `newforms/`
consolidated catalogs, reachable from the agent env (no reCAPTCHA / no
rate-limit). Format documented in newforms/schema.txt:

  field_label level_label letter level_gens 2 bc cm sfe L/P [AL] x [AP]

bc : 0 not-bc | d>0 bc of a form over Q(√d) (d=1 = over ℚ) | −d twist
cm : 0 not-CM | d<0 CM-field disc
[AP]: Fourier coeffs at all prime ideals (good primes ⇒ Hecke eigenvalues),
      positionally indexed in Cremona's standard ordering — the ordering
      itself is the §D.0b decode residue, resolved by select_ordering()
      against the bc≠0 base-change structural signature (§7.ter.55).

This module: fetch+cache, parse, prime-ideal generators (two candidate
orderings), the §4 decode gate, RP-normalisation, bad-prime drop, and the
three-way (cm,bc) stratifier. NO Sato-Tate here (that is run_cohh.py).
"""
from __future__ import annotations

import os
import sys
import math
import urllib.request

THIS = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(THIS)
DATA = os.path.join(ROOT, "data", "phase34f_cohh")          # data/ is gitignored
os.makedirs(DATA, exist_ok=True)

RAW = "https://raw.githubusercontent.com/JohnCremona/bianchi-data/master/newforms/"
# field_label -> (remote newforms file, ramified rational prime, split test)
FIELDS = {
    "2.0.4.1": dict(file="newforms.1.1-100000", ram=2,
                    split=lambda p: p % 4 == 1),   # Q(i),   Z[i]
    "2.0.3.1": dict(file="newforms.3.1-150000", ram=3,
                    split=lambda p: p % 3 == 1),   # Q(√−3), Z[ω]
}


def fetch(field_label: str) -> str:
    """Download (cached) the consolidated newforms catalog for a field."""
    fn = FIELDS[field_label]["file"]
    local = os.path.join(DATA, fn)
    if not os.path.exists(local) or os.path.getsize(local) == 0:
        url = RAW + fn
        print(f"  fetching {url} → {local}")
        req = urllib.request.Request(url, headers={"User-Agent": "cohh/1.0"})
        with urllib.request.urlopen(req, timeout=120) as r, open(local, "wb") as o:
            o.write(r.read())
    return local


def parse_newforms(path: str):
    """Yield dicts: field,level_label,level_norm,letter,bc,cm,sfe,ap[list]."""
    n_ok = n_bad = 0
    with open(path) as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            t = line.split()
            if len(t) != 12 or t[4] != "2" or t[10] != "x":
                n_bad += 1
                continue
            try:
                ap = [int(x) for x in t[11].strip("[]").split(",") if x != ""]
            except ValueError:
                n_bad += 1
                continue
            if not ap:
                n_bad += 1
                continue
            n_ok += 1
            yield dict(field=t[0], level_label=t[1], letter=t[2],
                       level_norm=int(t[1].split(".")[0]),
                       bc=int(t[5]), cm=int(t[6]), sfe=t[7], ap=ap)
    parse_newforms.stats = dict(n_ok=n_ok, n_bad=n_bad)


def _sieve(n: int):
    s = bytearray([1]) * (n + 1)
    s[0] = s[1] = 0
    for i in range(2, int(n ** 0.5) + 1):
        if s[i]:
            s[i * i::i] = bytearray(len(s[i * i::i]))
    return [i for i in range(2, n + 1) if s[i]]


def prime_ideals(field_label: str, n_needed: int, ordering: str):
    """Return [(rat_p, norm, kind)] of length ≥ n_needed.

    ordering='ratprime': rational primes ascending; each split p emits its
        two ideals (norm p) adjacently, inert p one ideal (norm p²),
        ramified one ideal (norm p).
    ordering='idealnorm': same ideals, stably sorted by ideal norm.
    """
    f = FIELDS[field_label]
    ram, is_split = f["ram"], f["split"]
    out = []
    pbound = 200
    while True:
        out = []
        for p in _sieve(pbound):
            if p == ram:
                out.append((p, p, "ram"))
            elif is_split(p):
                out.append((p, p, "split"))
                out.append((p, p, "split"))
            else:
                out.append((p, p * p, "inert"))
        if ordering == "idealnorm":
            out.sort(key=lambda r: r[1])          # stable: split pair stays adjacent
        if len(out) >= n_needed:
            return out[:max(n_needed, len(out))]
        pbound *= 2


def _split_pair_positions(ideals):
    """[(i, rat_p)] where ideals[i],[i+1] are conjugates of one split p."""
    pos = []
    i = 0
    while i + 1 < len(ideals):
        a, b = ideals[i], ideals[i + 1]
        if a[2] == "split" and b[2] == "split" and a[0] == b[0]:
            pos.append((i, a[0]))
            i += 2
        else:
            i += 1
    return pos


def select_ordering(forms: list) -> dict:
    """§4 decode gate — pick the prime-ideal ordering empirically.

    Correct ordering ⇒ on bc≠0 (base-change) forms the two conjugate
    split-prime [AP] entries are EQUAL (a(𝔭)=a(𝔭̄)=classical a_p), on
    bc=0&cm=0 forms they are generically UNEQUAL (negative control), and
    RP-normalised |a(𝔭)|/√N(𝔭) ≤ 2 holds (BCGNT Thm A; norm-misaligned
    ordering blows this). Pick the ordering passing all three; HALT
    (return verdict=UNRESOLVED) if zero or both qualify ambiguously.
    """
    fld = forms[0]["field"]
    maxlen = max(len(f["ap"]) for f in forms)
    # §4 cross-check substrate is bc==1 ONLY (base change over ℚ ⇒
    # a(𝔭)=a(𝔭̄)=classical aₚ exactly). bc=d>1 (bc over Q(√d)) and bc<0
    # (twist of a bc) do NOT carry the clean conjugate-equality signature
    # — pooling them (all bc≠0) dilutes the statistic. Bad split primes
    # are excluded (coefficient there is a U_p / AL term, not classical aₚ).
    bc1_forms = [f for f in forms if f["bc"] == 1][:400]
    c_forms = [f for f in forms if f["bc"] == 0 and f["cm"] == 0][:400]
    report = {}
    for od in ("ratprime", "idealnorm"):
        ide = prime_ideals(fld, maxlen, od)
        pairs = _split_pair_positions(ide)        # [(i, rat_p)]

        def frac_pair_equal(fs):
            eq = tot = 0
            for f in fs:
                ap, L = f["ap"], len(f["ap"])
                bad = _bad_rat_primes(fld, f["level_norm"])
                for i, rp in pairs:
                    if i + 1 < L and rp not in bad:   # good split primes only
                        tot += 1
                        eq += (ap[i] == ap[i + 1])
            return (eq / tot) if tot else float("nan"), tot

        eq_bc, n_bc = frac_pair_equal(bc1_forms)
        eq_c, n_c = frac_pair_equal(c_forms)
        # RP bound on good primes, sampled across all strata
        within = tot = 0
        for f in forms[:600]:
            bad = _bad_rat_primes(fld, f["level_norm"])
            for k, v in enumerate(f["ap"]):
                if k >= len(ide):
                    break
                p, nrm, _ = ide[k]
                if p in bad:
                    continue
                tot += 1
                within += (abs(v) <= 2.0 * math.sqrt(nrm) + 1e-9)
        frac_within = (within / tot) if tot else float("nan")
        report[od] = dict(frac_pair_equal_bc=eq_bc, n_bc_pairs=n_bc,
                          frac_pair_equal_genuine=eq_c, n_genuine_pairs=n_c,
                          frac_RP_within=frac_within, n_rp=tot)
    # decision
    def passes(r):
        return (r["frac_pair_equal_bc"] >= 0.98 and
                r["frac_pair_equal_genuine"] <= 0.60 and
                r["frac_RP_within"] >= 0.999)
    winners = [od for od, r in report.items() if passes(r)]
    verdict = ("RESOLVED:" + winners[0]) if len(winners) == 1 else "UNRESOLVED"
    return dict(verdict=verdict, ordering=(winners[0] if len(winners) == 1
                                           else None), report=report,
                n_bc1_crosscheck=len(bc1_forms))


def _bad_rat_primes(field_label: str, level_norm: int) -> set:
    bad = {FIELDS[field_label]["ram"]}
    m = level_norm
    d = 2
    while d * d <= m:
        while m % d == 0:
            bad.add(d)
            m //= d
        d += 1
    if m > 1:
        bad.add(m)
    return bad


def rp_good(form: dict, ideals: list):
    """[(x, norm)] : RP-normalised x=a(𝔭)/√N(𝔭) at GOOD primes + the
    ideal norm (kept so a finite-P / Chen-2019 NLO scan can truncate by
    prime bound — the disciplined instrument at large pooled n, where a
    KS p-value is uninformative)."""
    bad = _bad_rat_primes(form["field"], form["level_norm"])
    out = []
    for k, v in enumerate(form["ap"]):
        if k >= len(ideals):
            break
        p, nrm, _ = ideals[k]
        if p in bad:
            continue
        out.append((v / math.sqrt(nrm), nrm))
    return out


def stratum(form: dict) -> str:
    """Three-way (cm,bc) split (§5). A=CM, B=base-change non-CM, C=genuine."""
    if form["cm"] != 0:
        return "A"
    return "B" if form["bc"] != 0 else "C"


__all__ = ["FIELDS", "fetch", "parse_newforms", "prime_ideals",
           "select_ordering", "rp_good", "stratum", "_bad_rat_primes"]
