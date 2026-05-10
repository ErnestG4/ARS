"""
phase22a/loader.py — pvc-11 (Smith & Kohn) loader.

Unifies the three storage formats present in the dataset:
  - spontaneous .mat (v7, scipy)         data.EVENTS = (n_units,) cell of spike-time arrays
  - gratings    .mat (v7, scipy)         data.EVENTS = (n_units, 12 gratings, n_trials) cells
  - movies      .mat (v7.3 HDF5, h5py)   data['EVENTS'] = (n_trials, n_units) of HDF5 refs
                                         (transposed vs. MATLAB convention)

The loader returns a `Recording` dataclass with per-unit spike-time
arrays (numpy float64, seconds), per-unit metadata (channel, unit-index,
SNR), the 10x10 array MAP, and the stimulus-condition structure.

Cell coercion: scipy returns single-spike grating cells as Python `float`
and zero-spike cells as ndarray((0,)) — both are coerced to ndarray here.

This loader is the only place pvc-11 file structure is touched; downstream
code consumes Recording objects.
"""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

import h5py
import numpy as np
import scipy.io as sio


PVC11_ROOT = Path('/home/combust/fmexplorer/criticality_tool/data/pvc-11/data_and_scripts')


# Drifting-grating presentation: each grating shown for 1.28s, the
# canonical analysis window is the last 1.0s (skip the 0.28s onset
# transient — Cowley/Williamson convention).
GRATING_TRIAL_SEC = 1.0
GRATING_OFFSET_SEC = 0.28
GRATING_DIRECTIONS_DEG = np.arange(0, 360, 30, dtype=np.float64)  # 12 directions

# Movie trial duration (all three movie types are 30s)
MOVIE_TRIAL_SEC = 30.0

# Grating-direction movie: 100 gratings × 0.3s each
GRATING_MOVIE_DURATION_SEC = 30.0
GRATING_MOVIE_GRATING_DUR_SEC = 0.30
GRATING_MOVIE_N = 100


@dataclass
class Recording:
    """A single recording from one Utah-array session."""
    name: str                          # e.g. 'monkey1_spontaneous'
    monkey: int                        # 1..6
    subset: str                        # 'spontaneous' | 'gratings' | 'gratings_movie' | 'natural_movie' | 'noise_movie'
    n_units: int
    snr: np.ndarray                    # (n_units,) SNR per unit
    channels: np.ndarray               # (n_units, 2) [chan_num, unit_idx_on_chan]
    array_map: np.ndarray              # (10, 10) Utah array layout
    duration_sec: float                # condition duration (or per-trial duration)
    n_trials: int = 1                  # 1 for spontaneous; per-stim for gratings/movies
    n_conditions: int = 1              # 12 for drifting gratings; 1 for movies/spont
    # spike_times[unit_idx] = np.ndarray of seconds (spontaneous, single condition)
    # spike_times[unit_idx][cond_idx][trial_idx] = np.ndarray (gratings)
    # spike_times[unit_idx][trial_idx] = np.ndarray (movies)
    spike_times: list = field(default_factory=list)
    # Per-condition stimulus metadata (e.g. grating direction in radians)
    stim_meta: dict = field(default_factory=dict)

    def unit_id(self, u: int) -> str:
        """Stable unit identifier across recordings on the same monkey."""
        ch, uidx = int(self.channels[u, 0]), int(self.channels[u, 1])
        return f"M{self.monkey}_ch{ch:03d}_u{uidx}"

    def concatenated_spikes(self, unit: int, condition: Optional[int] = None,
                             gap_sec: float = 0.0) -> np.ndarray:
        """Return a single 1D spike-time array for one unit by concatenating
        trials (and optionally one condition) end-to-end with a fixed gap.

        - spontaneous:    returns spike_times[unit]
        - gratings:       if condition is None, all conditions × all trials
                          concatenated (in condition-major order); else just
                          that condition's trials.
        - movies:         all trials concatenated.

        Trial boundaries are stitched with `+gap_sec` of silence; trial
        durations come from `duration_sec` and `GRATING_TRIAL_SEC` etc.
        """
        if self.subset == 'spontaneous':
            return np.asarray(self.spike_times[unit], dtype=np.float64)

        if self.subset == 'gratings':
            trial_dur = GRATING_TRIAL_SEC
            chunks = []
            offset = 0.0
            cond_iter = (range(self.n_conditions) if condition is None
                         else [condition])
            for c in cond_iter:
                for t in range(self.n_trials):
                    sp = self.spike_times[unit][c][t]
                    sp = np.asarray(sp, dtype=np.float64).flatten()
                    # Restrict to the canonical [offset, offset+1] s window
                    sp = sp[(sp >= GRATING_OFFSET_SEC) &
                             (sp <  GRATING_OFFSET_SEC + GRATING_TRIAL_SEC)]
                    sp = sp - GRATING_OFFSET_SEC + offset
                    chunks.append(sp)
                    offset += trial_dur + gap_sec
            return (np.sort(np.concatenate(chunks))
                    if chunks else np.zeros(0, dtype=np.float64))

        # movies
        trial_dur = MOVIE_TRIAL_SEC
        chunks = []
        offset = 0.0
        for t in range(self.n_trials):
            sp = self.spike_times[unit][t]
            sp = np.asarray(sp, dtype=np.float64).flatten()
            sp = sp[(sp >= 0) & (sp < trial_dur)]
            sp = sp + offset
            chunks.append(sp)
            offset += trial_dur + gap_sec
        return (np.sort(np.concatenate(chunks))
                if chunks else np.zeros(0, dtype=np.float64))

    def n_spikes_per_unit(self) -> np.ndarray:
        """Total spike count per unit, summed over all trials/conditions."""
        out = np.zeros(self.n_units, dtype=np.int64)
        for u in range(self.n_units):
            out[u] = self.concatenated_spikes(u).size
        return out

    def mean_rate_per_unit(self) -> np.ndarray:
        """Mean firing rate (sp/s) per unit across the recording."""
        if self.subset == 'spontaneous':
            return self.n_spikes_per_unit() / max(self.duration_sec, 1e-9)
        if self.subset == 'gratings':
            total_dur = self.n_conditions * self.n_trials * GRATING_TRIAL_SEC
        else:
            total_dur = self.n_trials * MOVIE_TRIAL_SEC
        return self.n_spikes_per_unit() / max(total_dur, 1e-9)


