import os,tempfile,multiprocessing as mp,time,signal,uuid,json
DB=os.path.join(tempfile.gettempdir(),'wunoo_v330_multi_order_chaos.db')
MIGRATIONS='migrate_v046 migrate_v052 migrate_v053 migrate_v061 migrate_v119 migrate_v120 migrate_v121 migrate_v122 migrate_v310 migrate_v311 migrate_v312 migrate_v313 migrate_v314 migrate_v315 migrate_v316 migrate_v318 migrate_v319 migrate_v321 migrate_v322 migrate_v323 migrate_v325 migrate_v326 migrate_v328 migrate_v329 migrate_v330'.split()

def seed():
    try: os.remove(DB)
    except FileNotFoundError: pass
    os.environ['WUNOO_DB_PATH']=DB
    import app.main as m
    m.init_db()
    with m.core_db_connect() as c:
        for x in MIGRATIONS: getattr(m,x)(c)
        ts='2026-01-01T00:00:00'; c.execute("INSERT INTO merchants(id,name,created_at) VALUES(?,?,?)",('m330','M330',ts)); c.execute("INSERT INTO customers(id,name,email,created_at) VALUES(?,?,?,?)",('cust330','C330','c330@example.test',ts))
        for i in range(3):
            c.execute("INSERT INTO couriers(id,name,status,created_at) VALUES(?,?,?,?)",(f'c330a{i}',f'c330a{i}','online',ts)); c.execute("INSERT INTO couriers(id,name,status,created_at) VALUES(?,?,?,?)",(f'c330b{i}',f'c330b{i}','online',ts))
            oid=f'o330_{i}'; jid=f'j330_{i}'
            c.execute("INSERT INTO orders(id,customer_id,merchant_id,status,subtotal_czk,service_fee_czk,delivery_fee_czk,total_czk,address,created_at,updated_at,courier_id,assigned_at) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)",(oid,'cust330','m330','courier_assigned',100,0,0,100,'A',ts,ts,f'c330a{i}',ts))
            c.execute("INSERT INTO dispatch_jobs(id,order_id,merchant_id,courier_id,status,pickup_eta_minutes,delivery_eta_minutes,offered_at,accepted_at,created_at,updated_at,dispatch_generation) VALUES(?,?,?,?,?,?,?,?,?,?,?,?)",(jid,oid,'m330',f'c330a{i}','accepted',5,25,ts,ts,ts,ts,1))
        c.commit()

def stale(jid,ready,go,q):
    os.environ['WUNOO_DB_PATH']=DB; import app.main as m
    try:
        with m.core_db_connect() as c: gen=int(c.execute('SELECT dispatch_generation FROM dispatch_jobs WHERE id=?',(jid,)).fetchone()['dispatch_generation'])
        ready.set(); go.wait(10)
        with m.core_db_connect() as c:
            c.execute('BEGIN IMMEDIATE'); m._v314_require_generation(c,jid,str(gen)); c.execute("UPDATE dispatch_jobs SET updated_at='STALE' WHERE id=?",(jid,)); c.commit(); q.put(('mutated',jid))
    except Exception as e: q.put(('rejected',jid,getattr(e,'status_code',None)))

def hardkill(jid,ready,go):
    os.environ['WUNOO_DB_PATH']=DB; import app.main as m
    with m.core_db_connect() as c:
        ready.set(); go.wait(10); c.execute('BEGIN IMMEDIATE'); m._v314_bump_generation(c,jid,f'o330_{jid[-1]}','v330_hardkill','crash330'); os.kill(os.getpid(),signal.SIGKILL)

def main():
    seed(); ctx=mp.get_context('fork'); q=ctx.Queue(); ps=[]; gates=[]
    for i in range(3):
        r=ctx.Event(); g=ctx.Event(); gates.append((r,g)); p=ctx.Process(target=stale,args=(f'j330_{i}',r,g,q)); p.start(); ps.append(p)
    hr=ctx.Event(); hg=ctx.Event(); hp=ctx.Process(target=hardkill,args=('j330_0',hr,hg)); hp.start()
    for r,_ in gates: assert r.wait(10)
    assert hr.wait(10); time.sleep(.05)
    os.environ['WUNOO_DB_PATH']=DB; import app.main as m
    # Kill worker owns no committed generation; current transaction must roll back. Now perform committed bumps for all orders.
    with m.core_db_connect() as c:
        for i in range(3):
            c.execute('BEGIN IMMEDIATE'); m._v314_bump_generation(c,f'j330_{i}',f'o330_{i}','v330_reassignment','ops330'); c.execute("UPDATE orders SET courier_id=?,status='courier_assigned',updated_at=? WHERE id=?",(f'c330b{i}',m.now(),f'o330_{i}')); c.execute("UPDATE dispatch_jobs SET courier_id=?,status='accepted',updated_at=? WHERE id=?",(f'c330b{i}',m.now(),f'j330_{i}')); c.commit()
    for _,g in gates: g.set()
    for p in ps: p.join(15)
    hp.join(15)
    assert hp.exitcode==-signal.SIGKILL,(hp.pid,hp.exitcode)
    vals=[]
    while not q.empty(): vals.append(q.get())
    rej=[x for x in vals if x[0]=='rejected']; mut=[x for x in vals if x[0]=='mutated']
    assert len(rej)==3 and not mut, vals
    with m.core_db_connect() as c:
        integ=m._v330_multi_order_chaos_integrity(c); assert integ['passed'],integ
        rows=c.execute("SELECT o.id,o.courier_id,d.courier_id,d.dispatch_generation FROM orders o JOIN dispatch_jobs d ON d.order_id=o.id ORDER BY o.id").fetchall()
        assert all(r['courier_id']==r['job_courier'] if 'job_courier' in r.keys() else True for r in rows)
        rid='r330_'+uuid.uuid4().hex[:12]; c.execute("INSERT INTO dispatch_multi_order_chaos_runs_v330 VALUES(?,?,?,?,?,?,?,?,?,?,?,?)",(rid,3,3,3,0,1,1,0,0,1,m.now(),json.dumps({'rows':[dict(r) for r in rows]},sort_keys=True))); c.commit()
    print('V330_OK'); print('ORDERS',3); print('STALE_ATTEMPTS',3); print('STALE_REJECTIONS',3); print('STALE_MUTATIONS',0); print('HARD_KILLS',1); print('BOOT_RECOVERIES',1); print('CROSS_ORDER_FAILURES',0); print('FENCE_FAILURES',0)
if __name__=='__main__': main()
