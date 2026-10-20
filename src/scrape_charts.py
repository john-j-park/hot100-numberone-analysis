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
        if any(str(c).startswith("Issue date") for c in t.columns):
            potential_tables.append(t)

    return potential_tables[len(potential_tables)-1]

def clean_year(df: pd.DataFrame, year: int) -> pd.DataFrame:
    """Weekly rows with tidy columns: no, song, artist, week (a real date)."""
    # Renames and cleans table
    df = df.drop(columns=["Ref."],errors="ignore")
    df = df.drop(columns=["Reference"],errors="ignore")
    df = df.drop(columns=["Reference(s)"],errors="ignore")
    df.columns = ["no", "week", "song", "artist"]
    df = df[df["song"].str.contains('"', na=False)]
    df["week"] = df["week"].str.replace(r"\[.*?\]", "", regex=True).str.strip()
    new_column = df["week"]+ " " + str(year)
    new_column = pd.to_datetime(new_column, format="%B %d %Y")
    df["week"] = new_column
    new_song = df["song"]
    new_song = new_song.str.extract(r'"(.*?)"',expand=False)
    df["song"] = new_song

    df["no"] = pd.to_numeric(df["no"], errors="coerce").astype("Int64")
    df["artist"] = df["artist"].str.replace(r"\[.*?\]", "", regex=True).str.strip()
    return df

def scrape_all(start=1958, end=2026) -> pd.DataFrame:
    """All weekly rows for every year, concatenated."""
    list_of_tables = []
    for y in range(start,end):
        list_of_tables.append(clean_year(find_chart_table(fetch_year(y)), y))

    return pd.concat(list_of_tables, ignore_index=True)

def collapse_to_songs(weekly: pd.DataFrame) -> pd.DataFrame:
    weekly = weekly.copy()
    weekly["no"] = weekly["no"].fillna(
        weekly.groupby(["song", "artist"])["no"].transform("min")
    )
    songs = weekly.groupby("no").agg(
        song=("song", "first"),
        artist=("artist", "first"),
        first_week=("week", "min"),
        weeks_at_1=("week", "count"),
    ).reset_index()
    return songs

if __name__ == "__main__":
    html = fetch_year(2023)
    print(len(html), "characters fetched")