# ─── format readers ─────────────────────────────────────────────────────────


def _coerce_cell(c) -> np.ndarray:
    """Coerce one spike-time cell to a flat float64 ndarray.

    scipy returns single-spike cells as Python `float`, zero-spike as
    ndarray((0,)).  Movie-format cells (HDF5) are 2D (1 x n).
    """
    if c is None:
        return np.zeros(0, dtype=np.float64)
    if np.isscalar(c):
        return np.asarray([c], dtype=np.float64)
    arr = np.asarray(c, dtype=np.float64).flatten()
    return arr


def _read_spontaneous(monkey: int) -> Recording:
    p = PVC11_ROOT / 'spikes_spontaneous' / f'spiketimesmonkey{monkey}spont.mat'
    m = sio.loadmat(p, squeeze_me=True, struct_as_record=False)
    d = m['data']
    ev = d.EVENTS
    spike_times = [_coerce_cell(c) for c in ev]
    duration = float(max((c.max() if c.size else 0.0) for c in spike_times))
    return Recording(
        name=f'monkey{monkey}_spontaneous',
        monkey=monkey,
        subset='spontaneous',
        n_units=len(spike_times),
        snr=np.asarray(d.SNR, dtype=np.float64).flatten(),
        channels=np.asarray(d.CHANNELS, dtype=np.int64),
        array_map=np.asarray(d.MAP, dtype=np.float64),
        duration_sec=duration,
        spike_times=spike_times,
    )


def _read_gratings(monkey: int) -> Recording:
    p = PVC11_ROOT / 'spikes_gratings' / f'data_monkey{monkey}_gratings.mat'
    m = sio.loadmat(p, squeeze_me=True, struct_as_record=False)
    d = m['data']
    ev = d.EVENTS                                        # (units, gratings, trials)
    n_units, n_gratings, n_trials = ev.shape
    spike_times = [
        [
            [_coerce_cell(ev[u, g, t]) for t in range(n_trials)]
            for g in range(n_gratings)
        ]
        for u in range(n_units)
    ]
    return Recording(
        name=f'monkey{monkey}_gratings',
        monkey=monkey,
        subset='gratings',
        n_units=n_units,
        snr=np.asarray(d.SNR, dtype=np.float64).flatten(),
        channels=np.asarray(d.CHANNELS, dtype=np.int64),
        array_map=np.asarray(d.MAP, dtype=np.float64),
        duration_sec=GRATING_TRIAL_SEC,
        n_trials=n_trials,
        n_conditions=n_gratings,
        spike_times=spike_times,
        stim_meta={'directions_deg': GRATING_DIRECTIONS_DEG.copy()},
    )


