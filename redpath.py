"""Non-vacuity floors for red-path probes.

WHY: on 2026-08-21 a red-path probe for `verify_seal_order.py` was run from /tmp,
where its ROOT resolved to /tmp, so it found ZERO pairs, exercised nothing, and
exited 0. That is the ASSERT_MIN_BLOBS extractor bug wearing a different shirt --
a check that exercises nothing and reports clean. The same antibody applies:

    A RED-PATH MUST ASSERT ITS OWN REACH.

A probe that misses its planted target should be a LOUD ERROR, not a quiet
0/0/0. Otherwise the red-path is itself a one-sided test of the guard: it can
pass vacuously, and this arc has now twice measured what such tests are worth.

    with redpath("seal-order INVERTED", expect_min=1) as rp:
        rp.observed(n_inverted)          # raises if < 1

HOW TO PLANT expect_min, AND WHAT TO DO WHEN IT FIRES
------------------------------------------------------
    OPTIMISTIC FLOORS FAIL LOUD. PESSIMISTIC FLOORS PASS VACUOUS.

Plant the number you would want the probe to reach if the design were as strong
as you intend it, not the number you expect it to scrape past. A floor set at
what a run is likely to produce has stopped policing anything before it is ever
evaluated.

**When it fires, raise the POWER, never lower the floor.** On 2026-08-25 it
fired three times in one session -- 3248/4000, 5456/20000, 214/300 -- and each
time the fix was a wider population, a longer base, another horizon, with the
amendment recorded BEFORE the verdict was read. Lowering the bar to what the
run produced is recalibrating the probe against the data it polices; doing it at
planting time is the same defect as doing it at scoring time, one step earlier
and harder to see.

A high fire rate is therefore the CORRECT equilibrium for this guard, not a
nuisance to tune out. If this floor stops firing, suspect that expectations
have been planted to be met rather than to be informative.
"""
import sys

# NOTE 2026-08-25 (adversarial review): `expect_exit` was accepted by __init__
# and used by nothing -- a parameter that looked like a guard and guarded
# nothing. It is now enforced in __exit__; `assert_exit` remains for callers
# that check an exit code without a reach floor.


class VacuousRedPath(AssertionError):
    pass


class redpath:
    def __init__(self, what, expect_min=1, expect_exit=None):
        self.what, self.expect_min, self.expect_exit = what, expect_min, expect_exit
        self._n = None
        self._exit = None

    def __enter__(self):
        return self

    def observed(self, n, exit_code=None):
        self._n = int(n)
        if exit_code is not None:
            self._exit = int(exit_code)
        return self._n

    def __exit__(self, exc_type, exc, tb):
        if exc_type is not None:
            return False
        if self._n is None:
            raise VacuousRedPath(
                f"red-path '{self.what}' never reported what it exercised — "
                "a probe that does not count its own reach cannot distinguish "
                "'the guard failed to fire' from 'the probe never ran'")
        if self._n < self.expect_min:
            raise VacuousRedPath(
                f"VACUOUS RED-PATH: '{self.what}' exercised {self._n} case(s), "
                f"expected >= {self.expect_min}. The probe did not reach its "
                "planted target, so a clean exit here means NOTHING about the "
                "guard. Fix the probe before reading the guard's verdict.")
        if self.expect_exit is not None:
            if self._exit is None:
                raise VacuousRedPath(
                    f"red-path '{self.what}' declared expect_exit="
                    f"{self.expect_exit} and never reported one. Pass it to "
                    "observed(n, exit_code=...). A declared expectation that "
                    "nothing supplies is a guard that guards nothing — this "
                    "parameter was accepted and ignored until 2026-08-25.")
            if self._exit != self.expect_exit:
                raise VacuousRedPath(
                    f"red-path '{self.what}' expected exit "
                    f"{self.expect_exit}, observed {self._exit}")
        return False


def assert_exit(claimed, actual, what="probe"):
    """Guard the OTHER half: the exit code you claim vs the one you got."""
    if int(claimed) != int(actual):
        raise VacuousRedPath(
            f"{what}: claimed exit {claimed}, observed {actual} — the claim "
            "contradicts the observation. This is the narration failure of "
            "2026-08-21, where a commit message asserted 'exits 1' with "
            "'exit=0 (expect 1)' printed on screen.")
    return actual


if __name__ == "__main__":
    print("--- the probe that started this: reach below the planted floor ---")
    try:
        with redpath("seal-order pairs", expect_min=1) as rp:
            rp.observed(0)
        raise SystemExit("RED PATH FAILED: a zero-reach probe exited clean")
    except VacuousRedPath as e:
        print(f"    raised: {str(e)[:88]}...")

    print("\n--- a probe that never counts its own reach ---")
    try:
        with redpath("silent probe", expect_min=1):
            pass
        raise SystemExit("RED PATH FAILED: a probe that counted nothing passed")
    except VacuousRedPath as e:
        print(f"    raised: {str(e)[:88]}...")

    print("\n--- expect_exit, which was accepted and ignored until 2026-08-25 ---")
    try:
        with redpath("probe", expect_min=1, expect_exit=1) as rp:
            rp.observed(5)
        raise SystemExit("RED PATH FAILED: a declared expect_exit went unchecked")
    except VacuousRedPath as e:
        print(f"    unsupplied exit raised: {str(e)[:76]}...")
    try:
        with redpath("probe", expect_min=1, expect_exit=1) as rp:
            rp.observed(5, exit_code=0)
        raise SystemExit("RED PATH FAILED: a wrong exit code was accepted")
    except VacuousRedPath as e:
        print(f"    wrong exit raised:      {str(e)[:76]}...")

    print("\n--- green path ---")
    with redpath("probe", expect_min=3, expect_exit=1) as rp:
        rp.observed(7, exit_code=1)
    print("    reach 7 >= 3 and exit 1 == 1: clean")

    print("\nREDPATH_SELF_TEST_PASS — a probe below its floor, a probe that "
          "counts nothing, and a declared-but-unsupplied or wrong exit code "
          "are all refused.")
