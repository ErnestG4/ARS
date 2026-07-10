"""
phase24/loader.py — Allen Brain Observatory Visual Coding Neuropixels
loader, mirroring the pvc-11 loader's per-unit-spikes-plus-metadata
output structure.

The Allen NWB schema (visual-coding-neuropixels) exposes:
  - units table with spike_times, spike_amplitudes, quality metrics
  - electrodes table with peak channel → CCF brain-area lookup
  - intervals tables per stimulus type (drifting_gratings,
    static_gratings, natural_scenes, natural_movie_one,
    natural_movie_three, gabors, flashes, spontaneous, invalid_times)

The pvc-11 loader returned a `Recording` dataclass with:
  - per-unit spike-time arrays (numpy float64, seconds)
  - per-unit metadata (channel, SNR)
  - per-stimulus structured spike-times
  - stimulus metadata

Phase 24 returns an `AllenRecording` dataclass with the same semantic
shape, parameterised by the brain-area filter and the unit-quality
filter.  Spike times are loaded lazily into per-stimulus structures
on demand to keep memory footprint sane (each NWB file is ~3 GB but
we only need spike times — typically a few MB total post-filter).

Allen-default quality filter (matches the standard allensdk
unit_filter):
  quality == 'good'
  isi_violations < 0.5
  presence_ratio > 0.9
  amplitude_cutoff < 0.1
  snr > 1.0

The pvc-11 SNR threshold of ≥ 2.0 is not directly comparable (different
sort pipelines), but the Allen-default quality filter is the
established "matched restrictiveness" choice for awake-mouse-V1 work.
"""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

import numpy as np
import pandas as pd
import pynwb


ALLEN_CACHE = Path(os.path.expandvars('$HOME/fmexplorer/allen_cache')).expanduser()
DEFAULT_AREA = 'VISp'   # mouse primary visual cortex
DRIFTING_TRIAL_SEC = 2.0
NATURAL_MOVIE_ONE_FRAME_SEC = 1 / 30.0    # 30 fps Allen convention


@dataclass
class AllenRecording:
    """A single Allen Brain Observatory session, restricted to one area."""
    session_id: int
    subject_id: int
    genotype: str
    sex: str
    age_in_days: float
    area: str
    n_units_total: int                            # total in NWB units table
    n_units_in_area: int                          # before QC
    n_units_qc_passing: int                       # after QC
    units: pd.DataFrame                           # per-unit metadata (QC-passing
                                                    # only, indexed by NWB unit id)
    spike_times: dict[int, np.ndarray] = field(default_factory=dict)
                                                    # unit_id → spike-time array (s)
    drifting_gratings: pd.DataFrame = field(default_factory=pd.DataFrame)
                                                    # presentation table (start, stop,
                                                    # orientation, temporal_frequency)
    natural_movie_one: pd.DataFrame = field(default_factory=pd.DataFrame)
                                                    # presentation table per frame
    spontaneous: pd.DataFrame = field(default_factory=pd.DataFrame)
                                                    # spontaneous-epoch table
    static_gratings: pd.DataFrame = field(default_factory=pd.DataFrame)
    analysis_metrics: pd.DataFrame = field(default_factory=pd.DataFrame)
                                                    # Allen's precomputed tuning
                                                    # values for sanity check

    def n_spikes_per_unit(self) -> pd.Series:
        return pd.Series({uid: int(self.spike_times[uid].size)
                            for uid in self.units.index})

    def mean_rate_per_unit(self, duration_sec: float) -> pd.Series:
        n = self.n_spikes_per_unit()
        return n / max(duration_sec, 1e-9)

    def session_duration_sec(self) -> float:
        """Approximate session duration from all loaded spikes."""
        if not self.spike_times: return 0.0
        all_t = np.concatenate(list(self.spike_times.values()))
        if all_t.size == 0: return 0.0
        return float(all_t.max() - all_t.min())

    def spikes_in_window(self, unit_id: int,
                          start_s: float, end_s: float) -> np.ndarray:
        """Restrict a unit's spike train to a single time window."""
        sp = self.spike_times.get(unit_id, np.zeros(0))
        return sp[(sp >= start_s) & (sp < end_s)]

    def concatenated_spikes_drifting(self, unit_id: int,
                                       direction: Optional[float] = None,
                                       gap_sec: float = 0.0) -> np.ndarray:
        """Concatenate per-presentation spike trains for one unit on the
        drifting-gratings stimulus.  If direction is None, all directions
        are concatenated; else only presentations at that orientation."""
        if direction is not None:
            pres = self.drifting_gratings[
                self.drifting_gratings['orientation'] == direction]
        else:
            pres = self.drifting_gratings
        sp = self.spike_times.get(unit_id, np.zeros(0))
        chunks, offset = [], 0.0
        for _, row in pres.iterrows():
            mask = (sp >= row['start_time']) & (sp < row['stop_time'])
            ev = sp[mask] - row['start_time'] + offset
            chunks.append(ev)
            offset += (row['stop_time'] - row['start_time']) + gap_sec
        return (np.sort(np.concatenate(chunks)) if chunks
                  else np.zeros(0, dtype=np.float64))

    def concatenated_spikes_natural_movie_one(self, unit_id: int,
                                                gap_sec: float = 0.0) -> np.ndarray:
        """Concatenate spikes during all natural_movie_one presentations.
        Allen presents this as 30 repetitions of a 30 s clip, with each
        of the 600 frames as a separate row in the intervals table.  We
        group by stimulus_block (each block = one full clip presentation)."""
        if not len(self.natural_movie_one):
            return np.zeros(0, dtype=np.float64)
        sp = self.spike_times.get(unit_id, np.zeros(0))
        # Group by stimulus_block: each block is one full 30s clip
        chunks, offset = [], 0.0
        for block_id, group in self.natural_movie_one.groupby('stimulus_block',
                                                                  sort=True):
            t0 = float(group['start_time'].min())
            t1 = float(group['stop_time'].max())
            mask = (sp >= t0) & (sp < t1)
            ev = sp[mask] - t0 + offset
            chunks.append(ev)
            offset += (t1 - t0) + gap_sec
        return (np.sort(np.concatenate(chunks)) if chunks
                  else np.zeros(0, dtype=np.float64))

    def concatenated_spikes_spontaneous(self, unit_id: int,
                                          min_block_sec: float = 5.0,
                                          gap_sec: float = 0.0) -> np.ndarray:
        """Concatenate spikes from all spontaneous epochs ≥ min_block_sec."""
        if not len(self.spontaneous):
            return np.zeros(0, dtype=np.float64)
        sp = self.spike_times.get(unit_id, np.zeros(0))
        chunks, offset = [], 0.0
        for _, row in self.spontaneous.iterrows():
            dur = row['stop_time'] - row['start_time']
            if dur < min_block_sec: continue
            mask = (sp >= row['start_time']) & (sp < row['stop_time'])
            ev = sp[mask] - row['start_time'] + offset
            chunks.append(ev)
            offset += dur + gap_sec
        return (np.sort(np.concatenate(chunks)) if chunks
                  else np.zeros(0, dtype=np.float64))


