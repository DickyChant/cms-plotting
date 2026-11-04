"""cmsproject -- read a project's plotting customization (<project>/.claude/cms-plotting/style.toml).

No plotting imports, so it works with either back end:

    import cmsproject as cp
    cms_label(ax, **cp.label("run3"))                  # matplotlib (cmsplot or the project's module)
    cms_label(fig, **cp.label("run3", html=True))      # Plotly (cmsplot_plotly)
    ax.set_xlabel(cp.axis("m_jpsik")); color = SERIES[cp.slot("signal")]

The file is found by walking up from the working directory; CMS_PLOTTING_CUSTOM points elsewhere.
"""
from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path

try:
    import tomllib
except ModuleNotFoundError:  # Python < 3.11
    import tomli as tomllib

REL = Path(".claude") / "cms-plotting" / "style.toml"


def find(start="."):
    """Path of the project's style.toml, or None."""
    env = os.environ.get("CMS_PLOTTING_CUSTOM")
    if env:
        p = Path(env)
        return p / "style.toml" if p.is_dir() else p
    for d in [Path(start).resolve(), *Path(start).resolve().parents]:
        if (d / REL).is_file():
            return d / REL
    return None


@lru_cache(maxsize=None)
def load(path=None):
    """The customization as a dict ({} when the project has none)."""
    p = Path(path) if path else find()
    if p is None or not p.is_file():
        return {}
    with open(p, "rb") as f:
        return tomllib.load(f)


def _get(section, key):
    d = load().get(section, {})
    if key not in d:
        raise KeyError(f"'{key}' not in [{section}] of {find() or REL} (known: {', '.join(d) or 'none'})")
    return d[key]


def label(era, html=False):
    """Keyword arguments for cms_label: com, data, rlabel."""
    e = _get("era", era)
    rl = e.get("rlabel_html", e.get("rlabel")) if html else e.get("rlabel")
    return {"com": e.get("com", 13.6), "data": e.get("data", True), "rlabel": rl}


def axis(name):
    """x-axis label (with unit) of an observable."""
    return _get("axis", name)


def name(key):
    """Legend label of a physics object."""
    return _get("name", key)


def slot(species):
    """SERIES slot ('s1', 'comb', ...) a species keeps on every canvas."""
    return _get("species", species)


def style_module(default=None):
    return load().get("style_module", default)
