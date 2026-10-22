# Deník projektu – Journals

Ve dvojici děláme evidenci časopisů a jejich typů. Používáme učitelův projekt `gql_evolution`, větev `2026`.

Příkazy ke spuštění a práci s databází máme v [PRIKAZY.md](PRIKAZY.md). Původní poznámky učitele jsou v [README_UCITEL.md](README_UCITEL.md).

## 12. 10. 2026 – Začátek a databáze

Připravili jsme Python prostředí, nainstalovali knihovny a spustili PostgreSQL v Dockeru. Ověřili jsme, že se k databázi připojíme. Přes pgAdmin můžeme prohlížet tabulky a data.

Podle učitelova vzoru jsme vytvořili dva modely:

- `JournalModel` – časopis, jeho název, vydavatel, ISSN a další údaje ze zadání.
- `JournalTypeModel` – typ časopisu. Může mít i podtypy, jak požaduje zadání.

Oba používají učitelův `BaseDBModel`. Časopis je propojený se svým typem přes `journal_type_id`.

Nejdřív nám nefungoval import `ComposeConnectionString`, protože jsme špatně upravili `__init__.py`. Vrátili jsme potřebný původní kód a doplnili importy našich modelů. Potom už šly tabulky vytvořit a vypsat přes učitelův databázový `main.py`.

Vložili jsme první ukázkový typ a časopis pomocí příkazu `create`. Zkusili jsme také spustit backend. GraphQL stránka se otevřela, ale připojení ke službě UG zatím nefunguje.

## 19. 10. 2026 – Data a testování

Do `systemdata.json` jsme doplnili pět typů včetně jednoho podtypu a jeden ukázkový časopis. Názvy `scientific`, `professional`, `reviewed` a `conference_series` jsou příklady ze zadání. Podtyp, fiktivní časopis a jejich další údaje jsme doplnili pro testování.

Při načítání dat vznikala chyba databázové transakce. V učitelově `seed.py` jsme upravili použití databázových sessions a pořadí importu tabulek. Potom se data načetla. Při dalším spuštění se záznamy se stejným ID přeskočí.

Doplnili jsme 20 testů. Zkouší vytváření, čtení, úpravy, mazání a vazby mezi záznamy. Našli jsme také problém, kdy se při mazání nadřazeného typu jeho podtyp odpojil. Upravili jsme vazbu tak, aby smazání používaného typu databáze odmítla.

Všech 20 testů prošlo. Pokrytí našich modelů a `seed.py` bylo 97 %. Není to pokrytí celého projektu. Testy mají vlastní dočasná schémata, takže nemění naše běžná data.

Na GitHub jsme odeslali commit `22f7f69` se základními modely, demodaty a návody. Pozdější doplnění testů, společných dat a oprav importu zatím není odeslané.

## 22. 10. 2026 – Kontrola před projektovým dnem

Znovu jsme vyzkoušeli výpis obou tabulek přes databázový `main.py`. Nejdřív se nešlo připojit, protože byl vypnutý PostgreSQL kontejner. Po jeho zapnutí se vypsalo pět typů a jeden časopis.

Prošli jsme si, jak fungují podtypy a načítání `systemdata.json`. Samotná změna JSON souboru databázi nezmění. Nová data načteme při spuštění backendu s `DEMODATA=True`; existující záznamy tím nepřepisujeme.

Zjednodušili jsme přehled příkazů a tento deník. Hlavní ani databázový `main.py` jsme neměnili.

Ukázková data jsme sjednotili do `systemdata.json` a odstranili jejich samostatné kopie. V `journaltypes` jsou nejdřív hlavní typy a potom podtyp. Hlavní typ má `parent_id: null`, podtyp má v `parent_id` ID svého rodiče. `_chunk` určuje pořadí importu: 0 pro hlavní typy a 1 pro podtyp. V `journals` je časopis s odkazem `journal_type_id` na jeho typ.

Odstranili jsme nepotřebné pomocné soubory a příklady z návodu. Deník máme jen tady v README. Test porovnávající původní kopie dat už nepotřebujeme; testy načítání ze `systemdata.json` zůstaly.

Po této úpravě prošlo všech 19 zbývajících databázových testů, včetně opakovaného importu bez duplicit.

## Co ještě potřebujeme udělat

Před projektovým dnem 23. 10. musíme uložit a odeslat poslední změny na GitHub a projít si ukázku ve dvojici.

Potom budeme doplňovat loadery, služby a vlastní GraphQL operace. Budeme dodržovat pořadí `GraphQL → Service → Loader → DBModel`. Ještě potřebujeme vyřešit kontroly vstupních údajů, přihlášení, oprávnění a propojení s publikacemi. Další požadavky ze zadání, například chybové kódy, HTML stránky, testy celé aplikace a zveřejnění Docker image, nám také zbývají.
