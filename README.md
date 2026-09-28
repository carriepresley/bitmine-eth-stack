# BitMine's ETH Stack

A time-lapse of BitMine Immersion Technologies (BMNR) building its ETH position since it announced its ETH treasury strategy on June 30, 2025. The whole ETH supply is drawn as dots of 10,000 ETH, and a scrubbable timeline shows the stack growing. A second section gives a live estimate of the staking rewards BitMine earns.

- Public page: https://bitmine-eth-stack.vercel.app. Vercel deploys it from this repo's `main` branch on every push.
- Claude artifact copy: https://claude.ai/artifact/8UXbyDDUSZaJFwTEh9r5wr. It's private until shared from the page's Share menu.
- Updated every Monday after BitMine's weekly holdings release, with a Tuesday catch-up for holiday weeks. See `UPDATING.md`.

## Files

| Path | What it is |
| --- | --- |
| `data/holdings.csv` | One row per BitMine ETH-holdings release, Jul 14, 2025 onward, with staked ETH, staking yield and the release URL. The source of truth. |
| `data/network.json` | Total ETH staked network-wide (from ultrasound.money), refreshed on every build. |
| `data/holders.json` | The next five largest ETH holders (ETFs and company treasuries), each with its own date and source. They're shown as colored slices of the orb at the latest week. |
| `src/page.html` | The page template. The build injects the data at `/*__DATA__*/null`. |
| `scripts/build.py` | Pulls daily ETH supply and issuance from Coin Metrics and builds the page. Standard library only. |
| `index.html` | The built page as a standalone document, with link-preview tags. Vercel serves this. |
| `og.jpg` | The 1200×630 link-preview image. It shows no weekly numbers, so it doesn't need a weekly refresh. |
| `scripts/og_image.py` | Optional. Re-renders `og.jpg` from the built page with Playwright, e.g. after a redesign. |
| `artifact.html` | The same page as a fragment for the Claude artifact, which adds `<html>`, `<head>` and `<body>` itself. |
| `data/site_data.json` | The exact data embedded in the built page. |
| `UPDATING.md` | The weekly update procedure. |

## Build

```
python3 scripts/build.py
```

It needs network access to `community-api.coinmetrics.io` and, optionally, `ultrasound.money`.

## Live data

When the page runs on the open web, it fetches two things in the browser once a minute:

- the ETH price, from Coinbase
- total ETH staked, from ultrasound.money

The staking counter ticks in real time. Inside the Claude artifact those fetches are blocked, so the page uses the weekly figures.

## Method

- **Holdings:** BitMine's disclosed totals as of each release's stated time, from its PR Newswire releases. Cross-checked against the same releases filed with the SEC as 8-K exhibits (CIK 0001829311).
- **Supply and issuance:** Coin Metrics Community API, daily `SplyCur` and `IssTotNtv`.
- **Burn:** issuance minus the change in supply.
- **Share of supply:** holdings divided by on-chain supply on the same date. BitMine's releases used 120.7M as the denominator until September 2026, so their stated percentages run slightly higher.
- **Staking rewards:** an estimate, staked ETH × the 7-day annualized yield in BitMine's latest release. It isn't an on-chain measurement.
- **Scale:** one dot or block is 10,000 ETH, and counts are rounded.

Independent visualization built from public data. Not an official BitMine publication. Not investment advice.
