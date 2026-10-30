"""Theme-page carousel look (1080x1440), modelled on the covers of big viral news pages.

Cover: full-bleed photo or video fading to black, ringed circle insets (logos, close-ups, clips) with
an optional hand-drawn arrow, a thin accent divider carrying the brand badge, a heavy condensed caps
headline in white + accent, and a handle / SWIPE FOR MORE footer. Body slides keep the same frame.

Any `media()` / `bubble()` given a .mp4/.mov/.webm becomes a video slot, and the slide renders as MP4
through video.py (clips are capped at 2 minutes). Pass THEME_CSS to kit.run(..., css=THEME_CSS).
Colors and brand come from theme-page.json (config.py), so every carousel on a page matches.
"""
import math
import pathlib
import sys

import config
from cutout import available as cutout_available, cut_image, cut_video
from kit import esc

CONFIG = config.load()
ACCENT = CONFIG["theme"]["accent"]
BRAND = CONFIG["brand"]  # handle, name, badge (round logo image path or None), monogram
VIDEO_EXT = (".mp4", ".mov", ".webm", ".m4v")


def theme_css(accent):
    return f"""
@import url('https://fonts.googleapis.com/css2?family=Anton&family=Inter:wght@500;600;800&display=block');
.a {{ color:{accent}; }}
.tfade {{ position:absolute; inset:0;
  background:linear-gradient(180deg, rgba(0,0,0,0) 40%, rgba(0,0,0,.55) 54%, rgba(0,0,0,.93) 64%, #000 70%); }}
.stack {{ position:absolute; left:40px; right:40px; bottom:86px; text-align:center; }}
.th {{ font:400 112px/1.0 Anton,sans-serif; text-transform:uppercase; color:#fff; letter-spacing:.002em;
  margin-top:26px; }}
.rule {{ position:relative; height:66px; }}
.rule:before {{ content:""; position:absolute; left:0; right:0; top:32px; height:2px;
  background:linear-gradient(90deg, transparent, {accent} 18%, {accent} 82%, transparent); opacity:.85; }}
.badge {{ position:absolute; left:50%; top:0; transform:translateX(-50%); width:66px; height:66px;
  border-radius:50%; background:#000; border:3px solid {accent}; overflow:hidden; display:flex;
  align-items:center; justify-content:center; font:400 30px/1 Anton,sans-serif; color:#fff; }}
.badge img {{ width:100%; height:100%; object-fit:cover; }}
.foot {{ position:absolute; left:34px; right:34px; bottom:26px; display:flex; justify-content:space-between;
  align-items:center; font:500 25px/1 Inter,sans-serif; color:#d6d6d6; }}
.foot b {{ font:600 24px/1 Inter,sans-serif; letter-spacing:.06em; color:#fff; }}
.bub {{ position:absolute; border-radius:50%; overflow:hidden; box-shadow:0 10px 40px rgba(0,0,0,.45); }}
.bub > div > img, .bub > div > .vslot {{ width:100%; height:100%; border-radius:50%; object-fit:cover; display:block; }}
.body {{ position:absolute; left:64px; right:64px; font:500 46px/1.28 Inter,sans-serif; color:#ececec;
  letter-spacing:-.01em; }}
.body p + p {{ margin-top:34px; }}
.body strong {{ font-weight:800; color:#fff; }}
.kick {{ font:400 64px/1 Anton,sans-serif; text-transform:uppercase; color:{accent}; margin-bottom:30px; }}
.srcline {{ position:absolute; left:64px; right:64px; bottom:84px; font:500 26px/1.3 Inter,sans-serif;
  color:#8a8a8a; text-align:center; }}
"""


THEME_CSS = theme_css(ACCENT)


def _is_video(src):
    return src.lower().endswith(VIDEO_EXT)


def media(src, pos="50% 50%", *, start=0, dur=None, audio=True, style=""):
    """Full-bleed photo or video (object-fit: cover). Video keeps its sound unless audio=False."""
    if not _is_video(src):
        return f'<img class="bg" src="{src}" style="object-position:{pos};{style}">'
    return vslot(src, pos, start=start, dur=dur, audio=audio, cls="bg", style=style)


