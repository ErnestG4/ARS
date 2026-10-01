#!/bin/bash
# Watchdog (after three WSL crashes on 2026-09-25 = Windows commit exhaustion: vmmemWSL 20.6 GB while Windows
# apps held ~30 GB of the 49.7 GB commit limit). Logs WSL RAM incl. page cache, GPU, C: free and the HOST's free
# commit every 20 s; writes llmspec/STOP (jobs exit cleanly, resumable) if host commit free < 5 GB.
cd "$(dirname "$0")"
while true; do
  host=$(timeout 15 powershell.exe -NoProfile -Command '$o=Get-CimInstance Win32_OperatingSystem; "{0:N1}" -f ($o.FreeVirtualMemory/1MB)' 2>/dev/null | tr -d '\r ')
  echo "$(date +%T) $(free -m | awk '/Mem/{print "used="$3"M cache="$6"M avail="$7"M"}') gpu=$(nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits)M F_free=$(df -BG --output=avail /mnt/f | tail -1 | tr -d ' ') host_commit_free=${host}G"
  if [ -n "$host" ] && awk -v h="$host" 'BEGIN{exit !(h < 5.0)}'; then
    echo "$(date +%T) HOST COMMIT LOW (${host}G < 5G): writing STOP"; [ -e STOP ] || echo memwatch > STOP
  fi
  sleep 20
done
