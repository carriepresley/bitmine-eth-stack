# Weekly update

Runs every Monday after BitMine's weekly ETH-holdings release (usually about 8:30am ET), with a Tuesday catch-up for weeks when a holiday pushes the release back.

- Public page: https://bitmine-eth-stack.vercel.app
- GitHub: `carriepresley/bitmine-eth-stack`. It's the source of truth, and Vercel deploys the public page from its `main` branch on every push.
- Artifact: https://claude.ai/artifact/8UXbyDDUSZaJFwTEh9r5wr (its `source/` files mirror this repo)

## 1. Get the source

- If the GitHub repo is reachable (attach it with push access), clone it. The clone is the project root.
- Otherwise, use the Artifact tool with `action: "read"` on the artifact. Pass these paths:

  ```
  source/README.md
  source/UPDATING.md
  source/scripts/build.py
  source/src/page.html
  source/data/holdings.csv
  source/data/network.json
  source/data/holders.json
  ```

  The downloaded `source` folder is the project root.

## 2. Find new releases

The last row of `data/holdings.csv` is the newest release already included. Search PR Newswire for "Bitmine Immersion Technologies (BMNR) Announces ETH Holdings" releases dated after that row's `pr_date`. Open each with WebFetch and read:

- the release date
- the "as of" date and time
- total ETH holdings
- the ETH price used
- the % of ETH supply and the supply figure it cites ("of N million ETH")
- staked ETH
- the staking yield, in the wording "7-day yield of X% (annualized)"

If EDGAR (CIK 0001829311) already has the release as an 8-K exhibit, confirm the ETH figure matches. Never estimate or interpolate. If a figure can't be confirmed from the release itself, leave that release out and say why.

If there's no new release yet, stop and change nothing.

## 3. Add the rows

Append one row per release to `data/holdings.csv`, oldest first:

```
pr_date,as_of,eth_held,eth_price_usd,pct_supply,staked_eth,source_type,source_url,supply_denominator,staking_yield
2026-09-28,2026-09-27 3:00pm ET,6001302,2698,4.9%,5067309,primary,https://www.prnewswire.com/news-releases/...,122.1M,2.62
```

- `staking_yield` is the percent number only (`2.62`).
- Leave `staked_eth` and `staking_yield` empty when the release doesn't state them. The live staking counter uses the newest row that has both.

## 3b. Refresh the other large holders (best effort)

`data/holders.json` lists the next-largest ETH holders after BitMine. The page colors them on the orb at the latest week. Refresh what you can verify and keep the rest. Each entry keeps its own `asOf` and `source`, so only change a date when you actually refreshed that entry.

- **BlackRock ETHA:** WebFetch the iShares product page. Read "Basket Ether Amount" and "Shares Outstanding". ETH held = basket ETH × shares outstanding ÷ 40,000.
  - Sanity check: net assets ÷ ETH held should be close to the ETH price.
- **SharpLink (SBET) and The Ether Machine (ETHM):** WebFetch https://www.coingecko.com/en/treasuries/ethereum.
- **Grayscale (ETHE + ETH) and Fidelity FETH:** update only from an issuer page or a tracker that shows ETH held. If you can't get a current figure, keep the old one.

Keep the list sorted by ETH, largest first, and limit it to the top five. If another ETF or treasury company overtakes one of them, swap it in with its source.

## 4. Build

```
python3 scripts/build.py
```

Run it from the project root. It pulls Coin Metrics daily supply and issuance, refreshes `data/network.json` (total ETH staked) from ultrasound.money, and writes `artifact.html`, `index.html` and `data/site_data.json`.

If it says Coin Metrics hasn't published a day yet, wait 30 minutes and retry, up to three times.

## 5. Check

- In the printed summary line, holdings should never fall.
- Re-read the copy in `src/page.html` and fix only a sentence that the new data made false. Most numbers are computed.

## 6. Publish

First run the Artifact tool with `action: "read"` on the artifact URL. Then publish:

- `file_path` = `artifact.html`
- `url` = the artifact URL (keeps the same link)
- `root` = the project root
- `label` = "Data through <as-of date>"
- `files` =

  ```
  {"source/README.md":"README.md",
   "source/UPDATING.md":"UPDATING.md",
   "source/scripts/build.py":{"from":"scripts/build.py","contentType":"text/plain"},
   "source/src/page.html":{"from":"src/page.html","contentType":"text/plain"},
   "source/data/holdings.csv":"data/holdings.csv",
   "source/data/network.json":"data/network.json",
   "source/data/holders.json":"data/holders.json"}
  ```

## 7. Push

If the GitHub repo is attached, commit `data/`, `artifact.html` and `index.html` with the message "Data through <as-of date>: <ETH held> ETH", then push to `main`. Vercel redeploys the public page from that push within a minute or two. Confirm that https://bitmine-eth-stack.vercel.app serves the new holdings figure.

`og.jpg`, the link-preview image, carries no weekly numbers, so it doesn't need refreshing. The preview text is rebuilt with the page.

## 8. Report

One or two lines: the releases added, new holdings, ETH added that week, share of all ETH, the staking yield, and anything skipped.
