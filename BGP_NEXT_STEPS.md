# BGP Phase 20 — decision document

This document is filled in by Tier 5 of the Phase 20 PoC.  It records
the per-verdict-map outcome and what the next steps are conditional
on that outcome.  It is intentionally short — a go/no-go on a longer-
term study, not the longer-term study itself.

The PoC verdict and supporting numbers are populated automatically
from the Tier 3/4 outputs:

  - `data/phase20_classification.parquet`
  - `data/phase20_trajectory_descriptors.parquet`
  - `data/phase20_falsification.parquet`

See §7.ter.27 in `RESULTS.md` for the methodology details.

## Verdict

**Distinct cascade trajectory per collector, surviving topology-aware
Hawkes and Phase 18 surrogates, with weak topology correlation under
the chosen metric.**

The cascade-peak BR_artifact reading (rep_med 0.85–0.90) is uniformly
present at all 4 collectors and uniformly survives all three surrogates
applied (phase_randomized_iei → TR, cumulant_matched → BL,
topology_hawkes → BL).  Per-collector cascade depth varies across
collectors (0.58–0.85), so the trajectory itself is structured.

The route-topology framing's primary metric — median AS-hop distance
to AS 32934 — is degenerate on this 4-collector panel: AS 32934 has
401 direct neighbours and every collector includes direct-FB peers,
so the median is identically 1.0.  Mean AS-hop distance varies
modestly (1.15–1.37) and gives R² = 0.14 with cascade depth
(n = 4), below the verdict-map's R² > 0.5 "topology-supported"
threshold.

The cascade-shape itself is real (varies meaningfully per collector,
survives surrogates).  The route-topology framing is *not* strongly
supported by AS-hop distance on this panel.  Whether alternative
topology metrics (geographic distance, business-relationship class,
transit-customer hierarchy) yield stronger correlation is the
follow-up question.

PoC verdict in the Delta-2 verdict-map terms: **closest to "distinct
trajectories per collector, uncorrelated with topology under chosen
metric"** with the additional refinement that the surrogate-survival
result is positive (so the cascade-shape is real, but the framing
needs alternative metrics).

## Outcome-conditioned next steps

### If verdict is "real cascade-shape finding survives topology-aware Hawkes (and adds beyond Kitsak/Matcharashvili)"

A longer-term study is justified.  The contribution is a methodological
extension building on:

- Kitsak, M., Elmokashfi, A., Havlin, S., Krioukov, D. (2015). Long-Range
  Correlations and Memory in the Dynamics of Internet Interdomain
  Routing. *PLOS One* 10(11): e0141481.  Established BGP's long-range
  correlations and broad-class membership in the cascade universality
  cluster.
- Matcharashvili, T., Elmokashfi, A., Prangishvili, A. (2020). Analysis
  of the regularity of the Internet Interdomain Routing dynamics.
  *Physica A* 551: 124142.  Multifractal DFA, multiscale entropy,
  per-AS variability, outlier-day identification.
- Elmokashfi, A., Kvalbein, A., Dovrolis, C. (2012). BGP churn evolution.
  *IEEE/ACM Trans. Networking* 20(2): 571-584.  Seven-year BGP churn at
  backbone level.

Apply the same per-vantage-point trajectory analysis to additional
well-documented BGP outage events:

- Rogers Canada outage, July 8, 2022 (~07:43 UTC).  Source AS 812
  (Rogers).  Comparable scale to the Facebook outage, similarly
  well-documented in CAIDA / NANOG postmortems.
- AS7007 leak, April 25, 1997.  The canonical "small AS announces the
  whole table" event; pre-RPKI era, smaller pre-cascade routing system,
  good baseline for cascade-shape evolution over 25 years of routing-
  protocol scale changes.
- YouTube/Pakistan, February 24, 2008.  Targeted route hijack with
  global propagation.  Different cascade morphology from a
  withdrawal-driven outage.

