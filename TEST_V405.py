"""v1.405 regression: legacy /api/orders/{id}/deliver respects modern settlement rows."""
import os, sys, tempfile, uuid
from pathlib import Path
from fastapi import HTTPException
ROOT = Path(__file__).resolve().parent
os.environ["WUNOO_DB_PATH"] = os.path.join(tempfile.gettempdir(), "wunoo_v405_" + uuid.uuid4().hex + ".db")
sys.path.insert(0, str(ROOT))
from app import main
class Result:
    def __init__(self, row=None): self.row = row
    def fetchone(self): return self.row
class FakeDB:
    backend = "sqlite"
    def __init__(self):
        self.queries=[]; self.writes=[]
        self.order={"id":"order-405","status":"out_for_delivery","courier_id":"courier-1","delivery_proof_status":"not_required","delivery_distance_km":1.0,"total_czk":200.0,"subtotal_czk":150.0,"merchant_id":"merchant-1"}
    def __enter__(self): return self
    def __exit__(self,*args): return False
    def execute(self,sql,params=()):
        self.queries.append((sql,params))
        if sql.startswith("BEGIN IMMEDIATE"): return Result()
        if "SELECT * FROM orders WHERE id=?" in sql: return Result(self.order)
        if "SELECT 1 FROM settlements WHERE order_id=?" in sql: return Result(None)
        if "SELECT 1 FROM settlement_runs WHERE order_id=?" in sql: return Result({"1":1})
        if sql.startswith(("INSERT ","UPDATE ","DELETE ")): self.writes.append(sql)
        raise AssertionError("unexpected query after settlement conflict check: "+sql)
db=FakeDB()
main.current_user=lambda authorization:{"id":"admin-405","role":"admin"}
main.require_role=lambda user,*roles:None
main.core_db_connect=lambda:db
try: main.deliver("order-405",None)
except HTTPException as exc:
    assert exc.status_code==409, exc.status_code
    assert "jiné API generaci" in str(exc.detail), exc.detail
else: raise AssertionError("legacy delivery accepted modern settlement")
assert any("BEGIN IMMEDIATE" in sql for sql,_ in db.queries),db.queries
assert any("FROM settlement_runs WHERE order_id=?" in sql for sql,_ in db.queries),db.queries
assert not db.writes,db.writes
source=(ROOT/"app"/"main.py").read_text()
route=source[source.index('def deliver(order_id: str'):source.index('def _latest_courier_location')]
assert "_v247_begin_order_transaction(c, order_id)" in route
assert "_v253_modern_settlement_exists(c, order_id)" in route
assert route.index("_v247_begin_order_transaction(c, order_id)") < route.index('SELECT * FROM orders WHERE id=?')
print("V405_LEGACY_DELIVERY_CROSS_API_SETTLEMENT_GUARD_PASS conflict=409 no_writes=PASS transaction_before_read=PASS")
