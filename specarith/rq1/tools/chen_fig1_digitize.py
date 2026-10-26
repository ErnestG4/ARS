"""Digitize Chen et al. Figure 1 (raster, extracted from the PDF): dark dot centroids, axes calibrated on the major
gridlines (every 0.2). Usage: python -I chen_fig1_digitize.py FIG1.png OUT.json"""
import json, sys
import numpy as np
from PIL import Image
from scipy import ndimage
im = np.asarray(Image.open(sys.argv[1]).convert("RGB")).astype(int)
H, W, _ = im.shape
dark = (im.max(2) < 90)
lab, n = ndimage.label(dark)
cents = ndimage.center_of_mass(dark, lab, range(1, n + 1))
sizes = ndimage.sum(dark, lab, range(1, n + 1))
dots = [(c[1], c[0]) for c, s in zip(cents, sizes) if 80 <= s <= 400]          # dot area ~150 px; text/axes excluded
grey = (np.abs(im[..., 0] - im[..., 1]) < 12) & (im.max(2) < 200) & (im.max(2) > 90)
colfrac, rowfrac = grey.mean(0), grey.mean(1)
cols = [x for x in range(1, W - 1) if colfrac[x] > 0.5 and colfrac[x] >= colfrac[x - 1] and colfrac[x] >= colfrac[x + 1]]
rows = [y for y in range(1, H - 1) if rowfrac[y] > 0.5 and rowfrac[y] >= rowfrac[y - 1] and rowfrac[y] >= rowfrac[y + 1]]
json.dump(dict(dots=dots, major_cols=cols, major_rows=rows, size=[W, H]), open(sys.argv[2], "w"))
print(len(dots), "dots; major cols", cols, "rows", rows)
