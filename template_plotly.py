"""Reference canvases in the house CMS style, Plotly / plotlyhep edition -- the same toy inputs and canvases
as template.py (a made-up J/psi K+ peak); labels are placeholders. Writes <outdir>/plotly_<name>.json (for
HTML embedding) and .png (kaleido).

    python template_plotly.py --demo all --outdir /tmp/cmsplot_demo
"""
from __future__ import annotations

import argparse
import os
import sys

import numpy as np
from scipy.stats import chi2 as chi2dist

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from cmsplot_plotly import (SERIES, PLAIN_SIZE, bin_label, cms_label, data_points, draw_pull, figure,  # noqa: E402
                            fill_between, fit_figure, headroom, legend, line, save, step, xlabel, ylabel, zero_line)

RUN3 = dict(com=13.6, rlabel="2024, X fb<sup>−1</sup> (13.6 TeV)")
LO, HI, NB = 5.15, 5.45, 60
M0, S0 = 5.2793, 0.013
MLB = "m(J/ψ K<sup>+</sup>) [GeV]"
MKPI = "m(K<sup>+</sup>π<sup>−</sup>) [GeV]"
SEL = "p<sub>T</sub>(K<sup>+</sup>) > 1 GeV"
rng = np.random.default_rng(1)


def toy_mass(nsig=4000, nbkg=60000):
    x = np.r_[rng.normal(M0, S0, nsig), LO + (HI - LO) * rng.power(0.8, nbkg)]
    h, e = np.histogram(x, bins=NB, range=(LO, HI))
    cen, bw = 0.5 * (e[:-1] + e[1:]), e[1] - e[0]
    sig = nsig * bw * np.exp(-0.5 * ((cen - M0) / S0) ** 2) / (S0 * np.sqrt(2 * np.pi))
    bkg = nbkg * 0.8 * ((cen - LO) / (HI - LO)) ** -0.2 / (HI - LO) * bw
    return cen, bw, h.astype(float), sig, bkg


def demo_fit(out):
    """Mass fit: data, background, stacked signal, total, pull; selection in the legend title."""
    cen, bw, h, sig, bkg = toy_mass()
    fig, ax, axp = fit_figure()
    cms_label(fig, **RUN3)
    line(fig, cen, bkg, SERIES["comb"], "background", dash="dash", width=1.5)
    fill_between(fig, cen, bkg, bkg + sig, SERIES["s1"], "B<sup>+</sup>: 4000 ± 120")
    line(fig, cen, bkg + sig, SERIES["total"], "fit")
    data_points(fig, cen, h)                                            # data last: drawn on top
    ylabel(fig, bin_label(bw))                                          # bin width in GeV, never MeV
    headroom(fig, np.max(h + np.sqrt(h)))                               # room for the legend
    legend(fig, title=SEL)
    draw_pull(fig, axp, cen, h, bkg + sig, LO, HI, MLB)
    save(fig, f"{out}/plotly_fit.png")


def demo_weighted(out):
    """Weighted spectrum (sWeights / COWs): errors sqrt(sum w^2), zero line, pull with err=."""
    lo, hi, nb = 0.60, 1.40, 80
    x = rng.uniform(lo, hi, 40000); w = rng.normal(0.25, 1.0, len(x))
    h, e = np.histogram(x, bins=nb, range=(lo, hi), weights=w)
    h2, _ = np.histogram(x, bins=nb, range=(lo, hi), weights=w * w)
    cen, bw, err = 0.5 * (e[:-1] + e[1:]), e[1] - e[0], np.sqrt(h2)
    model = np.full(nb, h.mean())
    fig, ax, axp = fit_figure()
    cms_label(fig, **RUN3)
    zero_line(fig)
    step(fig, e, model, SERIES["total"], "fit", width=2)
    data_points(fig, cen, h, err, label="B<sup>+</sup> → J/ψ K<sup>+</sup>")
    ylabel(fig, bin_label(bw, what="weighted candidates"))
    headroom(fig, np.max(h + err), bottom=min(0, np.min(h - err)) * 1.1, factor=1.35)
    legend(fig, title=SEL)
    draw_pull(fig, axp, cen, h, model, lo, hi, MKPI, err=err)
    save(fig, f"{out}/plotly_weighted.png")


