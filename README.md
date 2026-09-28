# BitMine's ETH Stack

A time-lapse and a set of charts showing how BitMine Immersion Technologies (BMNR) has built up its ETH position since it announced its ETH treasury strategy on June 30, 2025, set inside the whole ETH supply: ETH minted by staking, ETH burned by fees, and BitMine's climb toward 5% of all ETH.

- Live page: https://claude.ai/artifact/8UXbyDDUSZaJFwTEh9r5wr (private until it is shared from the page's Share menu)
- Refreshed every Monday after BitMine's weekly holdings release (Tuesday catch-up for holiday weeks). See `UPDATING.md`.

## Files

| Path | What it is |
| --- | --- |
| `data/holdings.csv` | One row per BitMine ETH-holdings release, Jul 14, 2025 onward, with the release URL. The source of truth. |
| `data/ledger.json` | Etherscan's all-time ETH supply breakdown (genesis, mining, staking rewards, burn). |
| `src/page.html` | The page template. The build injects the data at `/*__DATA__*/null`. |
| `scripts/build.py` | Pulls daily ETH supply and issuance from Coin Metrics and builds the page. Standard library only. |
| `artifact.html` | Built page fragment, published to the artifact (the host adds `<html>`, `<head>` and `<body>`). |
| `index.html` | Built standalone page for local preview or GitHub Pages. |
| `data/site_data.json` | The exact data embedded in the built page. |
| `UPDATING.md` | The weekly update procedure. |

## Build

```
python3 scripts/build.py
```

Needs network access to `community-api.coinmetrics.io`. It stops with a message if Coin Metrics hasn't published the latest day yet.

## Method

- **Holdings:** BitMine's disclosed totals as of each release's stated time, from its PR Newswire releases, cross-checked against the same releases filed with the SEC as 8-K exhibits (CIK 0001829311).
- **Supply and issuance:** Coin Metrics Community API, daily `SplyCur` and `IssTotNtv`.
- **Burn:** derived each day as issuance minus the change in supply; it lines up with ultrasound.money's burn totals.
- **Share of supply:** holdings divided by on-chain supply on the same date. BitMine's releases used 120.7M as the denominator until September 2026, so their stated percentages run slightly higher.
- **Scale:** one dot or block is 10,000 ETH; counts are rounded.

Independent visualization built from public data. Not an official BitMine publication. Not investment advice.
