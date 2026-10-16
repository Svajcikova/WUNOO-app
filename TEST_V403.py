"""v1.403 regression: repository API generations reject cross-table settlement conflicts."""
import os, sys, tempfile, uuid
from pathlib import Path
from fastapi import HTTPException
ROOT = Path(__file__).resolve().parent
os.environ['WUNOO_DB_PATH'] = os.path.join(tempfile.gettempdir(), 'wunoo_v403_' + uuid.uuid4().hex + '.db')
sys.path.insert(0, str(ROOT))
from app import main

class FakeDB:
    backend = 'sqlite'
    def __init__(self, legacy, modern):
        self.legacy, self.modern = legacy, modern
        self.queries = []
    def execute(self, sql, params=()):
        self.queries.append(sql)
        if 'FROM settlements WHERE order_id=?' in sql:
            row = self.legacy
        elif 'FROM settlement_runs WHERE order_id=?' in sql:
            row = self.modern
        else:
            raise AssertionError(f'unexpected query before conflict guard: {sql}')
        class Result:
            def fetchone(self_inner): return row
        return Result()

# The older repository path used to prefer legacy if both sources existed.
db = FakeDB({'id':'legacy-1'}, {'id':'modern-1'})
try:
    main.V132SettlementRepository(db).create_for_delivered({'id':'order-1','total_czk':100,'delivery_distance_km':1}, 'actor-1')
except HTTPException as exc:
    assert exc.status_code == 409
    assert exc.detail['code'] == 'SETTLEMENT_DUPLICATE_SOURCES'
else:
    raise AssertionError('repository accepted simultaneous legacy and modern settlement rows')
assert len(db.queries) == 2, db.queries  # no normalization, insert, or ledger writes after detection

source = (ROOT / 'app' / 'main.py').read_text(encoding='utf-8')
repo = source[source.index('class V132SettlementRepository'):source.index('class V132RepositoryContext')]
assert '_v402_guard_single_settlement_source(existing_modern, existing_legacy)' in repo
assert repo.index('_v402_guard_single_settlement_source(existing_modern, existing_legacy)') < repo.index('if existing_legacy:')
print('V403_CROSS_API_REPOSITORY_SETTLEMENT_GUARD_PASS conflict=409 writes_after_detection=0')
