#!/usr/bin/env python3
"""Build the BitMine ETH stack page.

Inputs
  data/holdings.csv  one row per BitMine ETH-holdings release (source of truth)
  data/ledger.json   Etherscan all-time ETH supply breakdown
  src/page.html      page template; the data is injected at /*__DATA__*/null

Fetched
  Coin Metrics Community API: daily ETH supply (SplyCur) and issuance (IssTotNtv)

Outputs
  artifact.html        page fragment published to the Claude artifact
                       (the artifact host adds <html>/<head>/<body> itself)
  index.html           the same page as a standalone document (GitHub Pages, local preview)
  data/site_data.json  the exact data embedded in the page
"""
import csv
import datetime as dt
import json
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BASE = dt.date(2025, 6, 29)       # day 0 = end of Jun 29, 2025; BitMine announced its ETH treasury Jun 30
LONG_START = dt.date(2021, 8, 1)  # EIP-1559 burn went live Aug 5, 2021
CM = "https://community-api.coinmetrics.io/v4/timeseries/asset-metrics"


def cm_series(metrics, start, end):
    url = (f"{CM}?assets=eth&metrics={metrics}&frequency=1d"
           f"&start_time={start}&end_time={end}&page_size=10000")
    rows = []
    while url:
        req = urllib.request.Request(url, headers={"User-Agent": "bitmine-eth-stack/1.0"})
        with urllib.request.urlopen(req, timeout=90) as r:
            d = json.load(r)
        rows += d.get("data", [])
        url = d.get("next_page_url")
    return rows


def main():
    rows = list(csv.DictReader(open(ROOT / "data/holdings.csv", newline="")))
    rows.sort(key=lambda r: r["as_of"][:10])
    end = dt.date.fromisoformat(rows[-1]["as_of"][:10])
    K = (end - BASE).days

    daily = cm_series("SplyCur,IssTotNtv", BASE.isoformat(), end.isoformat())
    S = {r["time"][:10]: float(r["SplyCur"]) for r in daily if r.get("SplyCur")}
    I = {r["time"][:10]: float(r["IssTotNtv"]) for r in daily if r.get("IssTotNtv")}
    days = [(BASE + dt.timedelta(k)).isoformat() for k in range(K + 1)]
    missing = [d for d in days if d not in S or (d != days[0] and d not in I)]
    if missing:
        sys.exit(f"Coin Metrics has no data yet for {missing[-1]} ({len(missing)} day(s) missing). "
                 "It usually publishes a day's figures by early the next morning UTC; rerun later.")

    supply, iss, burn, ci, cb = [], [], [], 0.0, 0.0
    for k, d in enumerate(days):
        if k:
            ci += I[d]
            cb += I[d] - (S[d] - S[days[k - 1]])  # burn = new issuance - change in supply
        supply.append(round(S[d]))
        iss.append(round(ci))
        burn.append(round(cb))

    prs = []
    for r in rows:
        a = dt.date.fromisoformat(r["as_of"][:10])
        prs.append([(a - BASE).days, r["pr_date"], a.isoformat(), r["as_of"][11:], int(r["eth_held"]),
                    float(r["eth_price_usd"]), r["pct_supply"],
                    int(r["staked_eth"]) if r["staked_eth"] else None,
                    r["source_url"], r.get("supply_denominator", "")])

    lr = cm_series("SplyCur", LONG_START.isoformat(), end.isoformat())
    LS = {r["time"][:10]: float(r["SplyCur"]) for r in lr if r.get("SplyCur")}
    pts, d = [], end
    while d >= LONG_START:
        if d.isoformat() not in LS:
            sys.exit(f"Coin Metrics long-run series is missing {d}")
        pts.append(round(LS[d.isoformat()]))
        d -= dt.timedelta(7)
    pts.reverse()
    long_start = (end - dt.timedelta(7 * (len(pts) - 1))).isoformat()

    ledger = json.load(open(ROOT / "data/ledger.json"))
    out = {"asOf": rows[-1]["pr_date"], "base": BASE.isoformat(),
           "supply": supply, "iss": iss, "burn": burn, "prs": prs,
           "long": {"start": long_start, "step": 7, "v": pts}, "ledger": ledger}
    blob = json.dumps(out, separators=(",", ":"))
    (ROOT / "data/site_data.json").write_text(blob + "\n")

    tpl = (ROOT / "src/page.html").read_text()
    if tpl.count("/*__DATA__*/null") != 1 or tpl.count("<!--BODY-->") != 1:
        sys.exit("src/page.html must contain exactly one /*__DATA__*/null and one <!--BODY--> marker")
    frag = tpl.replace("/*__DATA__*/null", blob)
    (ROOT / "artifact.html").write_text(frag)
    head, body = frag.split("<!--BODY-->", 1)
    doc = ("<!doctype html>\n<html lang=\"en\">\n<head>\n<meta charset=\"utf-8\">\n"
           "<meta name=\"viewport\" content=\"width=device-width, initial-scale=1, viewport-fit=cover\">\n"
           + head + "</head>\n<body>\n" + body + "\n</body>\n</html>\n")
    (ROOT / "index.html").write_text(doc)

    last = prs[-1]
    print(f"Built {len(prs)} releases through {last[2]}: {last[4]:,} ETH = "
          f"{last[4] / supply[-1] * 100:.3f}% of {supply[-1]:,} ETH | "
          f"since Jun 30, 2025: minted {iss[-1]:,}, burned {burn[-1]:,}, net {supply[-1] - supply[0]:,}")


if __name__ == "__main__":
    main()
