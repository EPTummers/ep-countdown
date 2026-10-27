# EP countdown voor e-mail

Animated countdown-GIF's voor de Ternair-nieuwsbrieven van EP:Tummers.
De broncode staat op GitHub, GitHub Actions maakt de GIF en GitHub Pages publiceert hem.
Er is geen PHP en geen eigen server nodig.

## Zo werkt het

1. Elke 5 minuten start GitHub Actions het script `scripts/generate_countdown.py`.
2. Het script leest alle campagnes in `campaigns/` en maakt per campagne een GIF:
   610 × 164 px, maximaal 180 frames van 1 seconde (3 minuten aftellen),
   met vier vakken: DAGEN | UREN | MINUTEN | SECONDEN.
3. Na de einddatum toont de GIF de eindmelding.
4. De GIF's worden gepubliceerd op GitHub Pages:
   `https://eptummers.github.io/<repository>/<slug>/countdown.gif`

De GIF speelt één keer af en blijft dan op het laatste frame staan.
Outlook voor Windows (desktop) toont alleen het eerste frame. Dat is een geldige stand van de countdown.

> **Let op:** GitHub Pages is statische hosting. De GIF wordt niet bij iedere opening
> opnieuw gemaakt, en e-mailclients kunnen hem cachen. Lees [docs/CACHING.md](docs/CACHING.md).

## Repositorystructuur

```
ep-countdown/
├── .github/
│   └── workflows/
│       └── countdown.yml          GitHub Actions: genereren + publiceren op Pages
├── campaigns/
│   └── tv-inruilactie.json        één bestand per campagne (einddatum, teksten, kleuren)
├── docs/
│   ├── INSTALLATIE.md             stappenplan zonder programmeerkennis
│   ├── CACHING.md                 caching en beperkingen in Gmail/Outlook/Apple Mail
│   └── CLOUDFLARE.md              alternatief: echt live per opening via Cloudflare Workers
├── fonts/
│   └── LEESMIJ.txt                optioneel eigen lettertype (bijv. Montserrat)
├── scripts/
│   └── generate_countdown.py      de GIF-generator (Python + Pillow)
├── ternair/
│   └── tv-inruilactie.html        HTML-snippet voor Ternair (Outlook-geschikt)
├── .gitignore
├── requirements.txt
└── README.md
```

De map `_site/` wordt tijdens het draaien aangemaakt en staat niet in de repository.

## Campagne-instellingen

Voorbeeld `campaigns/tv-inruilactie.json`:

| Veld | Betekenis |
|---|---|
| `actief` | `true` = GIF maken, `false` = overslaan (GIF verdwijnt dan van Pages) |
| `naam` | Naam voor het overzicht |
| `slug` | Mapnaam in de URL: alleen kleine letters, cijfers en streepjes |
| `einde` | Einddatum en -tijd als `JJJJ-MM-DD UU:MM:SS` |
| `tijdzone` | Altijd `Europe/Amsterdam` (zomer- en wintertijd gaan automatisch) |
| `kop` | Grote titel bovenaan de GIF |
| `subkop` | Regel onder de titel, bijv. `NOG T/M 1 NOVEMBER  •  OP=OP` |
| `labels` | Teksten in de oranje balken, bijv. `["DAGEN", "UREN", "MIN", "SEC"]` |
| `eindmelding` | Tekst in het witte vak na afloop |
| `eindmelding_sub` | Tekst in de oranje balk na afloop (mag `""` zijn) |
| `kleuren` | Hex-kleuren: `achtergrond`, `rand`, `vak`, `cijfers`, `labelbalk`, `labeltekst`, `schaduw`, `kop` |

De vormgeving volgt de eerdere EP-countdown: geel vlak (`#FFF200`), groene rand (`#2CA843`),
witte vakken met schaduw, donkergrijze cursieve cijfers en oranje labelbalken (`#F37300`).
Teksten en cijfers worden smal en cursief getekend, zodat het met elk vet lettertype lijkt op het origineel.

**Nieuwe campagne:** kopieer een JSON-bestand, geef het een nieuwe naam en een nieuwe `slug`,
pas `einde` en de teksten aan en sla op. De workflow draait dan automatisch.
Maak een nieuwe Ternair-snippet door `ternair/tv-inruilactie.html` te kopiëren en
de slug, link en teksten aan te passen.

## Lokaal testen (optioneel)

```bash
pip install -r requirements.txt
python scripts/generate_countdown.py --now "2026-11-01 23:58:30"
```

Het resultaat staat in `_site/`. Met `--now` simuleer je een tijdstip, bijvoorbeeld om de eindmelding te testen.
