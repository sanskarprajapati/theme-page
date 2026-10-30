# Researching the news

## Where to look

- **X:** xpoz `getTwitterPostsByKeywords` with niche keywords, sorted by engagement. Then `getTwitterPostsByIds` for live stats, and `getTwitterPostComments` for the top replies.
- **Reddit:** xpoz `getRedditPostsByKeywords` / `getRedditSubredditWithPostsByName` for the niche's main subreddits.
- **Instagram / TikTok:** xpoz keyword and hashtag search to see what's already spreading.
- **Web:** WebSearch for "<niche> news <date>". Then the primary source: company blog, filing, paper, the person's own post.
- **Accounts:** the user's own accounts and 2–3 big pages in the niche, to see what's already been covered.

## Rules for a candidate

- **It broke in the window.** Confirm the first post or article timestamp. Reshares of old news are the most common trap; drop them and list them as dropped.
- **Facts come from a primary source**, or two reputable outlets agreeing. Mark anything unconfirmed. Unconfirmed claims never go on a slide.
- **Virality is measured, not guessed.** Use views, likes, reposts, bookmarks, upvotes, comment counts and the number of outlets, with post IDs/URLs.
- **Visuals exist.** A story with a video or a strong photo beats a dry one. Note durations and resolutions of available videos.
- **Rights.** Note who owns each photo or video: Commons license, brand asset, creator upload (not licensed: credit it), news still (not licensed: flag it).

## Subagent brief (when delegating the sweep)

> Today is <date>. Find stories in the niche "<niche>" that broke between <start> and <end> and are going viral. Use xpoz (load via ToolSearch) and WebSearch. Return the 6 best, ranked. For each: a one-line cover hook; 4–8 key facts each with a source URL (primary preferred, mark unconfirmed); virality numbers with post IDs; video/photo assets with URLs, durations and license; the exact time it broke. List stories you dropped and why (too old, unverifiable, political). Do not fabricate; say when you couldn't find something.

## What to show the user

| # | Hook | Why it's viral | Broke | Visuals | Source |
|---|---|---|---|---|---|

Mark your top 3 and give a one-line reason for each. Then wait for their pick.
