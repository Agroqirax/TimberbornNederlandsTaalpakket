# Contributing

Bedankt dat je wilt helpen vertalen!

Volg het volgende stappen om een nieuwe mod toe te voegen.

> [!WARNING]
> Als je niet weet hoe git werkt is dit niet te doen.<br>
> Maak dan gewoon een [issue](https://github.com/agroqirax/TimberbornNederlandsTaalpakket/issues/new?template=new-translations.yml) aan zodat wij de mod kunnen toevoegen.

## Een mod toevoegen

- Clone de repo

  ```sh
  git clone https://github.com/agroqirax/TimberbornNederlandsTaalpakket.git
  ```

  en maak een nieuwe branch aan

  ```sh
  git checkout -b MOD_NAAM
  ```

- Download de te vertalen mod (dit kan op [mod.io](https://mod.io/g/timberborn) of op [steam](https://steamcommunity.com/app/1062090/workshop/))

  > [!TIP]
  > De bestanden van de steam workshop worden opgeslagen in `C:\Program Files (x86)\Steam\steamapps\workshop\content\1062090`

- Kopieer het csv bestand van `/Localizations/enUS.csv` naar [`/Data/Localizations/Plugins/MOD.ID/nlNL_MODID.csv`](/Data/Localizations/Plugins)

- Vertaal kolom `B` (`Text`) van het bestand. Dit kan in elke text editor of in een spreadsheet editor zoals Excel of LibreOfficeCalc.

  > [!TIP]
  > Gebruik [tools/translate.py](tools/translate.py) om automatisch te vertalen.<br>
  > Installeer [requirements.txt](tools/requirements.txt) en check dat de vertalingen kloppen.

- Voeg de mod toe aan alle vereiste documenten:

  - [CHANGELOG.md](CHANGELOG.md)

  ```md
  #### Mods

  - [MOD.ID](Data/Localizations/Plugins/MOD.ID)
  ```

  - [manifest.json](manifest.json) (`OptionalMods`)

  ```json
  {
    "Id": "MOD_ID"
  }
  ```

  - [README.md](README.md) (`Ondersteunde mods`)

  ```md
  - [MOD.ID](https://steamcommunity.com/sharedfiles/filedetails/?id=STEAMID) (vX.X.X.X)
  ```

- Commit je veranderingen
  ```sh
  git commit -m "Vertalingen voor mod MOD_NAAM toegevoegd"
  ```
  push de branch
  ```sh
  git push -u origin <branch>
  ```
  en maak een [pull request](https://github.com/agroqirax/TimberbornNederlandsTaalpakket/compares) aan.
  Ik zal er binnenkort naar kijken en een nieuwe versie naar steam, mod.io en github uploaden.

## Adding a mod (English)

- Clone the repo

  ```sh
  git clone https://github.com/agroqirax/TimberbornNederlandsTaalpakket.git
  ```

  create a new branch

  ```sh
  git checkout -b MOD_NAME
  ```

- Download the mod to translate (you can do this on [mod.io](https://mod.io/g/timberborn) or on [steam](https://steamcommunity.com/app/1062090/workshop/))

  > [!TIP]
  > The steam worksop items are stored at `C:\Program Files (x86)\Steam\steamapps\workshop\content\1062090`

- Copy the csv language file `/Localizations/enUS.csv` to [`/Data/Localizations/Plugins/MOD.ID/nlNL_MODID.csv`](/Data/Localizations/Plugins)

- Translate column `B` (`Text`) of the csv file. This can be done in any text editor or in spreadsheet editors like Excel or LibreOfficeCalc.

  > [!TIP]
  > Use [tools/translate.py](tools/translate.py) to translate automatically.<br>
  > Install [requirements.txt](tools/requirements.txt) and verify that the translations are correct.

- Add references to all files:

  - [CHANGELOG.md](CHANGELOG.md)

  ```md
  #### Mods

  - [MOD.ID](Data/Localizations/Plugins/MOD.ID)
  ```

  - [manifest.json](manifest.json) (`OptionalMods`)

  ```json
  {
    "Id": "MOD_ID"
  }
  ```

  - [README.md](README.md) (`Ondersteunde mods`)

  ```md
  - [MOD.ID](https://steamcommunity.com/sharedfiles/filedetails/?id=STEAMID) (vX.X.X.X)
  ```

- Commit your changes
  ```sh
  git commit -m "Added translations for mod MOD.NAME"
  ```
  push the branch
  ```sh
  git push -u origin <branch>
  ```
  and create a [pull request](https://github.com/agroqirax/TimberbornNederlandsTaalpakket/compares).
  I'll look it it shortly and upload a new build to steam, mod.io and github.
