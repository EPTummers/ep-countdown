# Installatie in 8 stappen (zonder programmeerkennis)

Alles gebeurt in de webbrowser op github.com. Je hoeft niets te installeren.

## 1. Inloggen

Log in op [github.com](https://github.com) met het account **EPTummers**
(hetzelfde account als voor de webshop).

## 2. Repository aanmaken

1. Klik rechtsboven op **+** en kies **New repository**.
2. Bij **Repository name** vul je bijvoorbeeld `ep-countdown` in.
   Deze naam komt in de GIF-URL, dus kies hem nu definitief.
3. Kies **Public**. Op een gratis GitHub-account werkt Pages alleen met openbare repositories.
   Er staan geen wachtwoorden of klantgegevens in deze code.
4. Vink niets anders aan en klik op **Create repository**.

## 3. Bestanden uploaden

1. Klik op de lege repositorypagina op de link **uploading an existing file**.
2. Open de map `ep-countdown` in Finder.
3. **Belangrijk:** de map `.github` is op een Mac verborgen omdat de naam met een punt begint.
   Druk in Finder op **Cmd + Shift + .** (punt) om verborgen mappen te tonen.
4. Selecteer alle bestanden en mappen in `ep-countdown`, ook `.github`, en sleep ze naar het uploadvak in de browser.
5. Klik onderaan op **Commit changes**.
6. Controleer of de map `.github/workflows` met `countdown.yml` in de repository staat.

   **Niet gelukt?** Klik op **Add file → Create new file**, typ als naam
   `.github/workflows/countdown.yml` (de schuine strepen maken automatisch mappen),
   plak de inhoud van het bestand en klik op **Commit changes**.

## 4. GitHub Pages aanzetten

1. Ga naar **Settings** (tandwiel bovenaan de repository) en dan in het menu links naar **Pages**.
2. Bij **Build and deployment → Source** kies je **GitHub Actions**.

Meer is niet nodig. De workflow regelt de rest.

## 5. De eerste keer handmatig starten

1. Ga naar het tabblad **Actions**. Vraagt GitHub om workflows aan te zetten, klik dan op de groene knop.
2. Klik links op **Countdown bijwerken**, rechts op **Run workflow** en daarna nog een keer op **Run workflow**.
3. Na 1 à 2 minuten verschijnt een groen vinkje. Bij een rood kruis klik je op de run om de foutmelding te lezen.

Daarna draait de workflow vanzelf, ongeveer elke 5 minuten.

## 6. Controleren

Open in je browser (vervang `ep-countdown` als je een andere naam koos):

- Overzicht: `https://eptummers.github.io/ep-countdown/`
- GIF: `https://eptummers.github.io/ep-countdown/tv-inruilactie/countdown.gif`

## 7. In Ternair plaatsen

1. Open `ternair/tv-inruilactie.html`.
2. Vervang `[REPOSITORY]` door de naam van je repository (bijvoorbeeld `ep-countdown`).
3. Controleer de headerafbeelding onder de countdown (Shopify CDN) en vervang de URL als er een specifieke TV-header is.
4. Plak de HTML in Ternair als HTML-blok of snippet.
5. Stuur testmails naar Gmail, Outlook (desktop en app) en een iPhone, en controleer de weergave en de klik.
6. Controleer in de Ternair-preview dat `~tid~` in de link en de afbeeldings-URL wordt ingevuld.

## 8. Na de campagne

- Laat de GIF na de einddatum nog enkele weken staan. Mensen openen oude mails nog en zien dan de eindmelding.
- Daarna: **Actions → Countdown bijwerken → ⋯ (rechtsboven) → Disable workflow**.
  Zet hem weer aan (**Enable workflow**) bij een nieuwe campagne.
- Een campagne uitzetten zonder de rest te stoppen: zet `"actief": false` in het JSON-bestand.
  Let op: daarmee verdwijnt die GIF van de website en zien oude mails een lege afbeelding.

## Dagelijks gebruik

**Einddatum wijzigen:** open `campaigns/tv-inruilactie.json` op GitHub, klik op het potloodje,
pas `einde` aan en klik op **Commit changes**. Binnen enkele minuten staat de nieuwe GIF online.

**Nieuwe campagne:** open een bestaand campagnebestand, kopieer de inhoud en maak via
**Add file → Create new file** een nieuw bestand aan in `campaigns/`, bijvoorbeeld
`campaigns/black-friday-2026.json`. Pas `slug`, `naam`, `einde` en de teksten aan.
De GIF komt dan op `.../black-friday-2026/countdown.gif`.

**Eigen lettertype:** upload een vet `.ttf`-bestand, bijvoorbeeld Montserrat ExtraBold van
fonts.google.com, naar de map `fonts/`. Zonder eigen lettertype gebruikt GitHub DejaVu Sans Bold.
