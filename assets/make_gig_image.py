"""Render the gig images from the real demo output (books.xlsx): 1280x769 (Fiverr) and 1024x768 (Upwork/Contra)."""
import math
from pathlib import Path
import openpyxl
from PIL import Image, ImageDraw, ImageFont

root = Path(__file__).resolve().parent.parent
wb = openpyxl.load_workbook(root / "books.xlsx")
rows = list(wb["Books"].iter_rows(values_only=True))[1:]
n = wb["Summary"]["B1"].value
H = "/System/Library/Fonts/HelveticaNeue.ttc"
f = lambda s, b=False: ImageFont.truetype(H, s, index=1 if b else 0)
BG, GREEN, WHITE = (15, 42, 36), (110, 231, 183), (255, 255, 255)


def fit(d, t, font, w):
    while d.textlength(t, font=font) > w:
        t = t[:-2].rstrip() + "…"
    return t


def render(size, out, k):
    """k scales fonts/left column so the narrower 4:3 version still fits."""
    W, Hh = size
    im = Image.new("RGB", size, BG)
    d = ImageDraw.Draw(im)
    s = lambda v: int(v * k)
    y0 = (Hh - 769) // 2 + 140 if k == 1 else 150
    d.text((60, y0), "Website data", font=f(s(64), True), fill=WHITE)
    d.text((60, y0 + s(75)), "to Excel", font=f(s(64), True), fill=GREEN)
    d.text((60, y0 + s(150)), "scraped, cleaned and deduped", font=f(s(30)), fill=(200, 220, 212))
    for i, t in enumerate(["Any public site, all pages", "Clean, deduped columns",
                           "Excel, CSV or Google Sheets", "Reusable Python script"]):
        yy = y0 + s(230) + i * s(44)
        d.line([(62, yy + s(15)), (70, yy + s(23)), (84, yy + s(7))], fill=GREEN, width=4)
        d.text((98, yy), t, font=f(s(26)), fill=WHITE)
    x = 60
    for t, c in [("WEB", (59, 130, 246)), ("EXCEL", (33, 150, 83)), ("CSV", (120, 120, 130))]:
        w = d.textlength(t, font=f(18, True)) + 28
        d.rounded_rectangle((x, y0 + s(440), x + w, y0 + s(440) + 36), 8, fill=c)
        d.text((x + 14, y0 + s(448)), t, font=f(18, True), fill=WHITE); x += w + 14

    # spreadsheet card built from real output
    X, Y = int(W * 0.44), y0 + 10
    PW = W - 40 - X
    cols = [("Title", PW - 330), ("Category", 120), ("Price", 80), ("Rating", 70)]
    d.rounded_rectangle((X, Y, X + PW, Y + 470), 14, fill=WHITE)
    d.text((X + 24, Y + 20), "books.xlsx", font=f(20, True), fill=(30, 30, 30))
    d.text((X + PW - 24, Y + 24), f"{n:,} rows", font=f(16, True), fill=(33, 150, 83), anchor="ra")
    ty = Y + 64
    d.rectangle((X + 20, ty, X + PW - 20, ty + 38), fill=(232, 240, 236))
    cx = X + 30
    for name, w in cols:
        d.text((cx, ty + 10), name, font=f(16, True), fill=(40, 40, 40)); cx += w
    for i, r in enumerate(rows[:8]):
        ty += 40
        if i % 2:
            d.rectangle((X + 20, ty - 2, X + PW - 20, ty + 36), fill=(246, 248, 247))
        cx = X + 30
        for v, (_, w) in zip([r[0], r[4], f"£{r[1]:.2f}"], cols):
            d.text((cx, ty + 8), fit(d, v, f(16), w - 14), font=f(16), fill=(50, 50, 50)); cx += w
        for j in range(5):  # star rating, drawn (Helvetica has no star glyph)
            c = (cx + 7 + j * 13, ty + 18)
            pts = [(c[0] + (6 if q % 2 == 0 else 2.6) * math.sin(q * math.pi / 5),
                    c[1] - (6 if q % 2 == 0 else 2.6) * math.cos(q * math.pi / 5)) for q in range(10)]
            d.polygon(pts, fill=(235, 165, 20) if j < r[2] else (220, 220, 220))
    d.text((X + 24, Y + 430), f"Real output: {n:,} books from books.toscrape.com (a scraping-practice site)",
           font=f(14), fill=(110, 110, 110))
    im.save(out)


render((1280, 769), root / "assets" / "gig-image.png", 1)
render((1024, 768), root / "assets" / "gig-4x3.png", 0.78)
