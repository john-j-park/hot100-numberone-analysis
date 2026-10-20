from pathlib import Path
import time

import pandas as pd
import requests
import io

ROOT = Path(__file__).resolve().parents[1]   # src/ -> repo root
RAW_DIR = ROOT / "data" / "raw" / "wikipedia"
HEADERS = {"User-Agent": "hot100-lyrics-project/0.1 (john.park8+hot100@gmail.com)"}

def url_for_year(year: int) -> str:
    return f"https://en.wikipedia.org/wiki/List_of_Billboard_Hot_100_number_ones_of_{year}"

def fetch_year(year: int) -> str:
    """Return the page HTML for a year, using a disk cache."""
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    cache_file = RAW_DIR / f"{year}.html"
    if cache_file.exists():
        return cache_file.read_text(encoding="utf-8")

    resp = requests.get(url_for_year(year), headers=HEADERS, timeout=30)
    resp.raise_for_status()           # raises an error on 404/500 instead of failing silently
    cache_file.write_text(resp.text, encoding="utf-8")
    time.sleep(1)                     # be polite to the server
    return resp.text

def find_chart_table(html: str) -> pd.DataFrame:
    """Return the weekly Hot 100 table from one year's page."""
    # Finds the chart table in the html, returns the last one that has a column called "Issue Date" (because of 1958)
    tables = pd.read_html(io.StringIO(html))

    potential_tables = []
    for t in tables:
        if "Issue date" in list(t):
            potential_tables.append(t)

    return potential_tables[len(potential_tables)-1]

def clean_year(df: pd.DataFrame, year: int) -> pd.DataFrame:
    """Weekly rows with tidy columns: no, song, artist, week (a real date)."""
    # rename Title->Song, drop Ref., strip quotes and [footnotes],
    # turn "January 28" + year into a date with pd.to_datetime,
    # pull the number out of "397 (re)" (hint: .str.extract(r"(\d+)")).

def scrape_all(start=1958, end=2026) -> pd.DataFrame:
    """All weekly rows for every year, concatenated."""

def collapse_to_songs(weekly: pd.DataFrame) -> pd.DataFrame:
    """One row per song: first_week, weeks_at_1, no."""
    # groupby song + artist, then .agg(first_week=("week","min"), weeks_at_1=("week","count"), ...)

if __name__ == "__main__":
    html = fetch_year(2023)
    print(len(html), "characters fetched")
