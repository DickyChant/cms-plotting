"""Reference canvases in the house CMS style -- copy the block you need. Toy inputs only (a made-up
J/psi K+ peak); labels are placeholders.

    python template.py --demo all --outdir /tmp/cmsplot_demo
"""
from __future__ import annotations
import argparse, os, sys
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy.stats import chi2 as chi2dist

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from cmsplot import make_fit_axes, draw_pull, cms_label, bin_label, SERIES

RUN3 = dict(com=13.6, rlabel="2024, X fb$^{-1}$ (13.6 TeV)")
LO, HI, NB = 5.15, 5.45, 60
M0, S0 = 5.2793, 0.013
MLB = r"$m(J/\psi\,K^+)$ [GeV]"
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
    fig = plt.figure(figsize=(7.8, 6.6)); ax, axp = make_fit_axes(fig, fig.add_gridspec(1, 1)[0])
    cms_label(ax, **RUN3, fontsize=15)
    ax.errorbar(cen, h, yerr=np.sqrt(h), fmt="o", ms=3.4, color=SERIES["data"], label="data", zorder=5)
    ax.plot(cen, bkg, "--", color=SERIES["comb"], lw=1.5, label="background")
    ax.fill_between(cen, bkg, bkg + sig, color=SERIES["s1"], alpha=0.45, lw=0, label=r"$B^+$: 4000 $\pm$ 120")
    ax.plot(cen, bkg + sig, "-", color=SERIES["total"], lw=2, label="fit")
    ax.set_ylabel(bin_label(bw))                                        # bin width in GeV, never MeV
    ax.set_ylim(0, np.max(h + np.sqrt(h)) * 1.4)                       # headroom for the legend
    ax.legend(frameon=False, loc="upper right", fontsize=10, title=r"$p_T(K^+) > 1$ GeV", title_fontsize=10)
    draw_pull(axp, cen, h, bkg + sig, LO, HI, MLB)
    fig.tight_layout(); fig.savefig(f"{out}/fit.png", dpi=140); plt.close(fig)


def demo_weighted(out):
    """Weighted spectrum (sWeights / COWs): errors sqrt(sum w^2), zero line, pull with err=."""
    lo, hi, nb = 0.60, 1.40, 80
    x = rng.uniform(lo, hi, 40000); w = rng.normal(0.25, 1.0, len(x))
    h, e = np.histogram(x, bins=nb, range=(lo, hi), weights=w)
    h2, _ = np.histogram(x, bins=nb, range=(lo, hi), weights=w * w)
    cen, bw, err = 0.5 * (e[:-1] + e[1:]), e[1] - e[0], np.sqrt(h2)
    model = np.full(nb, h.mean())
    fig = plt.figure(figsize=(7.8, 6.6)); ax, axp = make_fit_axes(fig, fig.add_gridspec(1, 1)[0])
    cms_label(ax, **RUN3, fontsize=15)
    ax.axhline(0, color="grey", lw=0.8)
    ax.plot(cen, model, "-", color=SERIES["total"], lw=2, label="fit", drawstyle="steps-mid")
    ax.errorbar(cen, h, yerr=err, fmt="o", ms=3.4, color=SERIES["data"], label=r"$B^+\to J/\psi\,K^+$", zorder=5)
    ax.set_ylabel(bin_label(bw, what="weighted candidates"))
    ax.set_ylim(min(0, np.min(h - err)) * 1.1, np.max(h + err) * 1.35)
    ax.legend(frameon=False, loc="upper right", fontsize=10, title=r"$p_T(K^+) > 1$ GeV", title_fontsize=11)
    draw_pull(axp, cen, h, model, lo, hi, r"$m(K^+\pi^-)$ [GeV]", err=err)
    fig.tight_layout(); fig.savefig(f"{out}/weighted.png", dpi=140); plt.close(fig)


