# WUNOO v1.370 Candidate

## Security hardening
- Hardened `/api/v134/auth/me` to return only public identity fields.
- Prevented exposure of `users.password_hash` through the authenticated identity endpoint.
- Prevented exposure of internal `session_expires_at` repository metadata.

## Regression coverage
- Added `TEST_V370.py` for secret-field exposure regression.
- V365 courier IDOR regression: PASS.
- V368 dispatch-generation IDOR regression: PASS.
- Python compileall: PASS.

## Status
Candidate only. No production release claim.
