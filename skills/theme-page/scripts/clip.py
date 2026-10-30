"""9:16 clip post: a crazy video re-framed with the page's branding and a headline (1080x1920 MP4).

Layout (the viral "repost" look): black frame, page avatar + name + check mark, a bold sentence-case
headline, then the video full-width in the middle with its sound.

Usage:
  python3 clip.py --src <file or X/YouTube/TikTok URL> --headline "They put Mike Tyson in Zelda 😭" \
      --out <workspace>/clips/<slug>/<slug>.mp4 [--start 0] [--dur 45] [--pos "50% 50%"] [--dir <workspace>]
URLs are downloaded with yt-dlp into the output folder (source.mp4) first. Clips are capped at 2 minutes.
"""
import argparse
import json
import os
import pathlib
import subprocess
import sys

import config

CW, CH = 1080, 1920
MAX_VIDEO_H = 1240  # vertical sources are cropped to this height so the header still fits


def download(url, folder):
    folder.mkdir(parents=True, exist_ok=True)
    out = folder / "source.mp4"
    if out.exists():
        return out
    subprocess.run(["yt-dlp", "-f", "bv*[ext=mp4]+ba[ext=m4a]/b[ext=mp4]/bv*+ba/b", "--merge-output-format", "mp4",
                    "-o", str(out), url], check=True)
    return out


def dimensions(src):
    res = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
                          "stream=width,height:stream_side_data=rotation", "-of", "json", str(src)],
                         check=True, capture_output=True, text=True)
    stream = json.loads(res.stdout)["streams"][0]
    w, h = stream["width"], stream["height"]
    rotated = any(abs(int(d.get("rotation", 0))) == 90 for d in stream.get("side_data_list", []))
    return (h, w) if rotated else (w, h)


def check_mark(color, size):
    return (f'<svg viewBox="0 0 22 22" width="{size}" height="{size}" style="vertical-align:-.14em">'
            f'<circle cx="11" cy="11" r="10" fill="{color}"/>'
            f'<path fill="#fff" d="M9.6 14.8 6.4 11.6l1.3-1.3 1.9 1.9 4.7-5.1 1.4 1.3z"/></svg>')


def page_html(theme, kit, src_rel, video_h, headline, start, dur, pos):
    brand, accent = theme.BRAND, theme.ACCENT
    avatar = (f'<img src="{brand["badge"]}" style="width:100%;height:100%;object-fit:cover">' if brand.get("badge")
              else f'<span style="font:400 40px/1 Anton,sans-serif;color:#fff">{kit.esc(brand.get("monogram", ""))}</span>')
    head = (f'<div style="display:flex;align-items:center;gap:22px;margin:0 48px 30px">'
            f'<div style="width:96px;height:96px;border-radius:50%;overflow:hidden;background:#111;flex:none;'
            f'border:3px solid {accent};display:flex;align-items:center;justify-content:center">{avatar}</div>'
            f'<div style="font:700 38px/1 Inter,sans-serif;color:#fff">{kit.esc(brand["name"])} '
            f'{check_mark(accent, 34)}</div></div>'
            f'<div data-fit="330" style="margin:0 48px 44px;font:800 66px/1.16 Inter,-apple-system,sans-serif;'
            f'color:#fff;letter-spacing:-.015em">{kit.esc(headline)}</div>')
    slot = theme.vslot(src_rel, pos, start=start, dur=dur, audio=True, style=f"width:{CW}px;height:{video_h}px")
    # The video's centre sits a little below the middle of the frame, with the header right above it.
    top = max(140, int(CH * 0.56 - video_h / 2))
    return (f'<div style="position:absolute;left:0;right:0;bottom:{CH - top}px">{head}</div>'
            f'<div style="position:absolute;left:0;top:{top}px">{slot}</div>'
            f'<div style="position:absolute;left:0;right:0;top:{top + video_h + 40}px;text-align:center;'
            f'font:600 30px/1 Inter,sans-serif;color:#8a8a8a">{kit.esc(brand["handle"])}</div>')


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--src", required=True)
    ap.add_argument("--headline", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--start", type=float, default=0)
    ap.add_argument("--dur", type=float)
    ap.add_argument("--pos", default="50% 50%", help="crop focus for vertical sources")
    ap.add_argument("--dir", help="workspace with theme-page.json (default: search from --out)")
    args = ap.parse_args(argv)

    out = pathlib.Path(args.out).expanduser().resolve()
    found = config.find(pathlib.Path(args.dir).expanduser() if args.dir else out.parent)
    if not found:
        sys.exit("no theme-page.json found; run setup.py first or pass --dir")
    os.environ["THEME_PAGE_CONFIG"] = str(found)
    import kit  # noqa: E402  (theme reads the config at import)
    import theme  # noqa: E402
    import video  # noqa: E402

    src = download(args.src, out.parent) if args.src.startswith("http") else pathlib.Path(args.src).expanduser().resolve()
    if not src.exists():
        sys.exit(f"video not found: {src}")
    w, h = dimensions(src)
    video_h = min(MAX_VIDEO_H, round(CW * h / w / 2) * 2)

    out.parent.mkdir(parents=True, exist_ok=True)
    page = out.parent / f"{out.stem}.html"
    css = theme.THEME_CSS + f"html,body{{width:{CW}px!important;height:{CH}px!important;background:transparent!important}}"
    kit.write_page(page, page_html(theme, kit, str(src), video_h, args.headline, args.start, args.dur, args.pos), css)
    secs = video.render(kit.CHROME, page, (CW, CH), out, out.with_suffix(".jpg"))
    print(f"wrote {out} ({secs:.1f}s) and poster {out.with_suffix('.jpg').name}")


if __name__ == "__main__":
    main()
