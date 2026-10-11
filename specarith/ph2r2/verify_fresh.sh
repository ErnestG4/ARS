#!/usr/bin/env bash
# Verify the five fresh Platt files against the md5s pinned in FRESH_PLATT_PINS.md (commit 697ddbb3). Hashing only —
# nothing is decoded before the R₂ seal. Writes results/logs/fresh_platt_md5_verified.log; exit 1 on any mismatch.
set -u
cd "$(dirname "$0")"
mkdir -p results/logs
LOG=results/logs/fresh_platt_md5_verified.log
fail=0
{
  date -Is
  while read -r f m; do
    got=$(md5sum "data/platt/$f" 2>/dev/null | cut -d' ' -f1)
    if [ "$got" = "$m" ]; then echo "OK   $f $got $(stat -c %s "data/platt/$f")"; else echo "FAIL $f got '$got' pinned $m"; fail=1; fi
  done <<'EOF'
zeros_6746000.dat 7da68bfe58799d9ad96d6e47f3c3fb3a
zeros_55046000.dat a702b364cf5f262b9f36963c58e12599
zeros_412046000.dat b38965a1e947a9d5ebb69b4fd70bcde5
zeros_3047546000.dat 75781990d6be699da0e7a80d5e184be3
zeros_22522946000.dat 7b9726648af12152eda3ec9cde888210
EOF
  echo "DONE fail=$fail"
} > "$LOG"
cat "$LOG"
exit $fail
