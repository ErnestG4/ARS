"""A verdict is composed from arms with declared ROLES. Negation is not free.

WHY STRUCTURAL — THREE INSTANCES, AND THE THIRD IS THE DAMNING ONE
-------------------------------------------------------------------
A verdict lattice is an if/elif over booleans, so it looks like the safest code
in the file. It is where three findings have been mislabelled:

  1. `SURVIVES_EXTENSION` at 44.5% — keyed on ONE threshold at ONE value of N,
     while the series ran 5% -> 17% -> 45% -> 66%. The label contradicted the
     table printed directly above it. (Fixed at the statistic, in existence.py.)
  2. `NOT_DIFFERENTIATED` in brocot_above_horizon — H1 and H4 both fired (every
     above-horizon ratio has a positive gap; 79.2% beat audibly), but the label
     required H3, which asks whether the spread is EXPLAINED BY 1/q. A wrong
     guess about WHY was wired to read as an absence of WHAT.
  3. `PARENT_LABEL_DOES_NOT_HOLD` in brocot_above_horizon_parent — P1 and P2
     read 100.0% and 100.0%. The label was negative because P4, an injectivity
     arm, missed. **Committed one file after instance 2's amendment was
     written, by the author of that amendment.**

Instance 3 is the whole argument for this module. Knowing the rule, having just
written the rule down, in the next file, did not prevent the rule being broken.
That is the third time this repo has measured what a rule-in-prose is worth.

    A RULE YOU CONSULT IS A RULE YOU'LL SKIP.

THE FIX: ARMS CARRY ROLES, AND ONLY ONE ROLE CAN NEGATE
--------------------------------------------------------
    PREMISE     definitional; if it fails nothing else is readable
    EXISTENCE   does the thing hold at all -- THE ONLY ROLE THAT SETS THE HEAD
    MECHANISM   is it explained by the proposed cause -- qualifies, never negates
    RESOLUTION  how finely does it resolve / how complete -- qualifies only

`compose()` builds the label from the arms. There is no argument you can pass
that makes a MECHANISM or RESOLUTION miss produce a negative head, because the
head is a function of the EXISTENCE arms alone. The wrong lattice is not
discouraged here; it is unrepresentable.

THE MIRROR: A DISPOSITION MUST NOT STAND IN FOR A FINDING
-----------------------------------------------------------
The three instances above are a LABEL computed from the wrong arms. The same
defect runs in the other direction, and it was committed in this arc too:
reporting "the morph question is closed rather than parked" as though that were
the result. It is not. The result is L2 = 0.985x against a sealed bar of 3x.
"Closed" is a status compatible with either outcome — validated and the feature
reopens, or missed and the negative claim strengthens — so a reader who accepts
the status has learned nothing about which happened. It took being asked twice.

The two directions bracket one defect:

    a RESOLUTION miss must not negate an EXISTENCE result   (label from wrong arms)
    a DISPOSITION must not stand in for a FINDING           (label without its arms)

So the affordance: `cite()` renders a verdict together with the governing arm
values and their bars, and it is the form to quote. Quoting the head alone is
still possible — nothing can stop a sentence being typed — but the cheap path
now carries the numbers, which is the only fix that has ever held here.

    compose(...)["citation"]
    -> "NOT_LINEARISABLE_ON_ERB  [L2 0.985 vs >=3.0 MISSED; L4 0.43 vs >=2.0 MISSED]"

Inert arms are dropped from the composition with a note and never counted in a
tally -- `reachable.Bar` is the natural source of that flag.

WHAT THIS CANNOT DO — two limits, the second found the hard way.

(1) It cannot tell you that you assigned a role wrongly. Call an existence arm
    MECHANISM and it will qualify instead of negate. What it buys is that the
    role is written down beside the arm, in the seal, where a reader who
    disagrees can see the choice was made.

(2) IT CANNOT STOP THE HEAD'S NAME FROM PRESUMING A MECHANISM ARM'S CONCLUSION.
    `brocot_index_routing` sealed the positive head as
    COLUMN_IS_CONDITIONED_ON_ROUTING, composed correctly from two EXISTENCE
    arms that both fired — while the MECHANISM arm testing whether a routing
    CONVENTION exists came back at 50.0%, a coin. The composition obeyed every
    rule in this module and the resulting label still asserted the thing the
    data denied, because "conditioned on routing" is a string the author chose
    and the head is only ever a string.

    The guard covers the LOGIC of the label, not its SEMANTICS. The practical
    defence is `cite()`: the citation carries every governing arm's value, so a
    head that overreaches sits next to the number that contradicts it. That is
    weaker than unrepresentability and it is what is available.
"""

