# WUNOO v1.397 Candidate

## Změna

- Zpřísněna idempotentní kontrola refund ledgeru: opakování nyní kromě vyvážené dvojice účetních zápisů ověřuje také `refund_id`, `provider_refund_id` a částku v `metadata_json` každé položky.
- Opakované použití stejného provider reference s jinou identitou refundace nebo poškozenými metadaty skončí bezpečně HTTP 409 `REFUND_LEDGER_INCONSISTENT`.
- Beze změny zůstává chování přesného opakování stejné refundace.

## Ověření

- `TEST_V397.py`: PASS — přesné opakování idempotentní; změněné ID refundace a poškozená metadata vrací HTTP 409.
- Regresní testy předchozích verzí se spouštějí samostatně; tato lokální sada používá SQLite.
- Produkční PostgreSQL integrace, skutečný platební provider a nasazení nejsou tímto kandidátem potvrzeny.
