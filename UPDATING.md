# Weekly update

Runs every Monday after BitMine's weekly ETH-holdings release (usually about 8:30am ET), with a Tuesday catch-up for weeks when a holiday pushes the release back.

Artifact: https://claude.ai/artifact/8UXbyDDUSZaJFwTEh9r5wr

The project's source is published with the artifact under `source/` (same layout as this repo). That copy is what the weekly run works from.

## 1. Get the source

Artifact tool, `action: "read"`, `url` = the artifact, `paths` =

```
source/README.md
source/UPDATING.md
source/scripts/build.py
source/src/page.html
source/data/holdings.csv
source/data/ledger.json
```

The files land under `<out_dir>/source/...`. That `source` folder is the project root for every step below.

## 2. Find new releases

- The last row of `data/holdings.csv` is the newest release already included (`pr_date`, `as_of`).
- Search PR Newswire for "Bitmine Immersion Technologies (BMNR) Announces ETH Holdings" releases dated after that `pr_date`. Open each release page with WebFetch and read:
  - release date
  - the "as of" date and time
  - total ETH holdings
  - the ETH price used (and its source)
  - the % of ETH supply and the supply figure it cites ("of N million ETH")
  - staked ETH
- If EDGAR already has the release as an 8-K exhibit (CIK 0001829311), confirm the ETH figure matches.
- Never estimate or interpolate. If a figure can't be confirmed from the release itself, leave that release out and say why in the report.
- If there is no new release yet, stop here, change nothing and report "no new release yet".

## 3. Add the rows

Append one row per new release to `data/holdings.csv`, oldest first, in the existing format:

```
pr_date,as_of,eth_held,eth_price_usd,pct_supply,staked_eth,source_type,source_url,supply_denominator
2026-09-28,2026-09-27 3:00pm ET,6001302,2698,4.9%,5067309,primary,https://www.prnewswire.com/news-releases/...,122.1M
```

- `as_of` is `YYYY-MM-DD h:mmam/pm ET`, exactly as the release states it.
- `pct_supply` is the release's own wording (e.g. `4.9%`).
- Leave `staked_eth` empty if the release doesn't state it.

## 4. Refresh the all-time ledger

WebFetch https://etherscan.io/stat/supply and update `data/ledger.json`:

| Field | Etherscan line |
| --- | --- |
| `crowdsale` | Genesis (crowdsale) |
| `genesisOther` | Genesis (other) |
| `powBlock` | Mining block rewards |
| `powUncle` | Mining uncle rewards |
| `pos` | Eth2 staking rewards |
| `burnt` | Burnt fees |
| `total` | Total supply |
| `asOf` | today's date |

Check that `crowdsale + genesisOther + powBlock + powUncle + pos - burnt` equals `total` within 1 ETH. If the page won't load or the numbers don't reconcile, keep the old file and mention it.

## 5. Build

```
python3 scripts/build.py
```

Run it from the project root. It pulls Coin Metrics daily supply and issuance and writes `artifact.html`, `index.html` and `data/site_data.json`. If it says Coin Metrics hasn't published the latest day yet, wait 30 minutes and retry, up to three times, then report.

## 6. Check

- Read the printed summary line. Holdings should never fall. Share equals holdings ÷ supply. The weekly add is the difference from the previous row.
- Re-read the copy in `src/page.html` for statements the new data could make untrue, and fix only statements that are now false:
  - "BitMine's … is more than all the ETH ever burned and more than every staking reward ever paid"
  - "it slowed ETH buying in July and August 2026 while it bought back its own stock"
  - "BitMine now holds … of all the ETH in existence"

  Most numbers in the copy are computed from the data automatically.

## 7. Publish

First run the Artifact tool with `action: "read"` on the artifact URL. Then publish:

- `file_path` = `artifact.html`
- `url` = the artifact URL. This keeps the same link. Never publish without it.
- `label` = "Data through <as-of date>"
- `files` =

```
{
  "source/README.md": "README.md",
  "source/UPDATING.md": "UPDATING.md",
  "source/scripts/build.py": {"from": "scripts/build.py", "contentType": "text/plain"},
  "source/src/page.html": {"from": "src/page.html", "contentType": "text/plain"},
  "source/data/holdings.csv": "data/holdings.csv",
  "source/data/ledger.json": "data/ledger.json"
}
```

Use `root` = the project folder so the relative source paths resolve.

## 8. Report

End with one or two lines for Carrie: the releases added, new holdings, ETH added that week, share of supply, and anything skipped and why.
