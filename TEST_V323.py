import os, tempfile, multiprocessing as mp, time, json
DB=os.path.join(tempfile.gettempdir(),'wunoo_v323_full_lifecycle.db')

def stale_pickup_worker(db, expected, ready, go, q):
    os.environ['WUNOO_DB_PATH']=db
    from app.main import core_db_connect
    try:
        with core_db_connect() as c:
            row=c.execute("SELECT dispatch_generation,status,courier_id FROM dispatch_jobs WHERE id=?",('j323',)).fetchone()
            if not row or int(row['dispatch_generation'])!=expected: q.put('SNAPSHOT_BAD'); return
        ready.set(); go.wait(10)
        with core_db_connect() as c:
            cur=c.execute("UPDATE dispatch_jobs SET status='picked_up',picked_up_at=?,updated_at=? WHERE id=? AND dispatch_generation=? AND status='accepted' AND courier_id='cA'",('stale','stale','j323',expected))
            if cur.rowcount:
                c.commit(); q.put('MUTATION')
            else:
                c.rollback(); q.put('REJECTED')
    except Exception as e: q.put('ERROR:'+type(e).__name__+':'+str(e))

def operator_worker(db, ready, go, q):
    os.environ['WUNOO_DB_PATH']=db
    from app.main import core_db_connect, _v311_operator_reassign
    ready.wait(10)
    try:
        actor={'id':'ops323','role':'ops_agent'}
        with core_db_connect() as c:
            r=_v311_operator_reassign(c,'o323','cB',actor,'chaos_reassignment')
            c.commit(); q.put('REASSIGNED:'+str(r['courier_id']))
        go.set()
    except Exception as e:
        q.put('ERROR:'+type(e).__name__+':'+str(e)); go.set()

def seed():
    try: os.remove(DB)
    except FileNotFoundError: pass
    os.environ['WUNOO_DB_PATH']=DB
    from app.main import init_db, core_db_connect, migrate_v046, migrate_v052, migrate_v053, migrate_v061, migrate_v119, migrate_v120, migrate_v121, migrate_v122, migrate_v310, migrate_v311, migrate_v312, migrate_v313, migrate_v314, migrate_v315, migrate_v316, migrate_v318, migrate_v319, migrate_v321, migrate_v322, migrate_v323
    init_db()
    with core_db_connect() as c:
        for fn in (migrate_v046,migrate_v052,migrate_v053,migrate_v061,migrate_v119,migrate_v120,migrate_v121,migrate_v122,migrate_v310,migrate_v311,migrate_v312,migrate_v313,migrate_v314,migrate_v315,migrate_v316,migrate_v318,migrate_v319,migrate_v321,migrate_v322,migrate_v323): fn(c)
        ts='2026-01-01T00:00:00'
        c.execute("INSERT INTO merchants(id,name,created_at) VALUES(?,?,?)",('m323','M323',ts))
        c.execute("INSERT INTO customers(id,name,email,created_at) VALUES(?,?,?,?)",('cust323','C323','c323@example.test',ts))
        for cid in ('cA','cB'):
            c.execute("INSERT INTO couriers(id,name,status,created_at) VALUES(?,?,?,?)",(cid,cid,'online',ts))
        c.execute("INSERT INTO orders(id,customer_id,merchant_id,status,subtotal_czk,service_fee_czk,delivery_fee_czk,total_czk,address,created_at,updated_at,courier_id,assigned_at) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)",('o323','cust323','m323','courier_assigned',100,0,0,100,'A',ts,ts,'cA',ts))
        c.execute("INSERT INTO dispatch_jobs(id,order_id,merchant_id,courier_id,status,pickup_eta_minutes,delivery_eta_minutes,offered_at,accepted_at,created_at,updated_at,dispatch_generation) VALUES(?,?,?,?,?,?,?,?,?,?,?,?)",('j323','o323','m323','cA','accepted',5,25,ts,ts,ts,ts,1))
        c.commit()

