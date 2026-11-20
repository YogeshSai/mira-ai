# MIRA.AI – Mutual Funds Investment Research & Analysis . AI

A single-page mutual fund analyser for Indian Direct-plan Growth funds: returns (1M to 10Y and since inception), risk measures, EMA trend, category rank, SIP and lump-sum growth, and a Buy / Hold / Skip verdict.

## Use it online
**https://yogeshsai.github.io/mira-ai/**

Open the link in any modern browser (Chrome, Edge, Safari, Firefox), on desktop or mobile. Nothing to install and no sign-in needed.

## Use it offline
Download this repository and open `index.html` in a browser. It is self-contained: the NAV data is embedded, so it works without internet.

## Refresh the data
Source: https://github.com/rajadilipkolli/historical-mf-nav-data (daily release `funds.db.zst`).

    pip install -r requirements.txt
    python3 build_data.py

This downloads the latest database (about 180 MB, expands to about 1 GB), rebuilds `funds_data.json.gz`, and writes a fresh self-contained `fund-check.html` (copy it over `index.html`). It takes a few minutes.

What the build does: keeps active Direct-plan Growth schemes (no IDCW/dividend options, ETFs or unclaimed-amount schemes), fixes the source's decimal-point scale jumps, and drops one-day bad prices.

To refresh automatically, the `.github/workflows/refresh.yml` GitHub Action rebuilds and commits `index.html` on a schedule, and GitHub Pages republishes the site. If your computer hides the `.github` folder, use `refresh-workflow-copy.yml` instead: in GitHub click Add file > Create new file, type `.github/workflows/refresh.yml` as the name, paste the contents of `refresh-workflow-copy.yml`, and commit.

## Files
- `index.html`: the finished app (this is what the website serves).
- `fund-check.template.html`: the app code, with a `__BLOB__` placeholder where the data goes.
- `build_data.py`: downloads the data, cleans it, and injects it into the template.
- `requirements.txt`: the one extra Python library the build needs.
- `.github/workflows/refresh.yml`: optional scheduled GitHub Action for data refresh.
- `refresh-workflow-copy.yml`: a visible copy of the workflow file.

## Ranking method
Funds in a category are ranked by a score: 70% return a year (percentile among peers for the chosen period) + 30% trend. Trend is a 0-100 score from the NAV against its 14, 100 and 200 EMA (price above each: 15/20/25 points; 14 above 100: 10; 100 above 200: 15; 200 EMA rising over 20 days: 15). A "Return only" switch gives a pure return ranking.

## Notes
- Benchmarks are index-fund NAVs used as proxies for the index (small fee drag).
- Returns exclude exit loads and taxes.

## Disclaimer
This tool is for reference only and is not investment advice. We are not responsible for your decisions or for any gains or losses that follow from them. Please do your own research, and consult a qualified financial adviser, before you invest. Past performance does not guarantee future returns.
