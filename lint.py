"""Static check of plotting scripts against the cms-plotting rules (SKILL.md), for matplotlib (cmsplot)
and Plotly (plotlyhep, cmsplot_plotly) scripts. Line-based and conservative: it flags, you judge.
Exit code 1 if anything is flagged.

    python lint.py scripts/foo.py [more.py ...] [--style-module mypkg.plotting]

--style-module: the module that carries the house style in this project (default: cmsplot, cmsplot_plotly,
or any module whose name ends in "plotting").
"""
from __future__ import annotations
import argparse, re, sys

# y-label call sites: matplotlib ax.set_ylabel(...), plotlyhep php.set_ylabel(fig, ...), cmsplot_plotly ylabel(fig, ...),
# Plotly update_yaxes(title=...) / update_layout(yaxis_title=...)
YL = r"(?:\b(?:set_)?ylabel\(|update_yaxes\([^)]*title|yaxis_title\s*=)"
FIG = r"(?:\s*\w+\s*,)?"  # optional leading figure argument (php.set_ylabel(fig, "..."))

RULES = [
    (re.compile(YL + r"[^)]*/\s*\{?[^}]*1e3[^}]*\}?\s*MeV"), "bin width in MeV on the y axis -> write it in GeV"),
    (re.compile(YL + r"[^)]*/\s*\d+(\.\d+)?\s*MeV"), "bin width in MeV on the y axis -> write it in GeV"),
    (re.compile(r"\b(?:set_)?ylabel\(" + FIG + r"\s*f?[\"']cand\b"), "'cand /' -> 'candidates /'"),
    (re.compile(YL + r"[^)]*/\s*\{(len|n|nb|nbins|N)[^}]*\}"), "bin COUNT in the y label -> give the bin width"),
    (re.compile(r"\.(set_title|suptitle)\("), "title on the canvas -> no titles; use the legend title for the selection"),
    (re.compile(r"\b(ax\w*|plt|fig)\.text\(\s*[^,]+,\s*[^,]+,\s*f?[\"'][^\"']*\s\w+\s\w+\s\w+"),
     "sentence drawn with .text() -> no prose on canvases"),
    (re.compile(r"\.figtext\("), "figure-level text -> no prose; cms_label goes on an axes"),
    (re.compile(r"plt\.style\.use\(|rcParams\.update\("), "local restyling -> the style module sets the style"),
    # Plotly / plotlyhep
    (re.compile(r"\badd_annotation\([^)]*\btext\s*=\s*f?[\"'][^\"']*\s\w+\s\w+\s\w+"),
     "sentence drawn with add_annotation() -> no prose on canvases (selection in the legend title)"),
    (re.compile(r"\b(?:php|plotlyhep)\.style\.use\(|pio\.templates\.default\s*="), "local restyling -> the style module sets the style"),
]
TITLE_KW = {"title", "title_text"}


def layout_title(line):
    """update_layout(title=...) / update_layout(title_text=...) as a TOP-LEVEL keyword (legend=dict(title=...) is fine)."""
    i = line.find("update_layout(")
    while i >= 0:
        depth, word, j = 0, "", i + len("update_layout")
        while j < len(line):
            c = line[j]
            if c in "([{":
                depth += 1; word = ""
            elif c in ")]}":
                depth -= 1; word = ""
                if depth == 0:
                    break
            elif c == "=" and depth == 1 and line[j + 1:j + 2] != "=" and word.strip() in TITLE_KW:
                return True
            elif c.isalnum() or c == "_":
                word += c
            elif c != " ":
                word = ""
            j += 1
        i = line.find("update_layout(", j)
    return False


def lint(path, style=None):
    src = open(path).read().splitlines()
    hits = []
    for i, line in enumerate(src, 1):
        if line.lstrip().startswith("#"):
            continue
        for rx, msg in RULES:
            if rx.search(line):
                hits.append((i, msg, line.strip()))
        if layout_title(line):
            hits.append((i, "title on the canvas -> no titles; use the legend title for the selection", line.strip()))
    text = "\n".join(src)
    uses_style = (style in text) if style else bool(re.search(r"\b(cmsplot|cmsplot_plotly|\w*plotting)\b", text))
    saves = any(k in text for k in ("savefig", "write_image", "write_html", "write_json"))
    if saves and not uses_style:
        hits.append((0, f"saves figures without importing the style module ({style or 'cmsplot / cmsplot_plotly / *plotting'})", ""))
    if saves and not re.search(r"cms_label|cms\.label", text):
        hits.append((0, "no cms_label on any canvas", ""))
    grid = re.search(r"plt\.subplots\(\s*(\d+)\s*,\s*(\d+)", text)
    if grid and int(grid.group(1)) * int(grid.group(2)) > 1 and text.count("savefig") < 2:
        hits.append((0, "multi-panel grid with a single savefig -> also save every panel on its own", ""))
    return hits


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("files", nargs="+")
    ap.add_argument("--style-module", default=None)
    a = ap.parse_args()
    bad = 0
    for p in a.files:
        if p.endswith(("cmsplot.py", "cmsplot_plotly.py", "plotting.py")):
            continue
        for ln, msg, code in lint(p, a.style_module):
            bad += 1
            print(f"{p}:{ln}: {msg}" + (f"\n    {code}" if code else ""))
    print(f"{bad} issue(s)" if bad else "clean")
    sys.exit(1 if bad else 0)
