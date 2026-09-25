#!/bin/bash
cd "$(dirname "$0")"
while kill -0 "$1" 2>/dev/null; do sleep 15; done
shift
exec ./supervise.sh "$@"
