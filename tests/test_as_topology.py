"""
Tests for as_topology.py — Phase 20 Tier 1 AS-graph utilities.

Most tests use a small synthetic graph.  An optional integration test
loads the real CAIDA AS Relationships file if it has been downloaded.
"""
import os, sys
from pathlib import Path
import pytest

THIS = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(THIS))

from as_topology import (
    bfs_distances_from, per_collector_distance_summary,
    load_as_graph, FACEBOOK_AS,
)


# ─── Synthetic graph helper ─────────────────────────────────────────────────


def _toy_graph():
    """Linear-with-branches AS graph:
       1 — 2 — 3 — 4 — 5
                   \
                    6 — 7
    """
    return {
        1: {2}, 2: {1, 3}, 3: {2, 4}, 4: {3, 5, 6},
        5: {4}, 6: {4, 7}, 7: {6},
    }


def test_bfs_distances_from_node():
    g = _toy_graph()
    d = bfs_distances_from(g, 1)
    assert d[1] == 0
    assert d[2] == 1
    assert d[3] == 2
    assert d[4] == 3
    assert d[5] == 4
    assert d[7] == 5
    # Unreachable nodes should not appear
    assert 99 not in d


def test_bfs_distances_max_distance_cap():
    g = _toy_graph()
    d = bfs_distances_from(g, 1, max_distance=3)
    assert d[4] == 3
    assert 5 not in d, "node at distance 4 should not be returned"
    assert 7 not in d


def test_per_collector_distance_summary():
    g = _toy_graph()
    peers = {
        'collector_A': [2, 3],   # close to source=1: distances 1, 2
        'collector_B': [5, 7],   # far: distances 4, 5
    }
    df = per_collector_distance_summary(peers, g, target_as=1)
    assert len(df) == 2
    a = df.set_index('collector').loc['collector_A']
    b = df.set_index('collector').loc['collector_B']
    assert a['median_distance'] == 1.5
    assert b['median_distance'] == 4.5
    # B should have larger mean distance than A — the "topology dimension"
    assert b['mean_distance'] > a['mean_distance']


def test_per_collector_distance_handles_unreachable():
    g = _toy_graph()
    peers = {'far': [99, 100]}     # unreachable from 1
    df = per_collector_distance_summary(peers, g, target_as=1)
    assert df['n_peers_reachable'].iloc[0] == 0
    import numpy as np
    assert np.isnan(df['median_distance'].iloc[0])


# ─── Integration test against real CAIDA file (skipped if absent) ─────────


CAIDA_FILE = (Path(os.path.dirname(THIS)) / 'data' / 'phase20_topology'
               / 'caida_as_rel_20211001.txt.bz2')


@pytest.mark.skipif(not CAIDA_FILE.exists(),
                     reason="CAIDA AS Relationships file not downloaded")
def test_load_real_as_graph_has_facebook():
    g = load_as_graph(CAIDA_FILE)
    assert FACEBOOK_AS in g, "Facebook AS 32934 should be in the graph"
    # Facebook should have many neighbours (it peers widely)
    assert len(g[FACEBOOK_AS]) > 50, (
        f"AS{FACEBOOK_AS} has only {len(g[FACEBOOK_AS])} neighbours — "
        f"expected >50 for a major content-network AS")


@pytest.mark.skipif(not CAIDA_FILE.exists(),
                     reason="CAIDA AS Relationships file not downloaded")
def test_real_graph_has_short_diameter():
    """The AS graph has known diameter ~6.  Verify BFS from Facebook
    reaches most ASes within 5 hops."""
    g = load_as_graph(CAIDA_FILE)
    d = bfs_distances_from(g, FACEBOOK_AS, max_distance=16)
    # Most ASes in the graph should be reachable within 6 hops
    n_total = len(g)
    n_within_6 = sum(1 for v in d.values() if v <= 6)
    assert n_within_6 / n_total > 0.95, (
        f"only {n_within_6}/{n_total} ASes within 6 hops of "
        f"FB — expected >95%")


if __name__ == '__main__':
    sys.exit(pytest.main([__file__, '-v']))
