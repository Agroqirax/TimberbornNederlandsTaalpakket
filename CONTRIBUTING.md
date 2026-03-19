# Contributing

Bedankt dat je wilt helpen vertalen!

## Bestanden indeling

De bestanden zijn op de volgende manier ingedeeld:

```
Data
└─ Localizations
   ├─ nlNL.csv
   ├─ nlNL_donottranslate.csv
   ├─ nlNL_names.csv
   ├─ nlNL_wip.csv
   └─ Plugins
      └─ nlNL_Mod.ID.csv
```

## Werken met git/github

Fork de repo en werk in je eigen versie.
Als je klaar bent maak een pull request aan.
Ik zal er binnenkort naar kijken en een nieuwe versie naar steam, mod.io en github uploaden.

## Mods vertalen

Download de te vertalen mod (dit kan op [mod.io](https://mod.io/g/timberborn) of op [steam](https://steamcommunity.com/app/1062090/workshop))

> [!TIP]
> De bestanden van de steam workshop worden opgeslagen in `C:\Program Files (x86)\Steam\steamapps\workshop\content\1062090`<br>
> Op MacOS is dit `~/Library/Application Support/Steam/steamapps/workshop/content/1062090`

Kopier `/localizations/enUS.csv` (of `.txt`) (of `/version-x.x/...`) van de mod naar `/Data/Localizations/Plugins/nlNL_MOD.ID.csv`

Vertaal de `Text` kolom van het bestand. Dit kan in elke text editor of in een spreadsheet editor zoals Excel of LibreOffice Calc.

> [!TIP]
> Gebruik tools/translate.py om automatisch te vertalen.<br>
> In vscode gebruik: >Tasks: Run Task<br>
> Installeer wel eerst tools/requirements.txt en check na afloop dat de vertalingen kloppen.

Voeg de mod toe aan de changelog en modlijst

`CHANGELOG.md`

```md
## [x.x.x] - yyyy-mm-dd

### Changed

- Mod ... toegevoegd/verbeterd/...
```

`modlist.csv`

```csv
MOD.ID,Name,https://steamcommunity.com/sharedfiles/filedetails/?id=xxxxxxxxxx,https://mod.io/g/timberborn/m/ModName,x.x.x
```

Commit je veranderingen en push de branch

## Notities voor vertalers

Let op deze dingen tijdens het vertalen

- Termen
  - District -> Wijk
  - Settlement -> Nederzetting
  - Logs -> Hout
  - Hoomans, Hoomanity -> Mensjen, Mensjheit (incorrecte spelling aanhouden)
  - Floodgate, Sluice -> Sluisdeur
  - Badwater -> Slechtwater
  - Save (als znw.) -> Save
  - Haulers -> Transporteurs
  - Contaminated -> Besmet, Verontreinigd
  - Bot -> Robot
  - Timberbot -> Houtbot
  - Ironbot -> IJzerbot
  - Lodge, Barrack -> Hut
  - Science points -> Kennis
  - Tubeway -> Metro
  - Dirt -> Zand
  - Power shaft -> Aandrijfas
- Namen
  - Ma' Ngonel -> Oma Ngonel
  - Pina -> Pina
  - Suli -> Suli
  - Ol' Kazko -> Ouwe Kazko
- Quotes schrijven met een em-dash (U+2014), geen spatie en bijde delen met een hoofdletter (bijv. —Oma Ngonel)
- Houd het hoofdlettergebruik van het origineel aan
- Niet te lange samenstellingen (bijv. Slechtwater bron i.p.v. Slechtwaterbron)
- "FlavorDescriptions" verliezen vaak hun betekenis wanneer vertaald. Gebruik zo nodig een standaard vertaling i.p.v. de grap letterlijk over te nemen.
- Houd een informele toon aan
- Vermijd het gebruik van te ingewikkelde woorden
- Let op het correcte gebruik van de ZWSP (U+200B) & NBSP (U+00A0) (gebruik evt. een editor die onzichtbare tekens toont)