PREMISE = "PREMISE"
EXISTENCE = "EXISTENCE"
MECHANISM = "MECHANISM"
RESOLUTION = "RESOLUTION"
_ROLES = (PREMISE, EXISTENCE, MECHANISM, RESOLUTION)


class BadLattice(AssertionError):
    pass


class Arm:
    """One sealed arm: a name, a role, whether it fired, and whether it could.

    `value` and `thresh` are optional but strongly preferred: they are what
    makes `cite()` carry a finding rather than a disposition."""
    __slots__ = ("name", "role", "met", "inert", "note", "value", "thresh",
                 "direction", "claim")

    def __init__(self, name, role, met, inert=False, note="",
                 value=None, thresh=None, direction="ge", claim=""):
        if role not in _ROLES:
            raise BadLattice(
                f"'{name}': role must be one of {_ROLES}, not {role!r}. There is "
                "no default — which role an arm plays is the choice that decides "
                "whether it may negate, and it has been got wrong three times.")
        self.name, self.role = name, role
        self.met, self.inert, self.note = bool(met), bool(inert), note
        self.value, self.thresh, self.direction = value, thresh, direction
        self.claim = claim

    def cite(self):
        """This arm as evidence: value against bar, not just MET/MISSED."""
        state = "INERT" if self.inert else "MET" if self.met else "MISSED"
        if self.value is None or self.thresh is None:
            return f"{self.name} {state}"
        op = ">=" if self.direction == "ge" else "<="
        v = f"{self.value:.4g}" if isinstance(self.value, float) else self.value
        t = f"{self.thresh:.4g}" if isinstance(self.thresh, float) else self.thresh
        out = f"{self.name} {v} vs {op}{t} {state}"
        return out + (f' — "{self.claim}"' if self.claim else "")

    @classmethod
    def from_bar(cls, score, role, note="", claim=""):
        """Build from a `reachable.Bar.score()` dict, inheriting its inertness."""
        # An arm whose named rival also clears the bar is INERT: it separates
        # nothing, so it is dropped rather than counted as a pass. See
        # reachable.Bar's rival note.
        dead = score.get("out_of_range", False)
        if score.get("discriminating") is False:
            dead = True
            note = (note + "; " if note else "") + (
                f"rival {score.get('rival')!r} also clears this bar "
                f"({score.get('rival_value')})")
        return cls(score["name"], role, score["met"],
                   inert=dead, note=note,
                   value=score.get("value"), thresh=score.get("thresh"),
                   direction=score.get("direction", "ge"), claim=claim)

    def __repr__(self):
        state = ("INERT" if self.inert else "MET" if self.met else "MISSED")
        return f"Arm({self.name!r}, {self.role}, {state})"


