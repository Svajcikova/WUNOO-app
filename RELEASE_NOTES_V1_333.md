# WUNOO v1.333 — Dispatch Command State Machine Integrity

## Cíl
Zajistit, že dispatch command může být označen jako `completed` pouze tehdy, když po mutaci skutečný stav `orders` + `dispatch_jobs` přesně odpovídá očekávanému post-condition.

## Změny
- Nová tabulka `ai_dispatch_command_postconditions_v333` pro atomický důkaz výsledného stavu commandu.
- Completed journal entry je povolena pouze po úspěšném post-condition checku.
- Kontroluje se současně:
  - `orders.status`
  - `orders.courier_id`
  - `dispatch_jobs.status`
  - `dispatch_jobs.courier_id`
  - `dispatch_jobs.dispatch_generation`
- Pro operator reassignment je vyžadován přesný generation increment `expected_generation + 1`.
- Pokud post-condition selže, výjimka zabrání commitu celé transakce: mutace i pending journal se rollbacknou.
- Exact completed replay zůstává ne-mutující i po pozdější změně generation.
- Stale nový idempotency key je odmítnut před mutací.
- Přidán endpoint `GET /api/v333/policy`.
- Přidán endpoint `POST /api/v333/ai/dispatch/command/{order_id}`.
- Přidán endpoint `GET /api/v333/ai/dispatch/postconditions`.
- V rámci v333 je explicitně ošetřeno chybějící `dispatch_job` fail-closed chováním.

## Ověření
- `TEST_V333.py` — PASS
- `TEST_V331.py` — PASS
- `TEST_V332.py` — PASS
- Python `py_compile` — PASS
- Python `compileall` — PASS
- Concurrent same-key: 8 requestů → 1 skutečná mutace + 7 replayů
- Post-condition failure rollback: PASS
- Stale generation rejection: PASS
- Exact replay po generation bump: PASS
- Double mutations: 0

## Release
- Version: `1.333`
- Artifact: `WUNOO_MVP_v1_333_DISPATCH_COMMAND_STATE_MACHINE_INTEGRITY.zip`
- Hash: SHA-256
