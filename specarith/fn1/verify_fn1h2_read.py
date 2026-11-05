# SPDX-License-Identifier: AGPL-3.0-or-later
"""Check the FN1-h2 sealed read record in results/h2/read/ (written after the read; it decides nothing).

Checks, independently of fn1h2_read.py (pure Python, sealed constants restated from FN1H2_SEAL.md):
1. READ1.json and READ2.json are byte-identical, their sha256 is the one in status.txt twice, cmp.txt is empty, and
   status.txt has "read1 rc 0", "read2 rc 0" and "cmp 0".
2. The read used the sealed pins (e591fc3f…), mode "read", X = X* = 2·10¹⁰, K_P = 57,801 / 7,873 / 2,906.
3. The h = 1 references in the record equal the committed D2 (b) file results/h2/FN1H2_REFS.json exactly.
4. The field sets are as sealed (18 h = 2 fields; the primary nine), and each h = 2 C equals log|D| (w = 2).
5. The primary (§4): OLS of the nine h = 1 R(0.55) on C_F = log(|D|(w/2)²); s = mean over the primary nine of
   (R − a − b·C)/b; the recorded line and s agree to 1e-12; the verdict follows from s under the sealed rule
   (CONDUCTOR iff s > −0.4·log 4, L-VALUE iff s < −0.6·log 4, else INCONCLUSIVE; VOID if b ≤ 0); the recorded cuts
   are those values.
6. Descriptive arms carry no verdict: only the β 0.55 primary has a "verdict" key; K0's reading is descriptive; the
   matched-N s recomputes from its own references.
7. The report FN1H2_READ_REPORT.md carries the read sha256 and the verdict.
Exits 0 iff all hold.
    python verify_fn1h2_read.py [READ_DIR [REPORT]]      (defaults: results/h2/read, FN1H2_READ_REPORT.md)
"""
import hashlib, json, math, os, sys

H = os.path.dirname(os.path.abspath(__file__))
D = sys.argv[1] if len(sys.argv) > 1 else os.path.join(H, "results", "h2", "read")
REPORT = sys.argv[2] if len(sys.argv) > 2 else os.path.join(H, "FN1H2_READ_REPORT.md")
PINS = "e591fc3f370880be8b6fd780d6fc3d533989dbe1d53d8f3e49dcec2fa90bce96"
H2 = [-15, -20, -24, -35, -40, -51, -52, -88, -91, -115, -123, -148, -187, -232, -235, -267, -403, -427]
PRIMARY = [-35, -40, -51, -52, -88, -91, -115, -123, -148]
H1 = {"-7": (-7, 2), "-8": (-8, 2), "-11": (-11, 2), "zi": (-4, 4), "-19": (-19, 2), "zw": (-3, 6), "-43": (-43, 2),
      "-67": (-67, 2), "-163": (-163, 2)}
CUT_C, CUT_L = -0.4 * math.log(4), -0.6 * math.log(4)
bad = []


def need(cond, msg):
    print(("ok   " if cond else "FAIL ") + msg)
    if not cond:
        bad.append(msg)


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def ols(xs, ys):
    n = len(xs); mx = sum(xs) / n; my = sum(ys) / n
    b = sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / sum((x - mx) ** 2 for x in xs)
    return my - b * mx, b


def label(s, b):
    if b <= 0:
        return "VOID (reference slope <= 0)"
    return "CONDUCTOR" if s > CUT_C else ("L-VALUE" if s < CUT_L else "INCONCLUSIVE")


r1, r2 = os.path.join(D, "READ1.json"), os.path.join(D, "READ2.json")
b1, b2 = open(r1, "rb").read(), open(r2, "rb").read()
need(b1 == b2, "READ1.json and READ2.json byte-identical")
s256 = sha(r1)
status = open(os.path.join(D, "status.txt")).read().splitlines()
need(os.path.getsize(os.path.join(D, "cmp.txt")) == 0, "cmp.txt empty")
for ln in ("read1 rc 0", "read2 rc 0", "cmp 0"):
    need(ln in status, f"status.txt has '{ln}'")
need(sum(1 for ln in status if ln.startswith(s256 + " ")) == 2, f"status.txt sha256 lines match the local reads "
                                                                f"({s256[:8]})")

d = json.loads(b1)
need(d["pins_sha256"] == PINS, "pins_sha256 is the sealed fn1h2_pins.json")
need(d["mode"] == "read" and d["X"] == d["X_star"] == 20_000_000_000, "mode read at X* = 2e10")
need(d["K_P"] == {"0.55": 57801, "0.45": 7873, "0.4": 2906}, "K_P as sealed")

committed = json.load(open(os.path.join(H, "results", "h2", "FN1H2_REFS.json")))["h1_refs"]
need(d["h1_refs"] == committed, "h = 1 references equal the committed D2 (b) file exactly")

need(sorted(int(k) for k in d["h2"]) == sorted(H2), "h = 2 field set as sealed (18)")
need(sorted(int(k) for k, v in d["h2"].items() if v["primary"]) == sorted(PRIMARY), "primary nine as sealed")
need(all(abs(d["h2"][str(k)]["C"] - math.log(abs(k))) < 1e-12 for k in H2), "each h = 2 C equals log|D|")

C1 = {f: math.log(abs(D_) * (w / 2) ** 2) for f, (D_, w) in H1.items()}
a, b = ols([C1[f] for f in H1], [d["h1_refs"][f]["R"]["0.55"] for f in H1])
t55 = d["tests"]["0.55"]
need(abs(a - t55["line"][0]) < 1e-12 and abs(b - t55["line"][1]) < 1e-12,
     f"reference line recomputed (a {a:.6f}, b {b:.6f})")
s = sum((d["h2"][str(k)]["R"]["0.55"] - a - b * math.log(abs(k))) / b for k in PRIMARY) / len(PRIMARY)
need(abs(s - t55["s"]) < 1e-12 and abs(s - d["primary"]["s"]) < 1e-12, f"primary s recomputed ({s:.6f})")
need(abs(d["primary"]["cuts"][0] - CUT_C) < 1e-15 and abs(d["primary"]["cuts"][1] - CUT_L) < 1e-15,
     "recorded cuts are -0.4 and -0.6 of log 4")
v = label(s, b)
need(t55["verdict"] == v and d["primary"]["verdict"] == v, f"primary verdict {d['primary']['verdict']!r} follows "
                                                            f"from s {s:.4f} and b {b:.4f}")

need(all("verdict" not in d["tests"][x] for x in ("0.45", "0.4")), "beta 0.45 / 0.40 carry no verdict")
need(t55["K0"]["reading"].startswith("descriptive") and "verdict" not in t55["K0"], "K0 descriptive, no verdict")
mN = d["matched_N"]
am, bm = ols([C1[f] for f in H1], [mN["refs"][f]["R"]["0.55"] for f in H1])
sm = sum((d["h2"][str(k)]["R"]["0.55"] - am - bm * math.log(abs(k))) / bm for k in PRIMARY) / len(PRIMARY)
need(abs(sm - mN["s"]) < 1e-12, f"matched-N s recomputed ({sm:.6f}; descriptive)")

rep = open(REPORT, encoding="utf-8").read()
need(s256 in rep, "report carries the read sha256")
need(f"**{v}**" in rep, f"report carries the verdict **{v}**")
print("READ RECORD", "OK" if not bad else f"BAD ({len(bad)})")
sys.exit(0 if not bad else 1)
