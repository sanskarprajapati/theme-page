"""Scaffold <workspace>/<carousels_dir>/<slug>/ with assets/, a build.py template and CAPTION.md.

Usage: python3 new_carousel.py <slug> [--dir <workspace>]
The workspace is the folder holding theme-page.json (run setup.py first).
"""
import argparse
import pathlib
import re
import sys

import config

SCRIPTS = pathlib.Path(__file__).resolve().parent

BUILD = '''"""{title}. Usage: python3 build.py [n ...]

Facts and sources: CAPTION.md. Slides with a video clip render as MP4, the rest as JPG.
"""
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, "{scripts}")
from kit import run, tweet  # noqa: E402,F401
from theme import (THEME_CSS, arrow, bubble, cover, follow, framed, media, stat_rows,  # noqa: E402,F401
                   story, subject, text_slide, vslot)

A = "../assets"  # slide paths are relative to html/
SRC = "Source: <primary source>, <date>"

SLIDES = {{
    1: cover(media(f"{{A}}/cover.jpg", "50% 30%"),
             [("Headline in white", "w"), ("accent words", "a"), ("more white", "w")],
             extras=bubble(f"{{A}}/logo.svg", 600, 40, 420, logo=True, bg="#fff"),
             fg=subject(f"{{A}}/cover.jpg", "50% 30%")),
    2: text_slide(["What happened, in one or two short sentences."], kicker="What happened", source=SRC),
    3: follow(media(f"{{A}}/cover.jpg", "50% 30%")),
}}

if __name__ == "__main__":
    run(ROOT, "{slug}", SLIDES, css=THEME_CSS)
'''

CAPTION = """# Caption

<hook line>

<2-4 short lines with the key facts>

<question for comments>

Follow {handle} for more.

<media credits>

<3-5 hashtags>

---

# Sources

| Claim (slide) | Source |
|---|---|

## Assets
- <file> (slides): <author>, <license or "not licensed: credited">
"""


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("slug")
    ap.add_argument("--dir", default=".")
    ap.add_argument("--title", default="")
    args = ap.parse_args(argv)
    if not re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", args.slug):
        sys.exit("slug must be lowercase words joined by hyphens, e.g. robot-cleaner")
    cfg = config.load(pathlib.Path(args.dir).expanduser())
    if not cfg["_path"]:
        sys.exit("no theme-page.json found; run setup.py first")
    folder = pathlib.Path(cfg["_path"]).parent / cfg["carousels_dir"] / args.slug
    if folder.exists():
        sys.exit(f"{folder} already exists")
    (folder / "assets").mkdir(parents=True)
    (folder / "build.py").write_text(BUILD.format(title=args.title or args.slug, scripts=SCRIPTS, slug=args.slug))
    (folder / "CAPTION.md").write_text(CAPTION.format(handle=cfg["brand"]["handle"]))
    print(folder)


if __name__ == "__main__":
    main()
