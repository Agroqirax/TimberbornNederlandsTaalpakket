# Contributing

Bedankt dat je wilt helpen vertalen!

## Bestanden indeling

De bestanden zijn op de volgende manier ingedeeld:

```
Data
└─ Localizations
   ├─ nlNL.csv                (spel vertalingen)
   ├─ nlNL_donottranslate.csv (taal naam)
   ├─ nlNL_names.csv          (namenlijst)
   ├─ nlNL_wip.csv            (vertalingen van de exp branch)
   ├─ nlNL_old.csv            (verwijderde vertalingen die tijdelijk in de release blijven)
   └─ Plugins
      └─ nlNL_Mod.ID.csv      (mod vertaling met mod id als suffix)
```

## Werken met git/github

Fork de repo en werk in je eigen versie.
Als je klaar bent maak een pull request aan.
Ik zal er binnenkort naar kijken en een nieuwe versie naar steam, mod.io en github uploaden.

## Mods vertalen

Download de te vertalen mod (dit kan op [mod.io](https://mod.io/g/timberborn) of op [steam](https://steamcommunity.com/app/1062090/workshop))

> [!TIP]
> De bestanden van de steam workshop worden opgeslagen in `C:\Program Files (x86)\Steam\steamapps\workshop\content\1062090`<br>
> Op MacOS is dit `~/Library/Application Support/Steam/steamapps/workshop/content/1062090`<br>
> Op Linux is dit `~/.steam/steam/steamapps/workshop/content/1062090/`

Kopier `/localizations/enUS.csv` (of `.txt`) (of `/version-x.x/...`) van de mod naar `/Data/Localizations/Plugins/nlNL_MOD.ID.csv`

Vertaal de `Text` kolom van het bestand. Dit kan in elke text editor of in een spreadsheet editor zoals Excel of LibreOffice Calc.

> [!TIP]
> Gebruik `tools/translate.py` om automatisch te vertalen.<br>
> In vscode gebruik: `> Tasks: Run Task`<br>
> Installeer wel eerst `tools/requirements.txt` en check na afloop dat de vertalingen kloppen.

Voeg de mod toe aan de changelog en modlijst

`./CHANGELOG.md`

```md
## [x.x.x] - yyyy-mm-dd

### Changed

- Mod ... toegevoegd/verbeterd/...
```

`./modlist.csv`

```csv
Naam,Mod.Id,https://steamcommunity.com/sharedfiles/filedetails/?id=xxxxxxxxxx,https://mod.io/g/timberborn/m/xxx,x.x.x
```

Commit je veranderingen en push de branch

## Notities voor vertalers

Let op deze dingen tijdens het vertalen

- Quotes schrijven met een em-dash (U+2014), geen spatie en bijde delen met een hoofdletter (bijv. —Oma Ngonel)
- Houd het hoofdlettergebruik van het origineel aan
- "FlavorDescriptions" verliezen vaak hun betekenis wanneer vertaald. Gebruik zo nodig een standaard vertaling i.p.v. de grap letterlijk over te nemen.
- Houd een informele toon aan en maak het taalgebruik niet onnodig ingewikkeld
- Let op het correcte gebruik van de ZWSP (U+200B) & NBSP (U+00A0) (gebruik evt. een editor die onzichtbare tekens toont)
- Tip: check voor ongelidge tags:
  ```re
  <color=(?!(?:#(?:[0-9a-f]{6})|(?:red|green|blue|yellow|black|white|purple|orange|brown|gray|grey|pink|violet|turquoise|cyan|magenta|navy|maroon|lime|teal|silver|gold|beige)))([^>]+)>
  ```
