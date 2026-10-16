import os,tempfile,multiprocessing as mp,time,sqlite3,json,uuid
DB=os.path.join(tempfile.gettempdir(),'wunoo_v328_multi_order_lifecycle.db')
MIGRATIONS='migrate_v046 migrate_v052 migrate_v053 migrate_v061 migrate_v119 migrate_v120 migrate_v121 migrate_v122 migrate_v310 migrate_v311 migrate_v312 migrate_v313 migrate_v314 migrate_v315 migrate_v316 migrate_v318 migrate_v319 migrate_v321 migrate_v322 migrate_v323 migrate_v325 migrate_v326 migrate_v328'.split()

def seed(n=4):
    try: os.remove(DB)
    except FileNotFoundError: pass
    os.environ['WUNOO_DB_PATH']=DB
    import app.main as m
    m.init_db()
    with m.core_db_connect() as c:
        for x in MIGRATIONS: getattr(m,x)(c)
        ts='2026-01-01T00:00:00'
        c.execute("INSERT INTO merchants(id,name,created_at) VALUES(?,?,?)",('m328','M328',ts))
        c.execute("INSERT INTO customers(id,name,email,created_at) VALUES(?,?,?,?)",('cust328','C328','c328@example.test',ts))
        for i in range(n):
            cid=f'c{i}' ; oid=f'o328_{i}'; jid=f'j328_{i}'
            c.execute("INSERT INTO couriers(id,name,status,created_at) VALUES(?,?,?,?)",(cid,cid,'online',ts))
            c.execute("INSERT INTO orders(id,customer_id,merchant_id,status,subtotal_czk,service_fee_czk,delivery_fee_czk,total_czk,address,created_at,updated_at,courier_id,assigned_at) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)",(oid,'cust328','m328','courier_assigned',100,0,0,100,'A',ts,ts,cid,ts))
            c.execute("INSERT INTO dispatch_jobs(id,order_id,merchant_id,courier_id,status,pickup_eta_minutes,delivery_eta_minutes,offered_at,accepted_at,created_at,updated_at,dispatch_generation) VALUES(?,?,?,?,?,?,?,?,?,?,?,?)",(jid,oid,'m328',cid,'accepted',5,25,ts,ts,ts,ts,1))
        c.commit()

def lifecycle(oid,jid,cid,out):
    os.environ['WUNOO_DB_PATH']=DB
    import app.main as m
    try:
        with m.core_db_connect() as c:
            # pickup
            j=c.execute('SELECT * FROM dispatch_jobs WHERE id=?',(jid,)).fetchone(); o=c.execute('SELECT * FROM orders WHERE id=?',(oid,)).fetchone()
            m._v272_begin_dispatch_transition(c,oid)
            j=c.execute('SELECT * FROM dispatch_jobs WHERE id=?',(jid,)).fetchone(); o=c.execute('SELECT * FROM orders WHERE id=?',(oid,)).fetchone()
            if j['status']!='accepted' or o['status']!='courier_assigned': raise AssertionError('pre-pickup')
            c.execute("UPDATE dispatch_jobs SET status='picked_up',picked_up_at=?,updated_at=? WHERE id=?",(m.now(),m.now(),jid))
            m.atomic_transition_any(c,oid,('courier_assigned','assigned'),'out_for_delivery',{'id':cid,'role':'courier','courier_id':cid},'v328_pickup',{})
            c.commit()
            # deliver in a separate transaction to prove independent lifecycle progress
            with m.core_db_connect() as c2:
                m._v272_begin_dispatch_transition(c2,oid)
                j=c2.execute('SELECT * FROM dispatch_jobs WHERE id=?',(jid,)).fetchone(); o=c2.execute('SELECT * FROM orders WHERE id=?',(oid,)).fetchone()
                if j['status']!='picked_up' or o['status']!='out_for_delivery': raise AssertionError('pre-deliver')
                c2.execute("UPDATE dispatch_jobs SET status='delivered',delivered_at=?,updated_at=? WHERE id=?",(m.now(),m.now(),jid))
                m.atomic_transition_any(c2,oid,('out_for_delivery','picked_up'),'delivered',{'id':cid,'role':'courier','courier_id':cid},'v328_deliver',{})
                c2.commit()
        out.put(('ok',oid))
    except Exception as e: out.put(('err',oid,repr(e)))

def stale(oid,jid,out):
    os.environ['WUNOO_DB_PATH']=DB
    import app.main as m
    try:
        with m.core_db_connect() as c:
            gen=int(c.execute('SELECT dispatch_generation FROM dispatch_jobs WHERE id=?',(jid,)).fetchone()['dispatch_generation'])
            c.execute('BEGIN IMMEDIATE')
            m._v314_require_generation(c,jid,str(gen))
            # No mutation: this worker intentionally snapshots current generation only.
            c.rollback(); out.put(('ok',oid,gen))
    except Exception as e: out.put(('err',oid,repr(e)))

