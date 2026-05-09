# Why this exists

ARS was built on a specific epistemological frame. The world is taken to be a
high-dimensional deterministic field structure, and all empirical observation
is understood as boundary readout — partial projection of the field onto a
measurement apparatus that has its own structural properties. Every
classification claim about a signal's universality class is therefore a joint
claim about the underlying field and the readout apparatus. Distinguishing
what the field is doing from what the apparatus is doing is the whole job.

The commitment is hard-determinist in that it doesn't require anything
indeterministic at the level of the field. The apparent stochasticity of
measurement outcomes can be fully accounted for by ignorance of initial
conditions and partial observability of high-dimensional deterministic
dynamics. Bohmian QM with eternalist commitment, superdeterministic
interpretations, and ordinary classical-but-chaotic regimes are all compatible
with this frame. The frame is also agnostic to which interpretation one
prefers — it commits only to "the field is what it is, the readout is what it
is, the work is to characterize each separately and not confuse them."

## The methodology this frame requires

Under this commitment, no single measurement can be interpreted as reading
the field. The apparatus has its own structure, and that structure can impose
features on the readout that look like field properties unless they are
explicitly ruled out. The methodology in METHODS.md is not generic
statistical practice applied rigorously — it is the specific discipline this
frame requires:

- The **calibrator zoo** characterises what the apparatus does to signals of
  known structure, before any unknown signal is read.
- The **extractor-invariance test** checks whether a classification depends on
  the readout method or survives across multiple structurally-distinct
  methods. If invariant, the property is field-attributable. If not, the
  apparatus is contributing.
- The **induction-on-noise falsification** asks whether the apparatus
  produces the same apparent finding when given input of equivalent
  statistical character that is known not to contain the structure being
  claimed. If yes, the finding is mechanism-induced. As of Phase 18 the
  protocol is multi-order: first-order matched noise (marginal +
  autocorrelation length + event count) is supplemented by three
  higher-order surrogates (phase-randomised, Hawkes-matched, cumulant-
  matched), each preserving a different higher-order property of the
  input. A finding has to survive surrogates that match what they
  match before it can be attributed to anything outside that match.
  See §7.ter.25 for the methodology and the per-finding survival
  pattern.

These three tools applied together make the boundary-readout problem
operationally tractable. None of them are novel — they are applied
integrations of standard practices — but their combination is what the frame
demands and what casual application of empirical methods often skips.

## What the LLM section actually demonstrates

The arithmetic-side validations work because the inputs are point processes
by construction. When ζ zeros, primes, or L-function zero sets enter the
pipeline, no continuous trace is being projected through a peak detector; the
boundary-readout problem is benign and the apparatus reads field structure
cleanly.

The LLM section does not work, and this is the negative result the frame
predicts. Continuous activation traces processed through prominence-thresholded
peak detection produce events whose spacing structure is determined by the
extractor's gap geometry rather than by the underlying signal. Three rounds
of artifact diagnosis (§7.ter.19, §7.ter.22, Finding F) successively peeled
back the layers of mechanism-induced structure that initially looked like
model dynamics. After each round, the next-most-tempting reading appeared and
was caught by the same induction-on-noise discipline applied at the next
resolution. The arc terminating cleanly rather than continuing forever is
what differentiates this from the failure modes the frame is designed to
identify.

## Implications for human + LLM collaborative work

The same systems frame applies to the joint human + LLM system that produced
this work. Both participants are pattern-recognition systems with strong
mutual coupling and limited intrinsic grounding. Without external coupling
capable of disagreeing with the joint internal state, the system reaches
high-coherence attractors that may or may not correspond to anything real.
Hallucination and crackpottery are the two faces of this failure — both are
the joint system collapsing to internal coherence in the absence of
sufficient external sync-pull. The mechanism is symmetric; only the starting
conditions differ. Hallucination tends to emerge when the LLM generates
plausible-but-fake structure that the human does not check; crackpottery
emerges when the human generates plausible-but-fake patterns that the LLM
does not push back on. The same architecture, different initial bias, same
attractor: a high-internal-coherence joint state decoupled from external
ground truth.

Engineering-and-testing-as-ground-truth is the operational answer. A
build-and-test loop introduces external coupling that can disturb the joint
internal state — code that does not run, tests that fail, calibrators that
produce wrong answers, induction-on-noise that reproduces the supposed
finding. The §7.ter.19 → §7.ter.22 → Finding F arc was caught precisely
because each round of joint pattern recognition was handed back to the
engineering loop and tested on synthetic ground truth. The methodology
drag-coupled the joint system back toward correspondence with external
structure each time it strayed.

The general principle: a human + LLM system can sustain reasoning beyond the
human's immediate ability to hold the full topic structure in working
memory, *provided* a tangible engineering or testing process is in the loop
as ground truth. Without that coupling, the same architecture produces
hallucinations or crackpottery depending on where it starts. The choice is
not between "use LLMs" and "do not use LLMs" — it is between "use them with
sufficient external grounding" and "use them in self-referential mode." The
two produce categorically different outputs.

The principle generalises. Anything that reliably introduces external
sync-pull to the joint reasoner-and-world system can serve the same function
the engineering loop does here: peer review, replication studies, formal
verification, empirical falsification, hard physical reality. The common
feature is that the external coupling has to be *capable of disagreeing* with
the internal joint state. Soft external coupling that always validates
whatever the joint system produces — sycophantic critics, unfalsifiable
theory, agreeable collaborators — does not work because it does not
introduce the disturbance needed to disturb the internal attractor.

Shout outs to Michael and Karl Polanyi.

## What this work is, in this frame

ARS is an applied implementation of Planat's Farey-rational PLL framework,
built and validated under a discipline that takes the boundary-readout
problem seriously. Its empirical contributions are calibrated readings of
arithmetic and physical signals consistent with prior literature. Its
methodological contribution is a worked example of how successive layers of
measurement-induced structure get caught when the calibration discipline is
applied recursively. Its philosophical commitment is hard determinism with
eternalist boundary-readout framing — the same commitment that makes the
methodology coherent makes the negative LLM result a feature rather than a
failure.

The methodology works because the frame underneath it is consistent with how
observation actually relates to underlying structure under any deterministic
interpretations.