# ─── default quality filter ────────────────────────────────────────────────


def allen_default_qc(units_df: pd.DataFrame) -> pd.Series:
    """Boolean mask of units passing the Allen-default quality filter.

    Mirrors `allensdk.brain_observatory.ecephys.ecephys_session_api.
    EcephysNwbSessionApi`'s default filter.
    """
    return ((units_df['quality'] == 'good')
              & (units_df['isi_violations'] < 0.5)
              & (units_df['presence_ratio'] > 0.9)
              & (units_df['amplitude_cutoff'] < 0.1)
              & (units_df['snr'] > 1.0))


# ─── loader ────────────────────────────────────────────────────────────────


def load_session(session_id: int,
                 area: str = DEFAULT_AREA,
                 cache_dir: Path = ALLEN_CACHE) -> AllenRecording:
    """Load an Allen Brain Observatory Visual Coding Neuropixels session
    and restrict to units in `area`."""
    nwb_path = cache_dir / f'session_{session_id}' / f'session_{session_id}.nwb'
    metrics_path = cache_dir / f'session_{session_id}' / f'session_{session_id}_analysis_metrics.csv'
    if not nwb_path.exists():
        raise FileNotFoundError(f'NWB not found: {nwb_path}')

    io = pynwb.NWBHDF5IO(str(nwb_path), 'r', load_namespaces=True)
    nwb = io.read()
    subject = nwb.subject

    # Units + electrode-area join
    units_df = nwb.units.to_dataframe()
    elec_df = nwb.electrodes.to_dataframe()
    peak_to_loc = elec_df['location']
    units_df['area'] = units_df['peak_channel_id'].map(
        lambda ch: peak_to_loc.get(ch, 'unknown'))

    n_units_total = len(units_df)
    in_area = units_df[units_df['area'] == area].copy()
    n_in_area = len(in_area)
    qc_mask = allen_default_qc(in_area)
    keep = in_area[qc_mask].copy()
    n_qc = len(keep)

    # Spike-times: pull only the kept units' spike trains
    spike_times = {}
    units = nwb.units
    # Build unit_id → row index map
    id_list = list(units.id[:])
    id_to_row = {uid: i for i, uid in enumerate(id_list)}
    for uid in keep.index:
        row_idx = id_to_row[uid]
        sp = np.asarray(units['spike_times'][row_idx], dtype=np.float64)
        spike_times[int(uid)] = sp

    # Stimulus tables (drop heavyweight tags/timeseries cols)
    def _table(name):
        if name not in nwb.intervals: return pd.DataFrame()
        df = nwb.intervals[name].to_dataframe()
        keep_cols = [c for c in df.columns if c not in ('tags', 'timeseries')]
        return df[keep_cols].reset_index(drop=True)

    drifting = _table('drifting_gratings_presentations')
    natural_one = _table('natural_movie_one_presentations')
    spontaneous = _table('spontaneous_presentations')
    static = _table('static_gratings_presentations')

    # Allen precomputed metrics (sanity check)
    if metrics_path.exists():
        metrics = pd.read_csv(metrics_path).set_index('ecephys_unit_id')
    else:
        metrics = pd.DataFrame()

    rec = AllenRecording(
        session_id=int(session_id),
        subject_id=int(subject.subject_id),
        genotype=str(subject.genotype),
        sex=str(subject.sex),
        age_in_days=float(subject.age_in_days),
        area=area,
        n_units_total=int(n_units_total),
        n_units_in_area=int(n_in_area),
        n_units_qc_passing=int(n_qc),
        units=keep,
        spike_times=spike_times,
        drifting_gratings=drifting,
        natural_movie_one=natural_one,
        spontaneous=spontaneous,
        static_gratings=static,
        analysis_metrics=metrics,
    )
    io.close()
    return rec