def demo_compare(out):
    """Two estimates of one spectrum: markers offset by +-0.15 bin, lower panel the difference / sigma."""
    lo, hi, nb = 0.60, 1.40, 40
    cen = np.linspace(lo, hi, nb + 1); bw = cen[1] - cen[0]; cen = cen[:-1] + bw / 2
    a, ea = 200 + rng.normal(0, 30, nb), np.full(nb, 30.0)
    b, eb = a + rng.normal(0, 15, nb), np.full(nb, 32.0)
    fig = plt.figure(figsize=(7.8, 6.6)); ax, axp = make_fit_axes(fig, fig.add_gridspec(1, 1)[0])
    cms_label(ax, **RUN3, fontsize=15)
    ax.errorbar(cen - 0.15 * bw, b, yerr=eb, fmt="s", ms=3, color=SERIES["comb"], label="weighted")
    ax.errorbar(cen + 0.15 * bw, a, yerr=ea, fmt="o", ms=3.4, color=SERIES["data"], label="fitted yield per bin")
    ax.set_ylabel(bin_label(bw, what="signal candidates")); ax.set_ylim(0, np.max(a + ea) * 1.35)
    ax.legend(frameon=False, loc="upper right", fontsize=10)
    axp.axhline(0, color="grey", lw=0.8); axp.plot(cen, (a - b) / ea, "o", ms=3, color=SERIES["data"])
    axp.set_ylabel(r"$\Delta/\sigma_\mathrm{fit}$"); axp.set_ylim(-3, 3); axp.set_xlim(lo, hi)
    axp.set_xlabel(r"$m(K^+\pi^-)$ [GeV]")
    fig.tight_layout(); fig.savefig(f"{out}/compare.png", dpi=140); plt.close(fig)


def demo_scan(out):
    """Stability scan: value vs the scanned choice, nominal dashed; no pull panel."""
    order = np.arange(3, 11); v = 900 + rng.normal(0, 60, len(order)); e = np.linspace(210, 260, len(order))
    fig, ax = plt.subplots(figsize=(7.8, 5.2))
    cms_label(ax, **RUN3, fontsize=15)
    ax.errorbar(order, v, yerr=e, fmt="o", ms=4, color=SERIES["data"], label="signal yield")
    ax.axhline(v[0], color=SERIES["total"], ls="--", label="chosen order")
    ax.set_xlabel("background Chebyshev coefficients"); ax.set_ylabel("yield")
    ax.legend(frameon=False, fontsize=10)
    fig.tight_layout(); fig.savefig(f"{out}/scan.png", dpi=140); plt.close(fig)


def demo_toys(out):
    """Toy calibration: toy histogram, expected chi2(ndf), observed value; label the bin width, not the count."""
    q = rng.chisquare(6, 300); bw = 1.0; edges = np.arange(0, 32 + bw, bw)
    fig, ax = plt.subplots(figsize=(7.8, 5.2))
    cms_label(ax, **RUN3, fontsize=15)
    ax.hist(q, bins=edges, histtype="step", lw=1.6, color=SERIES["data"], label="toys")
    xs = np.linspace(0, 32, 400)
    ax.plot(xs, len(q) * bw * chi2dist.pdf(xs, 6), color=SERIES["total"], lw=2, label=r"$\chi^2(6)$")
    ax.axvline(21.0, color=SERIES["s1"], lw=2, label="data")
    ax.set_xlabel(r"$q = 2\Delta\mathrm{NLL}$"); ax.set_ylabel(f"toys / {bw:g}")
    ax.legend(frameon=False, fontsize=10)
    fig.tight_layout(); fig.savefig(f"{out}/toys.png", dpi=140); plt.close(fig)


DEMOS = {"fit": demo_fit, "weighted": demo_weighted, "compare": demo_compare, "scan": demo_scan, "toys": demo_toys}

if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--demo", choices=list(DEMOS) + ["all"], default="all")
    ap.add_argument("--outdir", default="plots/style_demo")
    a = ap.parse_args()
    os.makedirs(a.outdir, exist_ok=True)
    for k, f in DEMOS.items():
        if a.demo in (k, "all"):
            f(a.outdir); print(f"wrote {a.outdir}/{k}.png")
