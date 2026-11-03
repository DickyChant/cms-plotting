---
name: cms-plotting
description: CMS-style analysis canvases (mass fits with pulls, weighted spectra, method comparisons, scans, toy calibrations) and the rules for showing results, in matplotlib/mplhep and in Plotly/plotlyhep (interactive figures for HTML slides). Use whenever writing or editing code that saves or embeds a plot in a HEP/CMS analysis (matplotlib, mplhep, plotly, plotlyhep), before reporting any fitted number, or when choosing figures for a note or slides.
---

# CMS plotting

`cmsplot.py` (next to this file) is the style: mplhep CMS style on import, `cms_label`, fit + pull axes,
`draw_pull`, `bin_label`, the validated `SERIES` palette, `save` / `save_panels`. A project either imports it
or keeps its own copy in its package (e.g. `<pkg>/plotting.py`) -- if the project already has a plotting
module, use that one and never restyle locally. `template.py` draws every standard canvas on toy inputs;
`lint.py` checks scripts against the rules. All three sit in this skill's base directory. Run lint on every
plotting script you write or edit:

```bash
python <skill base dir>/lint.py path/to/script.py --style-module <pkg>.plotting
```

A project without a plotting module: copy `cmsplot.py` into it (do not import it from the skills folder, which
changes on every `git pull`). For Plotly canvases the same holds for `cmsplot_plotly.py` (see "Plotly (plotlyhep)"
below); `lint.py` covers both.

## Hard rules

1. **No number without its fitting canvas.** Every yield, width, significance or fraction reported comes
   with the canvas of the fit that produced it, and the canvas states the data portion used: the
   selection goes in the legend title (window, cuts, range, era). Numbers go to stdout / the message.
2. **No prose on the canvas.** Only the CMS label + sample/luminosity, the legend and the axis labels. No
   sentences via `ax.text`/`figtext`, no `set_title`/`suptitle`, no "red = our cut". A fitted value only as
   a legend entry (e.g. `signal: 416 ± 56`) when the canvas is about that number. Interpretation goes in
   the message, the note or the slide.
3. **Bin width in the x-axis unit.** `candidates / 0.005 GeV` when x is in GeV -- never `/ 5 MeV`, never
   `cand / …`, never the number of bins or entries (`replicas / 234` is a bug). `bin_label(bw, "GeV")`.
   Fitted μ, σ may still be quoted in MeV in text.
4. **Individual plots always.** A multi-panel grid only in addition to one file per panel (`save_panels`).
   Slides use single panels. `cms_label` on a real axes, never figure-level text on a grid.