def demo_compare(out):
    """Two estimates of one spectrum: markers offset by +-0.15 bin, lower panel the difference / sigma."""
    lo, hi, nb = 0.60, 1.40, 40
    cen = np.linspace(lo, hi, nb + 1); bw = cen[1] - cen[0]; cen = cen[:-1] + bw / 2
    a, ea = 200 + rng.normal(0, 30, nb), np.full(nb, 30.0)
    b, eb = a + rng.normal(0, 15, nb), np.full(nb, 32.0)
    fig, ax, axp = fit_figure()
    cms_label(fig, **RUN3)
    data_points(fig, cen - 0.15 * bw, b, eb, label="weighted", color=SERIES["comb"], symbol="square", size=3)
    data_points(fig, cen + 0.15 * bw, a, ea, label="fitted yield per bin")
    ylabel(fig, bin_label(bw, what="signal candidates"))
    headroom(fig, np.max(a + ea), factor=1.35)
    legend(fig)
    zero_line(fig, axp)
    data_points(fig, cen, (a - b) / ea, np.zeros(nb), label=None, ax=axp, size=3)
    ylabel(fig, "Δ/σ<sub>fit</sub>", ax=axp)
    fig.update_layout(yaxis2=dict(range=[-3, 3]))
    fig.update_xaxes(range=[lo, hi])
    xlabel(fig, MKPI)
    save(fig, f"{out}/plotly_compare.png")


def demo_scan(out):
    """Stability scan: value vs the scanned choice, nominal dashed; no pull panel."""
    order = np.arange(3, 11); v = 900 + rng.normal(0, 60, len(order)); e = np.linspace(210, 260, len(order))
    fig = figure(PLAIN_SIZE)
    cms_label(fig, **RUN3)
    data_points(fig, order, v, e, label="signal yield", size=4)
    line(fig, [order[0] - 0.5, order[-1] + 0.5], [v[0], v[0]], SERIES["total"], "chosen order", dash="dash")
    fig.update_xaxes(range=[order[0] - 0.5, order[-1] + 0.5])
    headroom(fig, np.max(v + e), bottom=0.9 * np.min(v - e), factor=1.2)
    xlabel(fig, "background Chebyshev coefficients"); ylabel(fig, "yield")
    legend(fig)
    save(fig, f"{out}/plotly_scan.png")


def demo_toys(out):
    """Toy calibration: toy histogram, expected chi2(ndf), observed value; label the bin width, not the count."""
    q = rng.chisquare(6, 300); bw = 1.0; edges = np.arange(0, 32 + bw, bw)
    h, _ = np.histogram(q, bins=edges)
    fig = figure(PLAIN_SIZE)
    cms_label(fig, **RUN3)
    step(fig, edges, h, SERIES["data"], "toys")
    xs = np.linspace(0, 32, 400)
    line(fig, xs, len(q) * bw * chi2dist.pdf(xs, 6), SERIES["total"], "χ<sup>2</sup>(6)")
    line(fig, [21.0, 21.0], [0, 1.15 * h.max()], SERIES["s1"], "data")
    headroom(fig, h.max(), factor=1.3)
    xlabel(fig, "q = 2ΔNLL"); ylabel(fig, f"toys / {bw:g}", chars=2)
    legend(fig)
    save(fig, f"{out}/plotly_toys.png")


DEMOS = {"fit": demo_fit, "weighted": demo_weighted, "compare": demo_compare, "scan": demo_scan, "toys": demo_toys}

if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--demo", choices=list(DEMOS) + ["all"], default="all")
    ap.add_argument("--outdir", default="plots/style_demo")
    a = ap.parse_args()
    os.makedirs(a.outdir, exist_ok=True)
    for k, f in DEMOS.items():
        if a.demo in (k, "all"):
            f(a.outdir); print(f"wrote {a.outdir}/plotly_{k}.png (+ .json)")
