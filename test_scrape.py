"""Offline check of the HTML parsing on a saved page (no network). Run: python test_scrape.py"""
from pathlib import Path
from scrape import dedupe, parse_page

url = "https://books.toscrape.com/catalogue/category/books/mystery_3/index.html"
books, nxt = parse_page(Path(__file__).with_name("fixture_mystery.html").read_text(encoding="utf-8"), url)
assert len(books) == 20, len(books)
assert nxt == "https://books.toscrape.com/catalogue/category/books/mystery_3/page-2.html", nxt
b = books[0]
assert b["category"] == "Mystery" and b["availability"] == "In stock", b
assert isinstance(b["price"], float) and b["price"] > 0 and b["rating"] in range(1, 6), b
assert b["url"].startswith("https://books.toscrape.com/catalogue/") and not b["url"].count(".."), b
assert all(bk["title"] and not bk["title"].endswith("...") for bk in books)
assert len(dedupe(books + books[:3])) == 20
print("ok")
