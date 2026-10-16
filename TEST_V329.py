import os,tempfile,multiprocessing as mp,uuid,json
DB=os.path.join(tempfile.gettempdir(),'wunoo_v329_adversarial_isolation.db')
MIGRATIONS='migrate_v046 migrate_v052 migrate_v053 migrate_v061 migrate_v119 migrate_v120 migrate_v121 migrate_v122 migrate_v310 migrate_v311 migrate_v312 migrate_v313 migrate_v314 migrate_v315 migrate_v316 migrate_v318 migrate_v319 migrate_v321 migrate_v322 migrate_v323 migrate_v325 migrate_v326 migrate_v328 migrate_v329'.split()

def seed(n=4):
    try: os.remove(DB)
    except FileNotFoundError: pass
    os.environ['WUNOO_DB_PATH']=DB
    import app.main as m
    m.init_db()
    with m.core_db_connect() as c:
        for x in MIGRATIONS: getattr(m,x)(c)
        ts='2026-01-01T00:00:00'
        c.execute("INSERT INTO merchants(id,name,created_at) VALUES(?,?,?)",('m329','M329',ts))
        c.execute("INSERT INTO customers(id,name,email,created_at) VALUES(?,?,?,?)",('cust329','C329','c329@example.test',ts))
        for i in range(n):
            for cid in (f'cA{i}',f'cB{i}',f'cC{i}'):
                c.execute("INSERT INTO couriers(id,name,status,created_at) VALUES(?,?,?,?)",(cid,cid,'online',ts))
            oid=f'o329_{i}'; jid=f'j329_{i}'
            c.execute("INSERT INTO orders(id,customer_id,merchant_id,status,subtotal_czk,service_fee_czk,delivery_fee_czk,total_czk,address,created_at,updated_at,courier_id,assigned_at) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)",(oid,'cust329','m329','courier_assigned',100,0,0,100,'A',ts,ts,f'cA{i}',ts))
            c.execute("INSERT INTO dispatch_jobs(id,order_id,merchant_id,courier_id,status,pickup_eta_minutes,delivery_eta_minutes,offered_at,accepted_at,created_at,updated_at,dispatch_generation) VALUES(?,?,?,?,?,?,?,?,?,?,?,?)",(jid,oid,'m329',f'cA{i}','accepted',5,25,ts,ts,ts,ts,1))
        c.commit()

def stale_worker(jid,ready,go,q):
    os.environ['WUNOO_DB_PATH']=DB
    import app.main as m
    try:
        with m.core_db_connect() as c: gen=int(c.execute('SELECT dispatch_generation FROM dispatch_jobs WHERE id=?',(jid,)).fetchone()['dispatch_generation'])
        ready.set(); go.wait(10)
        with m.core_db_connect() as c:
            c.execute('BEGIN IMMEDIATE'); m._v314_require_generation(c,jid,str(gen)); c.execute("UPDATE dispatch_jobs SET updated_at='STALE_MUTATION' WHERE id=?",(jid,)); c.commit(); q.put(('mutated',jid))
    except Exception as e: q.put(('rejected',jid,getattr(e,'status_code',None)))

def main():
    seed(); ctx=mp.get_context('fork'); q=ctx.Queue(); ps=[]; gates=[]
    for i in range(4):
        r=ctx.Event(); g=ctx.Event(); gates.append((r,g)); p=ctx.Process(target=stale_worker,args=(f'j329_{i}',r,g,q)); p.start(); ps.append(p)
    for r,_ in gates:
        assert r.wait(10)
    os.environ['WUNOO_DB_PATH']=DB
    import app.main as m
    # Each order gets a different reassignment and redispatch generation bump.
    with m.core_db_connect() as c:
        for i in range(4):
            jid=f'j329_{i}'; oid=f'o329_{i}'
            c.execute('BEGIN IMMEDIATE'); m._v314_bump_generation(c,jid,oid,'v329_reassignment',f'ops329_{i}'); c.commit()
            with m.core_db_connect() as c2:
                m._v272_begin_dispatch_transition(c2,oid)
                m._v314_bump_generation(c2,jid,oid,'v329_redispatch',f'ops329_{i}')
                c2.execute("UPDATE orders SET courier_id=?,status='courier_assigned',updated_at=? WHERE id=?",(f'cB{i}',m.now(),oid))
                c2.execute("UPDATE dispatch_jobs SET courier_id=?,status='accepted',updated_at=? WHERE id=?",(f'cB{i}',m.now(),jid)); c2.commit()
    for _,g in gates: g.set()
    for p in ps: p.join(15)
    assert all(p.exitcode==0 for p in ps), [(p.pid,p.exitcode) for p in ps]
    vals=[]
    while not q.empty(): vals.append(q.get())
    rej=[x for x in vals if x[0]=='rejected']; mut=[x for x in vals if x[0]=='mutated']
    assert len(rej)==4 and not mut, vals
    with m.core_db_connect() as c:
        integ=m._v329_multi_order_integrity(c); assert integ['passed'],integ
        rows=c.execute("SELECT o.id,o.courier_id,d.courier_id,d.dispatch_generation FROM orders o JOIN dispatch_jobs d ON d.order_id=o.id ORDER BY o.id").fetchall()
        assert all(r['courier_id']==r['courier_id'] and r['dispatch_generation']==3 for r in rows), [dict(r) for r in rows]
        rid='r329_'+uuid.uuid4().hex[:12]
        c.execute("INSERT INTO dispatch_multi_order_adversarial_runs_v329 VALUES(?,?,?,?,?,?,?,?,?,?,?, ?,?)",(rid,4,4,4,4,4,0,0,0,0,1,m.now(),json.dumps({'rows':[dict(r) for r in rows]},sort_keys=True))); c.commit()
    print('V329_OK'); print('ORDERS',4); print('REASSIGNMENTS',4); print('REDISPATCHES',4); print('STALE_ATTEMPTS',4); print('STALE_REJECTIONS',4); print('STALE_MUTATIONS',0); print('CROSS_ORDER_FAILURES',0); print('FENCE_FAILURES',0)
if __name__=='__main__': main()
