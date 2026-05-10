"""
run_phase20_acquire.py — Phase 20 Tier 1 driver.

Acquire all 12 (collector × window) cells of MRT update data and parse
them into per-cell parquet files.  Then compute per-collector AS-hop
distance to AS 32934 (Facebook) using the CAIDA Oct 2021 AS-graph.

Uses ProcessPoolExecutor to parallelise across (collector, window)
cells (each cell is a sequential download-and-parse pipeline; multiple
cells can run concurrently).

Outputs:
  data/phase20_facebook_2021/raw/{collector}/{window}/  — raw MRT files
  data/phase20_facebook_2021/{collector}_{window}.parquet — parsed events
  data/phase20_topology/per_collector_distance.parquet
"""
from __future__ import annotations

import os, sys, time, argparse
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path
import pandas as pd

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, THIS_DIR)

from bgp_pipeline import COLLECTORS, WINDOWS, acquire_window, \
    cell_parquet_exists
from as_topology import (
    download_caida_as_rel, load_as_graph,
    per_collector_distance_summary, peer_asns_from_parquet,
    FACEBOOK_AS,
)


DATA = Path(THIS_DIR) / 'data'
RAW_ROOT = DATA / 'phase20_facebook_2021' / 'raw'
PARQUET_ROOT = DATA / 'phase20_facebook_2021'
TOPO_DIR = DATA / 'phase20_topology'


def acquire_one_cell(args):
    """Worker: acquire (collector, window) cell.  Importable so it works
    with ProcessPoolExecutor."""
    collector, window_name = args
    parquet_path = PARQUET_ROOT / f"{collector}_{window_name}.parquet"
    t0 = time.time()
    summary = acquire_window(
        collector=collector,
        window_name=window_name,
        raw_dir=RAW_ROOT,
        parquet_path=parquet_path,
        parser='auto',
        skip_if_exists=True,
        progress=False,
    )
    summary['collector'] = collector
    summary['window'] = window_name
    summary['parquet_path'] = str(parquet_path)
    summary['wall_time_s'] = time.time() - t0
    return summary


def topology_summary():
    """Compute per-collector AS-distance to AS32934."""
    print("\n" + "=" * 80)
    print("Topology — per-collector distance to AS32934")
    print("=" * 80)
    caida_file = TOPO_DIR / 'caida_as_rel_20211001.txt.bz2'
    if not caida_file.exists():
        print("Downloading CAIDA AS Relationships…")
        ok = download_caida_as_rel(caida_file)
        if not ok:
            print("  FAILED")
            return None

    print("Loading AS graph…")
    t0 = time.time()
    g = load_as_graph(caida_file)
    print(f"  {len(g):,} ASNs, {sum(len(v) for v in g.values()) // 2:,} "
          f"edges  ⏱{time.time() - t0:.1f}s")

    # Pull peer ASNs from each collector's quiescent parquet (the most
    # stable view of the collector's peering set).  Fall back to event
    # window if quiescent isn't present.  Supports sharded layout.
    peers_per_col = {}
    for collector in COLLECTORS:
        for window in ('quiescent', 'event', 'normal_load'):
            p = PARQUET_ROOT / f"{collector}_{window}.parquet"
            if cell_parquet_exists(p):
                peers_per_col[collector] = peer_asns_from_parquet(p)
                print(f"  {collector}: {len(peers_per_col[collector])} "
                      f"peer ASNs (from {window})")
                break
        else:
            print(f"  {collector}: no parquet found, skipping topology")

    if not peers_per_col:
        return None
    df = per_collector_distance_summary(peers_per_col, g,
                                          target_as=FACEBOOK_AS)
    out = TOPO_DIR / 'per_collector_distance.parquet'
    df.to_parquet(out, index=False)
    print(f"\n  Per-collector distance to AS{FACEBOOK_AS}:")
    print(df.to_string(index=False))
    print(f"\n  → {out}")
    return df


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--workers', type=int, default=2,
                    help='parallel cells (each cell pipelines '
                         'download + parse)')
    p.add_argument('--cells', nargs='*', default=None,
                    help='subset of cells, format collector/window '
                         '(e.g. rrc00/event)')
    p.add_argument('--skip-topology', action='store_true')
    args = p.parse_args()

    PARQUET_ROOT.mkdir(parents=True, exist_ok=True)
    TOPO_DIR.mkdir(parents=True, exist_ok=True)

    cells = []
    if args.cells:
        for c in args.cells:
            collector, window = c.split('/')
            cells.append((collector, window))
    else:
        for collector in COLLECTORS:
            for window in WINDOWS:
                cells.append((collector, window))

    print("=" * 80)
    print(f"Phase 20 Tier 1 — acquiring {len(cells)} cells "
          f"with {args.workers} workers")
    print("=" * 80)
    for c, w in cells:
        print(f"  {c}/{w}")

    summaries = []
    t_start = time.time()
    with ProcessPoolExecutor(max_workers=args.workers) as ex:
        futures = {ex.submit(acquire_one_cell, cell): cell for cell in cells}
        for f in as_completed(futures):
            cell = futures[f]
            try:
                s = f.result()
            except Exception as e:
                print(f"  [{cell[0]}/{cell[1]}] WORKER FAIL: {e}")
                continue
            tag = '(cached)' if s.get('skipped') else ''
            print(f"  ✓ {cell[0]}/{cell[1]:<11} "
                  f"files={s.get('n_files_total', 0):>4} "
                  f"records={s['n_records']:>10,} "
                  f"⏱{s['wall_time_s']:>6.0f}s {tag}")
            summaries.append(s)

    print(f"\n  cells acquired: {len(summaries)}/{len(cells)}  "
          f"total wall time: {(time.time() - t_start) / 60:.1f} min")

    # Save acquisition summary
    pd.DataFrame(summaries).to_parquet(
        PARQUET_ROOT / '_acquisition_summary.parquet', index=False)

    if not args.skip_topology:
        topology_summary()


if __name__ == '__main__':
    main()
