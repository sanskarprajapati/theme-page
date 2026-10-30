---
name: theme-page
description: "Run an Instagram/TikTok news theme page: on first use, ask for the page's niche and account links and let the user pick a color theme from rendered previews; then research the latest viral news in that niche, show the ranked stories, and after the user confirms, build swipeable carousel posts (1080x1440 photo + video slides) with verified sources. Also turns a crazy video (a file, or an X/YouTube/TikTok link the user sends or you find) into a branded 9:16 clip post with a headline. Use when the user types /theme-page, asks for carousels, news posts or clip posts for their page, sends a video link to repost, or wants today's/yesterday's news turned into posts."
trigger: /theme-page
---

# /theme-page

Turns the latest news in a niche into carousel posts in the viral news-page look (full-bleed photo or video, big ringed logo circles, cut-out subject in front, heavy caps headline with accent words). Four steps, in order, each waiting on the user where marked. Never post anything; the deliverable is files.

Scripts live in the `scripts/` folder next to this SKILL.md (the base directory shown when the skill loads). Call it `$TP` and use its absolute path in every command.

Needs Python 3.9+, Chrome (or Chromium/Edge) and ffmpeg. Optional: yt-dlp for clip posts from links, and macOS 14+ with Xcode command line tools for the cut-out subject on covers (without it, covers render without the cut-out). The xpoz MCP server makes research much better (live X/Reddit/TikTok/Instagram stats); without it, use WebSearch and the browser.

## Step 0: find the workspace

The workspace is the folder holding `theme-page.json`; carousels go in its `carousels/`, clip posts in `clips/`.

```bash
python3 -c "import sys; sys.path.insert(0, '$TP'); import config; print(config.find('.'))"
```

- **Found:** say in one line which page it's set up for (niche, handle, color) and go to step 3. If the user asks to change the niche, accounts or color, rerun only that part of steps 1–2.
- **Not found:** this is a first run. Run `python3 $TP/doctor.py` first. If anything required is missing, tell the user exactly what to install (the doctor prints the command) and stop until it's fixed. Then run steps 1 and 2. Use the current directory as the workspace unless the user names one.

## Step 1: niche, accounts and logo (ask, then wait)

Ask in one message:
1. What is the page's niche? (e.g. "AI and tech", "football transfers", "luxury cars"). Push for specific over broad, since it drives the research.
2. Links to the page's accounts (Instagram, TikTok, X, YouTube…). They're used for the handle and name on every post.
3. The page's logo: a file path, an image link, or "use my profile picture". A square image works best; it's shown in a circle on every carousel and clip post.

Then look the accounts up yourself (xpoz MCP: `getInstagramUser`, `getTwitterUser`, `getTiktokUser`; else open the profile in the browser) to get the handle, display name and profile picture. Also note what the page already posts (recent topics and tone) if you can see it; it sharpens story picks in step 3.

For the logo, use what they gave. If they chose their profile picture (or gave no logo), use the profile picture URL from the account lookup. Show them how it looks later on the theme preview.

```bash
python3 $TP/setup.py --dir <workspace> --niche "<niche>" --handle <handle> --name "<display name>" \
    --account instagram=<url> [--account x=<url> ...] --badge <logo file or image URL>
```

`--badge` copies or downloads the logo into `<workspace>/brand/`. With no logo at all, the badge shows the name's initials.

## Step 2: color theme (show, ask, then wait)

```bash
python3 $TP/preview_themes.py --dir <workspace> --out <workspace>/theme-preview.jpg \
    --headline "<a sample hook from their niche, *accent words* in asterisks>" [--image <a photo from their niche>]
```

Show the sheet to the user (SendUserFile, or open it) and ask which color they want. The sheet also shows their logo in the badge, so ask them to check it looks right. Each tile is labelled with its palette id: electric-cyan, acid-lime, hot-orange, signal-red, gold, violet, mint, hot-pink. If they want something else, take a hex code. Save it:

```bash
python3 $TP/setup.py --dir <workspace> --palette <id>     # or --accent "#33CCFF"
```

## Step 3: research the news (show, then wait for the pick)

