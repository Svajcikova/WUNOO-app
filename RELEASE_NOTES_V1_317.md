# WUNOO v1.317 — Dispatch Generation Post-Lock Recheck

Closes a check-then-lock race in generation fencing. Courier dispatch commands now validate the generation before acquiring the canonical lifecycle lock and again after the lock/re-read. A generation change caused by redispatch, recovery, or reassignment between those checks causes HTTP 409 and no stale lifecycle mutation.

Validation: V317_OK, V316_OK, V315_OK, V314_OK, V313_OK, py_compile OK, compileall OK.
