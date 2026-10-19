# Spuštění projektu a příkazy

Postup pro naši současnou databázovou část projektu. Pracujeme ve VS Code a používáme PowerShell.

## 1. Zapneme Docker Desktop

Počkáme, až Docker naběhne. V části **Containers** rozbalíme skupinu **uois**.

| Kontejner | Co dělá | Kdy ho potřebujeme |
| --- | --- | --- |
| `uois-postgres_gql-1` | Databáze projektu na portu 5432. | Pro backend a databázové příkazy. |
| `uois-pgadmin-1` | Webové rozhraní pro prohlížení databáze. | Když chceme používat pgAdmin. |

U těchto kontejnerů klikneme na **Start ▶**. Pokud už běží, necháme je běžet. Počkáme na stav Running, případně Healthy.

Používáme skupinu `uois`. Starou skupinu `uois-latest` nespouštíme.

Pro současnou práci s databází další kontejnery nepotřebujeme. Pokud už běží Valkey, můžeme ho nechat běžet. Úplné přihlášení a zapojení do UOIS ještě nemáme nastavené; tento postup spouští náš místní backend a databázi.

## 2. Otevřeme projekt ve VS Code

Otevřeme složku:

```text
C:\Users\User\Desktop\gql_evolution
```

Přes **Terminal → New Terminal** otevřeme PowerShell a zadáme:

```powershell
cd C:\Users\User\Desktop\gql_evolution
.\.venv\Scripts\Activate.ps1
```

Na začátku řádku se objeví `(.venv)`. Tím používáme knihovny našeho projektu.

Prostředí už máme vytvořené a knihovny nainstalované. Při běžném spuštění je znovu neinstalujeme.

## 3. Zkontrolujeme databázi

```powershell
python -m src.DBDefinitions.main JournalType list
python -m src.DBDefinitions.main Journal list
```

Příkazy vypíšou uložené typy a časopisy. `[]` znamená prázdnou tabulku. Hláška `BaseDBModel.metadata.create_all finished` je v pořádku: nástroj zkontroloval tabulky a vytvořil ty chybějící.

Pokud spojení selže, nejdřív zkontrolujeme, že běží `uois-postgres_gql-1` a má port `5432:5432`.

## 4. Otevřeme pgAdmin

V prohlížeči otevřeme **http://localhost:31122** a přihlásíme se naším uloženým účtem.

Vlevo rozbalíme:

```text
Servers → db → Databases → data → Schemas → public → Tables
```

Najdeme `journals` nebo `journaltypes`, klikneme pravým tlačítkem a vybereme **View/Edit Data → All Rows**.

Pokud tabulky nevidíme, klikneme pravým na **Tables → Refresh**. V pgAdminu vidíme stejná data jako ve výpisu z terminálu.

## 5. Spustíme backend

V terminálu s aktivním `(.venv)` zadáme:

```powershell
python -m uvicorn main:app --reload
```

Počkáme na `Application startup complete.` a otevřeme **http://localhost:8000/gql**.

Terminál necháme běžet. `--reload` znovu načte aplikaci při změně kódu.

Pro další příkazy otevřeme druhý terminál a znovu v něm aktivujeme `.venv`. Pokud jen zkoušíme databázové příkazy nebo prohlížíme tabulky, server Uvicorn běžet nemusí.

### Co zatím není hotové

Stránka GraphQL obsahuje učitelův vzor. Vlastní GraphQL operace pro časopisy ještě nemáme.

Může se objevit `error with ug endpoint`. To znamená problém při získávání uživatele přes službu UG. Spuštění databáze a backendu jsme ověřili, ale přihlašování ještě musíme zprovoznit. Samotná hláška `200 OK` u GraphQL požadavku nezaručuje, že všechny jeho operace proběhly bez chyb.

## 6. Když skončíme

1. Uložíme soubory ve VS Code.
2. V terminálu, kde běží backend, stiskneme **Ctrl+C**.
3. Počkáme na vypnutí serveru a návrat příkazového řádku.
4. Prostředí můžeme vypnout příkazem:

```powershell
deactivate
```

5. V Docker Desktop zastavíme přes **Stop ■** `uois-pgadmin-1` a `uois-postgres_gql-1`, pokud je už nepotřebujeme.
6. Můžeme zavřít VS Code a ukončit Docker Desktop.

Používáme **Stop**, čímž se kontejnery vypnou a uložená databázová data zůstanou zachovaná.

---

## Další příkazy – tahák

Tato část je pro jednotlivé úkony. Nespouštíme všechny příkazy postupně. První příprava a vložení ukázkových dat už proběhly. Úpravy, mazání a automatické testy nás ještě čekají.

### První příprava na novém počítači

Stažení forku s větví `2026`:

```powershell
git clone --branch 2026 https://github.com/lukylinek/gql_evolution.git C:\Users\User\Desktop\gql_evolution
cd C:\Users\User\Desktop\gql_evolution
```

Cestu si každý upravíme podle svého počítače. Pokud už složku s projektem máme, znovu ho neklonujeme.

