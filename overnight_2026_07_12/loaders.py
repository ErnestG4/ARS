"""Per-cell raw spike-train loaders for the 2026-07-12 overnight ISI-shuffle recompute.

Yields (cell_id, spike_times) so Job A can shuffle ISIs *within cell*.
Extraction replicates each port module exactly (verified by reading them); cell
counts are compared against the banked coordinates so selection drift is VISIBLE.
"""
import os, sys, glob
import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "cross_substrate"))

MIN_SPIKES = 100


def load_allen_hpf():
    import h5py
    import allen_hpf as A
    tg = A.build_hpf_targets()
    for f in sorted(glob.glob(A.NWB_GLOB)):
        sid = int(os.path.basename(os.path.dirname(f)).split("_")[1])
        sub = tg[tg["session_id"] == sid]
        if sub.empty:
            continue
        with h5py.File(f, "r") as h:
            iv = A._spont_intervals(h)
            if iv is None:
                continue
            ids = h["units/id"][:]
            row_of = {int(u): r for r, u in enumerate(ids)}
            sti = h["units/spike_times_index"]
            st_all = h["units/spike_times"]
            for _, rec in sub.iterrows():
                uid = int(rec["id"])
                if uid not in row_of:
                    continue
                r = row_of[uid]
                lo = 0 if r == 0 else int(sti[r - 1])
                spk = np.asarray(st_all[lo:int(sti[r])], dtype=np.float64)
                m = np.zeros(spk.size, bool)
                for s0, s1 in iv:
                    m |= (spk >= s0) & (spk < s1)
                spk = np.sort(spk[m])
                if spk.size < MIN_SPIKES:
                    continue
                yield (f"allen/{sid}/{uid}", spk)


def load_hc3():
    import hc3_port as H
    cellmap = H.load_cell_table()
    for sdir in sorted(glob.glob(os.path.join(H.SESS_ROOT, "*", "*"))):
        if not os.path.isdir(sdir):
            continue
        parts = sdir.rstrip(os.sep).split(os.sep)
        topdir, session = parts[-2], parts[-1]
        try:
            units, tmax, pos, sr = H.parse_session(sdir, topdir, session, cellmap)
        except Exception:
            continue
        for u in units or []:
            spk = np.sort(np.asarray(u["spk"], dtype=np.float64))
            if spk.size < MIN_SPIKES:
                continue
            yield (f"hc3/{topdir}/{session}/{u['ele']}/{u['clu']}", spk)


def load_ret1():
    import scipy.io
    import ret1_port as R
    for f in sorted(glob.glob(os.path.join(R.DATA, "*.mat"))):
        try:
            m = scipy.io.loadmat(f, squeeze_me=True, struct_as_record=False)
            stim = np.atleast_1d(m["stimulus"])
            ncell = int(getattr(m["datainfo"], "Ncell"))
            nstim = len(stim)
            sp = np.asarray(m["spikes"], dtype=object)
            if sp.ndim == 1:
                sp = sp.reshape(ncell, nstim) if nstim == 1 else sp.reshape(nstim, ncell).T
            elif sp.shape[0] != ncell and sp.shape[1] == ncell:
                sp = sp.T
            durs = [float(s.frame) * int(s.Nframes) for s in stim]
            blk = int(np.argmax(durs))
        except Exception:
            continue
        rid = os.path.basename(f).replace(".mat", "")
        for i in range(sp.shape[0]):
            spk = np.atleast_1d(sp[i, blk]).astype(float)
            spk = np.sort(spk[np.isfinite(spk)])
            if spk.size < MIN_SPIKES:
                continue
            yield (f"ret1/{rid}/{i}", spk)


LOADERS = {"allen-hpf-cell": load_allen_hpf,
           "hc3-port-cell": load_hc3,
           "ret1-cell": load_ret1}

# banked counts, for a selection-drift check (dr-port is remote-streamed: out of scope, logged)
BANKED_N = {"allen-hpf-cell": 4358, "hc3-port-cell": 923, "ret1-cell": 325}


def load_buzsaki():
    import h5py, glob as _g
    import buzsaki_port as B
    for f in sorted(_g.glob(B.BUZ_GLOB)):
        try:
            with h5py.File(f, "r") as h:
                sti = h["units/spike_times_index"][:]
                st_all = h["units/spike_times"]
                for r in range(len(sti)):
                    lo = 0 if r == 0 else int(sti[r - 1])
                    spk = np.sort(np.asarray(st_all[lo:int(sti[r])], dtype=np.float64))
                    if spk.size < MIN_SPIKES:
                        continue
                    yield (f"buz/{os.path.basename(f)}/{r}", spk)
        except Exception:
            continue


def load_ibl():
    import h5py, glob as _g
    import ibl_port as I
    for f in sorted(_g.glob(I.IBL_GLOB)):
        try:
            with h5py.File(f, "r") as h:
                u = h["units"]
                sti = u["spike_times_index"][:]
                st_all = u["spike_times"]
                for r in range(len(sti)):
                    lo = 0 if r == 0 else int(sti[r - 1])
                    spk = np.sort(np.asarray(st_all[lo:int(sti[r])], dtype=np.float64))
                    if spk.size < MIN_SPIKES:
                        continue
                    yield (f"ibl/{os.path.basename(f)}/{r}", spk)
        except Exception:
            continue


LOADERS_EXT = dict(LOADERS)
LOADERS_EXT["buzsaki-port-cell"] = load_buzsaki
LOADERS_EXT["ibl-port-cell"] = load_ibl
