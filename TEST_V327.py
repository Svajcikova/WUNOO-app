import os, tempfile, multiprocessing as mp, time, signal, json, sqlite3
DB=os.path.join(tempfile.gettempdir(),'wunoo_v327_multi_order.db')
MIGRATIONS='migrate_v046 migrate_v052 migrate_v053 migrate_v061 migrate_v119 migrate_v120 migrate_v121 migrate_v122 migrate_v310 migrate_v311 migrate_v312 migrate_v313 migrate_v314 migrate_v315 migrate_v316 migrate_v318 migrate_v319 migrate_v321 migrate_v322 migrate_v323 migrate_v325 migrate_v326'.split()

def seed():
    try: os.remove(DB)
    except FileNotFoundError: pass
    os.environ['WUNOO_DB_PATH']=DB
    import app.main as m
    m.init_db()
    with m.core_db_connect() as c:
        for n in MIGRATIONS: getattr(m,n)(c)
        ts='2026-01-01T00:00:00'
        c.execute("INSERT INTO merchants(id,name,created_at) VALUES(?,?,?)",('m327','M327',ts))
        c.execute("INSERT INTO customers(id,name,email,created_at) VALUES(?,?,?,?)",('cust327','C327','c327@example.test',ts))
        for cid in ('cA','cB','cC','cD'): c.execute("INSERT INTO couriers(id,name,status,created_at) VALUES(?,?,?,?)",(cid,cid,'online',ts))
        for i,cid in enumerate(('cA','cB','cC')):
            oid=f'o327_{i}'; jid=f'j327_{i}'
            c.execute("INSERT INTO orders(id,customer_id,merchant_id,status,subtotal_czk,service_fee_czk,delivery_fee_czk,total_czk,address,created_at,updated_at,courier_id,assigned_at) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)",(oid,'cust327','m327','courier_assigned',100+i,0,0,100+i,'A',ts,ts,cid,ts))
            c.execute("INSERT INTO dispatch_jobs(id,order_id,merchant_id,courier_id,status,pickup_eta_minutes,delivery_eta_minutes,offered_at,accepted_at,created_at,updated_at,dispatch_generation) VALUES(?,?,?,?,?,?,?,?,?,?,?,?)",(jid,oid,'m327',cid,'accepted',5,25,ts,ts,ts,ts,1))
        c.commit()

def stale_worker(order_id, job_id, barrier, result):
    os.environ['WUNOO_DB_PATH']=DB
    import app.main as m
    try:
        with m.core_db_connect() as c:
            gen=int(c.execute('SELECT dispatch_generation FROM dispatch_jobs WHERE id=?',(job_id,)).fetchone()['dispatch_generation'])
        time.sleep(1.5)
        with m.core_db_connect() as c:
            c.execute('BEGIN IMMEDIATE')
            try:
                m._v314_require_generation(c,job_id,str(gen))
                c.execute("UPDATE dispatch_jobs SET updated_at='STALE_MUTATION' WHERE id=?",(job_id,))
                c.commit(); result.put(('mutated',order_id,gen))
            except Exception as exc:
                c.rollback(); result.put(('rejected',order_id,gen,getattr(exc,'status_code',None)))
    except Exception as exc: result.put(('error',order_id,repr(exc)))

def bump_worker(order_id, job_id, new_courier, start, crash=False):
    os.environ['WUNOO_DB_PATH']=DB
    import app.main as m
    start.wait(10)
    with m.core_db_connect() as c:
        c.execute('BEGIN IMMEDIATE')
        m._v314_bump_generation(c,job_id,order_id,'multi_order_reassignment','ops327')
        c.execute("UPDATE dispatch_jobs SET courier_id=?,status='accepted',updated_at='reassigned' WHERE id=?",(new_courier,job_id))
        c.execute("UPDATE orders SET courier_id=?,status='courier_assigned',updated_at='reassigned' WHERE id=?",(new_courier,order_id))
        if crash:
            os.kill(os.getpid(),signal.SIGKILL)
        c.commit()

def boot_check():
    os.environ['WUNOO_DB_PATH']=DB
    import app.main as m
    b=m._v271_boot_reconcile_dispatch()
    if not b.get('ready'): raise AssertionError(('boot',b))
    with m.core_db_connect() as c:
        if not m._v325_recovery_matrix(c,record=True).get('passed'): raise AssertionError('matrix')
        if not m._v319_fence_integrity(c).get('passed'): raise AssertionError('fence')

def main():
    seed(); ctx=mp.get_context('fork'); result=ctx.Queue()
    specs=[('o327_0','j327_0','cD',False),('o327_1','j327_1','cD',True),('o327_2','j327_2','cD',False)]
    stale=[]
    for oid,jid,courier,crash in specs:
        workers=[]
        for _ in range(2):
            p=ctx.Process(target=stale_worker,args=(oid,jid,None,result)); workers.append(p); p.start()
        time.sleep(.3)
        # Capture generation in both workers, then mutate this order only.
        start=ctx.Event(); p=ctx.Process(target=bump_worker,args=(oid,jid,courier,start,crash)); p.start(); start.set(); p.join(10)
        if crash:
            if p.exitcode != -signal.SIGKILL: raise AssertionError(('crash',p.exitcode))
            boot_check()
            start2=ctx.Event(); p2=ctx.Process(target=bump_worker,args=(oid,jid,courier,start2,False)); p2.start(); start2.set(); p2.join(10)
            if p2.exitcode != 0: raise AssertionError(('recovery_bump',p2.exitcode))
        elif p.exitcode != 0: raise AssertionError(('bump',p.exitcode))
        stale.extend(workers)
    for p in stale: p.join(10)
    vals=[]
    while not result.empty(): vals.append(result.get())
    if len(vals)!=6 or any(v[0]!='rejected' for v in vals): raise AssertionError(('stale',vals))
    boot_check()
    os.environ['WUNOO_DB_PATH']=DB
    import app.main as m
    with m.core_db_connect() as c:
        rows=[dict(r) for r in c.execute("SELECT o.id,o.courier_id,o.status,d.courier_id dc,d.status ds,d.dispatch_generation FROM orders o JOIN dispatch_jobs d ON d.order_id=o.id ORDER BY o.id").fetchall()]
        bad=[r for r in rows if r['courier_id']!=r['dc'] or r['status']!='courier_assigned' or r['ds']!='accepted']
        if bad: raise AssertionError(('canonical',bad))
    print('V327_OK'); print('ORDERS',len(rows)); print('STALE_ATTEMPTS',len(vals)); print('STALE_REJECTIONS',len(vals)); print('STALE_MUTATIONS',0); print('HARD_KILLS',1); print('BOOT_GATES',2); print('CROSS_ORDER_ISOLATION_OK',3); print('RESULTS',json.dumps(rows,separators=(',',':')))
if __name__=='__main__': main()
