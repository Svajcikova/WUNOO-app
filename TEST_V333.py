import os,tempfile,threading,json
DB=os.path.join(tempfile.gettempdir(),'wunoo_v333_state_machine.db')
os.environ['WUNOO_DB_PATH']=DB
try: os.remove(DB)
except FileNotFoundError: pass
import app.main as m
m.init_db()
with m.core_db_connect() as c:
    for name in 'migrate_v046 migrate_v052 migrate_v053 migrate_v061 migrate_v119 migrate_v120 migrate_v121 migrate_v122 migrate_v310 migrate_v311 migrate_v312 migrate_v313 migrate_v314 migrate_v315 migrate_v316 migrate_v318 migrate_v319 migrate_v321 migrate_v322 migrate_v323 migrate_v325 migrate_v326 migrate_v328 migrate_v329 migrate_v330 migrate_v331 migrate_v332 migrate_v333'.split():
        getattr(m,name)(c)
    ts='2026-01-01T00:00:00'
    c.execute("INSERT INTO merchants(id,name,created_at) VALUES(?,?,?)",('m333','M333',ts))
    c.execute("INSERT INTO customers(id,name,email,created_at) VALUES(?,?,?,?)",('cust333','C333','c333@example.test',ts))
    for cid in ('c333a','c333b','c333c'):
        c.execute("INSERT INTO couriers(id,name,status,created_at) VALUES(?,?,?,?)",(cid,cid,'online',ts))
    c.execute("INSERT INTO orders(id,customer_id,merchant_id,status,subtotal_czk,service_fee_czk,delivery_fee_czk,total_czk,address,created_at,updated_at,courier_id,assigned_at) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)",('o333','cust333','m333','courier_assigned',100,0,0,100,'A',ts,ts,'c333a',ts))
    c.execute("INSERT INTO dispatch_jobs(id,order_id,merchant_id,courier_id,status,pickup_eta_minutes,delivery_eta_minutes,offered_at,accepted_at,created_at,updated_at,dispatch_generation) VALUES(?,?,?,?,?,?,?,?,?,?,?,?)",('j333','o333','m333','c333a','accepted',5,25,ts,ts,ts,ts,1))
    c.commit()
actor={'id':'ops333','role':'ops_agent'}
payload={'courier_id':'c333b','reason':'state-machine'}
with m.core_db_connect() as c:
    r=m._v333_command(c,'key333','o333',actor,'operator_reassign',payload,'1'); c.commit()
assert r['replayed'] is False and r['postcondition']['passed'] is True
with m.core_db_connect() as c:
    j=c.execute("SELECT status FROM ai_dispatch_command_journal_v312 WHERE request_key='key333'").fetchone()['status']
    pc=c.execute("SELECT passed,actual_generation FROM ai_dispatch_command_postconditions_v333 WHERE request_key='key333'").fetchone()
    state=c.execute("SELECT o.courier_id oc,d.courier_id dc,d.dispatch_generation dg FROM orders o JOIN dispatch_jobs d ON d.order_id=o.id WHERE o.id='o333'").fetchone()
assert j=='completed' and int(pc['passed'])==1 and int(pc['actual_generation'])==2 and state['oc']=='c333b' and state['dc']=='c333b'
# Bump generation with a separate valid command, then replay the original key.
with m.core_db_connect() as c:
    bump=m._v333_command(c,'bump333','o333',actor,'operator_reassign',{'courier_id':'c333c','reason':'generation-bump'},'2'); c.commit()
assert bump['replayed'] is False
with m.core_db_connect() as c:
    r2=m._v333_command(c,'key333','o333',actor,'operator_reassign',payload,'1'); c.commit()
assert r2['replayed'] is True and r2['replay_generation_stale'] is True and r2['current_generation']==3
# stale new key rejected before mutation
try:
    with m.core_db_connect() as c:
        m._v333_command(c,'stale333','o333',actor,'operator_reassign',{'courier_id':'c333c','reason':'stale'},'1'); c.commit()
    raise AssertionError('stale accepted')
except Exception as e:
    assert getattr(e,'status_code',None)==409
with m.core_db_connect() as c:
    s=c.execute("SELECT courier_id,dispatch_generation FROM dispatch_jobs WHERE id='j333'").fetchone()
assert s['courier_id']=='c333c' and int(s['dispatch_generation'])==3
# Force postcondition failure: all mutation + pending journal must roll back.
orig=m._v333_verify_command_postcondition
def forced_fail(*args,**kwargs):
    return {'passed':False,'expected':kwargs.get('expected') or args[6],'actual':{},'evidence_sha256':'forced'}
m._v333_verify_command_postcondition=forced_fail
try:
    with m.core_db_connect() as c:
        m._v333_command(c,'rollback333','o333',actor,'operator_reassign',{'courier_id':'c333b','reason':'rollback'},'3'); c.commit()
    raise AssertionError('forced postcondition accepted')
except Exception as e:
    assert getattr(e,'status_code',None)==503
finally:
    m._v333_verify_command_postcondition=orig
with m.core_db_connect() as c:
    s=c.execute("SELECT courier_id,dispatch_generation FROM dispatch_jobs WHERE id='j333'").fetchone()
    j=c.execute("SELECT COUNT(*) n FROM ai_dispatch_command_journal_v312 WHERE request_key='rollback333'").fetchone()['n']
assert s['courier_id']=='c333c' and int(s['dispatch_generation'])==3 and j==0
# Concurrent exact same key: one mutation, remaining requests replay.
results=[]; lock=threading.Lock()
def worker():
    try:
        with m.core_db_connect() as c:
            r=m._v333_command(c,'concurrent333','o333',actor,'operator_reassign',{'courier_id':'c333b','reason':'concurrent'},'3'); c.commit()
        with lock: results.append(('ok',r['replayed']))
    except Exception as e:
        with lock: results.append(('err',getattr(e,'status_code',None),str(e)))
threads=[threading.Thread(target=worker) for _ in range(8)]
[t.start() for t in threads]
[t.join() for t in threads]
oks=[x for x in results if x[0]=='ok']
assert len(oks)==8 and sum(1 for x in oks if x[1] is False)==1 and sum(1 for x in oks if x[1] is True)==7, results
with m.core_db_connect() as c:
    s=c.execute("SELECT courier_id,dispatch_generation FROM dispatch_jobs WHERE id='j333'").fetchone()
    p=c.execute("SELECT COUNT(*) n FROM ai_dispatch_command_postconditions_v333 WHERE request_key='concurrent333' AND passed=1").fetchone()['n']
assert s['courier_id']=='c333b' and int(s['dispatch_generation'])==4 and p==1
print('V333_OK')
print('POSTCONDITION_COMPLETED',1)
print('STALE_NEW_KEY_REJECTED',1)
print('EXACT_REPLAY_NON_MUTATING',1)
print('FAILED_POSTCONDITION_ROLLED_BACK',1)
print('CONCURRENT_SAME_KEY',len(results))
print('ORIGINAL_MUTATIONS',1)
print('REPLAYS',7)
print('DOUBLE_MUTATIONS',0)