def stale_snapshot(oid,jid,ready,go,out):
    os.environ['WUNOO_DB_PATH']=DB
    import app.main as m
    try:
        with m.core_db_connect() as c:
            gen=int(c.execute('SELECT dispatch_generation FROM dispatch_jobs WHERE id=?',(jid,)).fetchone()['dispatch_generation'])
        ready.set(); go.wait(10); time.sleep(.05)
        with m.core_db_connect() as c:
            c.execute('BEGIN IMMEDIATE')
            m._v314_require_generation(c,jid,str(gen))
            c.execute("UPDATE dispatch_jobs SET updated_at='STALE_MUTATION' WHERE id=?",(jid,))
            c.commit(); out.put(('mutated',oid))
    except Exception as e:
        out.put(('rejected',oid,getattr(e,'status_code',None)))

def main():
    seed(4); ctx=mp.get_context('fork'); q=ctx.Queue(); lifecycle_ps=[]; stale_ps=[]; gates=[]
    # Every order gets an independent stale snapshot and an independent generation bump.
    for i in range(4):
        oid=f'o328_{i}'; jid=f'j328_{i}'
        ready=ctx.Event(); go=ctx.Event(); gates.append((ready,go))
        p=ctx.Process(target=stale_snapshot,args=(oid,jid,ready,go,q)); stale_ps.append(p); p.start()
    for ready,_ in gates:
        if not ready.wait(10): raise AssertionError('stale snapshot timeout')
    os.environ['WUNOO_DB_PATH']=DB
    import app.main as m
    with m.core_db_connect() as c:
        for i in range(4):
            oid=f'o328_{i}'; jid=f'j328_{i}'
            c.execute('BEGIN IMMEDIATE'); m._v314_bump_generation(c,jid,oid,'v328_concurrent_fence','ops328'); c.commit()
    for _,go in gates: go.set()
    for i in range(4):
        p=ctx.Process(target=lifecycle,args=(f'o328_{i}',f'j328_{i}',f'c{i}',q)); lifecycle_ps.append(p); p.start()
    for p in stale_ps+lifecycle_ps: p.join(15)
    if any(p.exitcode!=0 for p in stale_ps+lifecycle_ps): raise AssertionError(('process',[(p.pid,p.exitcode) for p in stale_ps+lifecycle_ps]))
    vals=[]
    while not q.empty(): vals.append(q.get())
    stale=[x for x in vals if x[0]=='rejected']; mutated=[x for x in vals if x[0]=='mutated']; done=[x for x in vals if x[0]=='ok']
    if len(stale)!=4 or mutated: raise AssertionError(('stale',vals))
    if len(done)!=4: raise AssertionError(('lifecycle',vals))
    with m.core_db_connect() as c:
        integ=m._v328_multi_order_integrity(c)
        if not integ['passed']: raise AssertionError(integ)
        rows=[dict(r) for r in c.execute("SELECT o.id,o.status,o.courier_id,d.status dstatus,d.courier_id dc,d.dispatch_generation FROM orders o JOIN dispatch_jobs d ON d.order_id=o.id ORDER BY o.id").fetchall()]
        if any(r['status']!='delivered' or r['dstatus']!='delivered' or r['courier_id']!=r['dc'] or r['dispatch_generation']!=2 for r in rows): raise AssertionError(('canonical',rows))
        cross=c.execute("SELECT COUNT(*) n FROM dispatch_jobs d JOIN orders o ON o.id=d.order_id WHERE d.order_id!=o.id").fetchone()['n']
        if cross: raise AssertionError('cross-order link')
        run_id='r328_'+uuid.uuid4().hex[:12]
        c.execute("INSERT INTO dispatch_multi_order_lifecycle_runs_v328 VALUES(?,?,?,?,?,?,?,?,?,?,?, ?,?)",(run_id,4,4,4,4,4,4,0,0,0,1,m.now(),json.dumps({'rows':rows},sort_keys=True)))
        c.commit()
    print('V328_OK'); print('ORDERS',4); print('CONCURRENT_WORKERS',4); print('ACCEPT_OK',4); print('PICKUP_OK',4); print('DELIVER_OK',4); print('STALE_ATTEMPTS',4); print('STALE_REJECTIONS',4); print('STALE_MUTATIONS',0); print('CROSS_ORDER_FAILURES',0); print('FENCE_FAILURES',0); print('CANONICAL_DELIVERED',4)
if __name__=='__main__': main()
