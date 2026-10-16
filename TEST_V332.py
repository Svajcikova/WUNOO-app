import os,tempfile,threading
DB=os.path.join(tempfile.gettempdir(),'wunoo_v332_cross_fence.db')
os.environ['WUNOO_DB_PATH']=DB
try: os.remove(DB)
except FileNotFoundError: pass
import app.main as m
m.init_db()
with m.core_db_connect() as c:
    for name in 'migrate_v046 migrate_v052 migrate_v053 migrate_v061 migrate_v119 migrate_v120 migrate_v121 migrate_v122 migrate_v310 migrate_v311 migrate_v312 migrate_v313 migrate_v314 migrate_v315 migrate_v316 migrate_v318 migrate_v319 migrate_v321 migrate_v322 migrate_v323 migrate_v325 migrate_v326 migrate_v328 migrate_v329 migrate_v330 migrate_v331 migrate_v332'.split():
        getattr(m,name)(c)
    ts='2026-01-01T00:00:00'
    c.execute("INSERT INTO merchants(id,name,created_at) VALUES(?,?,?)",('m332','M332',ts))
    c.execute("INSERT INTO customers(id,name,email,created_at) VALUES(?,?,?,?)",('cust332','C332','c332@example.test',ts))
    for cid in ('c332a','c332b','c332c'):
        c.execute("INSERT INTO couriers(id,name,status,created_at) VALUES(?,?,?,?)",(cid,cid,'online',ts))
    c.execute("INSERT INTO orders(id,customer_id,merchant_id,status,subtotal_czk,service_fee_czk,delivery_fee_czk,total_czk,address,created_at,updated_at,courier_id,assigned_at) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)",('o332','cust332','m332','courier_assigned',100,0,0,100,'A',ts,ts,'c332a',ts))
    c.execute("INSERT INTO dispatch_jobs(id,order_id,merchant_id,courier_id,status,pickup_eta_minutes,delivery_eta_minutes,offered_at,accepted_at,created_at,updated_at,dispatch_generation) VALUES(?,?,?,?,?,?,?,?,?,?,?,?)",('j332','o332','m332','c332a','accepted',5,25,ts,ts,ts,ts,1))
    c.commit()
actor={'id':'ops332','role':'ops_agent'}
payload={'courier_id':'c332b','reason':'cross-fence'}
with m.core_db_connect() as c:
    r=m._v332_command(c,'key332','o332',actor,'operator_reassign',payload,'1'); c.commit()
assert r['replayed'] is False
with m.core_db_connect() as c:
    gen=c.execute("SELECT dispatch_generation FROM dispatch_jobs WHERE id='j332'").fetchone()['dispatch_generation']
assert int(gen)==2
# exact completed replay with old generation is safe and non-mutating
with m.core_db_connect() as c:
    r2=m._v332_command(c,'key332','o332',actor,'operator_reassign',payload,'1'); c.commit()
assert r2['replayed'] is True and r2['replay_generation_stale'] is True and r2['original_generation']==1 and r2['current_generation']==2
# new key with stale generation must reject and not mutate
try:
    with m.core_db_connect() as c:
        m._v332_command(c,'key332-stale','o332',actor,'operator_reassign',{'courier_id':'c332c','reason':'stale'},'1'); c.commit()
    raise AssertionError('stale accepted')
except Exception as e:
    assert getattr(e,'status_code',None)==409, (type(e),e)
# fresh generation new key must mutate
with m.core_db_connect() as c:
    r3=m._v332_command(c,'key332-fresh','o332',actor,'operator_reassign',{'courier_id':'c332c','reason':'fresh'},'2'); c.commit()
assert r3['replayed'] is False
with m.core_db_connect() as c:
    gen2=c.execute("SELECT dispatch_generation,courier_id FROM dispatch_jobs WHERE id='j332'").fetchone()
    fences=c.execute("SELECT COUNT(*) n FROM ai_dispatch_generation_fence_v332").fetchone()['n']
assert int(gen2['dispatch_generation'])==3 and gen2['courier_id']=='c332c' and fences==2
print('V332_OK')
print('INITIAL_MUTATION',1)
print('STALE_NEW_KEY_REJECTED',1)
print('EXACT_REPLAY_AFTER_GENERATION_BUMP',1)
print('FRESH_CURRENT_GENERATION_MUTATION',1)
print('DOUBLE_MUTATIONS',0)