Follow `references/research.md`. In short:
- Window: the last 24–48 hours unless the user names a day. Say the exact dates you searched.
- Find 6–8 candidate stories in the niche. Check every one really broke in the window. Drop reshared old stories and anything you can't verify.
- Rank by real virality evidence (views, likes, upvotes, outlets) and by how well it carousels: a person, a surprising number, a demo video, a "wait, what?" angle.
- For heavy research, hand the sweep to a subagent with the brief in research.md, then verify the top picks yourself.

Show a table: rank, hook (cover-ready), why it's viral (numbers), when it broke, visuals available (mark video), main source. Recommend 3 and ask which to build. **Do not build until the user confirms.**

While researching, also note any **crazy standalone videos** in the niche: a clip that is the story by itself (a wild demo, an AI-generated scene everyone is sharing, a robot doing something odd). List them under the table as clip-post ideas with view counts and links. Build them with the clip-post flow below if the user picks them.

## Step 4: build the carousels

For each confirmed story:

1. Scaffold: `python3 $TP/new_carousel.py <slug> --dir <workspace> --title "<story>"`
2. Collect assets into `<carousel>/assets/`:
   - the primary posts' media (photos and videos),
   - Wikimedia Commons photos (check the license on the file page),
   - logos from Simple Icons: `https://cdn.jsdelivr.net/npm/simple-icons@13.21.0/icons/<name>.svg`, then add `fill="<brand color>"` to the `<svg>` tag,
   - avatars for any recreated posts.
   Videos must be **2 minutes or less** on a slide. Pick the window with `start=`/`dur=` (the renderer refuses longer).
3. Verify every fact and number against the primary source. Pull live post stats (xpoz `getTwitterPostsByIds` etc.) for recreated posts.
4. Write `build.py` from the slide recipe in `references/design.md`, using the API in `references/api.md`. Cover first: the cover sells the post.
5. Render: `python3 build.py` (or `python3 build.py 1 3` for some slides). JPG slides land in `final/`, video slides as MP4 with a poster in `out/`.
6. Review every slide visually: make a contact sheet with ffmpeg `hstack`/`vstack` from the JPGs and posters, and look at it. Check the review list at the end of design.md and fix before showing.
7. Fill `CAPTION.md`: caption, a sources table (claim → slide → URL) and asset licenses. Flag media that isn't licensed (creator uploads, news stills) so the user can decide.

Deliver: send one sheet of all covers plus the video covers (SendUserFile). Then summarise per carousel: slide count, which slides are video, and anything left out because it couldn't be verified. Say plainly that nothing was posted.

## Clip posts (9:16 video)

Use this when the user sends a video or a video link (X, YouTube, TikTok, Instagram) or picks a clip-post idea from step 3. The page needs to be set up first (step 0).

1. **Watch it before writing anything.** Pull frames (`ffmpeg -vf fps=1/3,scale=320:-1,tile=6x3`) and look at them. Find out who made it and what it really is (real footage, AI-generated, a game mod, an ad) from the original post. Never call AI footage real.
2. **Write the headline:** one or two lines, sentence case, under ~15 words, what makes it crazy, and at most one emoji at the end (e.g. "They put Mike Tyson in Zelda and it's unbelievable 😭"). It must be literally true.
3. **Pick the window:** the best part, **2 minutes or less**. Short and punchy (10–45s) usually wins.
4. Render:
   ```bash
   python3 $TP/clip.py --src "<file or URL>" --headline "<headline>" \
       --out <workspace>/clips/<slug>/<slug>.mp4 [--start <s>] [--dur <s>] [--pos "50% 40%"]
   ```
   URLs are downloaded with yt-dlp to `source.mp4` next to the output. The clip keeps its sound. For vertical sources, `--pos` picks which part stays when the video is cropped to fit under the headline.
5. Check the poster (`<slug>.jpg`) and a frame or two from the MP4: headline fits, the action is in frame.
6. Write `<workspace>/clips/<slug>/CAPTION.md`: a short caption, the original post URL and the creator's handle as credit, plus the hashtags. Creator videos aren't licensed, so say that and leave the call to the user.

## Rules

- Never invent facts, quotes or stats. If a number differs between sources, use the primary source or leave it out, and say so in CAPTION.md.
- Keep politically loaded stories out unless the niche is politics.
- Don't name private individuals who went viral against their will.
- Captions and slide text: short, plain sentences; no hype words. Follow the be-human skill if it's installed.
