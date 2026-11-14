# Web Scraper Demo

Scrape every page of a website into one clean Excel workbook and a CSV file.

- Follows pagination across every category, so you get all 1,000 books and not only page 1
- Columns: title, price (a real number, not text), star rating 1-5, availability, category, product URL
- Duplicate rows are removed by URL
- The Excel file has a bold, frozen header row, filters on every column and sensible column widths. A `Summary` sheet shows the row count, when the scrape ran and how many books are in each category
- Polite by default: its own User-Agent, a delay between requests, retries with backoff, and a robots.txt check before every request

```
$ python scrape.py -o books.xlsx
[1/50] Travel: 11 books
[2/50] Mystery: 32 books
...
[50/50] Crime: 1 books
1000 scraped, 0 duplicates removed, 1000 rows
wrote books.xlsx and books.csv
```

Sample of `books.xlsx` (real output, committed in this repo):

| title | price | rating | availability | category |
|---|---|---|---|---|
| It's Only the Himalayas | £45.17 | 2 | In stock | Travel |
| Full Moon over Noah’s Ark: An Odyssey to Mount Ararat and Beyond | £49.43 | 4 | In stock | Travel |
| See America: A Celebration of Our National Parks & Treasured Sites | £48.87 | 3 | In stock | Travel |
| Vagabonding: An Uncommon Guide to the Art of Long-Term World Travel | £36.94 | 2 | In stock | Travel |
| Under the Tuscan Sun | £37.33 | 3 | In stock | Travel |

The target is [books.toscrape.com](https://books.toscrape.com), a sandbox site built for scraping practice. Two of its categories really are called "Default" and "Add a comment"; the scraper keeps them as the site lists them.

## Run it

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python scrape.py -o books.xlsx     # about 1 minute; writes books.xlsx and books.csv
python test_scrape.py              # offline test of the HTML parsing on a saved page
```

## Scope

This demo collects public data only. It respects robots.txt and the site's terms. For a real client site, the selectors in `parse_page` change and the rest of the script stays the same. Logins, JavaScript-rendered pages (Playwright), scheduled runs and Google Sheets export can be added when a job needs them.
