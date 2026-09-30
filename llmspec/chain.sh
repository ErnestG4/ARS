#!/bin/bash
# start queue $2 once the process $1 (a previous queue.sh) has exited
cd "$(dirname "$0")"
while kill -0 "$1" 2>/dev/null; do sleep 15; done
exec ./queue.sh "$2"
