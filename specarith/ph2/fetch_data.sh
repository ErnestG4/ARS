#!/usr/bin/env bash
# Phase 2 data acquisition (seal §3): sequential downloads, size check, hash check. Hashing only — no decoding before
# the seal. Platt files must match the md5 pinned in PH2_SEAL_2.1.md §3 (fails closed); Odlyzko zeros3/4/5 have no
# published checksum, so their sha256 is recorded at download for the seal JSON.
set -u
D=$(cd "$(dirname "$0")" && pwd)/data
cd "$D" || exit 1
fail=0
while read -r name md5; do
  url="https://beta.lmfdb.org/data/riemann-zeta-zeros/$name"
  # beta.lmfdb.org serves a JavaScript "human" gate (302 → gate.html) to scripted clients since at least 2026-10-07;
  # the files are fetched by hand in a browser from $url into data/platt/ and only VERIFIED here.
  if [ ! -s "platt/$name" ]; then echo "MISSING $name (fetch by hand: $url)"; fail=1; continue; fi
  got=$(md5sum "platt/$name" | cut -d' ' -f1)
  if [ "$got" = "$md5" ]; then echo "OK   $name md5 $got size $(stat -c %s "platt/$name")"
  else echo "FAIL $name md5 $got != pinned $md5"; fail=1; fi
done <<'EOF'
zeros_2546000.dat 5642999b13dc52270064a055b1b6b15f
zeros_19346000.dat 24dedbc917f3a006690026dd7cda930b
zeros_151646000.dat 242ca86d1691d1a93623b2f8ce2cbf33
zeros_1119746000.dat 8d01c4c244daf4751f3c251de53008af
zeros_8284946000.dat 8adc69731784c1958ca60d67686e98b4
zeros_30404246000.dat 95f2c89b2b4572e5529cd25a79e9def8
EOF
for z in zeros3 zeros4 zeros5; do
  if [ ! -s "odlyzko/$z" ]; then
    curl -sS --fail --retry 3 -o "odlyzko/$z.part" "https://www-users.cse.umn.edu/~odlyzko/zeta_tables/$z" && mv "odlyzko/$z.part" "odlyzko/$z"
  fi
  echo "REC  $z sha256 $(sha256sum "odlyzko/$z" | cut -d' ' -f1) size $(stat -c %s "odlyzko/$z")"
done
echo "DONE fail=$fail"
