#!/usr/bin/env python3
"""
EP countdown-GIF generator.

Leest alle campagnes uit de map campaigns/ (één JSON-bestand per campagne)
en maakt per campagne een animated GIF in _site/<slug>/countdown.gif.
De map _site/ wordt door GitHub Actions op GitHub Pages gepubliceerd.

Gebruik:
    python scripts/generate_countdown.py
    python scripts/generate_countdown.py --offset 60
    python scripts/generate_countdown.py --now "2026-11-01 23:58:30"   # testen
"""

import argparse
import html
import json
import sys
from datetime import datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
CAMPAIGN_DIR = ROOT / "campaigns"
OUTPUT_DIR = ROOT / "_site"

WIDTH = 610           # maximale breedte voor de nieuwsbrief (650 px)
HEIGHT = 190
FRAMES = 180          # maximaal 180 frames ...
FRAME_MS = 1000       # ... van 1 seconde = 180 seconden aftellen
PALETTE_COLORS = 48   # minder kleuren = kleiner bestand

LABELS = ["DAGEN", "UREN", "MINUTEN", "SECONDEN"]

DEFAULT_COLORS = {
    "achtergrond": "#171717",
    "vak": "#2B2B2B",
    "cijfers": "#FFFFFF",
    "labels": "#28A745",
    "accent": "#F28C00",
    "kop": "#FFFFFF",
}

# Eerst een eigen lettertype in fonts/, anders een systeemlettertype.
FONT_FALLBACKS = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",   # GitHub Actions (Ubuntu)
    "/System/Library/Fonts/Supplemental/Arial Bold.ttf",       # macOS
    "C:/Windows/Fonts/arialbd.ttf",                            # Windows
]


def find_font_path():
    own_fonts = sorted((ROOT / "fonts").glob("*.ttf")) + sorted((ROOT / "fonts").glob("*.otf"))
    for path in own_fonts + [Path(p) for p in FONT_FALLBACKS]:
        if path.exists():
            return str(path)
    sys.exit("Geen lettertype gevonden. Zet een .ttf-bestand in de map fonts/.")