def vslot(src, pos="50% 50%", *, start=0, dur=None, audio=False, cls="", style="", layer="under", zoom=1):
    """A see-through hole that video.py fills with the clip `src` from `start` for `dur` seconds.
    layer: "under" = backdrop beneath the slide, "over" = inset above the photo (bubbles, cards),
    "fg" = background-removed subject above the insets but under the fade and headline.
    zoom > 1 punches in before cropping, with pos choosing which part of the frame stays."""
    data = f'data-src="{src}" data-start="{start}" data-pos="{pos}" data-audio="{int(audio)}"'
    data += f' data-layer="{layer}"'
    data += f' data-zoom="{zoom}"' if zoom != 1 else ""
    data += f' data-dur="{dur}"' if dur else ""
    return f'<div class="vslot {cls}" {data} style="{style}"></div>'


def bubble(src, x, y, d, *, ring="#fff", ring_w=7, pos="50% 50%", logo=False, bg="#fff", pad=0.18,
           start=0, dur=None, zoom=1, cross=False):
    """Circle inset at (x, y) with diameter d (the reference covers use ~360-440px).
    logo=True contains the image on a solid `bg` disc; cross=True strikes it out with a red X."""
    box = f"left:{x}px;top:{y}px;width:{d}px;height:{d}px;border:{ring_w}px solid {ring}"
    if logo:
        inner = (f'<img src="{src}" style="width:100%;height:100%;object-fit:contain;'
                 f'padding:{d * pad:.0f}px;border-radius:0;background:{bg}">')
    elif _is_video(src):
        inner = vslot(src, pos, start=start, dur=dur, style="border-radius:50%", layer="over", zoom=zoom)
    else:
        inner = f'<img src="{src}" style="object-position:{pos}">'
    x_mark = (f'<svg viewBox="0 0 100 100" style="position:absolute;inset:-4%;width:108%;height:108%">'
              f'<path d="M14 14 86 86M86 14 14 86" stroke="#E8202A" stroke-width="11" stroke-linecap="round"/>'
              f'</svg>') if cross else ""
    return (f'<div class="bub" style="{box};background:{bg if logo else "transparent"};overflow:visible">'
            f'<div style="position:absolute;inset:0;border-radius:50%;overflow:hidden">{inner}</div>{x_mark}</div>')


def arrow(x1, y1, x2, y2, bend=0.35, width=7, color="#fff"):
    """Hand-drawn curved arrow from (x1, y1) to (x2, y2); bend > 0 bows it to the left of travel."""
    mx, my, dx, dy = (x1 + x2) / 2, (y1 + y2) / 2, x2 - x1, y2 - y1
    cx, cy = mx - dy * bend, my + dx * bend
    ang = math.atan2(y2 - cy, x2 - cx)
    head = [(x2 - 38 * math.cos(ang + s * 0.5), y2 - 38 * math.sin(ang + s * 0.5)) for s in (1, -1)]
    tips = "".join(f'<path d="M{hx:.0f} {hy:.0f} L{x2} {y2}"/>' for hx, hy in head)
    return (f'<svg class="front" style="position:absolute;inset:0" width="1080" height="1440" fill="none" stroke="{color}" '
            f'stroke-width="{width}" stroke-linecap="round" stroke-linejoin="round">'
            f'<path d="M{x1} {y1} Q{cx:.0f} {cy:.0f} {x2} {y2}"/>{tips}</svg>')


def badge():
    inner = f'<img src="{BRAND["badge"]}">' if BRAND.get("badge") else esc(BRAND.get("monogram", "")[:3])
    return f'<div class="rule"><div class="badge">{inner}</div></div>'


def footer(center="SWIPE FOR MORE"):
    return (f'<div class="foot front"><span>{esc(BRAND["handle"])}</span><b>{esc(center)}</b>'
            f'<span>{esc(BRAND["name"])}</span></div>')


def title(segments, size=112, max_h=470):
    """segments: [(text, 'w' | 'a')] -> white / accent caps, auto-shrunk to fit max_h pixels."""
    spans = " ".join(f'<span class="{c}">{esc(t)}</span>' for t, c in segments)
    return f'<h1 class="th" data-fit="{max_h}" style="font-size:{size}px">{spans}</h1>'


def _page_path(src):
    """Slide srcs are relative to <carousel>/html/, where kit.run writes the pages."""
    path = pathlib.Path(src)
    return path if path.is_absolute() else pathlib.Path(sys.modules["__main__"].__file__).resolve().parent / "html" / path


