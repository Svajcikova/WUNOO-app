# WUNOO v1.315 — Dispatch Generation Integration & Compatibility

## Co je nové
- Dokončeno napojení `dispatch_generation` na redispatch/reopen/recovery cesty.
- Generace se zvyšuje při redispatchi, znovuotevření starého dispatch jobu, recovery reopen a operator reassignment.
- Starý courier/worker snapshot tak nemůže pokračovat po změně dispatch cyklu.
- Přidána explicitní verze courier lifecycle API: `POST /api/v315/courier/jobs/{job_id}/action`.
- Nové klienty mají povinně posílat `X-Dispatch-Generation`.
- Využívá se stále jediná kanonická lifecycle logika v1.061/v1.314; žádná druhá implementace accept/pickup/deliver.
- Fail-closed při chybějící, nečíselné nebo zastaralé generaci.

## API
- `GET /api/v315/policy`
- `POST /api/v315/courier/jobs/{job_id}/action`
- `GET /api/v314/dispatch/jobs/{job_id}/generation`
- `GET /api/v314/dispatch/fence-audit`

## Testy
- `V315_OK`
- `V314_OK`
- `V313_OK`
- `py_compile` OK
- `compileall` OK

## Poznámka
v1.315 doplňuje integrační body k v1.314. Generace je nyní měněna v hlavních redispatch/reopen/recovery cestách, které vytvářejí nový dispatch cyklus.
