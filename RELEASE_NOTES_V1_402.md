# WUNOO v1.402 Candidate

## Změna
- `POST /api/v062/settlement/run` nyní načítá moderní `settlement_runs` i legacy `settlements` před vyhodnocením opakovaného požadavku.
- Pokud pro stejnou objednávku existuje záznam v obou tabulkách, endpoint skončí HTTP 409 `SETTLEMENT_DUPLICATE_SOURCES` a nevydá idempotentní potvrzení pouze na základě jedné tabulky.
- Důvod: každá tabulka má vlastní unikátní omezení `order_id`, ale tato omezení sama o sobě nezabraňují tomu, aby pro stejnou objednávku vznikl záznam v obou tabulkách. Konflikt vyžaduje účetní odsouhlasení, ne automatické rozhodnutí API.
- Při existenci právě jednoho zdroje zůstává zachována dosavadní validace v1.401. Vytvoření nového vyúčtování zůstává beze změny.

## Ověření
- `TEST_V402.py`: žádný zdroj / pouze moderní / pouze legacy záznam přijímán; souběžná existence obou zdrojů odmítnuta HTTP 409; kontrola zapojení guardu v route — PASS.
- `TEST_V401.py` — PASS (11 poškozených scénářů odmítnuto).
- `TEST_V400.py`, `TEST_V399.py`, `TEST_V398.py`, `TEST_V395.py`, `TEST_V394.py`, `TEST_V393.py`, `TEST_V392.py`, `TEST_V391.py`, `TEST_V390.py`, `TEST_V389.py`, `TEST_V381.py`, `TEST_V382.py`, `TEST_V362.py` — PASS.
- `python -m compileall -q app` — PASS.
- Finální ZIP zkontrolován pomocí `unzip -t` po sestavení.

## Omezení
- Testy byly spuštěny v lokálním prostředí, primárně SQLite. Tento běh neověřuje reálný PostgreSQL souběh, živého poskytovatele plateb ani produkční nasazení.
- Změny nebyly odeslány do GitHubu a nebyly nasazeny.
