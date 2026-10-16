"""v1.404: cached idempotency responses cannot bypass settlement source conflict checks."""
import os, sys, tempfile, uuid
from pathlib import Path
from fastapi import HTTPException
ROOT = Path(__file__).resolve().parent
os.environ['WUNOO_DB_PATH'] = os.path.join(tempfile.gettempdir(), 'wunoo_v404_' + uuid.uuid4().hex + '.db')
sys.path.insert(0, str(ROOT))
from app import main

class Result:
    def __init__(self, row): self.row = row
    def fetchone(self): return self.row
class FakeDB:
    backend = 'sqlite'
    def __init__(self):
        self.queries = []
        self.calls = []
    def __enter__(self): return self
    def __exit__(self, *args): return False
    def execute(self, sql, params=()):
        self.queries.append(sql)
        if sql.startswith('BEGIN IMMEDIATE'): return Result(None)
        if 'FROM orders WHERE id=?' in sql:
            return Result({'id':'order-404','status':'delivered','total_czk':100.0})
        if 'FROM settlement_runs WHERE order_id=?' in sql:
            return Result({'id':'modern-404','order_id':'order-404','status':'completed','gross_czk':100,'platform_fee_czk':10,'merchant_payout_czk':50,'courier_payout_czk':40,'delivery_fee_czk':40,'adjustment_czk':0,'net_czk':90})
        if 'FROM settlements WHERE order_id=?' in sql:
            return Result({'id':'legacy-404','order_id':'order-404'})
        raise AssertionError('unexpected query: '+sql)
    def commit(self): pass
    def rollback(self): pass

db = FakeDB()
main.current_user = lambda authorization: {'id':'admin-1','role':'admin'}
main.require_role = lambda user, roles: None
main.core_db_connect = lambda: db
cache_called = []
def cached(*args, **kwargs):
    cache_called.append(True)
    return {'settlement_id':'old-cache','status':'completed'}
main._v052_guard = cached
try:
    main.v062_settlement_run({'order_id':'order-404'}, None, 'same-key')
except HTTPException as exc:
    assert exc.status_code == 409, exc.status_code
    assert exc.detail['code'] == 'SETTLEMENT_DUPLICATE_SOURCES', exc.detail
else:
    raise AssertionError('cached idempotency response bypassed dual-source conflict')
assert not cache_called, 'idempotency cache was consulted before canonical settlement guard'
assert len(db.queries) == 4, db.queries  # BEGIN + order + both settlement sources; no writes

source = (ROOT/'app'/'main.py').read_text(encoding='utf-8')
route = source[source.index('def v062_settlement_run'):source.index('@app.get("/api/v062/settlement/{order_id}")')]
assert route.index('_v402_guard_single_settlement_source(existing, legacy)') < route.index('_v052_guard(c,')
assert 'SETTLEMENT_IDEMPOTENCY_WITHOUT_LEDGER' in route
print('V404_CACHED_IDEMPOTENCY_CANNOT_BYPASS_SETTLEMENT_GUARD_PASS conflict=409 cache_not_consulted writes=0')
