# Caching en beperkingen

## De kern

De GIF op GitHub Pages is een **vast bestand** dat ongeveer elke 5 minuten wordt vervangen.
Hij wordt **niet** per e-mailopening gemaakt. Wat de ontvanger ziet, hangt af van drie dingen:

1. **Wanneer GitHub de GIF voor het laatst heeft gemaakt.** Normaal is dat elke 5 minuten,
   maar GitHub kan geplande runs vertragen (soms 10 tot 30 minuten) of overslaan bij drukte.
2. **De cache van GitHub Pages.** Pages stuurt `Cache-Control: max-age=600` mee,
   dus browsers en proxy's mogen de GIF tot 10 minuten bewaren.
3. **De cache van de e-mailclient.** Zie hieronder.

De GIF telt 3 minuten af vanaf het moment van genereren en blijft daarna stilstaan.
Opent iemand de mail 12 minuten na het genereren, dan staat de countdown dus 12 minuten achter.
Bij een actie die over enkele dagen afloopt, valt dat nauwelijks op.
In het laatste uur valt het wel op. Het kan zelfs gebeuren dat de GIF nog een paar minuten
aftelt terwijl de actie al voorbij is.

## Per e-mailclient

| Client | Animatie | Actualiteit |
|---|---|---|
| **Gmail** (web en app) | Ja | Gmail haalt afbeeldingen op via een eigen proxy (googleusercontent.com) en cachet ze. Een ontvanger die de mail later opnieuw opent, kan de oude stand zien. |
| **Outlook voor Windows** (klassiek, 2016–2021, 365) | **Nee, alleen het eerste frame** | Wordt bij openen opgehaald. Toont een stilstaand beeld met de stand van het moment van genereren. |
| **Nieuwe Outlook / Outlook.com / Outlook-app** | Ja | Gebruikt ook een proxy, met vergelijkbare caching als Gmail. |
| **Apple Mail (iPhone/Mac)** | Ja | Met *Bescherming van Mail-privacy* laadt Apple de afbeeldingen al bij **aflevering** voor. De countdown toont dan de stand van het verzendmoment, niet die van de opening. |

Afbeeldingen uitgeschakeld? Dan ziet de ontvanger de alt-tekst
"Aftellen tot 1 november". Daarom staat de einddatum ook als tekst in de groene balk.

## Wat we al doen om de stand zo actueel mogelijk te houden

- **`?campagne=…&amp;tid=~tid~` achter de GIF-URL.** Elke ontvanger krijgt een unieke URL,
  dus de proxy van Gmail of Outlook haalt de GIF bij de eerste opening vers op in plaats van
  een kopie van een andere ontvanger te gebruiken. GitHub Pages negeert de parameters.
  Controleer in een testmail of Ternair `~tid~` ook in de afbeeldings-URL invult.
- **`--offset 60`** in de workflow: het aftellen begint ongeveer op het moment dat de GIF online staat.
- **De GIF speelt één keer af en loopt niet in een lus.** Hij springt dus niet terug naar een hogere tijd.
- **Geen tijdstempel in de GIF.** Een vast "bijgewerkt om"-tijdstip zou verouderd ogen.

## Andere beperkingen van GitHub

- Geplande workflows draaien minimaal elke 5 minuten. Vaker kan niet.
- Bij een openbare repository zet GitHub geplande workflows uit na **60 dagen zonder wijzigingen**.
  Je krijgt daar een mail over. Zet de workflow dan weer aan via **Actions**.
- De GIF zelf is ongeveer 210 KB voor 180 frames. Alleen het secondenvak verandert per frame,
  en de generator slaat alleen die wijziging op. Dat is ruim onder de 1 MB die we voor e-mail aanhouden.

## Conclusie

Deze oplossing past goed bij een actie die over **dagen** afloopt, zoals de TV-inruilactie.
Moet de countdown bij iedere opening op de seconde kloppen, bijvoorbeeld bij een flash sale van een paar uur,
gebruik dan het alternatief in [CLOUDFLARE.md](CLOUDFLARE.md).
Ook dat alternatief lost de caching van Gmail en de voorlading van Apple Mail niet volledig op:
dat zijn beperkingen van de e-mailclients.
