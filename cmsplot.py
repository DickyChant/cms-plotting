"""cmsplot -- one small module for CMS-style analysis canvases (matplotlib + mplhep).

Import it once; it applies the CMS style. Drop the file next to your scripts or into your package
(e.g. as `<pkg>/plotting.py`). Pure matplotlib/numpy; mplhep is optional (no CMS label without it).

    from cmsplot import fit_figure, cms_label, draw_pull, bin_label, SERIES, save
"""
from __future__ import annotations

import os
import numpy as np
import matplotlib.pyplot as plt

try:
    import mplhep as hep
    plt.style.use(hep.style.CMS)
    # fit + pull canvases are small; dial the CMS fonts down a touch
    plt.rcParams.update({"font.size": 13, "axes.labelsize": 15, "axes.titlesize": 13,
                         "legend.fontsize": 11, "xtick.labelsize": 12, "ytick.labelsize": 12})
    _HEP = True
except Exception:
    _HEP = False

# ---------------------------------------------------------------------------
# Categorical palette (validated: lightness band, chroma floor, CVD separation worst adjacent
# dE 9.1 protan, normal-vision floor 16.3). Assign in FIXED order, never cycle: a new component
# takes the next free slot. Some slots are below 3:1 contrast, so every series carries a legend entry.
# ---------------------------------------------------------------------------
SERIES = {
    "total":   "#4a3aa7",   # the summed model
    "comb":    "#2a78d6",   # combinatorial / main background
    "s1":      "#eb6834",   # component slot 1 (usually the signal)
    "s2":      "#1baf7a",   # component slot 2
    "s3":      "#eda100",   # component slot 3
    "s4":      "#e87ba4",   # component slot 4
    "data":    "#0b0b0b",   # data points wear text ink, not a series hue
    "signal":  "#008300",   # background-subtracted signal overlay
}
SERIES_ORDER = [SERIES["s1"], SERIES["s2"], SERIES["s3"], SERIES["s4"]]

FIT_SIZE = (7.8, 6.6)      # main + pull
PLAIN_SIZE = (7.8, 5.2)    # single panel
DPI = 140


def cms_label(ax, com=13.6, data=True, rlabel=None, fontsize=15, status="Work in Progress"):
    """'CMS <status>' top-left, rlabel (era, luminosity, energy) top-right. data=False -> Simulation."""
    if not _HEP:
        return
    hep.cms.label(status, data=data, com=com, ax=ax, rlabel=rlabel, fontsize=fontsize)


def make_fit_axes(fig, subplotspec):
    """Main + pull axes (heights 4:1) sharing x."""
    gs = subplotspec.subgridspec(2, 1, height_ratios=[4, 1], hspace=0.04)
    ax = fig.add_subplot(gs[0]); axp = fig.add_subplot(gs[1], sharex=ax)
    plt.setp(ax.get_xticklabels(), visible=False)
    return ax, axp


def make_fit_axes3(fig, subplotspec):
    """Main + background-subtracted + pull axes (heights 4:1.6:1) sharing x."""
    gs = subplotspec.subgridspec(3, 1, height_ratios=[4, 1.6, 1], hspace=0.05)
    ax = fig.add_subplot(gs[0]); axb = fig.add_subplot(gs[1], sharex=ax); axp = fig.add_subplot(gs[2], sharex=ax)
    plt.setp(ax.get_xticklabels(), visible=False); plt.setp(axb.get_xticklabels(), visible=False)
    return ax, axb, axp


def fit_figure(three=False):
    """New figure with fit axes: (fig, ax, axp) or, three=True, (fig, ax, axb, axp)."""
    fig = plt.figure(figsize=FIT_SIZE if not three else (7.8, 7.6))
    spec = fig.add_gridspec(1, 1)[0]
    return (fig, *(make_fit_axes3(fig, spec) if three else make_fit_axes(fig, spec)))


