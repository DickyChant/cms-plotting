# cms-plotting

A Claude Code skill (and a plain Python module) for CMS-style analysis canvases: mass fits with pull
panels, weighted spectra, method comparisons, stability scans and toy calibrations — plus the rules for
reporting results with them (every number with its fit canvas, no prose on canvases, bin widths in the
axis unit, single-panel files for slides).

| fit | weighted | compare |
|---|---|---|
| ![fit](examples/fit.png) | ![weighted](examples/weighted.png) | ![compare](examples/compare.png) |
| **scan** | **toys** | |
| ![scan](examples/scan.png) | ![toys](examples/toys.png) | |

All examples are toy inputs with placeholder labels.

## Install in Claude Code

The repository root is the skill. Clone it into a skills folder:

```bash
# for you, in every project
git clone https://github.com/DickyChant/cms-plotting ~/.claude/skills/cms-plotting

# or for one project (commit it, or add it as a submodule)
git clone https://github.com/DickyChant/cms-plotting .claude/skills/cms-plotting
```

Update with `git -C ~/.claude/skills/cms-plotting pull`. The skill loads whenever Claude writes plotting
code or reports fitted numbers.

## Use without Claude

`cmsplot.py` is a standalone module (numpy, matplotlib, optional mplhep). Copy it into
your project:

```python
from cmsplot import fit_figure, cms_label, data_points, draw_pull, bin_label, legend, headroom, save, SERIES

fig, ax, axp = fit_figure()
cms_label(ax, com=13.6, rlabel="2024, X fb$^{-1}$ (13.6 TeV)")
data_points(ax, cen, h)
ax.plot(cen, bkg, "--", color=SERIES["comb"], lw=1.5, label="background")
ax.fill_between(cen, bkg, bkg + sig, color=SERIES["s1"], alpha=0.45, lw=0, label="signal")
ax.plot(cen, bkg + sig, color=SERIES["total"], lw=2, label="fit")
ax.set_ylabel(bin_label(bw)); legend(ax, title="selection"); headroom(ax, h.max())
draw_pull(axp, cen, h, bkg + sig, lo, hi, r"$m(J/\psi\,K^+)$ [GeV]")
save(fig, "plots/fit.png")
```

`python template.py --outdir /tmp/demo` draws all five reference canvases;
`python lint.py my_script.py` checks a script against the rules.

## Contributing

Open an issue or a pull request. Keep it generic: no analysis results, unpublished luminosities or sample
paths. When the style changes, regenerate `examples/` with `python template.py --outdir examples`.

MIT licensed.
