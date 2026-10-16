# WUNOO v1.398 Candidate

## Změna

- Zpřísněna kontrola `amount_czk` v metadatech refund ledgeru při opakovaném zápisu.
- Akceptována je pouze skutečná JSON číselná hodnota; booleovské hodnoty (`true`/`false`) a číselné řetězce už nemohou projít jako platná účetní evidence.
- Přesné opakování nezměněné refundace zůstává idempotentní. Neplatná metadata vrací HTTP 409 `REFUND_LEDGER_INCONSISTENT`.

## Ověření

- `TEST_V398.py`: PASS — běžné opakování zachová dva zápisy; `true` a řetězec `"1.0"` v částce metadat jsou odmítnuty HTTP 409.
- `TEST_V397.py`: PASS.
- Testy jsou lokální a používají SQLite. PostgreSQL souběh, skutečný platební provider a produkční nasazení nejsou tímto kandidátem potvrzeny.
