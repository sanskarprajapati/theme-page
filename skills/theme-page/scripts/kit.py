"""Rendering core for theme-page carousels (1080x1440, 3:4).

A carousel's build.py defines SLIDES = {n: html} with theme.py helpers and calls run(). Each page is
rendered by headless Chrome; plain slides become JPGs, slides holding a video slot become MP4s (video.py).
"""
import html
import os
import pathlib
import shutil
import subprocess
import sys

CHROME_CANDIDATES = (
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "/Applications/Chromium.app/Contents/MacOS/Chromium",
    "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
    "google-chrome", "google-chrome-stable", "chromium", "chromium-browser", "microsoft-edge",
)


def find_chrome():
    """$THEME_PAGE_CHROME, else the first Chrome/Chromium/Edge found on this machine."""
    if os.environ.get("THEME_PAGE_CHROME"):
        return os.environ["THEME_PAGE_CHROME"]
    for cand in CHROME_CANDIDATES:
        path = cand if os.path.isabs(cand) else shutil.which(cand)
        if path and pathlib.Path(path).exists():
            return path
    return CHROME_CANDIDATES[0]


CHROME = find_chrome()
W, H = 1080, 1440
X_BLUE = "#1D9BF0"
X_GRAY = "#71767B"

BASE_CSS = f"""
* {{ margin:0; padding:0; box-sizing:border-box; }}
html, body {{ width:{W}px; height:{H}px; background:#000; overflow:hidden; }}
body {{ position:relative; color:#fff; -webkit-font-smoothing:antialiased;
  font-family:-apple-system,"SF Pro Text","Helvetica Neue",sans-serif; }}
.w {{ color:#fff; }}
.bg {{ position:absolute; inset:0; width:100%; height:100%; object-fit:cover; }}
.tw {{ font-family:-apple-system,"SF Pro Text",sans-serif; color:#E7E9EA; }}
.tw .name {{ font-weight:700; color:#E7E9EA; }}
.tw .handle {{ color:{X_GRAY}; }}
.tw .av {{ border-radius:50%; object-fit:cover; display:block; }}
.tw .stats {{ display:flex; gap:56px; color:{X_GRAY}; align-items:center; }}
.tw .stats span {{ display:flex; align-items:center; gap:12px; }}
"""

VERIFIED = (f'<svg viewBox="0 0 22 22" width="{{s}}" height="{{s}}" style="vertical-align:-.12em">'
            f'<path fill="{X_BLUE}" d="M20.4 11c0-1.3-.8-2.5-2-3 .4-1.3.1-2.7-.8-3.6-1-1-2.4-1.2-3.6-.8C13.5 2.4 12.3'
            f' 1.6 11 1.6s-2.5.8-3 2c-1.3-.4-2.7-.1-3.6.8-1 1-1.2 2.4-.8 3.6-1.2.5-2 1.7-2 3s.8 2.5 2 3c-.4 1.3-.1 2.7'
            f'.8 3.6 1 1 2.4 1.2 3.6.8.5 1.2 1.7 2 3 2s2.5-.8 3-2c1.3.4 2.7.1 3.6-.8 1-1 1.2-2.4.8-3.6 1.2-.5 2-1.7'
            f' 2-3z"/><path fill="#fff" d="M9.6 14.8 6.4 11.6l1.3-1.3 1.9 1.9 4.7-5.1 1.4 1.3z"/></svg>')
GOLD_CHECK = VERIFIED.replace(X_BLUE, "#E2B719")

ICONS = {
    "reply": '<svg viewBox="0 0 24 24" width="{s}" height="{s}"><path fill="none" stroke="currentColor" stroke-width="1.8" d="M4 11a7 7 0 0 1 7-7h2a7 7 0 0 1 0 14h-2.5L6 21v-3.6A7 7 0 0 1 4 11z"/></svg>',
    "rt": '<svg viewBox="0 0 24 24" width="{s}" height="{s}"><path fill="none" stroke="currentColor" stroke-width="1.8" d="M4 9l3-3 3 3M7 6v9a3 3 0 0 0 3 3h5M20 15l-3 3-3-3M17 18V9a3 3 0 0 0-3-3H9"/></svg>',
    "like": '<svg viewBox="0 0 24 24" width="{s}" height="{s}"><path fill="none" stroke="currentColor" stroke-width="1.8" d="M12 20s-7.5-4.6-9-9.2C2 7.6 4 5 7 5c2 0 3.3 1.2 5 3 1.7-1.8 3-3 5-3 3 0 5 2.6 4 5.8C19.5 15.4 12 20 12 20z"/></svg>',
    "views": '<svg viewBox="0 0 24 24" width="{s}" height="{s}"><path fill="currentColor" d="M4 20h2V10H4zm5 0h2V4H9zm5 0h2v-8h-2zm5 0h2V8h-2z"/></svg>',
}


