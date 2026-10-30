# Carousel design

Canvas 1080x1440 (3:4). Every slide shares the footer (handle · SWIPE FOR MORE · page name) and the accent color from theme-page.json.

## The cover

Layers, back to front (this is what makes the look):

1. **Backdrop**: full-bleed photo or video of the story's hero (a person, product, robot, scene). It fades to black over the bottom ~35%.
2. **Circles** (`bubble()`): 1–3 rings with a white border. Use them for:
   - company/product logos (`logo=True`, brand-color `bg`),
   - a close-up or second photo (a detail, the "before", a screenshot),
   - a video clip (the demo moment).
   Make them **big**: 360–450px diameter. Put them in the top half, at the frame edges, overlapping each other or bleeding off the edge a little (negative x is fine).
3. **Cut-out subject** (`subject()`): the backdrop with its background removed, laid over the circles so the person stands *in front* of the logos. Use it when the backdrop has one clear hero (a face, a person, a product). Skip it when the hero is small or busy (top-down shots, crowds, screenshots); the cut-out looks wrong there.
4. **Front layer**: the fade, a thin accent divider with the brand badge, the headline, the footer, and any `arrow()` (a hand-drawn arrow pointing from a circle to the detail it explains).

Variants seen on top news pages:
- "X kills Y" or "alternative to Y": the rival logos get `cross=True` (red X).
- "Watch what happens": a video circle and an arrow, with `cta="SWIPE TO WATCH"`.

Check placement: keep faces clear of the circles. Circles cover hair, shoulders and background, never eyes or mouth.

### Headline

- 3–5 lines of heavy caps, auto-shrunk to fit. 12–25 words.
- 1–3 accent phrases (the surprising part: the number, the twist, the payoff). Everything else white.
- Hook formulas that work:
  - "This guy just [did surprising thing] …"
  - "A [person] [did X] and found [Y]. Then [twist]."
  - "[Company] just [did X]. [Consequence]."
  - "You can now [surprising new thing]."
  - "[Number] [unit] faster/cheaper than [famous thing]."
- The headline must be literally true. Keep the punch, but the facts can't drift.

## Body slides (6–9 slides total)

A typical order:

1. Cover.
2. The primary source: `framed(tweet(...))` recreating the original post with real stats. It can carry its video (`vslot(..., layer="over")` as `media=`).
3. What happened: `story()` with a photo or video panel, or `text_slide()`.
4. The key detail or numbers: `story()` or `stat_rows()`.
5. The twist, catch or controversy.
6. Reactions: 1–2 top replies via `framed(tweet(... reply_to=...))`.
7. Optional engagement slide: a question asking for a comment.
8. `follow()`.

Body text: Inter, sentence case, max ~45 words per slide, `<strong>` for key facts, `<span class="a">` for one or two accent phrases. A kicker (short caps label) on top. A source line on every fact slide.

## Video

- Any `.mp4/.mov/.webm` given to `media()`, `bubble()` or `vslot()` makes that slide an MP4.
- **Hard cap 2 minutes** per clip. Usual lengths: cover clips 5–15s, clips inside a recreated post up to 60s, body clips 10–30s.
- Covers can be video too. For a video cover plus cut-out, call `subject()` with the same `src/pos/start/dur` as the backdrop; this takes about a minute per 15s.
- `zoom=` punches into part of the frame, for example a small detail inside a circle.
- Sound: the backdrop clip keeps its audio unless `audio=False`. Circles are silent.

## Review list (look at the rendered sheet)

- Headline fits, nothing clipped, and the accent words are the right ones.
- Circles: big enough to read the logo, and no face covered.
- The cut-out edge is clean (no halo, no missing hands or hair). Drop the cut-out if it isn't.
- No bystander pieces in front of a circle (Vision sometimes merges people standing close). Trim with `subject(clip=...)` or move the circle.
- Body text doesn't touch the source line or footer.
- Video posters show the right moment, and the circle crop shows the action (use `pos`/`zoom`).
- Every number on a slide matches CAPTION.md's sources table.
