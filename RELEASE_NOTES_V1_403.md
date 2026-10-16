# WUNOO v1.403 Candidate

## Změna
- `V132SettlementRepository.create_for_delivered()` nyní před idempotentním návratem ověřuje moderní `settlement_runs` i legacy `settlements`.
- Pokud pro jednu objednávku existují záznamy v obou tabulkách, repository odmítne operaci HTTP 409 `SETTLEMENT_DUPLICATE_SOURCES`.
- Oprava uzavírá cestu, kterou ochrana v1.402 nepokrývala: starší repository dříve upřednostnilo legacy záznam a vrátilo úspěch, aniž by řešilo moderní záznam.
- Při konfliktu se neprovádí normalizace ledgeru ani žádné další zápisy; případ vyžaduje ruční finanční odsouhlasení.

## Ověření
- `TEST_V403.py` — PASS: současná existence obou zdrojů přes repository odmítnuta HTTP 409; ověřeno, že po detekci konfliktu nenásledují další zápisy.
- `TEST_V402.py`, `TEST_V401.py`, `TEST_V400.py` — PASS.
- `TEST_V399.py`, `TEST_V398.py`, `TEST_V395.py`, `TEST_V394.py`, `TEST_V393.py`, `TEST_V392.py`, `TEST_V391.py`, `TEST_V390.py`, `TEST_V389.py` — PASS.
- `TEST_V381.py`, `TEST_V382.py`, `TEST_V362.py` — PASS.
- `python -m compileall -q app` — PASS.
- Finální ZIP prošel `unzip -t` a klíčové testy byly spuštěny znovu po rozbalení finálního archivu.
- Jedno kombinované spuštění regresních testů překročilo celkový časový limit po úspěšném V389; V381, V382 a V362 byly následně spuštěny samostatně a prošly.

## Omezení
- Lokální testy neprokazují souběh v produkčním PostgreSQL ani chování živého poskytovatele plateb.
- Kandidát nebyl nasazen a změny nebyly odeslány na GitHub.
