# MIRA.AI – Mutual Funds Investment Research & Analysis . AI

A single-page mutual fund analyser for Indian Direct-plan Growth funds: returns (1M to 10Y and since inception), risk measures, category rank, SIP and lump-sum growth, and a Buy / Hold / Skip verdict.

## Just use it
Open `index.html` in any modern browser (Chrome, Edge, Safari, Firefox). It is self-contained: the NAV data is embedded, so it works offline. NAV data is as of the date shown by the app's data snapshot (17 Nov 2026 in this package).

## Refresh the data
Source: https://github.com/rajadilipkolli/historical-mf-nav-data (daily release `funds.db.zst`).

    pip install -r requirements.txt
    python3 build_data.py

This downloads the latest database (about 180 MB, expands to about 1 GB), rebuilds `funds_data.json.gz`, and writes a fresh self-contained `fund-check.html` (copy it over `index.html`). It takes a few minutes.

What the build does: keeps active Direct-plan Growth schemes (no IDCW/dividend options, ETFs or unclaimed-amount schemes), fixes the source's decimal-point scale jumps, and drops one-day bad prints.

## Files
- `index.html`: the finished app (open this).
- `fund-check.template.html`: the app code, with a `__BLOB__` placeholder where the data goes.
- `build_data.py`: downloads the data, cleans it, and injects it into the template.
- `.github/workflows/refresh.yml`: optional daily GitHub Action that rebuilds and commits `index.html` (turn on GitHub Pages from the repo root to host it).

## Notes
- Benchmarks are index-fund NAVs used as proxies for the index (small fee drag).
- Returns exclude exit loads and taxes. For information and education only; not investment advice.

## Ranking method
Funds in a category are ranked by a score: 70% return a year (percentile among peers for the chosen period) + 30% trend. Trend is a 0-100 score from the NAV against its 14, 100 and 200 EMA (price above each: 15/20/25 points; 14 above 100: 10; 100 above 200: 15; 200 EMA rising over 20 days: 15). A "Return only" switch gives a pure return ranking.
