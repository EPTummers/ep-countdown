# Alternatief: live countdown per opening met Cloudflare Workers

**Status:** voorstel, nog niet gebouwd.

## Wanneer nodig?

Gebruik dit alternatief als de countdown bij elke opening vanaf het actuele moment moet aftellen,
bijvoorbeeld bij flash sales of acties die binnen enkele uren aflopen.

## Hoe het werkt

```
GitHub (broncode)  ──push──▶  Cloudflare Workers Builds / Wrangler-action
                                         │
E-mail opent <img> ──────────▶  Worker op https://<naam>.<account>.workers.dev/tv-inruilactie.gif
                                         │  1. leest einddatum uit de campagneconfig
                                         │  2. berekent de resterende tijd op dit moment
                                         │  3. stelt 60–180 frames samen en levert een GIF
                                         ▼
                                Cache-Control: no-store
```

- **Broncode blijft op GitHub.** De campagne-JSON's krijgen hetzelfde formaat als nu.
- **Uitvoering op Cloudflare.** De Worker koppel je aan de GitHub-repository via Cloudflare Workers Builds,
  zodat elke push automatisch wordt gepubliceerd. Een alternatief is een GitHub Action met `wrangler deploy`.
- **Snel genereren.** Het Python-script maakt vooraf een afbeelding met de achtergrond en een sprite met de cijfers 0–9.
  De Worker plakt alleen cijfers op de achtergrond en codeert de GIF met een kleine JavaScript-bibliotheek,
  bijvoorbeeld `gifenc`. Dat JavaScript draait op de server, niet in de e-mail.
- **Edge-cache per seconde.** Openingen in dezelfde seconde delen één gegenereerde GIF.
  Dat scheelt rekentijd bij een grote verzending.
- **Domein.** Gebruik `*.workers.dev`, of een subdomein van een domein dat via Cloudflare DNS loopt
  (bijvoorbeeld `countdown.eptummers.nl`, als het DNS daar zou staan).

## Aandachtspunten

- **Kosten en limieten.** De gratis Workers-versie heeft een zeer kleine CPU-limiet per verzoek.
  180 frames coderen past daar waarschijnlijk niet in. Reken op het betaalde Workers-plan
  (circa $5 per maand, controleer de actuele prijs) of beperk de GIF tot ongeveer 60 frames.
- **Pieken.** Een verzending naar tienduizenden adressen geeft veel verzoeken in korte tijd.
  De edge-cache per seconde vangt het grootste deel op.
- **Clientbeperkingen blijven bestaan.** De proxy van Gmail kan een GIF bewaren,
  Apple Mail laadt vooraf bij aflevering en Outlook voor Windows toont alleen het eerste frame.
  Wel is de eerste opening altijd actueel.

## Volgende stap

Als je hiervoor kiest, bouw ik de Worker in dezelfde repository (map `worker/`)
met dezelfde vormgeving en dezelfde campagnebestanden.
