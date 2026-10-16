# WUNOO v1.404 Candidate

## Změna
- `POST /api/v062/settlement/run` nyní kontroluje existenci moderního i legacy vyúčtování ještě před načtením výsledku z `Idempotency-Key` cache.
- Dříve mohl opakovaný požadavek se starším uloženým výsledkem vrátit HTTP 200 ještě před kontrolou, zda se později neobjevilo konfliktní vyúčtování ve druhém zdroji.
- Pokud existují současně `settlement_runs` a `settlements` pro stejnou objednávku, endpoint nyní odmítne požadavek HTTP 409 `SETTLEMENT_DUPLICATE_SOURCES`, a to i při opakování s již známým idempotency klíčem.
- Při cache replay se také znovu ověřuje integrita existujícího vyúčtování. Pokud cache existuje, ale účetní záznam chybí, endpoint vrátí HTTP 409 `SETTLEMENT_IDEMPOTENCY_WITHOUT_LEDGER`.
- Kontrola konfliktu probíhá před cache lookupem; při detekovaném konfliktu nevznikají žádné další zápisy.

## Ověření
- `TEST_V404.py` — PASS: přednastavená idempotency cache nemůže obejít konflikt obou zdrojů; HTTP 409; cache se nekonzultuje; po detekci konfliktu žádné zápisy.
- `TEST_V403.py` — PASS: legacy repository odmítne současné záznamy v obou tabulkách.
- `TEST_V402.py` — PASS: kontrola jediného zdroje vyúčtování.
- `TEST_V401.py` — PASS: integrita opakovaného vyúčtování; 11 poškozených případů odmítnuto.
- `TEST_V400.py` — PASS: výpočet a minimální částka vyúčtování.
- `TEST_V399.py` — PASS: integrita opakovaných výplat.
- `TEST_V398.py`, `TEST_V397.py`, `TEST_V396.py` — PASS: integrita účetních zápisů refundací.
- `python -m compileall -q app` — PASS.
- Při širším kombinovaném spuštění regresí došlo k vypršení časového limitu během `TEST_V392.py`; tento běh proto není označen jako kompletní. Výše uvedené jednotlivé testy dokončily běh úspěšně.
- Finální ZIP byl vytvořen z kandidátního zdrojového stromu a ověřen pomocí `unzip -t`.

## Omezení
- Testy používají lokální prostředí/SQLite nebo testovací náhrady; nedokazují souběh v produkčním PostgreSQL ani chování živého poskytovatele plateb.
- Kandidát nebyl nasazen a změny nebyly odeslány na GitHub.
