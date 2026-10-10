from pathlib import Path
import time
import requests

RAW_DIR = Path("data/raw/wikipedia")
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

if __name__ == "__main__":
    html = fetch_year(2023)
    print(len(html), "characters fetched")