def main():
    seed()
    ctx=mp.get_context('fork'); ITER=6
    stale_rej=stale_mut=redispatches=reopens=completions=failures=0
    for i in range(ITER):
        # Every iteration starts from a clean accepted pair with the current generation.
        with __import__('app.main',fromlist=['core_db_connect']).core_db_connect() as c:
            row=c.execute("SELECT dispatch_generation FROM dispatch_jobs WHERE id=?",('j323',)).fetchone()
            expected=int(row['dispatch_generation'])
            # Start each round from the same canonical accepted lifecycle pair while
            # preserving the monotonic generation/audit history.
            c.execute("UPDATE orders SET status='courier_assigned',courier_id='cA',assigned_at=?,picked_up_at=NULL,updated_at=? WHERE id='o323'",(f'r{i}',f'r{i}'))
            c.execute("UPDATE dispatch_jobs SET status='accepted',courier_id='cA',updated_at=? WHERE id='j323'",(f'r{i}',))
            c.commit()
        ready=ctx.Event(); go=ctx.Event(); q=ctx.Queue()
        ps=[ctx.Process(target=stale_pickup_worker,args=(DB,expected,ready,go,q)),ctx.Process(target=operator_worker,args=(DB,ready,go,q))]
        for p in ps:p.start()
        for p in ps:p.join(15)
        vals=[q.get(timeout=3) for _ in ps]
        for p in ps: assert p.exitcode==0,(i,p.exitcode,vals)
        assert any(v.startswith('REASSIGNED:cB') for v in vals), (i,vals)
        assert vals.count('REJECTED')==1 and not any(v.startswith('MUTATION') or v.startswith('ERROR') for v in vals),(i,vals)
        stale_rej+=1
        # Complete current courier lifecycle on the reassigned job.
        os.environ['WUNOO_DB_PATH']=DB
        from app.main import core_db_connect, _v119_reassign_locked, _v310_materialize_job, _v319_fence_integrity
        actor={'id':'ops323','role':'ops_agent'}
        with core_db_connect() as c:
            j=c.execute("SELECT * FROM dispatch_jobs WHERE id='j323'").fetchone(); o=c.execute("SELECT * FROM orders WHERE id='o323'").fetchone()
            assert j['courier_id']=='cB' and j['status']=='accepted' and o['courier_id']=='cB' and o['status']=='courier_assigned',(i,dict(j),dict(o))
            # pickup -> out_for_delivery
            c.execute("UPDATE dispatch_jobs SET status='picked_up',picked_up_at='p',updated_at='p' WHERE id='j323' AND status='accepted' AND courier_id='cB'")
            c.execute("UPDATE orders SET status='out_for_delivery',picked_up_at='p',updated_at='p' WHERE id='o323' AND status='courier_assigned' AND courier_id='cB'")
            c.commit()
        # Redispatch from an active delivery state; this must bump generation and invalidate the job.
        with core_db_connect() as c:
            o=c.execute("SELECT * FROM orders WHERE id='o323'").fetchone()
            _v119_reassign_locked(c,o,actor,'chaos_redispatch')
            c.commit(); redispatches+=1
            j=c.execute("SELECT * FROM dispatch_jobs WHERE id='j323'").fetchone()
            assert j['status']=='redispatched' and j['courier_id'] is None
            rd_gen=int(j['dispatch_generation'])
        # Recovery/reopen to the new courier and materialize the canonical accepted job.
        with core_db_connect() as c:
            c.execute("UPDATE orders SET status='courier_assigned',courier_id='cB',assigned_at='r',updated_at='r' WHERE id='o323'")
            result=_v310_materialize_job(c,'o323','cB',None)
            c.commit(); reopens += 1
            assert result['invariant_ok']
            j=c.execute("SELECT * FROM dispatch_jobs WHERE id='j323'").fetchone()
            assert j['status']=='accepted' and j['courier_id']=='cB'
            # final pickup + delivery
            c.execute("UPDATE dispatch_jobs SET status='picked_up',picked_up_at='f',updated_at='f' WHERE id='j323' AND status='accepted' AND courier_id='cB'")
            c.execute("UPDATE orders SET status='out_for_delivery',picked_up_at='f',updated_at='f' WHERE id='o323' AND status='courier_assigned' AND courier_id='cB'")
            c.execute("UPDATE dispatch_jobs SET status='delivered',delivered_at='d',updated_at='d' WHERE id='j323' AND status='picked_up' AND courier_id='cB'")
            c.execute("UPDATE orders SET status='delivered',updated_at='d' WHERE id='o323' AND status='out_for_delivery' AND courier_id='cB'")
            c.commit(); completions += 1
            final=c.execute("SELECT o.status os,o.courier_id oc,d.status ds,d.courier_id dc,d.dispatch_generation g FROM orders o JOIN dispatch_jobs d ON d.order_id=o.id WHERE o.id='o323'").fetchone()
            integ=_v319_fence_integrity(c)
            assert tuple(final[:4])==('delivered','cB','delivered','cB') and int(final['g'])>=expected+3,(i,dict(final))
            assert integ['passed'], integ
    print('V323_OK')
    print('ITERATIONS',ITER); print('PROCESS_RACES',ITER); print('STALE_REJECTIONS',stale_rej); print('STALE_MUTATIONS',stale_mut); print('REDISPATCHES',redispatches); print('RECOVERY_REOPENS',reopens); print('LIFECYCLE_COMPLETIONS',completions); print('FAILURES',failures); print('FENCE_INTEGRITY_OK')

if __name__=='__main__': mp.freeze_support(); main()