def summarize(rec: AllenRecording) -> dict:
    n_spk = rec.n_spikes_per_unit()
    return dict(
        session_id=rec.session_id,
        subject_id=rec.subject_id,
        genotype=rec.genotype,
        sex=rec.sex,
        age_in_days=rec.age_in_days,
        area=rec.area,
        n_units_total=rec.n_units_total,
        n_units_in_area=rec.n_units_in_area,
        n_units_qc_passing=rec.n_units_qc_passing,
        median_snr=float(rec.units['snr'].median()),
        median_firing_rate=float(rec.units['firing_rate'].median()),
        n_spikes_per_unit_median=int(n_spk.median()),
        n_spikes_per_unit_min=int(n_spk.min()),
        n_spikes_per_unit_max=int(n_spk.max()),
        n_drifting_presentations=len(rec.drifting_gratings),
        n_natural_movie_presentations=len(rec.natural_movie_one),
        n_spontaneous_blocks=len(rec.spontaneous),
        n_analysis_metrics=len(rec.analysis_metrics),
    )


# ─── stimulus templates (Phase 24 Full extension) ─────────────────────────


NATURAL_MOVIE_ONE_FRAME_RATE = 30.0   # fps; Allen documents 30 fps for
                                       # natural_movie_1 (the 30 s "Touch
                                       # of Evil" clip)


def load_natural_movie_one_template(cache_dir: Path = ALLEN_CACHE) -> np.ndarray:
    """Load the natural_movie_one template as a (n_frames, h, w) uint8 array.

    The file at `natural_movie_templates/natural_movie_1.h5` is misnamed
    — it's actually a NumPy .npy file with shape (900, 304, 608) uint8.
    Load via numpy.load.
    """
    path = cache_dir / 'natural_movie_1.h5'
    if not path.exists():
        raise FileNotFoundError(f'natural_movie_1 template not found: {path}')
    return np.load(path)


