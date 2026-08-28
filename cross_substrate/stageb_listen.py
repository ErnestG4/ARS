"""Stage B listening runner: play a trial, take an answer, save, repeat.

Deliberately minimal and deliberately blind. It plays trial_NNNN.wav, asks which
interval was the odd one, writes your answer to responses.csv, and moves on. It
never tells you whether you were right -- feedback would let you learn the odd
position's distribution and would contaminate the merge arm, which is the arm
carrying the negative prediction.

    python3 cross_substrate/stageb_listen.py            # start or resume
    python3 cross_substrate/stageb_listen.py --count 40 # a shorter sitting
    python3 cross_substrate/stageb_listen.py --player "aplay -q"

Answers: 1, 2, 3    r = replay    s = skip (leaves it blank)    q = save and quit
Partial data is fine. The scorer reports per-arm n and refuses to read a merge
null that has not cleared its gate.
"""
import argparse
import csv
import os
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
T = os.path.join(HERE, "stageb_trials")
SHEET = os.path.join(T, "responses.csv")


def pick_player():
    for cmd in ("aplay -q", "paplay", "ffplay -nodisp -autoexit -loglevel quiet",
                "play -q"):
        if shutil.which(cmd.split()[0]):
            return cmd
    return None


def load():
    rows = []
    with open(SHEET) as fh:
        for r in csv.DictReader(fh):
            rows.append(r)
    return rows


def save(rows):
    tmp = SHEET + ".tmp"
    with open(tmp, "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["trial", "file", "odd"])
        for r in rows:
            w.writerow([r["trial"], r["file"], r["odd"]])
    os.replace(tmp, SHEET)


ap = argparse.ArgumentParser()
ap.add_argument("--count", type=int, default=0,
                help="stop after this many answered this sitting (0 = all)")
ap.add_argument("--player", default=None, help='e.g. "aplay -q"')
a = ap.parse_args()

player = a.player or pick_player()
if not player:
    print("No audio player found (looked for aplay, paplay, ffplay, play).")
    print("Pass one with --player, or copy stageb_trials/ to Windows and play")
    print("there, filling responses.csv by hand.")
    sys.exit(1)

rows = load()
todo = [r for r in rows if not (r["odd"] or "").strip()]
done = len(rows) - len(todo)
print(f"Stage B — 3-interval odd-one-out.  {done}/{len(rows)} answered, "
      f"{len(todo)} to go.")
print(f"player: {player}")
print("Each trial is three sounds. Two are identical; one is not. Which one?")
print("Answer 1/2/3.   r = replay   s = skip   q = save and quit.\n")

n = 0
try:
    for r in todo:
        if a.count and n >= a.count:
            break
        path = os.path.join(T, r["file"])
        while True:
            subprocess.run(player.split() + [path], check=False)
            ans = input(f"  [{done + n + 1}/{len(rows)}]  odd interval? ").strip().lower()
            if ans == "r":
                continue
            if ans == "q":
                raise KeyboardInterrupt
            if ans == "s":
                break
            if ans in ("1", "2", "3"):
                r["odd"] = ans
                n += 1
                break
            print("    1, 2, 3, r, s or q.")
        save(rows)
except (KeyboardInterrupt, EOFError):
    print()
finally:
    save(rows)
    ans = sum(1 for r in rows if (r["odd"] or "").strip())
    print(f"\nsaved. {ans}/{len(rows)} answered ({n} this sitting).")
    print("score with:  python3 cross_substrate/brocot_stageb_score.py")
