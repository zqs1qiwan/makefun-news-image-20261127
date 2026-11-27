# The World in One Day — Friday, 27 November 2026

[![make.fun · news-image-20261127](https://make.fun/badge/news-image-20261127.svg)](https://make.fun/bounty/news-image-20261127?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261127)
[![rank](https://make.fun/badge/news-image-20261127/zqs1qiwan/makefun-news-image-20261127/rank.svg)](https://make.fun/bounty/news-image-20261127/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261127)
[![reward](https://make.fun/badge/news-image-20261127/zqs1qiwan/makefun-news-image-20261127/reward.svg)](https://make.fun/bounty/news-image-20261127?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261127)

A one-image newspaper front page summing up the world's news of
Friday 27 November 2026, built for the make.fun competition
`news-image-20261127`.

## The stories

1. **STORM SURGE TOPS SANDY** — A Thanksgiving nor'easter drove storm
   surges past Hurricane Sandy levels in parts of New Jersey, Virginia
   and Delaware, knocked out power to more than 850,000 customers and
   forced the first-ever weather postponement of the Macy's Thanksgiving
   Day Parade. (NY Post / AP, 26 Nov 2026)
2. **DRONE KILLS TWO IN KUWAIT** — Two Italian technicians were killed
   in a drone attack in Kuwait; Italy and Kuwait blame Iran, which
   denies any role. (AP / NYT, 26 Nov 2026)
3. **US UNVEILS TARIFFS ON 14 NATIONS** — The US Trade Representative
   proposed new duties on 14 trading partners, including China capped
   at 20%, after a months-long investigation into subsidised excess
   industrial capacity; a public hearing is set for January. (Reuters,
   26 Nov 2026)
4. **EU SPLIT OVER UKRAINE LOAN** — EU leaders split over budget
   spending and a $49 billion loan to Ukraine. (AP, 26 Nov 2026)
5. **SPAIN'S DE COS TO LEAD ECB** — Eurozone leaders chose Spain's
   former central bank head, Pablo Hernández de Cos, as the next
   president of the European Central Bank, succeeding Christine
   Lagarde. (AP, 26 Nov 2026)
6. **ISRAELI STRIKES KILL 10 IN GAZA** — Israeli strikes killed 10
   people in Gaza, the third straight night of attacks despite a
   year-old ceasefire. (AP, 26 Nov 2026)

Also today: Ebola cases in DR Congo passed 12,000, the second-largest
outbreak on record; judges in Benjamin Netanyahu's corruption trial
recommended prosecutors drop the bribery charge; Guinea-Bissau's
military junta postponed elections until 2028.

## How it was made

`assets/entry-source.png` is a fresh AI-generated 3×2 photo collage,
one cell per story. `build_image.py` (Python + Pillow) crops the six
cells, typesets the masthead, headlines, subheads and the ALSO band in
Noto Sans Condensed, and writes `entry.png` (1024×1024, under 1 MiB).
It ends with a `verify()` step that reopens the PNG, asserts the size
and byte limit, and prints its SHA-256.

## How to run

```sh
python3 build_image.py        # rebuild entry.png (deterministic)
mkdir -p out && MAKEFUN_OUTPUT_DIR=out node main.ts
```

`main.ts` (Node 22, standard library only) copies `entry.png` to
`$MAKEFUN_OUTPUT_DIR/entry.png` (default `/output`). Running it twice
produces byte-identical output.
