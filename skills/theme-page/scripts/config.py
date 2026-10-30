"""theme-page.json: the page's niche, accounts, brand and color theme, saved once at setup.

Lookup order: $THEME_PAGE_CONFIG, then theme-page.json in the folder of the running build script or any
parent folder. Missing keys fall back to DEFAULTS, so an old config keeps working when keys are added.
"""
import json
import os
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
NAME = "theme-page.json"
PALETTES = json.loads((HERE / "palettes.json").read_text())

DEFAULTS = {
    "niche": "",
    "accounts": {},
    "brand": {"handle": "@yourpage", "name": "Your Page", "badge": None, "monogram": "TP"},
    "theme": {"palette": "electric-cyan", **PALETTES["electric-cyan"]},
    "carousels_dir": "carousels",
}


def _merge(base, extra):
    out = dict(base)
    for key, val in extra.items():
        out[key] = _merge(base[key], val) if isinstance(val, dict) and isinstance(base.get(key), dict) else val
    return out


def find(start=None):
    env = os.environ.get("THEME_PAGE_CONFIG")
    if env:
        return pathlib.Path(env).expanduser().resolve()
    main = getattr(sys.modules.get("__main__"), "__file__", None)
    here = pathlib.Path(start or (pathlib.Path(main).parent if main else pathlib.Path.cwd())).resolve()
    for folder in (here, *here.parents):
        if (folder / NAME).exists():
            return folder / NAME
    return None


def load(start=None):
    path = find(start)
    data = json.loads(path.read_text()) if path else {}
    cfg = _merge(DEFAULTS, data)
    badge = cfg["brand"].get("badge")
    if badge and path and not pathlib.Path(badge).is_absolute():
        cfg["brand"]["badge"] = str((path.parent / badge).resolve())  # stored relative to the workspace
    cfg["_path"] = str(path) if path else None
    return cfg
