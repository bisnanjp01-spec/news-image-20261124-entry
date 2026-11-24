# news-image-20261124-entry

[![make.fun · news-image-20261124](https://make.fun/badge/news-image-20261124.svg)](https://make.fun/bounty/news-image-20261124)
[![rank](https://make.fun/badge/news-image-20261124/bisnanjp01-spec/news-image-20261124-entry/rank.svg)](https://make.fun/bounty/news-image-20261124/leaderboard)
[![reward](https://make.fun/badge/news-image-20261124/bisnanjp01-spec/news-image-20261124-entry/reward.svg)](https://make.fun/bounty/news-image-20261124)

A one-page newspaper front page that sums up Tuesday 24 November 2026 in a
single image. `main.py` (Python 3.13 standard library only) draws the
1024x1024 PNG itself — its own 5x7 bitmap font, its own PNG encoder — with
no network, no clock and no randomness, so every run writes identical bytes
to `/output/entry.png`, well under the 1 MiB cap.

## The day, in one page

- **Top story:** Nvidia reinstates Jensen Huang as chief executive less than
  two weeks after he resigned; the shares jump 31% in a day, and the S&P 500
  rises 4.73% with the Nikkei up 3.91%.
- **Hormuz:** Iran says tankers hit mines in the strait and tightens its
  curbs on passage.
- **Gaza:** an Israeli strike kills Hamas internal-security chief Naeem Abu
  Nahel and six others.
- **Ukraine:** an overnight strike on Zaporizhzhia kills 2 and wounds 40.
- **Justice:** the International Court of Justice finds Myanmar guilty of
  genocide against the Rohingya.
- **Space:** NATO vows to defend space after reports of a Russian
  nuclear-armed satellite.
- **Americas:** a car bomb injures 23 in Villavicencio, Colombia.
- **Also today:** the US blacklists Megaspeed, South Korea offers $375,000
  rewards to catch AI exam cheating, 25 die in strikes in Yemen, and an
  Indonesian factory fire kills 26.

Headlines grounded in the day's reporting (AP, Reuters, BBC, UN News,
Just Security early edition, 24 November 2026).

## Run it

```sh
python3 main.py
```

Writes `/output/entry.png`. To write elsewhere for a local test, set
`ENTRY_OUTPUT` to the target path, e.g. `ENTRY_OUTPUT=/tmp/entry.png
python3 main.py`.

## Design notes

The page is drawn, not pasted: every letter comes from the 5x7 bitmap font
in `main.py`, every panel, rule and pictogram (chip, tanker, globe, scales,
satellite, blast) from filled rectangles, circles and lines, and the PNG
itself from a small encoder in the same file. Nothing is read from disk at
run time, so the output depends only on the code.

## License

MIT — see `LICENSE`.