def compose(arms, holds, fails, sep="_"):
    """Compose a verdict. `holds`/`fails` are the two EXISTENCE head labels.

    Returns dict(label, head, qualifiers, dropped, arms). The head is a
    function of the EXISTENCE arms ALONE — by construction, not by convention.
    """
    arms = list(arms)
    if not any(a.role == EXISTENCE for a in arms):
        raise BadLattice(
            "no EXISTENCE arm. A verdict about whether something holds needs an "
            "arm that tests whether it holds; a lattice built only from "
            "MECHANISM and RESOLUTION arms will negate on the wrong evidence, "
            "which is exactly instances 2 and 3.")

    dropped = [a for a in arms if a.inert]
    live = [a for a in arms if not a.inert]

    bad_premise = [a for a in live if a.role == PREMISE and not a.met]
    if bad_premise:
        return dict(label=f"INVALID{sep}{bad_premise[0].name}",
                    head="INVALID", qualifiers=[],
                    dropped=[a.name for a in dropped],
                    unread=[a.name for a in live if a.role != PREMISE],
                    arms=[repr(a) for a in arms])

    ex = [a for a in live if a.role == EXISTENCE]
    if not ex:
        raise BadLattice("every EXISTENCE arm was inert — nothing was tested")
    head = holds if all(a.met for a in ex) else fails

    quals = []
    for a in live:
        if a.role == MECHANISM:
            quals.append(("AND_BY" if a.met else "BUT_NOT_BY") + sep + a.name)
        elif a.role == RESOLUTION:
            quals.append(("AT" if a.met else "COARSELY_AT") + sep + a.name)

    label = sep.join([head] + quals) if quals else head
    # the citation is the quotable form: a head is a disposition, a head with
    # its governing arms is a finding. Governing = the arms that decided it.
    gov = [a for a in live if a.role == EXISTENCE and not a.met] or \
          [a for a in live if a.role == EXISTENCE]
    gov = gov + [a for a in live if a.role in (MECHANISM, RESOLUTION) and not a.met]
    citation = f"{head}  [" + "; ".join(a.cite() for a in gov) + "]"
    return dict(label=label, head=head, qualifiers=quals, citation=citation,
                dropped=[a.name for a in dropped], unread=[],
                arms=[repr(a) for a in arms])


