"""
as_topology.py — Phase 20 AS-graph + per-collector topological-distance
utilities.

Loads the CAIDA AS Relationships dataset (serial-2 format, Oct 2021),
builds an undirected AS-graph (edges link adjacent AS pairs regardless
of provider/peer/customer relationship class), and computes shortest-path
AS-hop distances from any collector's peer ASNs to a target source AS
(AS 32934 for the Facebook Oct 4 2021 outage).

Source-AS distances are aggregated per collector:

  - The set of peer ASNs observed at each collector (from Tier 1
    parquet output).
  - For each peer ASN, AS-hop distance to the target.
  - Per-collector summary: median, mean, distribution.

CAIDA serial-2 format (as-rel2.txt.bz2):

    # comment lines (start with '#')
    <provider_AS>|<customer_AS>|-1|<source>     # provider-to-customer
    <peer_AS>|<peer_AS>|0|<source>              # peer-to-peer

For shortest-path purposes we treat all edges as undirected and
unweighted; the spec calls for "median AS-path length" which is the
canonical undirected hop count metric.
"""
from __future__ import annotations

import os, sys, bz2
import urllib.request
from collections import deque, defaultdict
from pathlib import Path
from typing import Iterable

import numpy as np
import pandas as pd


# CAIDA serial-2 AS Relationships, October 2021 snapshot.
CAIDA_AS_REL_URL = (
    "https://publicdata.caida.org/datasets/as-relationships/serial-2/"
    "20211001.as-rel2.txt.bz2")

FACEBOOK_AS = 32934


# ─── Loader ────────────────────────────────────────────────────────────────


def download_caida_as_rel(dest: Path, url: str = CAIDA_AS_REL_URL) -> bool:
    """Download the CAIDA AS Relationships file to `dest`."""
    if dest.exists() and dest.stat().st_size > 0:
        return True
    dest.parent.mkdir(parents=True, exist_ok=True)
    tmp = dest.with_suffix(dest.suffix + '.tmp')
    req = urllib.request.Request(url,
                                   headers={'User-Agent': 'phase20-bgp/1.0'})
    try:
        with urllib.request.urlopen(req, timeout=120) as r:
            with open(tmp, 'wb') as f:
                while True:
                    buf = r.read(1024 * 1024)
                    if not buf:
                        break
                    f.write(buf)
        tmp.rename(dest)
        return True
    except Exception as e:
        if tmp.exists():
            tmp.unlink()
        print(f"download_caida_as_rel: FAIL {e}")
        return False


def load_as_graph(path: Path) -> dict[int, set[int]]:
    """Parse the bzipped CAIDA AS Relationships file into an undirected
    adjacency dict.  AS numbers are integers; values are sets of
    neighbour AS numbers."""
    adj: dict[int, set[int]] = defaultdict(set)
    opener = bz2.open if str(path).endswith('.bz2') else open
    with opener(path, 'rt', encoding='utf-8', errors='replace') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            parts = line.split('|')
            if len(parts) < 3:
                continue
            try:
                a = int(parts[0])
                b = int(parts[1])
            except ValueError:
                continue
            if a == b:
                continue
            adj[a].add(b)
            adj[b].add(a)
    return dict(adj)


# ─── BFS distance ──────────────────────────────────────────────────────────


def bfs_distances_from(graph: dict[int, set[int]],
                        source: int,
                        max_distance: int = 16,
                        ) -> dict[int, int]:
    """Single-source BFS in the AS graph; returns ASN → hop-distance.
    Capped at `max_distance` to keep the search local on the global graph
    (the diameter of the AS graph is ~6, so this is generous)."""
    dist: dict[int, int] = {source: 0}
    queue = deque([source])
    while queue:
        cur = queue.popleft()
        d = dist[cur]
        if d >= max_distance:
            continue
        for nb in graph.get(cur, ()):
            if nb not in dist:
                dist[nb] = d + 1
                queue.append(nb)
    return dist


# ─── Per-collector distance to a target AS ─────────────────────────────────


def per_collector_distance_summary(
        peer_asns_per_collector: dict[str, list[int]],
        graph: dict[int, set[int]],
        target_as: int = FACEBOOK_AS,
        ) -> pd.DataFrame:
    """For each collector, compute the AS-hop distance from each of its
    peer ASNs to `target_as`, and return per-collector summary stats.

    Returns a DataFrame with columns:
      collector, n_peers, n_peers_reachable, median_distance,
      mean_distance, min_distance, max_distance.
    """
    dist_from_target = bfs_distances_from(graph, target_as,
                                            max_distance=16)
    rows = []
    for collector, peers in peer_asns_per_collector.items():
        peers = list(set(int(p) for p in peers))
        d = [dist_from_target[p] for p in peers
             if p in dist_from_target]
        rows.append(dict(
            collector=collector,
            n_peers=len(peers),
            n_peers_reachable=len(d),
            median_distance=float(np.median(d)) if d else float('nan'),
            mean_distance=float(np.mean(d)) if d else float('nan'),
            min_distance=int(min(d)) if d else -1,
            max_distance=int(max(d)) if d else -1,
        ))
    return pd.DataFrame(rows)


# ─── Convenience: pull peer ASNs from a per-collector parquet ──────────────


def peer_asns_from_parquet(parquet_path: Path) -> list[int]:
    """Extract the unique peer ASNs from a Tier 1 parquet output.
    Supports both legacy single-file and sharded layouts."""
    import sys, os
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from bgp_pipeline import load_cell_parquet
    df = load_cell_parquet(parquet_path, columns=['peer_asn'])
    return sorted(set(int(x) for x in df['peer_asn'].unique()))


__all__ = [
    'CAIDA_AS_REL_URL', 'FACEBOOK_AS',
    'download_caida_as_rel', 'load_as_graph',
    'bfs_distances_from', 'per_collector_distance_summary',
    'peer_asns_from_parquet',
]