Resourcing: estimate ~3–4 weeks calendar time for cross-event
generalisation (data acquisition, analysis on each event, writeup);
compute cost similar to this PoC (single-machine, no special
infrastructure required).

#### Target venues (Delta 5 — stat-phys primary)

Statistical physics / complex systems (primary, given existing
literature lives here):
- *Physica A* — both Kitsak follow-ups and Matcharashvili 2020
  published here.
- *Physical Review E* — Krioukov group's primary venue.
- *PLOS One* — Kitsak 2015's venue.
- *Nature Communications* — possible if cascade-shape result is
  particularly clean.

Network measurement (secondary, more applied framing):
- IMC (Internet Measurement Conference)
- PAM (Passive and Active Measurement)
- NDSS
- SIGCOMM CCR

Pick venue based on which framing the verdict supports:
- "Methodology with novel cascade-shape characterization" → stat-phys
- "Applied measurement of specific BGP events" → network measurement

#### Collaboration outreach (recommended for positive verdict)

If Phase 20 produces a positive verdict, the natural follow-through is
to write up the result as a tight 5–8 page methodology paper
(joint-plane framework + Facebook 2021 result + topology-aware Hawkes
survival), then send it to:

- **Dmitri Krioukov** (Northeastern Network Science Institute,
  krioukov@northeastern.edu): senior author on Kitsak et al. 2015,
  active in this neighborhood, known to engage with non-traditional
  collaborators when work is solid.
- **Shlomo Havlin** (Bar-Ilan, havlin@ophir.ph.biu.ac.il): co-author on
  Kitsak 2015, prolific senior figure in network statistical physics.
- **Ahmed Elmokashfi** (Simula): co-author on both Kitsak 2015 and
  Matcharashvili 2020, more empirically focused, possibly more
  accessible for direct collaboration.

Framing for the outreach letter:

> Building on your 2015/2020 work establishing BGP's long-range-
> correlated cascade dynamics, here's a methodology that classifies
> cascade events at sub-window resolution with topology-aware
> falsification, applied to the Facebook 2021 outage.  The PoC
> produced [verdict].  Would appreciate feedback, and would consider
> collaboration on a longer-term cross-event study (Rogers 2022,
> AS7007 1997, YouTube/Pakistan 2008) if there's mutual interest.

Strategy: regardless of response, the work gets cited correctly and the
relevant senior researchers are aware of it.  Best case: senior
co-authors on the longer-term paper, addresses credentialing
structurally for any follow-on publication.  Worst case: standalone
publication in stat-phys venue with their work cited as foundation.

### If verdict is "topology-aware Hawkes accounts for everything"

The cascade-shape finding reduces to "BGP cascades follow topology-
aware Hawkes dynamics" within the framework's classifier.  This is a
refinement compatible with both the existing BGP measurement literature
(Mao et al. 2002 on BGP convergence; Streibelt and Madhyastha 2022 on
the Facebook outage) and the statistical-physics characterisation
(Kitsak 2015, Matcharashvili 2020).  It does not constitute a
universality-class structural finding beyond what those works already
establish.

The methodological lesson — that topology-aware Hawkes is the right
falsification surrogate for cascade-driven systems with spatial
structure — does transfer.  Candidate domains for the same
methodology:

- Power grid cascading failures (e.g., 2003 Northeast Blackout,
  2021 Texas grid event).  The state-machine framing is similar:
  deterministic failure-propagation dynamics with topological
  structure.
- Financial-network contagion (e.g., 2008 Lehman cascade).
  Banking-network adjacency replaces AS-graph adjacency.
- Social-media information cascades.  The follower graph replaces
  the AS graph.

The methodology note is a publishable contribution on its own at a
methodology venue (PoMACS, SIGMETRICS).  No full per-domain study is
implied; it's a tool-paper contribution.

### If verdict is "vantage-point variation uncorrelated with chosen topology metric"

Vantage-point variation exists but isn't structured by AS-distance
under the chosen metric (median AS-path length to AS 32934).
Alternative metrics worth testing in any follow-up:

