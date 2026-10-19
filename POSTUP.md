# Deník projektu – Journals

## 12. 10. 2026

Dnes jsme začali s databázovou částí projektu. Používáme fork `gql_evolution`, větev `2026`, podle doporučení učitele.

Nejdřív jsme připravili Python prostředí a nainstalovali knihovny. V Dockeru běží PostgreSQL a podařilo se nám ověřit připojení z projektu.

V `src/DBDefinitions/Domain_Publications` máme dva modely:

- `JournalTypeModel` – typ časopisu, například vědecký.
- `JournalModel` – konkrétní časopis, jeho název, vydavatel, ISSN a další údaje ze zadání.

Oba vycházejí z učitelova `BaseDBModel`, takže už mají například ID a datum vytvoření. Časopis odkazuje na svůj typ přes `journal_type_id`. U typů je připravená i vazba na nadřazený typ.

Modely jsou zapojené přes `__init__.py`. Učitelovým databázovým nástrojem se vytvořily tabulky a vložila se ukázková data. Načtení časopisu i jeho typu funguje. Data jsou vidět také v pgAdminu.

Při úpravách se nám dostal kód modelu do špatného `__init__.py`, takže nešlo načíst připojení k databázi. Po vrácení původního obsahu a doplnění importů už příkaz fungoval.

Zkusili jsme spustit i celý backend. Stránka GraphQL se otevřela, ale objevila se chyba spojení se službou UG. Přihlašování ještě není nastavené. Hlavní `main.py` jsme neměnili.

## Co ještě zbývá na 23. 10.

Na první projektový den je podle zadání databázová vrstva. Ještě chceme:

- vyzkoušet úpravu a smazání záznamů,
- uložit a načíst typ s podtypem,
- doplnit testy a ověřit chybné odkazy,
- připravit demodata do `systemdata.json` se stálými ID,
- doplnit README a nahrát změny na GitHub.

Zatím je ověřené vložení a čtení dat, automatické testy pro naše modely ještě nejsou. Na projektový den má být commit na GitHubu nejvýš týden starý.

Použité příkazy máme zvlášť v [PRIKAZY.md](PRIKAZY.md).
