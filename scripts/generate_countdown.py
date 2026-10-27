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
HEIGHT = 164
FRAMES = 180          # maximaal 180 frames ...
FRAME_MS = 1000       # ... van 1 seconde = 180 seconden aftellen
PALETTE_COLORS = 48   # minder kleuren = kleiner bestand

DEFAULT_LABELS = ["DAGEN", "UREN", "MINUTEN", "SECONDEN"]

# EP-stijl van de eerdere countdown: geel vlak, groene rand, witte vakken, oranje labelbalk.
DEFAULT_COLORS = {
    "achtergrond": "#FFF200",
    "rand": "#2CA843",
    "vak": "#FFFFFF",
    "cijfers": "#222222",
    "labelbalk": "#F37300",
    "labeltekst": "#FFFFFF",
    "schaduw": "#222222",
    "kop": "#222222",
}

# Maten van de vier tijdvakken (in pixels)
BOX_W, BOX_GAP, BOX_LEFT = 121, 11, 48
BOX_TOP, BOX_BOTTOM, BOX_BORDER = 65, 150, 3
LABEL_H = 21
SHADOW = 4

# Cijfers en teksten worden smaller en schuin getekend (condensed italic),
# zodat het met elk vet lettertype op de originele EP-countdown lijkt.
CONDENSE = 0.82
SLANT = 0.2

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
        self.labels = campaign.get("labels", DEFAULT_LABELS)
        self.font_path = font_path
        self._fonts = {}

    def _font(self, size):
        if size not in self._fonts:
            self._fonts[size] = ImageFont.truetype(self.font_path, size)
        return self._fonts[size]

    def _text_mask(self, text, size):
        """Tekst als grijswaardenmasker, smaller gemaakt en schuin gezet."""
        font = self._font(size)
        left, top, right, bottom = font.getbbox(text)
        w, h = right - left, bottom - top
        mask = Image.new("L", (w + 4, h + 4), 0)
        ImageDraw.Draw(mask).text((2 - left, 2 - top), text, font=font, fill=255)
        mask = mask.resize((max(1, round(mask.width * CONDENSE)), mask.height), Image.LANCZOS)
        extra = round(SLANT * mask.height)
        return mask.transform((mask.width + extra, mask.height), Image.AFFINE,
                              (1, SLANT, -extra, 0, 1, 0), resample=Image.BICUBIC)

    def _text(self, img, center, text, size, color, max_width=None):
        """Tekst gecentreerd tekenen; zo nodig kleiner tot hij in max_width past."""
        mask = self._text_mask(text, size)
        while max_width and mask.width > max_width and size > 10:
            size -= 1
            mask = self._text_mask(text, size)
        bbox = mask.getbbox() or (0, 0, mask.width, mask.height)
        mask = mask.crop(bbox)
        x = round(center[0] - mask.width / 2)
        y = round(center[1] - mask.height / 2)
        img.paste(Image.new("RGB", mask.size, color), (x, y), mask)

    def _box(self, draw, x0, x1, label_top):
        """Wit vak met groene rand, oranje labelbalk en schaduw rechtsonder."""
        draw.rectangle([x0 + SHADOW, BOX_TOP + SHADOW, x1 + SHADOW, BOX_BOTTOM + SHADOW],
                       fill=self.colors["schaduw"])
        draw.rectangle([x0, BOX_TOP, x1, BOX_BOTTOM], fill=self.colors["rand"])
        inner = BOX_BORDER
        draw.rectangle([x0 + inner, BOX_TOP + inner, x1 - inner, label_top - 1],
                       fill=self.colors["vak"])
        draw.rectangle([x0 + inner, label_top, x1 - inner, BOX_BOTTOM - inner],
                       fill=self.colors["labelbalk"])

    def _base(self):
        img = Image.new("RGB", (WIDTH, HEIGHT), self.colors["achtergrond"])
        draw = ImageDraw.Draw(img)
        draw.rectangle([0, 0, WIDTH - 1, HEIGHT - 1], outline=self.colors["rand"], width=4)
        self._text(img, (WIDTH / 2, 24), self.c.get("kop", ""), 40, self.colors["kop"], WIDTH - 40)
        return img, draw

    def countdown_frame(self, seconds_left):
        days, rest = divmod(seconds_left, 86400)
        hours, rest = divmod(rest, 3600)
        minutes, seconds = divmod(rest, 60)
        values = [days, hours, minutes, seconds]

        img, draw = self._base()
        if self.c.get("subkop"):
            self._text(img, (WIDTH / 2, 50), self.c["subkop"], 22, self.colors["kop"], WIDTH - 60)

        label_top = BOX_BOTTOM - BOX_BORDER - LABEL_H
        for i, (value, label) in enumerate(zip(values, self.labels)):
            x0 = BOX_LEFT + i * (BOX_W + BOX_GAP)
            x1 = x0 + BOX_W - 1
            self._box(draw, x0, x1, label_top)
            mid = (x0 + x1) / 2
            self._text(img, (mid, (BOX_TOP + BOX_BORDER + label_top) / 2), f"{value:02d}",
                       72, self.colors["cijfers"], BOX_W - 16)
            self._text(img, (mid, label_top + LABEL_H / 2), label,
                       20, self.colors["labeltekst"], BOX_W - 14)
        return img

    def end_frame(self):
        img, draw = self._base()
        message = self.c.get("eindmelding", "DEZE ACTIE IS AFGELOPEN")
        if isinstance(message, list):
            message = " ".join(message)
        sub = self.c.get("eindmelding_sub", "")

        x0 = BOX_LEFT
        x1 = BOX_LEFT + 4 * BOX_W + 3 * BOX_GAP - 1
        label_top = BOX_BOTTOM - BOX_BORDER - (LABEL_H + 4 if sub else 0)
        draw.rectangle([x0 + SHADOW, 48 + SHADOW, x1 + SHADOW, BOX_BOTTOM + SHADOW],
                       fill=self.colors["schaduw"])
        draw.rectangle([x0, 48, x1, BOX_BOTTOM], fill=self.colors["rand"])
        draw.rectangle([x0 + BOX_BORDER, 48 + BOX_BORDER, x1 - BOX_BORDER, label_top - 1],
                       fill=self.colors["vak"])
        if sub:
            draw.rectangle([x0 + BOX_BORDER, label_top, x1 - BOX_BORDER, BOX_BOTTOM - BOX_BORDER],
                           fill=self.colors["labelbalk"])
            self._text(img, (WIDTH / 2, label_top + (LABEL_H + 4) / 2), sub,
                       20, self.colors["labeltekst"], x1 - x0 - 20)
        self._text(img, (WIDTH / 2, (48 + BOX_BORDER + label_top) / 2), message,
                   46, self.colors["cijfers"], x1 - x0 - 24)
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