if __name__ == "__main__":
    print("--- instance 2 · the real NOT_DIFFERENTIATED arms, re-composed ---")
    v = compose([Arm("gap_positive_above", EXISTENCE, True),
                 Arm("audible_beating", EXISTENCE, True),
                 Arm("1/q", MECHANISM, False),
                 Arm("span", RESOLUTION, False, inert=True,
                     note="bar 10 over a reachable ceiling of 5.72")],
                holds="DIFFERENTIATED", fails="NOT_DIFFERENTIATED")
    print(f"    sealed lattice said : NOT_DIFFERENTIATED")
    print(f"    composed            : {v['label']}")
    print(f"    inert arm dropped   : {v['dropped']}")

    print("\n--- instance 3 · the real PARENT arms, re-composed ---")
    v3 = compose([Arm("parent_below_horizon", EXISTENCE, True),
                  Arm("brocot_ancestor", EXISTENCE, True),
                  Arm("partition_nondegenerate", RESOLUTION, True),
                  Arm("injective_label", RESOLUTION, False)],
                 holds="HEARD_AS_A_DETUNED_PARENT",
                 fails="PARENT_LABEL_DOES_NOT_HOLD")
    print(f"    sealed lattice said : PARENT_LABEL_DOES_NOT_HOLD  (P1 = P2 = 100.0%)")
    print(f"    composed            : {v3['label']}")

    print("\n--- red path 0 · an EXISTENCE MISS MUST produce the negative head ---")
    # Until 2026-08-25 nothing asserted this. Adversarial review replaced the
    # head computation with `head = holds` -- so compose() could never return
    # the negative label, the exact laundering this module exists to prevent --
    # and the board stayed green, 8/8. Every red path tested the positive
    # direction. A guard against laundering whose own negation path was
    # unfalsifiable.
    neg0 = compose([Arm("holds", EXISTENCE, False)], holds="H", fails="N")
    if neg0["head"] != "N":
        raise SystemExit("RED PATH FAILED: an EXISTENCE miss did not negate")
    mixed = compose([Arm("a", EXISTENCE, True), Arm("b", EXISTENCE, False)],
                    holds="H", fails="N")
    if mixed["head"] != "N":
        raise SystemExit("RED PATH FAILED: one EXISTENCE miss among two did "
                         "not negate — the head must require ALL of them")
    print(f"    one arm missed -> {neg0['head']};  "
          f"one of two missed -> {mixed['head']}")

    print("\n--- red path 1 · a MECHANISM miss cannot produce a negative head ---")
    neg = compose([Arm("holds", EXISTENCE, True), Arm("cause", MECHANISM, False)],
                  holds="HOLDS", fails="DOES_NOT_HOLD")
    if neg["head"] != "HOLDS":
        raise SystemExit("RED PATH FAILED: a mechanism miss negated the head")
    print(f"    {neg['label']}  — head stays {neg['head']}, as it must")

    print("\n--- red path 2 · a lattice with no EXISTENCE arm ---")
    try:
        compose([Arm("cause", MECHANISM, True), Arm("fineness", RESOLUTION, True)],
                holds="HOLDS", fails="DOES_NOT_HOLD")
        raise SystemExit("RED PATH FAILED: a lattice with nothing to negate on")
    except BadLattice as e:
        print(f"    refused: {str(e)[:96]}...")

    print("\n--- red path 3 · an undeclared role ---")
    try:
        Arm("x", "SUPPORTING", True)
        raise SystemExit("RED PATH FAILED: an undeclared role was accepted")
    except BadLattice as e:
        print(f"    refused: {str(e)[:88]}...")

    print("\n--- red path 4 · a failed premise makes the rest unreadable ---")
    pv = compose([Arm("gap_zero_below_horizon", PREMISE, False),
                  Arm("holds", EXISTENCE, True), Arm("cause", MECHANISM, True)],
                 holds="HOLDS", fails="DOES_NOT_HOLD")
    print(f"    {pv['label']}   unread: {pv['unread']}")
    if pv["head"] != "INVALID":
        raise SystemExit("RED PATH FAILED: a broken premise was read past")

    print("\n--- the mirror · the real ERB linearisation, cited not dispositioned ---")
    erb = compose([Arm("smoothness", EXISTENCE, False, value=0.985, thresh=3.0),
                   Arm("worst_step", RESOLUTION, False, value=0.43, thresh=2.0)],
                  holds="LINEARISABLE_ON_ERB", fails="NOT_LINEARISABLE_ON_ERB")
    print(f"    disposition : {erb['head']}          <- says nothing about which way")
    print(f"    finding     : {erb['citation']}")
    if erb["citation"] == erb["head"]:
        raise SystemExit("RED PATH FAILED: the citation carried no arm values")

    print("\n--- (1b) · a head contradicting its own existence arm's claim ---")
    bad = compose([Arm("top-1 reachable", EXISTENCE, True, value=0.423,
                       thresh=0.5, direction="le",
                       claim="fewer than half of top-1 suggestions can "
                             "coincide at all")],
                  holds="RANKING_DOES_NOT_DEPEND_ON_EXACT_COINCIDENCE",
                  fails="RANKING_PARTLY_DEPENDS_ON_EXACT_COINCIDENCE")
    print(f"    {bad['citation']}")
    print("    the head and the claim cannot both be right — legible on sight")

    print("\n--- red path 5 · an arm with no value still cites honestly ---")
    bare = compose([Arm("holds", EXISTENCE, True)], holds="H", fails="N")
    print(f"    {bare['citation']}   (no numbers claimed where none were given)")

    print("\n--- green path · everything fires ---")
    print("   ", compose([Arm("holds", EXISTENCE, True), Arm("cause", MECHANISM, True),
                          Arm("fine", RESOLUTION, True)],
                         holds="HOLDS", fails="DOES_NOT_HOLD")["label"])

    print("\nVERDICTLATTICE_SELF_TEST_PASS — an EXISTENCE miss negates and a "
          "MECHANISM miss cannot, the head is a function of the EXISTENCE arms "
          "alone, a roleless arm is refused, both historical mislabellings "
          "re-compose to what their own tables said, and the quotable form "
          "carries its arms' values.")
