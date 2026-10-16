import os, tempfile, multiprocessing as mp, time, signal, json
DB=os.path.join(tempfile.gettempdir(),'wunoo_v325_recovery_matrix.db')

MIGRATION_NAMES='migrate_v046 migrate_v052 migrate_v053 migrate_v061 migrate_v119 migrate_v120 migrate_v121 migrate_v122 migrate_v310 migrate_v311 migrate_v312 migrate_v313 migrate_v314 migrate_v315 migrate_v316 migrate_v318 migrate_v319 migrate_v321 migrate_v322 migrate_v323 migrate_v325'.split()

def seed(stage):
    try: os.remove(DB)
    except FileNotFoundError: pass
    os.environ['WUNOO_DB_PATH']=DB
    import app.main as m
    m.init_db()
    with m.core_db_connect() as c:
        for name in MIGRATION_NAMES: getattr(m,name)(c)
        ts='2026-01-01T00:00:00'
        c.execute("INSERT INTO merchants(id,name,created_at) VALUES(?,?,?)",('m325','M325',ts))
        c.execute("INSERT INTO customers(id,name,email,created_at) VALUES(?,?,?,?)",('cust325','C325','c325@example.test',ts))
        for cid in ('cA','cB'): c.execute("INSERT INTO couriers(id,name,status,created_at) VALUES(?,?,?,?)",(cid,cid,'online',ts))
        if stage in ('accept','reassign','redispatch'):
            order_status='dispatch_pending' if stage=='accept' else 'courier_assigned'; courier=None if stage=='accept' else 'cA'; job_status='offered' if stage=='accept' else 'accepted'; gen=1
        elif stage=='pickup':
            order_status='courier_assigned'; courier='cA'; job_status='accepted'; gen=1
        elif stage=='recovery':
            order_status='dispatch_pending'; courier=None; job_status='redispatched'; gen=2
        else: # deliver
            order_status='out_for_delivery'; courier='cA'; job_status='picked_up'; gen=1
        c.execute("INSERT INTO orders(id,customer_id,merchant_id,status,subtotal_czk,service_fee_czk,delivery_fee_czk,total_czk,address,created_at,updated_at,courier_id,assigned_at) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)",
                  ('o325','cust325','m325',order_status,100,0,0,100,'A',ts,ts,courier,ts if courier else None))
        c.execute("INSERT INTO dispatch_jobs(id,order_id,merchant_id,courier_id,status,pickup_eta_minutes,delivery_eta_minutes,offered_at,accepted_at,picked_up_at,created_at,updated_at,dispatch_generation) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)",
                  ('j325','o325','m325',courier,job_status,5,25,ts,ts if job_status in ('accepted','picked_up') else None,ts if job_status=='picked_up' else None,ts,ts,gen))
        if gen == 2:
            c.execute("INSERT INTO dispatch_fence_audit_v314 VALUES (?,?,?,?,?,?,?,?)",('a325_seed','j325','o325',1,2,'seed_generation','seed',ts))
        c.commit()

