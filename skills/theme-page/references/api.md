# Slide API

Import in build.py (the scaffold does it): `from kit import run, tweet` and `from theme import ...`.
Paths in slides are relative to `<carousel>/html/`, so assets are `"../assets/<file>"`. `pos` is a CSS object-position ("50% 30%").

| Function | What it makes |
|---|---|
| `media(src, pos, *, start=0, dur=None, audio=True)` | Full-bleed backdrop, photo or video |
| `bubble(src, x, y, d, *, logo=False, bg="#fff", pad=.18, ring="#fff", ring_w=7, pos, start, dur, zoom=1, cross=False)` | Ringed circle: logo on a disc, photo or video clip. `cross=True` adds a red X |
| `subject(src, pos, *, start=0, dur=None, keep_all=False, clip=None)` | Background-removed copy of the backdrop (largest subject only, unless keep_all), laid over the circles. If a bystander gets merged into the cut-out, trim it with `clip="polygon(...)"` (CSS clip-path in slide %). Pass it to `cover(fg=...)` with the same src/pos (and start/dur for video) |
| `arrow(x1, y1, x2, y2, bend=.35)` | Hand-drawn white arrow, always on top |
| `cover(media_html, segments, extras="", fg="", size=112, max_h=470, cta="SWIPE FOR MORE")` | The cover. `segments` = `[("text", "w" or "a"), ...]`; `extras` = bubbles and arrows joined with `+` |
| `story(media_html, paras, *, media_h=760, kicker=None, source=None)` | Photo/video panel on top, text below (auto-shrinks to fit) |
| `text_slide(paras, *, kicker=None, source=None, top=None)` | Text on black |
| `stat_rows(rows, *, kicker=None, source=None)` | Big numbers: `rows = [("15 MIN", "label", "a" or "w"), ...]` |
| `framed(html, *, source=None)` | Centres any block (e.g. `tweet(...)`) on black |
| `tweet(av, name, handle, text, *, check="blue"/"gold"/None, date, stats={"reply","rt","like","views"}, media, reply_to, size=44, width=950)` | X dark-mode post recreation (from kit) |
| `vslot(src, pos, *, start, dur, layer="under"/"over"/"fg", zoom, style)` | Raw video hole; use `layer="over"` inside a tweet's `media=` with an explicit width/height style |
| `follow(media_html, line=None)` | Closing "Follow @handle for the <niche> that matters" cover |
| `run(ROOT, slug, SLIDES, css=THEME_CSS)` | Renders everything (or the slide numbers given on the command line) |

Paragraph strings may contain `<strong>` and `<span class="a">` (accent). Plain text inside `segments`, kickers and sources is escaped automatically; paragraphs are raw HTML, so escape `<` and `&` yourself.

Cut-outs and video:
- Cut-outs are cached in `assets/cut/` and rebuilt only when the source changes.
- Video slides are composited back to front: backdrop clip, page, circle clips, cut-out clip, then the text layer.
- Clips shorter than the slide loop. A slide lasts as long as its longest clip.
