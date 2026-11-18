[![make.fun](https://make.fun/badge/news-image-20261117.svg)](https://make.fun/bounty/news-image-20261117?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261117)
[![rank](https://make.fun/badge/news-image-20261117/Emjee22/news-image-20261117-entry-v5/rank.svg)](https://make.fun/bounty/news-image-20261117/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261117)
[![reward](https://make.fun/badge/news-image-20261117/Emjee22/news-image-20261117-entry-v5/reward.svg)](https://make.fun/bounty/news-image-20261117?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261117)

# Tuesday 17 November 2026 — The World's News in One Image (v5, serif poster)

Entry for the make.fun bounty `news-image-20261117`: a program that draws one
image summing up the world's news of Tuesday 17 November 2026 — 20 stories,
6 continents, one day. This is the third entry for the same competition
(v5, serif poster); it replaces the earlier entries if submitted last
before the deadline.

v5 is an edit of the v4 map-hero entry: same structure (navy masthead,
BY THE NUMBERS strip, dot-grid world map with numbered pins for the 10
biggest stories, 3 leads, numbered one-liner lists, DATE CHECK box, sources
footer), but rendered with Pillow and smooth Liberation Serif type — no
pixel-art bitmap font — plus flat illustrations in the 3 leads, region tags,
and a readable two-row numbered list for stories 4–10.

## How it works

`main.py` (Python 3.13, Pillow 10.2.0) draws a 1024x1024 PNG entirely from
scratch: smooth serif headlines (legible at ~300 px), a dot-grid world map
with numbered pins, flat illustrations for the 3 lead stories, flag chips,
region tags, a BY THE NUMBERS strip, a DATE CHECK box and a sources footer.
Fonts are bundled in `fonts/` (Liberation Serif/Sans, SIL OFL) and loaded
by relative path, so the program runs standalone from its own directory.
No network, no image files. Two runs write byte-identical output.

Run it:

```sh
mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
```

## Files

- `main.py` — the whole entry
- `fonts/` — bundled Liberation Serif/Sans TTFs the program loads
- `README.md` — this file
- `LICENSE` — MIT
