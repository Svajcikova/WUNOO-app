# WUNOO v1.405 Candidate

## Změna
- Starší endpoint `POST /api/orders/{order_id}/deliver` nyní před první četbou zahájí serializovanou transakci přes `_v247_begin_order_transaction`.
- Před dokončením doručení kontroluje jak `settlements`, tak `settlement_runs`. Dříve kontroloval pouze legacy tabulku `settlements`, takže mohl ignorovat moderní vyúčtování a pokračovat k vytvoření dalšího účetního efektu.
- Při existenci vyúčtování v kterémkoli zdroji endpoint vrací HTTP 409 a nepokračuje v doručení ani ve finančních zápisech.
- SQLite používá `BEGIN IMMEDIATE`; PostgreSQL helper zahajuje transakci a uzamyká řádek objednávky `FOR UPDATE`.

## Ověření
- `TEST_V405.py` — PASS: moderní settlement blokuje legacy delivery, HTTP 409, bez zápisů; transakce před prvním čtením.
- `TEST_V404.py`, `TEST_V403.py`, `TEST_V402.py`, `TEST_V401.py`, `TEST_V400.py` — PASS.
- `TEST_V399.py`, `TEST_V398.py`, `TEST_V397.py`, `TEST_V396.py`, `TEST_V395.py`, `TEST_V394.py`, `TEST_V389.py`, `TEST_V381.py` — PASS.
- `python -m compileall -q app` — PASS.
- ZIP integrity — PASS.
- `TEST_V362.py` vytiskl očekávané golden-order assertions, ale proces nepřestal v časovém limitu; nepovažuji jej proto za plně dokončený test.

## Omezení
- Regresní testy běží v lokálním SQLite/test-double prostředí. PostgreSQL souběh musí být potvrzen samostatným integračním testem.
- Kandidát nebyl nasazen a změny nebyly odeslány na GitHub.
