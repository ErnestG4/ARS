"""
Tests for bgp_pipeline.py — Phase 20 Tier 1 acceptance.

The pipeline functions are exercised against a single small RIPE RIS
update file from the event window (already cached at the test path
under data/phase20_facebook_2021/_smoke/).  The tests are skipped if
the smoke file is not present (avoids depending on network in CI).
"""
import os, sys
from pathlib import Path
import pytest

THIS = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(THIS))

from bgp_pipeline import (
    parse_mrt_file, list_files_in_window, COLLECTORS, WINDOWS,
    _bgpdump_available,
)


SMOKE = Path(os.path.dirname(THIS)) / 'data' / 'phase20_facebook_2021' \
        / '_smoke' / 'rrc00_15-30.gz'


@pytest.mark.skipif(not SMOKE.exists(),
                     reason="smoke file not downloaded")
def test_parser_returns_records():
    n = 0
    for rec in parse_mrt_file(SMOKE, prefer='mrtparse'):
        n += 1
        if n <= 5:
            assert 'timestamp_us' in rec
            assert 'peer_asn' in rec
            assert 'prefix' in rec
            assert rec['update_type'] in ('A', 'W')
            assert isinstance(rec['timestamp_us'], int)
            assert rec['timestamp_us'] > 1_500_000_000_000_000   # > 2017
        if n > 100:
            break
    assert n > 100, f"expected >100 records, got {n}"


@pytest.mark.skipif(not SMOKE.exists(),
                     reason="smoke file not downloaded")
def test_parser_timestamps_within_5min_window():
    """Records in a 5-minute file should fall inside that file's 5-minute
    window (allow some clock-drift slack)."""
    timestamps = []
    for rec in parse_mrt_file(SMOKE, prefer='mrtparse'):
        timestamps.append(rec['timestamp_us'])
        if len(timestamps) > 200:
            break
    span_us = max(timestamps) - min(timestamps)
    # Allow up to 12 minutes (filename label is start time; some collectors
    # spool a few extra minutes' worth into the file).
    assert span_us < 12 * 60 * 1_000_000, (
        f"timestamps span {span_us / 1_000_000:.1f}s — outside 5-min file")


def test_list_files_in_window_routeviews():
    """RouteViews 15-min cadence: 12-hour window → 48 files."""
    win = WINDOWS['event']
    files = list_files_in_window('route-views2', win['start'], win['end'])
    assert len(files) == 48, f"expected 48 RouteViews files, got {len(files)}"
    # Check filename pattern
    _, url = files[0]
    assert 'updates.20211004.1200.bz2' in url
    _, url_last = files[-1]
    assert 'updates.20211004.2345.bz2' in url_last


def test_list_files_in_window_ripe():
    """RIPE 5-min cadence: 12-hour window → 144 files."""
    win = WINDOWS['event']
    files = list_files_in_window('rrc00', win['start'], win['end'])
    assert len(files) == 144, f"expected 144 RIPE files, got {len(files)}"
    _, url = files[0]
    assert 'updates.20211004.1200.gz' in url


def test_collector_panel_is_complete():
    """The panel covers all four collectors in the SESSION-PLAN."""
    expected = {'route-views2', 'route-views.eqix', 'route-views.linx',
                 'rrc00'}
    assert set(COLLECTORS) == expected


def test_windows_are_complete():
    expected = {'quiescent', 'event', 'normal_load'}
    assert set(WINDOWS) == expected


if __name__ == '__main__':
    sys.exit(pytest.main([__file__, '-v']))