Python a knihovny:

```powershell
python --version
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m pip check
```

### Docker z terminálu

Přehled všech kontejnerů a jejich stavu:

```powershell
docker ps -a
```

Spuštění našich dvou kontejnerů místo klikání v Docker Desktop:

```powershell
docker start uois-postgres_gql-1 uois-pgadmin-1
```

Zastavení po skončení práce:

```powershell
docker stop uois-pgadmin-1 uois-postgres_gql-1
```

### Kontrola připojení bez změny tabulek

```powershell
python -c "import asyncio; from src.DBDefinitions import ComposeConnectionString, startEngine; asyncio.run(startEngine(ComposeConnectionString(), makeDrop=False, makeUp=False)); print('Pripojenie k databaze funguje.')"
```

### Nápověda učitelova databázového nástroje

```powershell
python -m src.DBDefinitions.main --help
```

### Vypsání dat

```powershell
python -m src.DBDefinitions.main JournalType list
python -m src.DBDefinitions.main Journal list
```

### Vložení dat ze souborů

```powershell
python -m src.DBDefinitions.main JournalType create "@demodata/journaltype.json"
python -m src.DBDefinitions.main Journal create "@demodata/journal.json"
```

`create` vloží nový záznam a `@` označuje vstupní soubor. Tyto příkazy už jsme použili. Opakováním vzniknou další záznamy.

V `journal.json` je zatím ID typu z naší databáze: `aa6b09ba-4baa-44b6-a99e-fe7e83195ff7`. V nové databázi dostane nově vytvořený typ jiné ID. Musíme proto upravit `journal_type_id` podle výsledku prvního příkazu. Stálá ID do demodat ještě doplníme.

### Načtení, úprava a smazání jednoho záznamu

Následující příkazy jsou vzory pro další práci. Soubory `vyber.json` a `uprava.json` zatím neexistují; před použitím je vytvoříme v `demodata`.

Do `vyber.json` dáme ID vybraného záznamu:

```json
{
    "id": "SEM_VLOZIME_SKUTECNE_ID"
}
```

Pro úpravu připravíme `uprava.json` s ID a měněnými údaji:

```json
{
    "id": "SEM_VLOZIME_SKUTECNE_ID",
    "name": "Upravený název časopisu"
}
```

Načtení jednoho časopisu:

```powershell
python -m src.DBDefinitions.main Journal get "@demodata/vyber.json"
```

Úprava časopisu:

```powershell
python -m src.DBDefinitions.main Journal update "@demodata/uprava.json"
```

Smazání vybraného zkušebního časopisu:

```powershell
python -m src.DBDefinitions.main Journal delete "@demodata/vyber.json"
```

Stejné operace pro typ časopisu:

```powershell
python -m src.DBDefinitions.main JournalType get "@demodata/vyber.json"
python -m src.DBDefinitions.main JournalType update "@demodata/uprava.json"
python -m src.DBDefinitions.main JournalType delete "@demodata/vyber.json"
```

Před použitím pro typ změníme ID v souborech na ID typu. `delete` záznam opravdu smaže; pro zkoušení použijeme dočasná data. U typu používaného časopisem nebo podtypem je potřeba vyřešit také tyto vazby.

### Načtení časopisu včetně jeho typu

Pro tento výpis si připravíme `demodata/journal-s-typem.json`:

```json
{
    "include": ["type"]
}
```

Potom použijeme:

```powershell
python -m src.DBDefinitions.main Journal list "@demodata/journal-s-typem.json"
```

Tento pomocný soubor zatím také není vytvořený.

### Testy – další krok

Nejdřív nainstalujeme testovací knihovny:

```powershell
python -m pip install -r requirements-dev.txt
```

Databázové testy:

```powershell
python -m pytest tests/db
```

Celá sada testů:

```powershell
python -m pytest
```

Před spuštěním databázových testů připravíme testovací databázi a její konfiguraci. Některé učitelovy testy pracují s databází určenou připojením projektu. Vlastní testy pro časopisy ještě musíme doplnit; tyto příkazy nejsou záznamem úspěšně provedených testů.

Podle současného `pytest.ini` se při testování měří coverage a ukládá HTML přehled do `htmlcov/index.html`.

### Git a uložení práce na GitHub

Kontrola větve, změn a posledních commitů:

```powershell
git branch --show-current
git status
git diff
git log -5 --oneline
```

Připravení našich souborů do commitu:

```powershell
git add src/DBDefinitions/Domain_Publications src/DBDefinitions/__init__.py demodata POSTUP.md PRIKAZY.md
```

Až upravíme také testy, README nebo společná data, přidáme je podle potřeby:

```powershell
git add tests README.md systemdata.json
```

Kontrola toho, co bude v commitu:

```powershell
git diff --cached
```

Vytvoření commitu a odeslání na naši větev `2026`:

```powershell
git commit -m "Pridani databazovych modelu pro casopisy"
git push origin 2026
```

Text commitu upravíme podle skutečných změn. Na projektový den 23. 10. má být na GitHubu commit nejvýš týden starý.
