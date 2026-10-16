import os,tempfile,sqlite3,threading,json,uuid
DB=os.path.join(tempfile.gettempdir(),'wunoo_v331_idempotency.db')
os.environ['WUNOO_DB_PATH']=DB
import app.main as m
try: os.remove(DB)
except FileNotFoundError: pass
m.init_db()
with m.core_db_connect() as c:
    for name in 'migrate_v046 migrate_v052 migrate_v053 migrate_v061 migrate_v119 migrate_v120 migrate_v121 migrate_v122 migrate_v310 migrate_v311 migrate_v312 migrate_v313 migrate_v314 migrate_v315 migrate_v316 migrate_v318 migrate_v319 migrate_v321 migrate_v322 migrate_v323 migrate_v325 migrate_v326 migrate_v328 migrate_v329 migrate_v330 migrate_v331'.split():
        getattr(m,name)(c)
    ts='2026-01-01T00:00:00'
    c.execute("INSERT INTO merchants(id,name,created_at) VALUES(?,?,?)",('m331','M331',ts))
    c.execute("INSERT INTO customers(id,name,email,created_at) VALUES(?,?,?,?)",('cust331','C331','c331@example.test',ts))
    for cid in ('c331a','c331b','c331c'):
        c.execute("INSERT INTO couriers(id,name,status,created_at) VALUES(?,?,?,?)",(cid,cid,'online',ts))
    c.execute("INSERT INTO orders(id,customer_id,merchant_id,status,subtotal_czk,service_fee_czk,delivery_fee_czk,total_czk,address,created_at,updated_at,courier_id,assigned_at) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)",('o331','cust331','m331','courier_assigned',100,0,0,100,'A',ts,ts,'c331a',ts))
    c.execute("INSERT INTO dispatch_jobs(id,order_id,merchant_id,courier_id,status,pickup_eta_minutes,delivery_eta_minutes,offered_at,accepted_at,created_at,updated_at,dispatch_generation) VALUES(?,?,?,?,?,?,?,?,?,?,?,?)",('j331','o331','m331','c331a','accepted',5,25,ts,ts,ts,ts,1))
    c.commit()
actor={'id':'ops331','role':'ops_agent'}
# concurrent same-key/same-payload commands: serialize through the same transaction and journal
results=[]; lock=threading.Lock()
def worker(payload):
    try:
        with m.core_db_connect() as c:
            r=m._v313_command(c,'same-key-331','o331',actor,'operator_reassign',payload); c.commit()
        with lock: results.append(('ok',r.get('replayed'),r['response'].get('courier_id')))
    except Exception as e:
        with lock: results.append(('err',getattr(e,'status_code',None),str(getattr(e,'detail',e))))
threads=[threading.Thread(target=worker,args=({'courier_id':'c331b','reason':'same'},)) for _ in range(8)]
for t in threads:t.start()
for t in threads:t.join()
assert sum(1 for x in results if x[0]=='ok' and x[1] is False)==1, results
assert sum(1 for x in results if x[0]=='ok' and x[1] is True)==7, results
assert not any(x[0]=='err' for x in results), results
# conflicting replay with same key but different payload must be rejected
try:
    with m.core_db_connect() as c:
        m._v313_command(c,'same-key-331','o331',actor,'operator_reassign',{'courier_id':'c331c','reason':'different'}); c.commit()
    raise AssertionError('conflicting payload unexpectedly accepted')
except Exception as e:
    assert getattr(e,'status_code',None)==409, (type(e),e)
    assert isinstance(getattr(e,'detail',None),dict) and e.detail.get('code')=='DISPATCH_REQUEST_KEY_PAYLOAD_CONFLICT', e.detail
with m.core_db_connect() as c:
    row=c.execute("SELECT request_payload_sha256 FROM ai_dispatch_command_journal_v312 WHERE request_key=?",('same-key-331',)).fetchone()
    assert row and row['request_payload_sha256']
    conflicts=c.execute("SELECT COUNT(*) n FROM ai_dispatch_idempotency_conflicts_v331 WHERE request_key=?",('same-key-331',)).fetchone()['n']
    assert conflicts==1, conflicts
print('V331_OK')
print('CONCURRENT_SAME_KEY',8)
print('ORIGINAL_MUTATIONS',1)
print('REPLAYS',7)
print('PAYLOAD_CONFLICTS',1)
print('DOUBLE_MUTATIONS',0)
