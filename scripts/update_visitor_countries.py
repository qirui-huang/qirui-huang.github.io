#!/usr/bin/env python3
"""Fetch per-country visitor totals from the public MapMyVisitors stats page
and write them to _data/visitor_countries.json for the homepage visitor map.

MapMyVisitors keeps counting through the map widget on the homepage; this
script only mirrors its all-time totals, so the counts never reset.
"""
import csv
import html
import json
import os
import re
import sys
import urllib.request

STATS_URL = "https://mapmyvisitors.com/web/1c30b"
# Live totals feed the stats page polls; the HTML total is a cached snapshot.
TOTALS_URL = "https://mapmyvisitors.com/ajax/orange_dots?id=2243387&last_hit_id=0&max_hit_id=0&max_visit_count=0"
OUT_PATH = os.path.join(os.path.dirname(__file__), "..", "_data", "visitor_countries.json")
# Country center points, from Google's DSPL canonical countries dataset.
CENTROIDS_PATH = os.path.join(os.path.dirname(__file__), "country_centroids.csv")

COUNTRY_ROW = re.compile(
    r'<span class="flag ([a-z]{2})"[^>]*></span>\s*<span class="vstor">([^<]+)</span>\s*</td>'
    r'\s*<td>.*?</td>\s*<td>\s*(\d+)\s*</td>',
    re.S,
)


def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    return urllib.request.urlopen(req, timeout=30).read().decode("utf-8", "replace")


def main():
    page = fetch(STATS_URL)
    total = json.loads(fetch(TOTALS_URL)).get("total_hits")
    countries = [
        {"code": code, "name": html.unescape(name).strip(), "visits": int(visits)}
        for code, name, visits in COUNTRY_ROW.findall(page)
    ]
    if not total or not countries:
        sys.exit("Could not parse the MapMyVisitors stats page; layout may have changed.")

    with open(CENTROIDS_PATH, encoding="utf-8") as f:
        centroids = {row["country"].lower(): row for row in csv.DictReader(f)}
    for c in countries:
        row = centroids.get(c["code"])
        if row:
            c["lat"], c["lng"] = float(row["latitude"]), float(row["longitude"])

    countries.sort(key=lambda c: c["visits"], reverse=True)
    data = {"total_pageviews": int(total), "countries": countries}

    with open(OUT_PATH, "w", encoding="utf-8", newline="\n") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")
    print(json.dumps(data, ensure_ascii=False))


if __name__ == "__main__":
    main()
