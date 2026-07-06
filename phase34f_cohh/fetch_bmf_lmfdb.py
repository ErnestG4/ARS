#!/usr/bin/env python3
"""
phase34f_cohh/fetch_bmf_lmfdb.py — pull the full cohomological Bianchi
newform corpus from the LMFDB API for the cohomological-H cell.

RUN THIS ON A MACHINE WHERE lmfdb.org IS NOT reCAPTCHA-WALLED (the agent
environment is; Will's machine is not — that's why this is handed over).

Fields: Q(i) = 2.0.4.1, Q(√−3) = 2.0.3.1.  Pulls the FULL bmf_forms
record per form (incl. the long `hecke_eigs` list, `CM`, `bc`, `weight`,
`dimension`, `hecke_poly`, `field_label`, `level_*`, bad-primes). No
`_fields` filter and no remote `dimension` filter — payload is dominated
by `hecke_eigs` anyway, and filtering locally (in the loader) can't
silently mis-filter on an API-syntax guess.

Disciplines baked in (the §D.0a/§D.0b rules that have caught every real
bug this arc):
  * FAIL LOUD: any page whose body contains 'recaptcha' or is not valid
    JSON aborts the run — a truncated pull is NEVER treated as complete.
  * POLITE: configurable sleep between pages; exponential backoff on
    HTTP 429/503 (shared volunteer academic server).
  * RESUMABLE: each page written to pages/<field>_pNNNN.json; a rerun
    skips pages already on disk, so a rate-limit kill just needs a rerun.
  * SELF-DIAGNOSING: --probe fetches only page 1 and prints the envelope
    shape, sample-record keys, detected total and paging mode, so the
    fetch contract is confirmed BEFORE pulling thousands of pages.

Usage:
  python3 fetch_bmf_lmfdb.py --probe                 # do this first
  # paste the printed PROBE block back for contract confirmation, then:
  python3 fetch_bmf_lmfdb.py                          # full pull, both fields
  python3 fetch_bmf_lmfdb.py --field 2.0.4.1 --sleep 1.5

Output (hand these back, or paste manifest.json + one .jsonl line):
  cohh_data/<field>.jsonl     one bmf_forms record per line
  cohh_data/manifest.json     per-field collected/total/complete + query
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
import urllib.request
import urllib.error
from urllib.parse import urljoin

API = "https://www.lmfdb.org/api/bmf_forms/"
FIELDS = ["2.0.4.1", "2.0.3.1"]            # Q(i), Q(√−3)
UA = "cohomological-H-fetch/1.0 (ARS instrument-validation; polite paged pull)"


def _get(url: str, max_retries: int = 5) -> str:
    """HTTP GET with backoff. Returns body text; raises on hard failure."""
    backoff = 5.0
    for attempt in range(max_retries):
        req = urllib.request.Request(
            url, headers={"User-Agent": UA, "Accept": "application/json",
                          "Accept-Encoding": "identity"})
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                return r.read().decode("utf-8", "replace")
        except urllib.error.HTTPError as e:
            if e.code in (429, 503):
                print(f"  HTTP {e.code} — backoff {backoff:.0f}s "
                      f"(attempt {attempt+1}/{max_retries})")
                time.sleep(backoff)
                backoff *= 2
                continue
            raise
        except (urllib.error.URLError, TimeoutError) as e:
            print(f"  net error {e!r} — backoff {backoff:.0f}s")
            time.sleep(backoff)
            backoff *= 2
    raise RuntimeError(f"GET failed after {max_retries} retries: {url}")


def _parse_or_die(body: str, where: str) -> dict | list:
    if "recaptcha" in body.lower():
        sys.exit(f"ABORT [{where}]: response is a reCAPTCHA challenge — "
                 f"lmfdb.org is bot-walling this machine. A partial pull "
                 f"is NOT complete. Run from a non-walled network.")
    try:
        return json.loads(body)
    except json.JSONDecodeError:
        sys.exit(f"ABORT [{where}]: non-JSON response (first 200 chars):\n"
                 f"{body[:200]}")


def _envelope(d):
    """Return (records_list, next_url_or_None, total_or_None)."""
    if isinstance(d, list):
        return d, None, None
    recs = d.get("data") if isinstance(d.get("data"), list) else None
    if recs is None:                       # some LMFDB endpoints nest differently
        for k in ("forms", "results", "rows"):
            if isinstance(d.get(k), list):
                recs = d[k]
                break
    nxt = d.get("next") or d.get("next_url") or None
    total = None
    for k in ("total", "count", "number", "num_results"):
        if isinstance(d.get(k), int):
            total = d[k]
            break
    return (recs or []), nxt, total


def probe(field: str):
    url = f"{API}?field_label={field}&_format=json&_limit=1&_offset=0"
    d = _parse_or_die(_get(url), "probe")
    recs, nxt, total = _envelope(d)
    print("=" * 70)
    print(f"PROBE  field={field}")
    print("=" * 70)
    print(f"top-level type: {type(d).__name__}; "
          f"keys: {list(d.keys()) if isinstance(d,dict) else '(list)'}")
    print(f"records on page: {len(recs)}; detected total: {total}; "
          f"next-link present: {bool(nxt)}  "
          f"({'follow next' if nxt else 'use _offset paging'})")
    if recs:
        r = recs[0]
        need = ["label", "field_label", "level_label", "level_norm",
                "weight", "dimension", "hecke_poly", "CM", "bc",
                "hecke_eigs", "field_bad_primes", "level_bad_primes"]
        print("sample record keys:", sorted(r.keys()))
        miss = [k for k in need if k not in r]
        print("REQUIRED FIELDS:",
              "ALL PRESENT ✓" if not miss else f"MISSING {miss} ✗")
        he = r.get("hecke_eigs")
        print(f"hecke_eigs: len={len(he) if isinstance(he,list) else 'N/A'}, "
              f"head={he[:8] if isinstance(he,list) else he}")
        print(f"CM={r.get('CM')} bc={r.get('bc')} weight={r.get('weight')} "
              f"dimension={r.get('dimension')} hecke_poly={r.get('hecke_poly')!r}")
    print("=" * 70)
    print("Paste this PROBE block back before the full pull (fail-fast on a "
          "rate-limited resource).")


def pull(field: str, outdir: str, page: int, sleep: float):
    pdir = os.path.join(outdir, "pages")
    os.makedirs(pdir, exist_ok=True)
    offset, pno, collected, total = 0, 0, 0, None
    nxt = f"{API}?field_label={field}&_format=json&_limit={page}&_offset=0"
    recs_all = []
    while nxt:
        cur = nxt
        pfile = os.path.join(pdir, f"{field}_p{pno:04d}.json")
        if os.path.exists(pfile):                       # resume
            d = json.load(open(pfile))
        else:
            d = _parse_or_die(_get(cur), f"{field} page {pno}")
            with open(pfile, "w") as fh:
                json.dump(d, fh)
        recs, nlink, t = _envelope(d)
        if t is not None:
            total = t
        recs_all.extend(recs)
        collected += len(recs)
        print(f"  {field} page {pno}: +{len(recs)} (total {collected}"
              f"{f'/{total}' if total else ''})")
        if nlink:
            # LMFDB returns `next` as a RELATIVE url ('?...' or
            # '/api/...'); urllib needs an absolute url, so resolve it
            # against the API base. Stop if it self-references
            # (end-of-list marker) or the page was empty (no progress).
            cand = urljoin(API, str(nlink))
            nxt = None if (cand == cur or not recs) else cand
        elif len(recs) == page:
            offset += page
            nxt = (f"{API}?field_label={field}&_format=json"
                   f"&_limit={page}&_offset={offset}")
        else:
            nxt = None                                  # short page = done
        pno += 1
        if nxt:
            time.sleep(sleep)
    jl = os.path.join(outdir, f"{field}.jsonl")
    with open(jl, "w") as fh:
        for r in recs_all:
            fh.write(json.dumps(r) + "\n")
    complete = (total is None) or (collected == total)
    print(f"  → {jl}: {collected} records; "
          f"{'COMPLETE ✓' if complete else f'INCOMPLETE ✗ (expected {total})'}")
    return dict(field=field, collected=collected, api_total=total,
                complete=complete, jsonl=os.path.basename(jl))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--field", action="append",
                    help="repeatable; default both Q(i) and Q(√−3)")
    ap.add_argument("--outdir", default="cohh_data")
    ap.add_argument("--sleep", type=float, default=1.0,
                    help="seconds between pages (be kind to the server)")
    ap.add_argument("--limit", type=int, default=100, help="page size")
    ap.add_argument("--probe", action="store_true",
                    help="page-1 diagnostic only; confirm contract first")
    a = ap.parse_args()
    fields = a.field or FIELDS

    if a.probe:
        for f in fields:
            probe(f)
        return

    os.makedirs(a.outdir, exist_ok=True)
    man = {"query": "bmf_forms full record, no _fields/dimension remote "
                     "filter (filter locally)", "fields": {}}
    for f in fields:
        print(f"\n=== full pull: {f} ===")
        man["fields"][f] = pull(f, a.outdir, a.limit, a.sleep)
    man["all_complete"] = all(v["complete"] for v in man["fields"].values())
    man["fetched_at"] = time.strftime("%Y-%m-%dT%H:%M:%S")
    with open(os.path.join(a.outdir, "manifest.json"), "w") as fh:
        json.dump(man, fh, indent=2)
    print(f"\nmanifest: {os.path.join(a.outdir,'manifest.json')}  "
          f"all_complete={man['all_complete']}")
    if not man["all_complete"]:
        sys.exit("INCOMPLETE — do not treat as the full set; rerun "
                 "(resumable) until all_complete=true.")


if __name__ == "__main__":
    main()
