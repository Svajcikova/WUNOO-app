# WUNOO

WUNOO is a food-ordering and delivery platform MVP. This repository contains a FastAPI backend and historical regression checks/release notes.

## Current release status

**BLOCKED — not production-ready. Do not deploy this repository as-is.**

The reviewed repository snapshot is incomplete for a full application launch. The backend references a `frontend_v029/` asset tree and PostgreSQL migration files under `migrations/postgresql/`, but those directories are not present in the repository root. The repository also lacks a verified dependency manifest. Consequently, full startup, UI delivery, and database initialization cannot be certified from this checkout.

## Required before release

1. Restore the authoritative `frontend_v029/` files from the original project source.
2. Restore and review all required `migrations/postgresql/*.sql` files in their intended order.
3. Restore release/security evidence files required by the backend's release gates.
4. Build and verify a dependency manifest against actual imports and the deployment environment.
5. Run the complete regression suite, then test startup and critical workflows against real PostgreSQL and configured external services.
6. Review secrets, CORS, allowed hosts, payment webhooks, courier dispatch, payouts, logging, and recovery procedures.
7. Produce a release archive only after completeness and integration gates pass.

## Repository contents

- `app/main.py` — FastAPI application and route definitions.
- `app/repository.py` — data-access helpers.
- `app/static/` — tracked static assets within the application package.
- `TEST_*.py` and `RELEASE_NOTES_*.md` — historical regression checks and release notes. A passing historical test does not prove the whole application is production-ready.

## Local checks

Until the full source and dependency manifest are restored, a reliable environment setup cannot be documented safely. After restoration, install dependencies from the verified manifest and run the full test suite from the repository root. Compilation and isolated static tests are not substitutes for live PostgreSQL and end-to-end tests.

## Secrets and local data

Never commit API keys, signing secrets, webhook secrets, database credentials, customer data, or a local database. Start from `.env.example`, keep actual `.env` untracked, and use local-only values for development.

## Release rule

A candidate may be labelled releasable only when source completeness, dependency installation, migration execution, regression tests, production-like integration tests, and security review all pass. Keep incomplete candidates explicitly marked as blocked.