def draw_pull(axp, centers, counts, expected, lo, hi, xlabel, ylabel="pull", err=None):
    """Pull panel (n - f) / err with a |pull| < 2 band. Pass err for weighted data (sqrt(sum w^2));
    the default sqrt(n) is only right for raw counts. Returns chi2 / filled bins."""
    if err is None:
        err = np.sqrt(np.where(counts > 0, counts, 1.0))
    pull = (counts - expected) / err
    axp.axhspan(-2, 2, color="0.85", zorder=0)
    axp.axhline(0, color="r", lw=1, zorder=1)
    axp.plot(centers, pull, "k.", ms=3, zorder=2)
    axp.set_ylim(-5, 5); axp.set_xlim(lo, hi); axp.set_yticks([-3, 0, 3])
    axp.set_ylabel(ylabel, fontsize=13); axp.set_xlabel(xlabel)
    mask = counts > 0
    return float(np.sum(pull[mask] ** 2) / max(int(mask.sum()), 1))


def draw_bkgsub(axb, centers, counts, bkg_at_centers, x_curve, sig_curve, lo, hi, ylabel="data $-$ bkg", err=None):
    """Data minus fitted background (points) with the fitted signal curve."""
    if err is None:
        err = np.sqrt(np.where(counts > 0, counts, 1.0))
    axb.axhline(0, color="grey", lw=0.8)
    axb.errorbar(centers, counts - bkg_at_centers, yerr=err, fmt="k.", ms=3, zorder=2)
    axb.plot(x_curve, sig_curve, "-", color=SERIES["signal"], lw=1.6, zorder=3)
    axb.set_xlim(lo, hi); axb.set_ylabel(ylabel, fontsize=13)


def bin_label(bw, unit="GeV", what="candidates"):
    """y label with the bin width in the x-axis unit: 'candidates / 0.005 GeV'. Never a bin count."""
    w = f"{bw:.3f}" if unit == "GeV" and bw < 1 else f"{bw:g}"
    return f"{what} / {w} {unit}".rstrip()


def data_points(ax, cen, h, err=None, label="data"):
    if err is None:
        err = np.sqrt(np.maximum(h, 0))
    return ax.errorbar(cen, h, yerr=err, fmt="o", ms=3.4, color=SERIES["data"], label=label, zorder=5)


def legend(ax, title=None, ncol=1, loc="upper right"):
    """House legend: no frame, the selection as the legend title (not as text on the canvas)."""
    return ax.legend(frameon=False, loc=loc, fontsize=10, ncol=ncol, title=title, title_fontsize=10)


def headroom(ax, top, bottom=0.0, factor=1.4):
    """Leave room above the data for the legend."""
    ax.set_ylim(bottom, top * factor)


def save(fig, path, dpi=DPI):
    """tight_layout + savefig + close, creating the folder."""
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    fig.tight_layout(); fig.savefig(path, dpi=dpi); plt.close(fig)
    return path


def save_panels(axes, stem, ext="png", dpi=DPI, **label_kw):
    """Re-draw is not possible in matplotlib, so for grids build each panel with a function and call it
    twice -- once into the grid, once into its own figure. This helper does that:
        save_panels({"pt": draw_pt, "eta": draw_eta}, "plots/feat")   # draw_x(ax) -> None
    writes plots/feat_pt.png, plots/feat_eta.png and plots/feat_grid.png."""
    names = list(axes)
    n = len(names); nc = min(n, 3); nr = (n + nc - 1) // nc
    fig, grid = plt.subplots(nr, nc, figsize=(5.2 * nc, 4.4 * nr), squeeze=False)
    for g, k in zip(grid.flat, names):
        axes[k](g)
    for g in list(grid.flat)[n:]:
        g.set_visible(False)
    save(fig, f"{stem}_grid.{ext}", dpi)
    out = []
    for k in names:
        f, a = plt.subplots(figsize=PLAIN_SIZE)
        if label_kw:
            cms_label(a, **label_kw)
        axes[k](a)
        out.append(save(f, f"{stem}_{k}.{ext}", dpi))
    return out
