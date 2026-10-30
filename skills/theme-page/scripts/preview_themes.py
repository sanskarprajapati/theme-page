"""Render one sample cover per color palette into a single contact sheet, so the user can pick a theme.

Usage: python3 preview_themes.py --out <sheet.jpg> [--dir <workspace>] [--image <photo>] [--headline "Text with *accent words*"]
       [--palettes electric-cyan,gold,...]
Words wrapped in *asterisks* in --headline are drawn in the accent color. Each tile is labelled with
its palette id (the value to pass to setup.py --palette).
"""
import argparse
import os
import pathlib
import subprocess
import sys
import tempfile

import config
import kit

DEFAULT_HEADLINE = "This guy just built an AI that *does his job* while he *sleeps*"


def segments(text):
    parts = text.split("*")
    return [(p.strip(), "a" if i % 2 else "w") for i, p in enumerate(parts) if p.strip()]


def backdrop(image):
    if image:
        return f'<img class="bg" src="{pathlib.Path(image).expanduser().resolve().as_uri()}" style="object-position:50% 30%">'
    return ('<div class="bg" style="background:radial-gradient(circle at 30% 25%,#4a4f5c,#1c1f26 55%,#0b0c0f)">'
            '</div>')


def tile(theme, palette_id, accent, image, headline):
    label = (f'<div style="position:absolute;left:40px;top:40px;background:rgba(0,0,0,.7);border:3px solid {accent};'
             f'border-radius:14px;padding:14px 22px;font:600 40px/1 Inter,sans-serif;color:#fff">{palette_id}</div>')
    sample_logo = (f'<div class="bub" style="left:640px;top:120px;width:360px;height:360px;border:7px solid #fff;'
                   f'background:{accent}"></div>')
    return theme.cover(backdrop(image) + sample_logo, segments(headline)) + label


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", required=True)
    ap.add_argument("--dir", help="workspace with theme-page.json, so tiles show the real handle")
    ap.add_argument("--image")
    ap.add_argument("--headline", default=DEFAULT_HEADLINE)
    ap.add_argument("--palettes", help="comma-separated palette ids (default: all)")
    args = ap.parse_args(argv)
    if args.dir:
        found = config.find(pathlib.Path(args.dir).expanduser())
        if found:
            os.environ["THEME_PAGE_CONFIG"] = str(found)
    import theme  # loads theme-page.json at import, so it must come after the env is set
    ids = args.palettes.split(",") if args.palettes else list(config.PALETTES)
    unknown = [i for i in ids if i not in config.PALETTES]
    if unknown:
        sys.exit(f"unknown palette(s): {', '.join(unknown)}; choose from {', '.join(config.PALETTES)}")
    with tempfile.TemporaryDirectory() as td:
        tmp, shots = pathlib.Path(td), []
        for pid in ids:
            accent = config.PALETTES[pid]["accent"]
            page = tmp / f"{pid}.html"
            kit.write_page(page, tile(theme, pid, accent, args.image, args.headline), theme.theme_css(accent))
            png = tmp / f"{pid}.png"
            kit.screenshot(page, png)
            shots.append(png)
        cols = 4 if len(shots) > 4 else len(shots)
        rows = -(-len(shots) // cols)
        inputs = sum((["-i", str(p)] for p in shots), [])
        pads = "".join(f"color=black:s=1080x1440:d=1[p{k}];" for k in range(rows * cols - len(shots)))
        names = [f"[{k}:v]" for k in range(len(shots))] + [f"[p{k}]" for k in range(rows * cols - len(shots))]
        grid = "".join(f"{''.join(names[r * cols:(r + 1) * cols])}hstack={cols}[r{r}];" for r in range(rows))
        stack = "".join(f"[r{r}]" for r in range(rows)) + (f"vstack={rows}," if rows > 1 else "")
        out = pathlib.Path(args.out).expanduser().resolve()
        subprocess.run(["ffmpeg", "-y", "-v", "error", *inputs, "-filter_complex",
                        f"{pads}{grid}{stack}scale={cols * 400}:-1", "-frames:v", "1", "-q:v", "3", str(out)],
                       check=True)
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
