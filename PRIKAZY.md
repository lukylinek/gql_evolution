# Příkazy

Používáme PowerShell v otevřené složce projektu. Příkazy navíc spouštíme podle potřeby.

## 1. Spuštění

Zapneme Docker Desktop. Kontejner `postgres_gql` je databáze, `pgadmin` je její webové rozhraní.

```powershell
docker start uois-postgres_gql-1 uois-pgadmin-1
.\.venv\Scripts\Activate.ps1
```

## 2. Kontrola tabulek

```powershell
python -m src.DBDefinitions.main JournalType list
python -m src.DBDefinitions.main Journal list
```

`[]` znamená prázdnou tabulku.

## 3. Backend a načtení systemdata.json

Všechna ukázková data máme v `systemdata.json`: `journaltypes` obsahuje typy i podtypy, `journals` obsahuje časopisy.

```powershell
$env:DEMODATA = "True"
python -m uvicorn main:app --reload
```

Existující záznamy se stejným ID se přeskočí, nepřepíšou se. Další příkazy zadáváme v druhém terminálu s aktivním `.venv`.

- Backend: http://localhost:8000/gql (zatím učitelův vzor, naše GraphQL operace ještě chybí).
- pgAdmin: http://localhost:31122
- Tabulky: **Servers → db → Databases → data → Schemas → public → Tables**.
- Data tabulky: pravé tlačítko → **View/Edit Data → All Rows**.

## 4. Ukončení

Backend zastavíme přes **Ctrl+C**, potom:

```powershell
deactivate
docker stop uois-pgadmin-1 uois-postgres_gql-1
```

## Příkazy navíc

### První stažení projektu

Spustíme ve složce, kam chceme projekt stáhnout. Pokud ho už máme, tento krok přeskočíme.

```powershell
git clone --branch 2026 https://github.com/lukylinek/gql_evolution.git
cd gql_evolution
```

### První příprava Pythonu

Každý si vytvoříme vlastní `.venv`. Používáme Python 3.12.

```powershell
python --version
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m pip check
```

### Stav kontejnerů a nápověda

```powershell
docker ps -a
python -m src.DBDefinitions.main --help
```

### Testy databáze

PostgreSQL musí běžet. Testovací knihovny instalujeme jednou:

```powershell
python -m pip install pytest pytest-cov pytest-asyncio
```

```powershell
python -m pytest tests/db/test_publications.py -q -o addopts=
```

Pokrytí našich modelů a importu dat:

```powershell
$env:COVERAGE_FILE = ".coverage.publications"
python -m pytest tests/db/test_publications.py -q -o addopts= --cov=src.DBDefinitions.Domain_Publications --cov=src.DBDefinitions.seed --cov-report=term-missing --cov-report=html:htmlcov-publications
```

Report: `htmlcov-publications/index.html`.

### Git

Kontrola změn:

```powershell
git status
git diff
git log -5 --oneline
```

Uložení práce (zkontrolujeme přidávané soubory a upravíme zprávu):

```powershell
git add -u
git add tests/db/test_publications.py README_UCITEL.md
git diff --cached
git commit -m "Doplneni databazove casti casopisu"
git push origin 2026
```

Stažení změn od spolužáka po uložení vlastní práce:

```powershell
git pull --ff-only origin 2026
```
