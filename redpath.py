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


class VacuousRedPath(AssertionError):
    pass


class redpath:
    def __init__(self, what, expect_min=1, expect_exit=None):
        self.what, self.expect_min, self.expect_exit = what, expect_min, expect_exit
        self._n = None

    def __enter__(self):
        return self

    def observed(self, n):
        self._n = int(n)
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