def align_movie_template_to_population_bins(rec: AllenRecording,
                                              template: np.ndarray,
                                              bin_ms: float = 5.0,
                                              downsample: int = 8,
                                              ) -> tuple[np.ndarray, list[tuple[float, float]]]:
    """Build a (n_bins, n_pixels) per-bin stimulus-drive matrix from the
    natural_movie_one template, aligned to each presentation-block's
    timing.

    Args:
      template: (n_frames, h, w) uint8 from load_natural_movie_one_template.
      bin_ms: classification bin width in ms.
      downsample: per-axis spatial downsample factor (default 8 →
                   38×76 ≈ 2,900 pixels at the original 304×608 template,
                   matrix size O(60K bins × 3K pixels × 4 bytes) ≈ 700 MB
                   per session, manageable).

    Returns:
      stim_per_bin: (n_total_bins, n_pixels) float32 in [0, 1].
      block_chunks: list of (start_s, stop_s) for each block.
    """
    if not len(rec.natural_movie_one):
        return np.zeros((0, 1), dtype=np.float32), []
    n_frames, h, w = template.shape
    # Downsample spatial via stride
    template_ds = template[:, ::downsample, ::downsample]
    h_ds, w_ds = template_ds.shape[1], template_ds.shape[2]
    n_pixels = h_ds * w_ds
    template_flat = (template_ds.reshape(n_frames, n_pixels)
                       .astype(np.float32) / 255.0)
    bin_s = bin_ms / 1000.0

    # Per-block timing
    block_chunks = []
    for blk, group in rec.natural_movie_one.groupby('stimulus_block', sort=True):
        t0 = float(group['start_time'].min())
        t1 = float(group['stop_time'].max())
        block_chunks.append((t0, t1))

    # Per-bin frame index, concatenated across blocks
    chunks_per_bin = []
    for (t0, t1) in block_chunks:
        n_block_bins = int(np.ceil((t1 - t0) / bin_s))
        bin_centres = (np.arange(n_block_bins) + 0.5) * bin_s
        # Frame index = bin_centre × frame_rate; cap at n_frames-1
        frame_idx = np.clip((bin_centres * NATURAL_MOVIE_ONE_FRAME_RATE)
                              .astype(np.int64), 0, n_frames - 1)
        chunks_per_bin.append(template_flat[frame_idx])
    stim_per_bin = np.concatenate(chunks_per_bin, axis=0)
    return stim_per_bin, block_chunks


def grating_template_per_bin(rec: AllenRecording,
                                stimulus: str = 'drifting',
                                bin_ms: float = 5.0,
                                grid_pixels: int = 32,
                                ) -> tuple[np.ndarray, list[tuple[float, float]]]:
    """Generate a per-bin stimulus matrix for drifting (or static) gratings.

    The grating is rendered as a grid_pixels × grid_pixels intensity image
    per bin, parameterised by Allen's per-presentation orientation +
    spatial frequency + temporal frequency + phase.  This is a simplified
    template (the actual stimulus is full-screen with Allen's specific
    parameters), sufficient for the LN-Poisson surrogate's STA → drive
    pipeline.

    Returns (stim_per_bin, chunks) matching the natural-movie template
    helper's interface.
    """
    if stimulus == 'drifting':
        pres = rec.drifting_gratings
    elif stimulus == 'static':
        pres = rec.static_gratings
    else:
        raise ValueError(f'unknown stimulus: {stimulus}')
    if not len(pres):
        return np.zeros((0, grid_pixels * grid_pixels), dtype=np.float32), []

    bin_s = bin_ms / 1000.0
    # Build a grid of (x, y) coordinates in [-1, 1]
    coords = np.linspace(-1, 1, grid_pixels)
    xx, yy = np.meshgrid(coords, coords)

    chunks_per_bin = []
    chunks = []
    for _, row in pres.iterrows():
        t0 = float(row['start_time']); t1 = float(row['stop_time'])
        chunks.append((t0, t1))
        ori = row.get('orientation', np.nan)
        sf = row.get('spatial_frequency', 0.04)
        tf = row.get('temporal_frequency', 2.0)
        phase = row.get('phase', 0.0)
        if isinstance(phase, str): phase = 0.0
        if pd.isna(ori) or pd.isna(sf) or pd.isna(tf):
            # Blank or unstructured presentation; render uniform grey
            n_b = int(np.ceil((t1 - t0) / bin_s))
            chunks_per_bin.append(np.full((n_b, grid_pixels * grid_pixels),
                                            0.5, dtype=np.float32))
            continue
        ori_rad = float(ori) * np.pi / 180
        kx = 2 * np.pi * sf * np.cos(ori_rad)
        ky = 2 * np.pi * sf * np.sin(ori_rad)
        n_b = int(np.ceil((t1 - t0) / bin_s))
        bin_centres = (np.arange(n_b) + 0.5) * bin_s
        # rendered_grating[t, x, y] = 0.5 + 0.5 * sin(kx*x + ky*y - 2π·tf·t + phase)
        block = np.zeros((n_b, grid_pixels * grid_pixels), dtype=np.float32)
        for i, t in enumerate(bin_centres):
            grating = 0.5 + 0.5 * np.sin(kx * xx + ky * yy
                                            - 2 * np.pi * tf * t + phase)
            block[i] = grating.flatten()
        chunks_per_bin.append(block)
    stim_per_bin = np.concatenate(chunks_per_bin, axis=0)
    return stim_per_bin, chunks


__all__ = [
    'AllenRecording', 'allen_default_qc', 'load_session', 'summarize',
    'ALLEN_CACHE', 'DEFAULT_AREA',
    'load_natural_movie_one_template',
    'align_movie_template_to_population_bins',
    'grating_template_per_bin',
    'NATURAL_MOVIE_ONE_FRAME_RATE',
]
