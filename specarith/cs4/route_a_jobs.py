"""Route (a) term jobs across machines (2026-10-12; Will: CPU on spot, this machine (6 workers) and the second box).

Same code path as route_a_zeta.run (RA._run_one: FastZeta with the long-double phase reduction), so every result is
from the one engine the 240 finished jobs used. This file is separate from route_a_zeta.py on purpose: route_a_zeta is
in ratios_t5's checkpoint code hash, and editing it would invalidate the running T₅ checkpoints.

Each machine gets a STATIC, DISJOINT job list (`split`), so no job is computed twice. A pool keeps up to P jobs
running; on spot it also takes over from the legacy 40-chunk run without losing work: each legacy chunk worker is
stopped (by PID) right after it writes its current job, and its slot then goes to the pool.

  python route_a_jobs.py split OUT W_SPOT W_LOCAL W_CHAR     → OUT/jobs_{spot,local,char}.txt (cost-weighted)
  python route_a_jobs.py pool OUT P JOBFILE [legacy]         run the list (legacy: retire spot's chunk workers)
  python route_a_jobs.py one OUT I                           one job → OUT/terms_cj{III}.jsonl
"""
import glob
import json
import os
import signal
import subprocess
import sys
import time

import route_a_zeta as RA

HERE = os.path.dirname(os.path.abspath(__file__))


def done_keys(out):
    keys = set()
    for fn in glob.glob(os.path.join(out, "terms_c*.jsonl")):
        for line in open(fn):
            try:
                r = json.loads(line)
            except ValueError:
                continue
            keys.add((r["file"], r["which"], r["pmax"], r["m"], r["s"]))
    return keys


def cost(job):
    """Relative cost: T₄ points × primes, small where T₃/T₄ are skipped (s ≤ 0.45)."""
    f, which, pm, m, s = job
    primes = {300_000: 25997, 1_000_000: 78498}[pm]
    pts = m * (m + 2)
    return pts * primes * (1.0 if s > 0.45 else 0.05)


def legacy_current(out):
    """The job each legacy chunk worker is on now: the first not-done job of its chunk (chunk c = jobs i ≡ c mod 40)."""
    J = RA.jobs()
    done = done_keys(out)
    cur = {}
    for c in range(40):
        rem = [i for i in range(len(J)) if i % 40 == c and J[i] not in done]
        if rem:
            cur[c] = rem[0]
    return cur


def split(out, w_spot, w_local, w_char):
    J = RA.jobs()
    done = done_keys(out)
    inprog = set(legacy_current(out).values())               # stay with spot's legacy workers
    todo = [i for i in range(len(J)) if J[i] not in done and i not in inprog]
    todo.sort(key=lambda i: -cost(J[i]))                     # longest first (greedy balance)
    caps = {"spot": float(w_spot), "local": float(w_local), "char": float(w_char)}
    load = {k: 0.0 for k in caps}
    lists = {k: [] for k in caps}
    for i in todo:
        k = min(caps, key=lambda k: (load[k] + cost(J[i])) / caps[k])
        lists[k].append(i)
        load[k] += cost(J[i])
    for k, v in lists.items():
        open(os.path.join(out, f"jobs_{k}.txt"), "w").write("\n".join(map(str, v)) + "\n")
        print(k, len(v), "jobs, relative load %.3g, per capacity %.3g" % (load[k], load[k] / caps[k]))
    print("in progress on spot's legacy workers:", sorted(inprog))


def one(out, i):
    J = RA.jobs()
    if J[i] in done_keys(out):
        return
    t0 = time.time()
    r = RA._run_one(J[i])
    r["secs"] = time.time() - t0
    r["host"] = os.uname().nodename
    with open(os.path.join(out, f"terms_cj{i:03d}.jsonl"), "a") as fh:
        fh.write(json.dumps(r) + "\n")
        fh.flush()
        os.fsync(fh.fileno())


def _legacy_workers():
    """{chunk: pid} of running `route_a_zeta.py run c 40` processes (python, not the sh wrapper)."""
    out = {}
    for d in os.listdir("/proc"):
        if not d.isdigit():
            continue
        try:
            cmd = open(f"/proc/{d}/cmdline", "rb").read().split(b"\0")
        except OSError:
            continue
        cmd = [c.decode(errors="replace") for c in cmd if c]
        if len(cmd) >= 5 and cmd[0].endswith("python") and cmd[1] == "route_a_zeta.py" and cmd[2] == "run" and cmd[4] == "40":
            out[int(cmd[3])] = int(d)
    return out


def _lines(out, c):
    fn = os.path.join(out, f"terms_c{c:02d}.jsonl")
    return sum(1 for _ in open(fn)) if os.path.exists(fn) else 0


def pool(out, P, jobfile, legacy=False):
    queue = [int(x) for x in open(jobfile).read().split()]
    J = RA.jobs()
    py = sys.executable
    env = dict(os.environ, OMP_NUM_THREADS="1", OPENBLAS_NUM_THREADS="1", MKL_NUM_THREADS="1",
               CS4_CHUNK=os.environ.get("CS4_CHUNK", "32"))
    os.makedirs(os.path.join(out, "logs"), exist_ok=True)
    base = {}
    if legacy:
        for c, pid in _legacy_workers().items():
            base[c] = (pid, _lines(out, c))
    kids = {}
    log = open(os.path.join(out, "logs", f"pool_{os.uname().nodename}.log"), "a")
    print(f"{time.strftime('%F %T')} pool start: {len(queue)} jobs, P = {P}, legacy workers {len(base)}", file=log, flush=True)
    while True:
        # retire legacy chunk workers once they have written their current job
        for c, (pid, n0) in list(base.items()):
            alive = os.path.exists(f"/proc/{pid}")
            if alive and _lines(out, c) > n0:
                os.kill(pid, signal.SIGTERM)
                print(f"{time.strftime('%F %T')} legacy chunk {c} (pid {pid}) finished its job; retired", file=log, flush=True)
                alive = False
            if not alive:
                del base[c]
        for i, pr in list(kids.items()):
            if pr.poll() is not None:
                print(f"{time.strftime('%F %T')} job {i} exit {pr.returncode}", file=log, flush=True)
                del kids[i]
        done = done_keys(out)
        queue = [i for i in queue if J[i] not in done and i not in kids]
        while queue and len(kids) + len(base) < P:
            i = queue.pop(0)
            lf = open(os.path.join(out, "logs", f"j{i:03d}.log"), "a")
            kids[i] = subprocess.Popen(["nice", "-n", "10", py, os.path.join(HERE, "route_a_jobs.py"), "one", out, str(i)],
                                       cwd=HERE, env=env, stdout=lf, stderr=subprocess.STDOUT)
            print(f"{time.strftime('%F %T')} job {i} started", file=log, flush=True)
        if not queue and not kids and not base:
            print(f"{time.strftime('%F %T')} pool done", file=log, flush=True)
            return
        time.sleep(20)


if __name__ == "__main__":
    a = sys.argv[1:]
    if a[0] == "split":
        split(a[1], *a[2:5])
    elif a[0] == "pool":
        pool(a[1], int(a[2]), a[3], legacy=len(a) > 4 and a[4] == "legacy")
    elif a[0] == "one":
        one(a[1], int(a[2]))
    else:
        raise SystemExit(__doc__)
