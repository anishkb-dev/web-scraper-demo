"""Scrape every book on books.toscrape.com (a site built for scraping practice) into Excel + CSV.

usage: python scrape.py -o books.xlsx
"""
import argparse
import csv
import time
from collections import Counter
from datetime import datetime
from pathlib import Path
from urllib.parse import urljoin
from urllib.robotparser import RobotFileParser

import openpyxl
import requests
from bs4 import BeautifulSoup
from openpyxl.styles import Font

BASE = "https://books.toscrape.com/"
UA = "web-scraper-demo"
DELAY = 0.5  # seconds between requests
FIELDS = ["title", "price", "rating", "availability", "category", "url"]
RATINGS = {"One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5}

session = requests.Session()
session.headers["User-Agent"] = UA
robots = RobotFileParser(urljoin(BASE, "robots.txt"))


def get(url: str, tries: int = 3) -> str:
    if not robots.can_fetch(UA, url):
        raise PermissionError(f"robots.txt disallows {url}")
    for i in range(tries):
        try:
            time.sleep(DELAY)
            r = session.get(url, timeout=20)
            r.raise_for_status()
            return r.content.decode("utf-8")
        except requests.RequestException as e:
            if i == tries - 1:
                raise
            print(f"  retry {i + 1} for {url}: {e}")
            time.sleep(2 ** i)


def parse_page(html: str, url: str) -> tuple[list[dict], str | None]:
    """One category listing page -> (books on it, next page URL or None)."""
    soup = BeautifulSoup(html, "html.parser")
    category = soup.h1.get_text(strip=True)
    books = []
    for pod in soup.select("article.product_pod"):
        a = pod.h3.a
        books.append(dict(
            title=a["title"],
            price=float(pod.select_one(".price_color").get_text(strip=True).lstrip("£")),
            rating=RATINGS[pod.select_one(".star-rating")["class"][1]],
            availability=pod.select_one(".availability").get_text(strip=True),
            category=category,
            url=urljoin(url, a["href"]),
        ))
    nxt = soup.select_one("li.next a")
    return books, urljoin(url, nxt["href"]) if nxt else None


def dedupe(rows: list[dict]) -> list[dict]:
    return list({r["url"]: r for r in rows}.values())


def scrape() -> list[dict]:
    robots.read()  # a missing robots.txt (404) means everything is allowed
    home = BeautifulSoup(get(BASE), "html.parser")
    categories = [urljoin(BASE, a["href"]) for a in home.select(".side_categories ul ul a")]
    rows = []
    for i, url in enumerate(categories, 1):
        n = 0
        while url:
            books, url = parse_page(get(url), url)
            rows += books; n += len(books)
        print(f"[{i}/{len(categories)}] {books[0]['category'] if books else '?'}: {n} books")
    return rows


def write(rows: list[dict], xlsx: Path):
    with open(xlsx.with_suffix(".csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, FIELDS); w.writeheader(); w.writerows(rows)
    wb = openpyxl.Workbook()
    ws = wb.active; ws.title = "Books"
    ws.append(FIELDS)
    for r in rows:
        ws.append([r[k] for k in FIELDS])
    for c in ws["B"][1:]:
        c.number_format = "£#,##0.00"
    for k, width in zip("ABCDEF", (60, 10, 8, 12, 20, 80)):
        ws.column_dimensions[k].width = width
    ws.freeze_panes = "A2"; ws.auto_filter.ref = ws.dimensions
    s = wb.create_sheet("Summary")
    s.append(["rows", len(rows)])
    s.append(["scraped at", datetime.now().strftime("%Y-%m-%d %H:%M")])
    s.append(["source", BASE]); s.append([])
    s.append(["category", "books"])
    for cat, n in Counter(r["category"] for r in rows).most_common():
        s.append([cat, n])
    s.column_dimensions["A"].width = 22; s.column_dimensions["B"].width = 28
    for c in (*ws[1], *s["A"][:3], *s[5]):
        c.font = Font(bold=True)
    wb.save(xlsx)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("-o", "--out", type=Path, default=Path("books.xlsx"))
    a = ap.parse_args()
    raw = scrape()
    rows = dedupe(raw)
    print(f"{len(raw)} scraped, {len(raw) - len(rows)} duplicates removed, {len(rows)} rows")
    write(rows, a.out)
    print("wrote", a.out, "and", a.out.with_suffix(".csv"))
