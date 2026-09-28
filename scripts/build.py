#!/usr/bin/env python3
"""Build the BitMine ETH stack page.

Inputs
  data/holdings.csv  one row per BitMine ETH-holdings release (source of truth)
  src/page.html      page template; the data is injected at /*__DATA__*/null

Fetched
  Coin Metrics Community API: daily ETH supply (SplyCur) and issuance (IssTotNtv)
  ultrasound.money: network-wide staked ETH (best effort; falls back to data/network.json)

Also reads
  data/holders.json  the next-largest ETH holders (ETFs, company treasuries) shown on the orb

Outputs
  artifact.html        page fragment published to the Claude artifact
                       (the artifact host adds <html>/<head>/<body> itself)
  index.html           the same page as a standalone document with link-preview tags
                       (served by Vercel; also works as a local preview)
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
CM = "https://community-api.coinmetrics.io/v4/timeseries/asset-metrics"
SITE = "https://bitmine-eth-stack.vercel.app"   # public address; link previews need absolute URLs
FAVICON = ("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'%3E"
           "%3Crect width='32' height='32' rx='7' fill='%2305050B'/%3E"
           "%3Crect x='10' y='10' width='12' height='12' fill='%23C6FF00'/%3E%3C/svg%3E")


def social_head(eth, share):
    """Link-preview tags for the standalone page (X, LinkedIn, iMessage, Slack)."""
    title = "BitMine's ETH Stack"
    desc = (f"BitMine holds {eth:,} ETH, {share:.2f}% of all the ETH in existence. "
            "Watch every weekly disclosure since June 2025 stack up, "
            "plus a live estimate of its staking rewards.")
    tags = [
        f'<link rel="canonical" href="{SITE}/">',
        f'<link rel="icon" href="{FAVICON}">',
        '<meta name="theme-color" content="#05050B">',
        '<meta property="og:type" content="website">',
        f'<meta property="og:url" content="{SITE}/">',
        f'<meta property="og:title" content="{title}">',
        f'<meta property="og:description" content="{desc}">',
        f'<meta property="og:image" content="{SITE}/og.jpg">',
        '<meta property="og:image:width" content="1200">',
        '<meta property="og:image:height" content="630">',
        '<meta property="og:image:alt" content="An orb of dots for the whole ETH supply, with BitMine\'s share pulled out into a stack of lime blocks.">',
        '<meta name="twitter:card" content="summary_large_image">',
        f'<meta name="twitter:title" content="{title}">',
        f'<meta name="twitter:description" content="{desc}">',
        f'<meta name="twitter:image" content="{SITE}/og.jpg">',
    ]
    return "\n".join(tags) + "\n"


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


def network_staked():
    """Total ETH staked network-wide (beacon chain balances). Best effort."""
    try:
        req = urllib.request.Request("https://ultrasound.money/api/v2/fees/supply-parts",
                                     headers={"User-Agent": "bitmine-eth-stack/1.0"})
        with urllib.request.urlopen(req, timeout=30) as r:
            v = int(json.load(r)["beaconBalancesSum"]) / 1e9
        if v > 1e7:
            net = {"staked": round(v), "asOf": dt.date.today().isoformat(), "source": "https://ultrasound.money"}
            (ROOT / "data/network.json").write_text(json.dumps(net, indent=2) + "\n")
            return net
    except Exception as e:  # noqa: BLE001 - keep the build going without it
        print(f"note: ultrasound.money unavailable ({e}); using the saved network figure")
    f = ROOT / "data/network.json"
    return json.loads(f.read_text()) if f.exists() else None


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
                    r["source_url"], r.get("supply_denominator", ""),
                    float(r["staking_yield"]) if r.get("staking_yield") else None])

    network = network_staked()
    hf = ROOT / "data/holders.json"
    holders = json.loads(hf.read_text()) if hf.exists() else None
    out = {"asOf": rows[-1]["pr_date"], "base": BASE.isoformat(),
           "supply": supply, "iss": iss, "burn": burn, "prs": prs, "network": network, "holders": holders}
    blob = json.dumps(out, separators=(",", ":"))
    (ROOT / "data/site_data.json").write_text(blob + "\n")

    tpl = (ROOT / "src/page.html").read_text()
    if tpl.count("/*__DATA__*/null") != 1 or tpl.count("<!--BODY-->") != 1:
        sys.exit("src/page.html must contain exactly one /*__DATA__*/null and one <!--BODY--> marker")
    frag = tpl.replace("/*__DATA__*/null", blob)
    (ROOT / "artifact.html").write_text(frag)
    last = prs[-1]
    head, body = frag.split("<!--BODY-->", 1)
    doc = ("<!doctype html>\n<html lang=\"en\">\n<head>\n<meta charset=\"utf-8\">\n"
           "<meta name=\"viewport\" content=\"width=device-width, initial-scale=1, viewport-fit=cover\">\n"
           + head + social_head(last[4], last[4] / supply[-1] * 100)
           + "</head>\n<body>\n" + body + "\n</body>\n</html>\n")
    (ROOT / "index.html").write_text(doc)

    print(f"Built {len(prs)} releases through {last[2]}: {last[4]:,} ETH = "
          f"{last[4] / supply[-1] * 100:.3f}% of {supply[-1]:,} ETH | "
          f"since Jun 30, 2025: minted {iss[-1]:,}, burned {burn[-1]:,}, net {supply[-1] - supply[0]:,}")


if __name__ == "__main__":
    main()