def esc(text):
    return html.escape(text).replace("\n", "<br>")


def tweet(av, name, handle, text, *, check="blue", date=None, stats=None, size=44, width=950,
          media=None, reply_to=None):
    """X dark-mode post recreation. stats: dict with reply/rt/like/views strings (real numbers only)."""
    badge = {"blue": VERIFIED, "gold": GOLD_CHECK}.get(check, "").format(s=int(size * .9))
    rep = (f'<div class="handle" style="font-size:{size*.82}px;margin:-4px 0 10px">Replying to '
           f'<span style="color:{X_BLUE}">@{esc(reply_to)}</span></div>') if reply_to else ""
    when = f'<div class="handle" style="font-size:{size*.8}px;margin-top:30px">{esc(date)}</div>' if date else ""
    st = ""
    if stats:
        isz = int(size * .9)
        st = '<div class="stats" style="font-size:{fs}px;margin-top:30px;padding-top:26px;border-top:1px solid #2F3336">{items}</div>'.format(
            fs=size * .8,
            items="".join(f'<span>{ICONS[k].format(s=isz)}{esc(v)}</span>' for k, v in stats.items()))
    med = f'<div style="margin-top:28px">{media}</div>' if media else ""
    return (f'<div class="tw" style="width:{width}px">'
            f'<div style="display:flex;gap:24px;align-items:center;margin-bottom:22px">'
            f'<img class="av" src="{av}" style="width:{size*2.6}px;height:{size*2.6}px">'
            f'<div><div class="name" style="font-size:{size*1.05}px">{esc(name)} {badge}</div>'
            f'<div class="handle" style="font-size:{size*.92}px">@{esc(handle)}</div></div></div>'
            f'{rep}<div style="font-size:{size}px;line-height:1.3;white-space:normal">{esc(text)}</div>'
            f'{med}{when}{st}</div>')


def write_page(path, body, css=""):
    from video import PAGE_SCRIPT
    path.write_text(f"<!doctype html><html><head><meta charset='utf-8'><style>{BASE_CSS}</style>"
                    f"<style>{css}</style></head><body>{body}{PAGE_SCRIPT}</body></html>")


def screenshot(page, png):
    if not pathlib.Path(CHROME).exists():
        raise FileNotFoundError(f"Chrome not found at {CHROME}; set THEME_PAGE_CHROME to its binary")
    subprocess.run([CHROME, "--headless=new", "--hide-scrollbars", "--force-device-scale-factor=1",
                    f"--window-size={W},{H}", "--virtual-time-budget=6000", "--allow-file-access-from-files",
                    f"--screenshot={png}", page.resolve().as_uri()], check=True, capture_output=True)


def to_jpg(png, jpg):
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", str(png), "-q:v", "2", str(jpg)], check=True)


def run(root, prefix, slides, css=""):
    """Render slides to <root>/final/. Pass slide numbers on the command line to render only those.
    css: theme.THEME_CSS. A slide holding a .vslot (see video.py) becomes an MP4, the rest JPGs."""
    from video import render as render_video
    root = pathlib.Path(root)
    out, page_dir, final = root / "out", root / "html", root / "final"
    for d in (out, page_dir, final):
        d.mkdir(exist_ok=True)
    picks = list(map(int, sys.argv[1:])) or sorted(slides)
    for n in picks:
        is_video = 'class="vslot' in slides[n]
        clear = "html,body{background:transparent!important}" if is_video else ""
        page = page_dir / f"slide{n:02d}.html"
        write_page(page, slides[n], css + clear)
        if is_video:
            mp4 = final / f"{prefix}-slide{n:02d}.mp4"
            secs = render_video(CHROME, page, (W, H), mp4, out / f"slide{n:02d}-poster.jpg")
            print(f"rendered {mp4.name} ({secs:.1f}s)")
            continue
        png = out / f"slide{n:02d}.png"
        screenshot(page, png)
        jpg = final / f"{prefix}-slide{n:02d}.jpg"
        to_jpg(png, jpg)
        print("rendered", jpg.name)