def _read_movie(monkey: int, movie: str) -> Recording:
    p = PVC11_ROOT / 'spikes_movies' / f'data_monkey{monkey}_{movie}.mat'
    with h5py.File(p, 'r') as f:
        d = f['data']
        ev = d['EVENTS']                                 # (trials, units) of refs
        n_trials, n_units = ev.shape
        snr = np.asarray(d['SNR']).flatten()
        # CHANNELS in HDF5: (2, n_units), transposed compared to scipy.
        chan = np.asarray(d['CHANNELS']).T.astype(np.int64)
        array_map = np.asarray(d['MAP']).astype(np.float64)
        spike_times = [
            [_coerce_cell(np.asarray(f[ev[t, u]])) for t in range(n_trials)]
            for u in range(n_units)
        ]
    stim_meta: dict = {}
    if movie == 'gratings_movie':
        # Load grating-direction labels for the 100 0.3s presentations
        theta_path = PVC11_ROOT / 'stimuli_movies' / 'theta_gratings_movie.mat'
        tm = sio.loadmat(theta_path, squeeze_me=True, struct_as_record=False)
        stim_meta['theta_rad'] = np.asarray(tm['theta'], dtype=np.float64)
        stim_meta['grating_dur_sec'] = GRATING_MOVIE_GRATING_DUR_SEC
        stim_meta['n_gratings'] = GRATING_MOVIE_N
    return Recording(
        name=f'monkey{monkey}_{movie}',
        monkey=monkey,
        subset=movie,
        n_units=n_units,
        snr=snr,
        channels=chan,
        array_map=array_map,
        duration_sec=MOVIE_TRIAL_SEC,
        n_trials=n_trials,
        spike_times=spike_times,
        stim_meta=stim_meta,
    )


# ─── public API ─────────────────────────────────────────────────────────────


SPONTANEOUS_MONKEYS = [1, 2, 3, 4, 5, 6]
GRATINGS_MONKEYS = [1, 2, 3]
MOVIE_MONKEYS = [1, 2]
MOVIE_KINDS = ['gratings_movie', 'natural_movie', 'noise_movie']


def load(name: str) -> Recording:
    """Load a recording by name.

    Names follow the convention:
        'monkey{N}_spontaneous'         N = 1..6
        'monkey{N}_gratings'            N = 1..3
        'monkey{N}_gratings_movie'      N = 1..2
        'monkey{N}_natural_movie'       N = 1..2
        'monkey{N}_noise_movie'         N = 1..2
    """
    if not name.startswith('monkey'):
        raise ValueError(f"unknown recording: {name!r}")
    rest = name[len('monkey'):]
    n_str, _, kind = rest.partition('_')
    monkey = int(n_str)
    if kind == 'spontaneous':
        return _read_spontaneous(monkey)
    if kind == 'gratings':
        return _read_gratings(monkey)
    if kind in MOVIE_KINDS:
        return _read_movie(monkey, kind)
    raise ValueError(f"unknown recording: {name!r}")


def list_all_recordings() -> list[str]:
    """All available recording names."""
    out = [f'monkey{m}_spontaneous' for m in SPONTANEOUS_MONKEYS]
    out += [f'monkey{m}_gratings' for m in GRATINGS_MONKEYS]
    for m in MOVIE_MONKEYS:
        for k in MOVIE_KINDS:
            out.append(f'monkey{m}_{k}')
    return out


def summarize(rec: Recording) -> dict:
    """One-line summary dict for cataloguing."""
    n_spk = rec.n_spikes_per_unit()
    rate = rec.mean_rate_per_unit()
    return dict(
        name=rec.name, subset=rec.subset, monkey=rec.monkey,
        n_units=rec.n_units,
        snr_mean=float(rec.snr.mean()), snr_min=float(rec.snr.min()),
        snr_max=float(rec.snr.max()),
        n_trials=rec.n_trials, n_conditions=rec.n_conditions,
        duration_sec=rec.duration_sec,
        n_spikes_per_unit_mean=float(n_spk.mean()),
        n_spikes_per_unit_min=int(n_spk.min()),
        n_spikes_per_unit_max=int(n_spk.max()),
        mean_rate_mean=float(rate.mean()),
        mean_rate_min=float(rate.min()),
        mean_rate_max=float(rate.max()),
    )


__all__ = [
    'Recording', 'load', 'list_all_recordings', 'summarize',
    'PVC11_ROOT', 'GRATING_DIRECTIONS_DEG', 'GRATING_TRIAL_SEC',
    'GRATING_OFFSET_SEC', 'MOVIE_TRIAL_SEC',
    'GRATING_MOVIE_GRATING_DUR_SEC', 'GRATING_MOVIE_N',
    'SPONTANEOUS_MONKEYS', 'GRATINGS_MONKEYS', 'MOVIE_MONKEYS', 'MOVIE_KINDS',
]