def crash_worker(db, stage, ready):
    os.environ['WUNOO_DB_PATH']=db
    import app.main as m
    try:
        with m.core_db_connect() as c:
            c.execute('BEGIN IMMEDIATE'); ready.set()
            ts='hardkill'
            if stage=='accept':
                c.execute("UPDATE dispatch_jobs SET courier_id='cA',status='accepted',accepted_at=?,updated_at=? WHERE id='j325'",(ts,ts))
                c.execute("UPDATE orders SET courier_id='cA',status='courier_assigned',assigned_at=?,updated_at=? WHERE id='o325'",(ts,ts))
            elif stage=='reassign':
                m._v314_bump_generation(c,'j325','o325','hardkill_reassignment','ops325')
                c.execute("UPDATE dispatch_jobs SET courier_id='cB',status='accepted',updated_at=? WHERE id='j325'",(ts,))
                c.execute("UPDATE orders SET courier_id='cB',status='courier_assigned',updated_at=? WHERE id='o325'",(ts,))
            elif stage=='pickup':
                c.execute("UPDATE dispatch_jobs SET status='picked_up',picked_up_at=?,updated_at=? WHERE id='j325'",(ts,ts))
                c.execute("UPDATE orders SET status='out_for_delivery',updated_at=? WHERE id='o325'",(ts,))
            elif stage=='redispatch':
                m._v314_bump_generation(c,'j325','o325','hardkill_redispatch','ops325')
                c.execute("UPDATE dispatch_jobs SET courier_id=NULL,status='redispatched',updated_at=? WHERE id='j325'",(ts,))
                c.execute("UPDATE orders SET courier_id=NULL,status='dispatch_pending',updated_at=? WHERE id='o325'",(ts,))
            elif stage=='recovery':
                m._v314_bump_generation(c,'j325','o325','hardkill_recovery_reopen','system:recovery')
                c.execute("UPDATE dispatch_jobs SET courier_id=NULL,status='offered',updated_at=? WHERE id='j325'",(ts,))
            elif stage=='deliver':
                c.execute("UPDATE dispatch_jobs SET status='delivered',delivered_at=?,updated_at=? WHERE id='j325'",(ts,ts))
                c.execute("UPDATE orders SET status='delivered',delivered_at=?,updated_at=? WHERE id='o325'",(ts,ts))
            else: raise ValueError(stage)
            time.sleep(2); c.commit()
    except Exception:
        pass

def boot_check():
    os.environ['WUNOO_DB_PATH']=DB
    import app.main as m
    # Simulate the actual post-restart order: canonical dispatch reconciliation,
    # then the v1.325 unified matrix gate.
    boot=m._v271_boot_reconcile_dispatch()
    assert boot.get('ready',False), boot
    with m.core_db_connect() as c:
        matrix=m._v325_recovery_matrix(c,record=True)
    assert matrix['passed'], matrix
    return matrix

def run(stage):
    seed(stage)
    import app.main as m
    with m.core_db_connect() as c:
        before=dict(c.execute("SELECT dispatch_generation,courier_id,status FROM dispatch_jobs WHERE id='j325'").fetchone())
        before_order=dict(c.execute("SELECT courier_id,status FROM orders WHERE id='o325'").fetchone())
    ctx=mp.get_context('fork'); ready=ctx.Event(); p=ctx.Process(target=crash_worker,args=(DB,stage,ready)); p.start()
    assert ready.wait(10),(stage,'worker not ready')
    time.sleep(.2); os.kill(p.pid,signal.SIGKILL); p.join(10)
    assert p.exitcode==-signal.SIGKILL,(stage,p.exitcode)
    matrix=boot_check()
    with m.core_db_connect() as c:
        after=dict(c.execute("SELECT dispatch_generation,courier_id,status FROM dispatch_jobs WHERE id='j325'").fetchone())
        after_order=dict(c.execute("SELECT courier_id,status FROM orders WHERE id='o325'").fetchone())
    assert before==after,(stage,before,after)
    assert before_order==after_order,(stage,before_order,after_order)
    return {'stage':stage,'rollback':True,'matrix_passed':matrix['passed'],'generation':after['dispatch_generation']}

def main():
    stages=['accept','reassign','pickup','redispatch','recovery','deliver']
    results=[run(s) for s in stages]
    print('V325_OK')
    print('HARD_KILL_POINTS',len(stages))
    print('ROLLBACK_VERIFIED',sum(r['rollback'] for r in results))
    print('POST_RESTART_BOOT_GATES',sum(r['matrix_passed'] for r in results))
    print('GENERATION_FENCE_OK',sum(r['matrix_passed'] for r in results))
    print('RESULTS',json.dumps(results,separators=(',',':')))

if __name__=='__main__': mp.freeze_support(); main()