def subject(src, pos="50% 50%", *, start=0, dur=None, keep_all=False, clip=None):
    """Background-removed copy of the cover's media, aligned with it, so the person or object stands in
    front of the bubbles. Pass the same src/pos/start/dur as the cover's media(). Only the largest
    subject is kept (bystanders stay behind the bubbles) unless keep_all=True. When Vision merges a
    bystander into the hero, trim with clip: a CSS clip-path in slide percentages, e.g.
    "polygon(0 0, 76% 0, 76% 42%, 100% 42%, 100% 100%, 0 100%)" (photos only)."""
    if not cutout_available():
        print("theme-page: subject cut-outs need macOS 14+ with Xcode command line tools; cover rendered without one",
              file=sys.stderr)
        return ""
    if not _is_video(src):
        cut = cut_image(_page_path(src), keep_all)
        trim = f"clip-path:{clip};" if clip else ""
        return f'<img class="bg front" src="{cut}" style="object-position:{pos};{trim}">'
    if not dur:
        raise ValueError("subject() on a video needs dur= so only that window is cut out")
    return vslot(str(cut_video(_page_path(src), start, dur, keep_all=keep_all)), pos, dur=dur, cls="bg",
                 layer="fg")


def cover(media_html, segments, extras="", size=112, max_h=470, cta="SWIPE FOR MORE", fg=""):
    """Layers, back to front: media, extras (bubble() insets), fg (subject() cut-out), fade + headline.
    arrow() always draws on top."""
    return (f'{media_html}{extras}{fg}<div class="tfade front"></div>'
            f'<div class="stack front">{badge()}{title(segments, size, max_h)}</div>{footer(cta)}')


def story(media_html, paras, *, media_h=760, kicker=None, source=None, extras=""):
    """Body slide: photo/video panel on top, sentence-case text below. paras may hold <strong>/<span class=a>."""
    ps = "".join(f"<p>{p}</p>" for p in paras)
    kick = f'<div class="kick">{esc(kicker)}</div>' if kicker else ""
    src = f'<div class="srcline">{esc(source)}</div>' if source else ""
    panel = (f'<div style="position:absolute;left:0;top:0;width:1080px;height:{media_h}px;overflow:hidden">'
             f'{media_html}<div style="position:absolute;inset:0;background:linear-gradient(180deg,'
             f'transparent 70%,#000)"></div>{extras}</div>')
    fit = 1440 - media_h - 40 - (150 if source else 100)
    return (f'{panel}<div class="body" data-fit="{fit}" style="top:{media_h + 40}px">{kick}{ps}</div>{src}'
            f'{footer("SWIPE")}')


def text_slide(paras, *, kicker=None, source=None, top=None):
    """Plain black slide for the explainer beats; centred vertically unless top is given."""
    ps = "".join(f"<p>{p}</p>" for p in paras)
    kick = f'<div class="kick">{esc(kicker)}</div>' if kicker else ""
    pos = f"top:{top}px" if top is not None else "top:50%;transform:translateY(-50%)"
    src = f'<div class="srcline">{esc(source)}</div>' if source else ""
    return f'<div class="body" style="{pos}">{kick}{ps}</div>{src}{footer("SWIPE")}'


def framed(inner_html, *, source=None):
    """Centre any block (a kit.tweet(), a chart) on black with the theme footer."""
    src = f'<div class="srcline">{esc(source)}</div>' if source else ""
    return (f'<div style="position:absolute;left:50%;top:47%;transform:translate(-50%,-50%)">{inner_html}</div>'
            f'{src}{footer("SWIPE")}')


def stat_rows(rows, *, kicker=None, source=None, top=260):
    """Big-number slide: rows = [(number, label, 'a' | 'w')]."""
    items = "".join(
        f'<div style="display:flex;align-items:center;gap:40px;padding:30px 0;border-top:2px solid #262626">'
        f'<div class="{c}" style="font:400 120px/0.9 Anton,sans-serif;width:400px;flex:none;white-space:nowrap">'
        f'{esc(n)}</div><div style="font:500 42px/1.25 Inter,sans-serif;color:#E9E9E9">{esc(t)}</div></div>'
        for n, t, c in rows)
    kick = f'<div class="kick" style="position:absolute;left:72px;top:{top - 120}px">{esc(kicker)}</div>' if kicker else ""
    src = f'<div class="srcline">{esc(source)}</div>' if source else ""
    return f'{kick}<div style="position:absolute;left:72px;right:72px;top:{top}px">{items}</div>{src}{footer("SWIPE")}'


def follow(media_html, line=None):
    """Last slide. line defaults to the niche from theme-page.json."""
    pitch = line or f"for the {CONFIG['niche'] or 'news'} that matters"
    return cover(media_html, [("Follow", "w"), (BRAND["handle"], "a"), (pitch, "w")], cta="FOLLOW FOR MORE")
