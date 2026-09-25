#!/usr/bin/env python3
"""Fetch per-country visitor totals from the public MapMyVisitors stats page
and write them to _data/visitor_countries.json for the homepage flag list.

MapMyVisitors keeps counting through the map widget on the homepage; this
script only mirrors its all-time totals, so the counts never reset.
"""
import html
import json
import os
import re
import sys
import urllib.request

STATS_URL = "https://mapmyvisitors.com/web/1c30b"
OUT_PATH = os.path.join(os.path.dirname(__file__), "..", "_data", "visitor_countries.json")

COUNTRY_ROW = re.compile(
    r'<span class="flag ([a-z]{2})"[^>]*></span>\s*<span class="vstor">([^<]+)</span>\s*</td>'
    r'\s*<td>.*?</td>\s*<td>\s*(\d+)\s*</td>',
    re.S,
)
TOTAL_PAGEVIEWS = re.compile(r'class="pvTV total-pageviews[^"]*"\s+data-value="(\d+)"')


def main():
    req = urllib.request.Request(STATS_URL, headers={"User-Agent": "Mozilla/5.0"})
    page = urllib.request.urlopen(req, timeout=30).read().decode("utf-8", "replace")

    total = TOTAL_PAGEVIEWS.search(page)
    countries = [
        {"code": code, "name": html.unescape(name).strip(), "visits": int(visits)}
        for code, name, visits in COUNTRY_ROW.findall(page)
    ]
    if not total or not countries:
        sys.exit("Could not parse the MapMyVisitors stats page; layout may have changed.")

    countries.sort(key=lambda c: c["visits"], reverse=True)
    data = {"total_pageviews": int(total.group(1)), "countries": countries}

    with open(OUT_PATH, "w", encoding="utf-8", newline="\n") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")
    print(json.dumps(data, ensure_ascii=False))


if __name__ == "__main__":
    main()
