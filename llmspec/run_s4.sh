#!/usr/bin/env bash
# S4 main run then S4-sup, each under checkrun; a STOP file between them ends the chain. Resumable: re-run this script.
cd "$(dirname "$0")"
export OMP_NUM_THREADS=1
../checkrun.sh stage3_calib_v2.py 10 > stage3_calib_v2.checkrun.log 2>&1
[ -e STOP ] && exit 3
../checkrun.sh stage3_calib_v2_sup.py 10 > stage3_calib_v2_sup.checkrun.log 2>&1
