"""
Refresh data/col_multipliers.json with BEA Regional Price Parities (all items) by state.

Source: FRED CSV export XXRPPALL (BEA, 100 = U.S. average). No API key required.
Housing ZIP factors use U.S. Census ACS B25064 at runtime in the app (see app.py).

Usage (from project root):
  py scripts/build_col_multipliers.py
"""

from __future__ import annotations

import csv
import io
import json
from pathlib import Path
import time
import urllib.error
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "col_multipliers.json"

# 50 states + DC → FRED series = USPS + "RPPALL"
USPS_TO_STATE_NAME: dict[str, str] = {
    "AL": "Alabama",
    "AK": "Alaska",
    "AZ": "Arizona",
    "AR": "Arkansas",
    "CA": "California",
    "CO": "Colorado",
    "CT": "Connecticut",
    "DE": "Delaware",
    "DC": "District of Columbia",
    "FL": "Florida",
    "GA": "Georgia",
    "HI": "Hawaii",
    "ID": "Idaho",
    "IL": "Illinois",
    "IN": "Indiana",
    "IA": "Iowa",
    "KS": "Kansas",
    "KY": "Kentucky",
    "LA": "Louisiana",
    "ME": "Maine",
    "MD": "Maryland",
    "MA": "Massachusetts",
    "MI": "Michigan",
    "MN": "Minnesota",
    "MS": "Mississippi",
    "MO": "Missouri",
    "MT": "Montana",
    "NE": "Nebraska",
    "NV": "Nevada",
    "NH": "New Hampshire",
    "NJ": "New Jersey",
    "NM": "New Mexico",
    "NY": "New York",
    "NC": "North Carolina",
    "ND": "North Dakota",
    "OH": "Ohio",
    "OK": "Oklahoma",
    "OR": "Oregon",
    "PA": "Pennsylvania",
    "RI": "Rhode Island",
    "SC": "South Carolina",
    "SD": "South Dakota",
    "TN": "Tennessee",
    "TX": "Texas",
    "UT": "Utah",
    "VT": "Vermont",
    "VA": "Virginia",
    "WA": "Washington",
    "WV": "West Virginia",
    "WI": "Wisconsin",
    "WY": "Wyoming",
}


def _fred_latest_rpp(usps: str) -> float | None:
    sid = f"{usps}RPPALL"
    url = f"https://fred.stlouisfed.org/graph/fredgraph.csv?id={sid}"
    req = urllib.request.Request(url, headers={"User-Agent": "WiseSpendingDataScript/1.0"})
    with urllib.request.urlopen(req, timeout=60) as resp:
        text = resp.read().decode("utf-8", errors="replace")
    rows = list(csv.reader(io.StringIO(text)))
    if len(rows) < 2:
        return None
    last = rows[-1]
    if len(last) < 2:
        return None
    try:
        return float(last[1])
    except ValueError:
        return None


def main() -> None:
    bea_state_rpp: dict[str, float] = {}
    for usps, full in USPS_TO_STATE_NAME.items():
        v = None
        for attempt in range(3):
            try:
                v = _fred_latest_rpp(usps)
                break
            except (urllib.error.URLError, ConnectionResetError, TimeoutError):
                time.sleep(1.2 * (attempt + 1))
        time.sleep(0.35)
        if v is None:
            print(f"warn: skip {usps} ({full})")
            continue
        key = full.lower()
        bea_state_rpp[key] = round(v, 3)
        print(f"{full}: {v}")

    payload = {
        "meta": {
            "model": "bea_state_rpp_plus_acs_median_rent_zcta",
            "version": 2,
            "baseline": "1.0 = U.S. average. BEA RPP uses 100 as national price level (see bea_state_rpp).",
            "housing_weight": 0.33,
            "acs_year": 2023,
            "sources": {
                "bea_rpp": "https://www.bea.gov/data/prices-inflation/regional-price-parities-state-and-metro-area",
                "fred_series": "https://fred.stlouisfed.org (series {USPS}RPPALL, all items)",
                "housing_rent": "https://api.census.gov ACS B25064 median gross rent; ZCTA ≈ ZIP",
            },
        },
        "bea_state_rpp": bea_state_rpp,
    }

    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)
        f.write("\n")
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()
