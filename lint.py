"""Static check of plotting scripts against the cms-plotting rules (SKILL.md). Line-based and
conservative: it flags, you judge. Exit code 1 if anything is flagged.

    python lint.py scripts/foo.py [more.py ...] [--style-module mypkg.plotting]

--style-module: the module that carries the house style in this project (default: cmsplot, or any module
whose name ends in "plotting").
"""
from __future__ import annotations
import argparse, re, sys

RULES = [
    (re.compile(r"set_ylabel\([^)]*/\s*\{?[^}]*1e3[^}]*\}?\s*MeV"), "bin width in MeV on the y axis -> write it in GeV"),
    (re.compile(r"set_ylabel\([^)]*/\s*\d+(\.\d+)?\s*MeV"), "bin width in MeV on the y axis -> write it in GeV"),
    (re.compile(r"set_ylabel\(\s*f?[\"']cand\b"), "'cand /' -> 'candidates /'"),
    (re.compile(r"set_ylabel\([^)]*/\s*\{(len|n|nb|nbins|N)[^}]*\}"), "bin COUNT in the y label -> give the bin width"),
    (re.compile(r"\.(set_title|suptitle)\("), "title on the canvas -> no titles; use the legend title for the selection"),
    (re.compile(r"\b(ax\w*|plt|fig)\.text\(\s*[^,]+,\s*[^,]+,\s*f?[\"'][^\"']*\s\w+\s\w+\s\w+"),
     "sentence drawn with .text() -> no prose on canvases"),
    (re.compile(r"\.figtext\("), "figure-level text -> no prose; cms_label goes on an axes"),
    (re.compile(r"plt\.style\.use\(|rcParams\.update\("), "local restyling -> the style module sets the style"),
]


def lint(path, style=None):
    src = open(path).read().splitlines()
    hits = []
    for i, line in enumerate(src, 1):
        if line.lstrip().startswith("#"):
            continue
        for rx, msg in RULES:
            if rx.search(line):
                hits.append((i, msg, line.strip()))
    text = "\n".join(src)
    uses_style = (style in text) if style else bool(re.search(r"\b(cmsplot|\w*plotting)\b", text))
    if "savefig" in text and not uses_style:
        hits.append((0, f"saves figures without importing the style module ({style or 'cmsplot / *plotting'})", ""))
    if "savefig" in text and "cms_label" not in text:
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
        if p.endswith(("cmsplot.py", "plotting.py")):
            continue
        for ln, msg, code in lint(p, a.style_module):
            bad += 1
            print(f"{p}:{ln}: {msg}" + (f"\n    {code}" if code else ""))
    print(f"{bad} issue(s)" if bad else "clean")
    sys.exit(1 if bad else 0)