class Renderer:
    def __init__(self, campaign, font_path):
        self.c = campaign
        self.colors = {**DEFAULT_COLORS, **campaign.get("kleuren", {})}
        self.font_digits = ImageFont.truetype(font_path, 70)
        # Labels zo groot mogelijk, maar 'SECONDEN' moet in het vak passen.
        size = 21
        while size > 12:
            self.font_label = ImageFont.truetype(font_path, size)
            if self.font_label.getlength(max(LABELS, key=len)) <= 116:
                break
            size -= 1
        self.font_head = ImageFont.truetype(font_path, 22)
        self.font_colon = ImageFont.truetype(font_path, 54)
        self.font_end = ImageFont.truetype(font_path, 42)
        self.font_end_sub = ImageFont.truetype(font_path, 20)

    def _base(self):
        img = Image.new("RGB", (WIDTH, HEIGHT), self.colors["achtergrond"])
        draw = ImageDraw.Draw(img)
        # Optioneel kader in de GIF; uit als de Ternair-snippet al een rand om de afbeelding zet.
        if self.c.get("kader", True):
            draw.rectangle([0, 0, WIDTH - 1, HEIGHT - 1], outline=self.colors["accent"], width=3)
        return img, draw

    def countdown_frame(self, seconds_left):
        days, rest = divmod(seconds_left, 86400)
        hours, rest = divmod(rest, 3600)
        minutes, seconds = divmod(rest, 60)
        values = [days, hours, minutes, seconds]

        img, draw = self._base()
        draw.text((WIDTH // 2, 28), self.c.get("kop", "NOG MAAR"),
                  font=self.font_head, fill=self.colors["kop"], anchor="mm")

        box_w, box_h, gap = 128, 122, 22
        left = (WIDTH - (4 * box_w + 3 * gap)) // 2
        top = 50
        for i, (value, label) in enumerate(zip(values, LABELS)):
            x = left + i * (box_w + gap)
            draw.rectangle([x, top, x + box_w, top + box_h], fill=self.colors["vak"])
            draw.rectangle([x, top, x + box_w, top + 4], fill=self.colors["accent"])
            draw.text((x + box_w // 2, top + 52), f"{value:02d}",
                      font=self.font_digits, fill=self.colors["cijfers"], anchor="mm")
            draw.text((x + box_w // 2, top + 104), label,
                      font=self.font_label, fill=self.colors["labels"], anchor="mm")
            if i < 3:
                draw.text((x + box_w + gap // 2, top + 48), ":",
                          font=self.font_colon, fill=self.colors["accent"], anchor="mm")
        return img

    def end_frame(self):
        img, draw = self._base()
        lines = self.c.get("eindmelding", ["DEZE ACTIE", "IS AFGELOPEN"])
        sub = self.c.get("eindmelding_sub", "")
        line_h = 50
        block_h = len(lines) * line_h + (34 if sub else 0)
        y = (HEIGHT - block_h) // 2 + line_h // 2
        fills = [self.colors["cijfers"], self.colors["accent"]]
        for i, line in enumerate(lines):
            draw.text((WIDTH // 2, y), line, font=self.font_end,
                      fill=fills[i % 2], anchor="mm")
            y += line_h
        if sub:
            draw.text((WIDTH // 2, y + 2), sub, font=self.font_end_sub,
                      fill=self.colors["labels"], anchor="mm")
        return img


def build_frames(campaign, renderer, now):
    tz = ZoneInfo(campaign.get("tijdzone", "Europe/Amsterdam"))
    end = datetime.strptime(campaign["einde"], "%Y-%m-%d %H:%M:%S").replace(tzinfo=tz)
    frames = []
    for i in range(FRAMES):
        left = int((end - (now + timedelta(seconds=i))).total_seconds())
        if left <= 0:
            frames.append(renderer.end_frame())
            break  # eindmelding blijft staan, verdere frames zijn overbodig
        frames.append(renderer.countdown_frame(left))
    return frames


def save_gif(frames, path):
    # Eén vast kleurenpalet voor alle frames: geen flikkering en een kleiner bestand.
    sample = Image.new("RGB", (WIDTH, HEIGHT * 2))
    sample.paste(frames[0], (0, 0))
    sample.paste(frames[-1], (0, HEIGHT))
    palette = sample.quantize(colors=PALETTE_COLORS, method=Image.Quantize.MEDIANCUT)
    indexed = [f.quantize(palette=palette, dither=Image.Dither.NONE) for f in frames]

    path.parent.mkdir(parents=True, exist_ok=True)
    # Geen 'loop'-parameter: de GIF speelt één keer af en blijft op het laatste frame staan,
    # in plaats van na 180 seconden terug te springen naar de begintijd.
    indexed[0].save(
        path,
        save_all=True,
        append_images=indexed[1:],
        duration=FRAME_MS,
        optimize=True,
        disposal=1,
    )


def write_index(campaigns, generated_at):
    rows = []
    for c in campaigns:
        slug = html.escape(c["slug"])
        rows.append(
            f'<h2>{html.escape(c["naam"])}</h2>'
            f'<p>Einde: {html.escape(c["einde"])} ({html.escape(c.get("tijdzone", "Europe/Amsterdam"))})<br>'
            f'GIF: <code>{slug}/countdown.gif</code></p>'
            f'<img src="{slug}/countdown.gif" width="610" alt="Countdown {slug}">'
        )
    page = (
        "<!doctype html><html lang=\"nl\"><head><meta charset=\"utf-8\">"
        "<meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">"
        "<meta name=\"robots\" content=\"noindex\"><title>EP countdowns</title>"
        "<style>body{font-family:Arial,sans-serif;background:#f4f4f4;color:#171717;"
        "max-width:650px;margin:0 auto;padding:16px}img{max-width:100%;height:auto}</style>"
        "</head><body><h1>EP countdowns</h1>"
        f"<p>Laatst bijgewerkt: {generated_at:%d-%m-%Y %H:%M:%S} (Europe/Amsterdam)</p>"
        + "".join(rows)
        + "</body></html>"
    )
    (OUTPUT_DIR / "index.html").write_text(page, encoding="utf-8")
    (OUTPUT_DIR / ".nojekyll").write_text("", encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(description="Genereer EP countdown-GIF's")
    parser.add_argument("--offset", type=int, default=0,
                        help="Start het aftellen zoveel seconden later (compenseert publicatietijd)")
    parser.add_argument("--now", help="Testtijd 'JJJJ-MM-DD UU:MM:SS' in Europe/Amsterdam")
    args = parser.parse_args()

    amsterdam = ZoneInfo("Europe/Amsterdam")
    if args.now:
        now = datetime.strptime(args.now, "%Y-%m-%d %H:%M:%S").replace(tzinfo=amsterdam)
    else:
        now = datetime.now(amsterdam).replace(microsecond=0)
    start = now + timedelta(seconds=args.offset)

    font_path = find_font_path()
    print(f"Lettertype: {font_path}")

    campaigns = []
    for config in sorted(CAMPAIGN_DIR.glob("*.json")):
        campaign = json.loads(config.read_text(encoding="utf-8"))
        if not campaign.get("actief", True):
            print(f"- {config.name}: overgeslagen (actief = false)")
            continue
        frames = build_frames(campaign, Renderer(campaign, font_path), start)
        out = OUTPUT_DIR / campaign["slug"] / "countdown.gif"
        save_gif(frames, out)
        frames[0].save(out.with_name("voorbeeld.png"), optimize=True)
        print(f"- {campaign['slug']}: {len(frames)} frames, {out.stat().st_size / 1024:.0f} KB")
        campaigns.append(campaign)

    OUTPUT_DIR.mkdir(exist_ok=True)
    write_index(campaigns, now)


if __name__ == "__main__":
    main()