5. **Look before you send.** Open every PNG you report and check it shows what the caption says (curves,
   run, luminosity, variable). File names say what is drawn; avoid ambiguous tags (`free` for "no mass
   constraint" was once read as "free width" and swapped two figures in a note).
6. Do not expose internal script names in captions, notes or slides unless asked.
7. Blind / sensitive quantities (e.g. a charge split, an asymmetry) only when explicitly requested.

## Anatomy

| element | convention |
|---|---|
| fit canvas | `fig, ax, axp = fit_figure()` (7.8 × 6.6, main : pull = 4 : 1); `fit_figure(three=True)` adds data − bkg |
| plain canvas | `plt.subplots(figsize=PLAIN_SIZE)` (7.8 × 5.2) |
| label | `cms_label(ax, com=13.6, rlabel="2024, 109 fb$^{-1}$ (13.6 TeV)")`; simulation `data=False, rlabel="Simulation"`; Run 2 `com=13` |
| x label | LaTeX + unit: `r"$m(J/\psi\,K^+)$ [GeV]"`; say which estimator when several exist (`…, kinematic fit [GeV]`) |
| y label | `bin_label(bw)`; weighted `bin_label(bw, what="weighted candidates")`; fitted yields `fitted yield / …` |
| data | `data_points(ax, cen, h, err)` -- black circles, ms 3.4, on top (zorder 5); label = the decay or `data` |
| model | total `SERIES["total"]` solid lw 2; background `SERIES["comb"]` dashed lw 1.5; components stacked on the background with `fill_between(..., alpha=0.45, lw=0)` in slot order s1 → s4 |
| legend | `legend(ax, title=<selection>)` -- frameless, upper right, fontsize 10; `ncol=2` above 4 entries; `headroom(ax, max(h+err))` |
| pull | `draw_pull(axp, cen, h, model, lo, hi, xlabel, err=err)` -- pass `err` for weighted data (√Σw²) |
| negative values | `ax.axhline(0, color="grey", lw=0.8)` and a lower ylim below the lowest point |
| save | `save(fig, "plots/<study>/<what>_<variant>.png")`, dpi 140; many per-bin canvases: subfolder `bins_<variant>/binNN.png`, dpi 110 |

## Palette (`SERIES`; fixed order, never cycled)

total `#4a3aa7` · background `#2a78d6` · s1 `#eb6834` · s2 `#1baf7a` · s3 `#eda100` · s4 `#e87ba4` · data
`#0b0b0b` · bkg-subtracted signal `#008300`. A 5th component folds into an existing slot or a separate
canvas, never a new hue. A species keeps its colour across every canvas of a study. Some slots are below
3:1 contrast, so every series has a legend entry.

## Standard canvases (`template.py --demo <name>`)

- `fit` -- mass fit: data, dashed background, stacked signal with its yield in the legend, total, pull.
- `weighted` -- sWeighted / COW spectrum: √Σw² errors, zero line, pull with `err=`.
- `compare` -- two estimates of one spectrum: markers offset ±0.15 bin, lower panel Δ/σ (label which σ).
- `scan` -- a result vs an analysis choice (background order, cut): points + errors, chosen value dashed.
- `toys` -- toy test statistic: histogram, expected distribution, observed value as a vertical line.
- per-bin / per-slice fits: one canvas per bin with the bin range in the legend title, plus summary canvases
  (per-bin χ² vs bin, fitted parameter vs bin).

## Plotly (plotlyhep)

`cmsplot_plotly.py` is the same style for Plotly, built on plotlyhep (mplhep mirrored for Plotly; not on PyPI:
`pip install git+https://github.com/DickyChant/plotlyhep`, needs `kaleido>=1` for PNG/PDF). Use it when the figure
lives in HTML: slide decks that embed live figures (hover for values, no PNGs), dashboards, web reports. A note or a
paper still takes matplotlib PNG/PDF. The hard rules above apply unchanged; `template_plotly.py --demo <name>`
draws the same five canvases (`examples/plotly_*.png`).

Plotly has no axes objects: one `go.Figure` per canvas, and `ax` / `axp` are axis references
(`{"xaxis": "x2", "yaxis": "y2"}`) passed as `ax=` to every drawing helper (default: the main panel).

| matplotlib (`cmsplot`) | Plotly (`cmsplot_plotly`) |
|---|---|
| `fig, ax, axp = fit_figure()` | `fig, ax, axp = fit_figure()` (780 × 660 px; `three=True`: 780 × 760) |
| `plt.subplots(figsize=PLAIN_SIZE)` | `fig = figure()` (780 × 520 px; one font scale for every size) |
| `cms_label(ax, com=13.6, rlabel=...)` | `cms_label(fig, com=13.6, rlabel=...)`; HTML in labels: `fb<sup>−1</sup>` |
| `ax.set_xlabel` / `ax.set_ylabel(bin_label(bw))` | `xlabel(fig, ...)` / `ylabel(fig, bin_label(bw))` (mplhep placement); lower panels `ylabel(fig, "pull", ax=axp)` |
| `data_points(ax, cen, h, err)` | `data_points(fig, cen, h, err)` -- add data last, it draws on top |
| `ax.plot(..., color=SERIES["total"], lw=2)` | `line(fig, x, y, SERIES["total"], "fit")`; background `dash="dash", width=1.5` |
| `ax.fill_between(..., alpha=0.45, lw=0)` | `fill_between(fig, x, lo, hi, SERIES["s1"], "signal: N ± dN")` |
| `histtype="step"` / `drawstyle="steps-mid"` | `step(fig, edges, values, color, label)` |
| `draw_pull(axp, ...)`, `draw_bkgsub(axb, ...)` | `draw_pull(fig, axp, ...)`, `draw_bkgsub(fig, axb, ...)` |
| `legend(ax, title=selection)`, `headroom(ax, top)` | `legend(fig, title=selection)`, `headroom(fig, top)` |
| `ax.axhline(0, color="grey", lw=0.8)` | `zero_line(fig, ax)` |
| `save(fig, "plots/x.png")` | `save(fig, "plots/x.png")` -- writes x.json (to embed) and x.png (kaleido, 1.4×) |
| -- | `embed(fig, "fig-id")` per figure + `head_script()` once per page |

Plotly-specific:
- Shaded ranges (signal window, sidebands, a cut) with `region(fig, x0, x1, "signal window 2.95–3.25 GeV")`: the
  shape plus a legend entry. Never `add_annotation` text to name them -- that is prose on the canvas.
- Hover text is fine (it is not drawn); put the per-point numbers there rather than on the canvas.
- No `update_layout(title=...)`: the selection goes in the legend title, as in matplotlib.
- Embedding: keep the figure's own template (`inherit_template=False`, the default of `embed`), so the slide shows
  the same canvas as the PNG. Plotly sizes are CSS px; convert matplotlib points with `plotlyhep._units.pt2px`.
- Plotly reverses the legend when a trace has a fill; `legend()` forces the drawing order.
- Look before you send applies here too: render the PNG (`save`) and open it, or screenshot the slide.

## Notes and slides

Captions state exactly what is drawn (how many curves, which sample, which luminosity). A label bug is
fixed in the script and the canvas remade, not explained in the caption. Keep a figure list (figure, page,
files, caption) next to a LaTeX note; `\graphicspath` to the plots folder instead of copying PNGs.

## Improving this skill

Shared across projects from the public repo github.com/DickyChant/cms-plotting (this folder is a clone of
it). To change a rule or the style: edit here, run `python template.py --outdir examples` (and
`python template_plotly.py --outdir examples` for the Plotly module), look at the canvases, then commit and push (or open a pull request). Keep it generic: no analysis results, luminosities of unpublished data, or sample paths.
