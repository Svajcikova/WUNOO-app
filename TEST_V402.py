"""v1.402 regression: modern and legacy settlement rows may not coexist for one order."""
import os, sys, tempfile, uuid
from pathlib import Path
from fastapi import HTTPException
ROOT = Path(__file__).resolve().parent
os.environ['WUNOO_DB_PATH'] = os.path.join(tempfile.gettempdir(), 'wunoo_v402_' + uuid.uuid4().hex + '.db')
sys.path.insert(0, str(ROOT))
from app import main

# Either source alone is allowed; absence of both is allowed before creation.
assert main._v402_guard_single_settlement_source(None, None) is None
assert main._v402_guard_single_settlement_source({'id': 'modern-1'}, None) is None
assert main._v402_guard_single_settlement_source(None, {'id': 'legacy-1'}) is None

# Both tables can have separate UNIQUE(order_id) constraints, so test the cross-table collision explicitly.
try:
    main._v402_guard_single_settlement_source({'id': 'modern-1'}, {'id': 'legacy-1'})
except HTTPException as exc:
    assert exc.status_code == 409
    assert exc.detail['code'] == 'SETTLEMENT_DUPLICATE_SOURCES'
else:
    raise AssertionError('accepted modern and legacy settlements for the same order')

# Ensure the production route invokes the guard before returning an existing settlement.
source = (ROOT / 'app' / 'main.py').read_text(encoding='utf-8')
route = source[source.index('def v062_settlement_run'):source.index('@app.get("/api/v062/settlement/{order_id}")')]
assert 'legacy=c.execute("SELECT * FROM settlements WHERE order_id=?",(oid,)).fetchone()' in route
assert '_v402_guard_single_settlement_source(existing, legacy)' in route
assert route.index('_v402_guard_single_settlement_source(existing, legacy)') < route.index('if existing:')
print('V402_CROSS_API_SETTLEMENT_SINGLE_SOURCE_PASS single_source=PASS duplicate_sources=409 route_guard=PASS')