- **Geographic distance** between collector peer ASes and AS 32934
  datacenter regions.  The AS graph is logical; geographic latency
  may matter independently.
- **Business-relationship-class distance**: weight provider-to-
  customer edges differently from peer-to-peer edges (CAIDA serial-2
  format provides this distinction).
- **Transit-customer hierarchy depth**: the number of tier-1
  transits crossed between collector peer and source AS.  Captures
  routing-policy structure that pure hop-count doesn't.

The methodology investment for a multi-metric follow-up is small;
the question is whether any single-metric correlation emerges, in
which case the framing is salvageable, vs. whether all metrics
yield uncorrelated results, in which case the framework is
insufficient for BGP cascade morphology.

### If verdict is "synchronised classifications across collectors during cascade"

Topology effect is below detection threshold at the chosen scale
(5-min sub-windows, 4 collectors, AS-hop-distance metric).  Either a
methodology limitation (finer sub-windows, more collectors, alternative
metrics) or a substantive finding (BGP cascades are too fast and too
globally synchronised for vantage-point trajectory analysis to
distinguish them).

The follow-up question is at what scale topology effects become
visible: 1-minute sub-windows? 30-second?  This would require either
sub-MRAI-period analysis (which is itself a separate methodological
project per §7.ter.27 stop conditions) or finer-grained
cross-collector clock synchronisation than the 5-min protocol uses.

### If verdict is "indistinguishable from quiescent"

Cascade signature not detectable at the joint-plane resolution.
Negative result.  The methodology limitation is documented and the
PoC closes; no longer-term BGP study is justified.

The lesson that transfers: timer-quantisation artifacts (MRAI-class)
and the limits of joint-plane classification at sub-second cascade
scales are documented for future ARS users.

## Methodological lessons (independent of the verdict)

- **Timer-quantisation artifacts** are a generic class of
  measurement-pipeline confound across protocols with periodic batch
  emission.  The MRAI-on-30s pattern documented in §7.ter.27 is one
  example; similar quantisation patterns exist in TCP RTO timers
  (1-second granularity), DNS TTL quantisation (per-zone TTL minimum),
  and many other protocol-level batched-emission mechanisms.  Future
  ARS applications to packet- or message-level timing should
  specifically test for timer-quantisation artifacts at the relevant
  protocol's timer scales.

- **Topology-aware Hawkes** is a concrete, implementable falsification
  surrogate for any system with cascade-driven dynamics and spatial-
  topological structure.  See `topology_hawkes.py` for the API; the
  generator stratifies the standard Hawkes fit by topological-distance
  bins relative to a known cascade source.

- **Vantage-point variation as signal, not noise.**  When multiple
  observers of a global system disagree, the disagreement itself
  carries structural information if and only if the disagreement is
  structured by some external invariant (topology, geography, time
  zone).  Phase 20's framing — variation correlated with topological
  distance — applies to any multi-observer measurement system; the
  protocol generalises beyond BGP.

## Provenance

- Tier 1 raw data and parquet outputs:
  `data/phase20_facebook_2021/`
- Topology data: `data/phase20_topology/`
- Tier 2 calibrators: `data/phase20_calibrators.parquet`
- Tier 3 trajectory: `data/phase20_classification.parquet`,
  `data/phase20_trajectory_descriptors.parquet`
- Tier 4 falsification: `data/phase20_falsification.parquet`
- Plots: `plots/53_phase20_mrai_artifact.png`,
  `plots/54_phase20_subwindow_stability.png`,
  `plots/55_phase20_trajectory_per_collector.png`,
  `plots/56_phase20_topology_vs_trajectory.png`,
  `plots/57_phase20_surrogate_survival.png`
- Source code: `bgp_pipeline.py`, `as_topology.py`,
  `topology_hawkes.py`, `run_phase20_*.py`,
  `tests/test_bgp_pipeline.py`, `tests/test_as_topology.py`.
