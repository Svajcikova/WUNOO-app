import os, tempfile, multiprocessing as mp, time, signal, json
DB=os.path.join(tempfile.gettempdir(),'wunoo_v326_adversarial.db')
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
        c.execute("INSERT INTO merchants(id,name,created_at) VALUES(?,?,?)",('m326','M326',ts))
        c.execute("INSERT INTO customers(id,name,email,created_at) VALUES(?,?,?,?)",('cust326','C326','c326@example.test',ts))
        for cid in ('cA','cB'): c.execute("INSERT INTO couriers(id,name,status,created_at) VALUES(?,?,?,?)",(cid,cid,'online',ts))
        c.execute("INSERT INTO orders(id,customer_id,merchant_id,status,subtotal_czk,service_fee_czk,delivery_fee_czk,total_czk,address,created_at,updated_at,courier_id,assigned_at) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)",('o326','cust326','m326','courier_assigned',100,0,0,100,'A',ts,ts,'cA',ts))
        c.execute("INSERT INTO dispatch_jobs(id,order_id,merchant_id,courier_id,status,pickup_eta_minutes,delivery_eta_minutes,offered_at,accepted_at,created_at,updated_at,dispatch_generation) VALUES(?,?,?,?,?,?,?,?,?,?,?,?)",('j326','o326','m326','cA','accepted',5,25,ts,ts,ts,ts,1))
        c.commit()

def stale_worker(barrier, result):
    os.environ['WUNOO_DB_PATH']=DB
    import app.main as m
    try:
        with m.core_db_connect() as c:
            gen=int(c.execute("SELECT dispatch_generation FROM dispatch_jobs WHERE id='j326'").fetchone()['dispatch_generation'])
        barrier.wait(10)
        with m.core_db_connect() as c:
            c.execute('BEGIN IMMEDIATE')
            try:
                m._v314_require_generation(c,'j326',str(gen))
                # Deliberately mutate only if fence check passes; stale workers must never reach here.
                c.execute("UPDATE dispatch_jobs SET updated_at='stale_mutation' WHERE id='j326'")
                c.commit(); result.put(('mutated',gen))
            except Exception as exc:
                c.rollback()
                result.put(('rejected',gen,getattr(exc,'status_code',None)))
    except Exception as exc:
        result.put(('error',repr(exc)))

def reassign_worker(start, done):
    os.environ['WUNOO_DB_PATH']=DB
    import app.main as m
    start.wait(10)
    with m.core_db_connect() as c:
        c.execute('BEGIN IMMEDIATE')
        m._v314_bump_generation(c,'j326','o326','adversarial_reassignment','ops326')
        c.execute("UPDATE dispatch_jobs SET courier_id='cB',status='accepted',updated_at='reassigned' WHERE id='j326'")
        c.execute("UPDATE orders SET courier_id='cB',status='courier_assigned',updated_at='reassigned' WHERE id='o326'")
        c.commit()
    done.set()

def crash_worker(start, ready):
    os.environ['WUNOO_DB_PATH']=DB
    import app.main as m
    start.wait(10)
    with m.core_db_connect() as c:
        c.execute('BEGIN IMMEDIATE'); ready.set()
        m._v314_bump_generation(c,'j326','o326','hardkill_reassignment','ops326')
        c.execute("UPDATE dispatch_jobs SET courier_id='cB',status='accepted',updated_at='hardkill' WHERE id='j326'")
        c.execute("UPDATE orders SET courier_id='cB',status='courier_assigned',updated_at='hardkill' WHERE id='o326'")
        time.sleep(5)

def boot_check():
    os.environ['WUNOO_DB_PATH']=DB
    import app.main as m
    boot=m._v271_boot_reconcile_dispatch()
    if not boot.get('ready'): raise AssertionError(boot)
    with m.core_db_connect() as c:
        matrix=m._v325_recovery_matrix(c,record=True)
        fence=m._v319_fence_integrity(c)
    if not matrix.get('passed') or not fence.get('passed'): raise AssertionError((matrix,fence))
    return True

def one_iteration(i, do_crash):
    seed()
    ctx=mp.get_context('fork')
    barrier=ctx.Barrier(5); result=ctx.Queue(); done=ctx.Event(); start=ctx.Event(); ready=ctx.Event()
    stale=[ctx.Process(target=stale_worker,args=(barrier,result)) for _ in range(4)]
    for p in stale: p.start()
    # Wait until all stale workers have captured generation 1, then bump to 2.
    time.sleep(.4)
    if do_crash:
        cr=ctx.Process(target=crash_worker,args=(start,ready)); cr.start(); start.set()
        if not ready.wait(10): raise AssertionError('crash worker not ready')
        time.sleep(.25); os.kill(cr.pid,signal.SIGKILL); cr.join(10)
        if cr.exitcode != -signal.SIGKILL: raise AssertionError(('crash_exit',cr.exitcode))
        # stale workers may now run against rolled-back generation 1, so reset to a committed bump after boot.
        boot_check()
        with __import__('contextlib').closing(__import__('sqlite3').connect(DB)) as raw: pass
    else:
        rw=ctx.Process(target=reassign_worker,args=(start,done)); rw.start(); start.set(); rw.join(10)
        if rw.exitcode!=0: raise AssertionError(('reassign_exit',rw.exitcode))
    if do_crash:
        # The hard-killed transaction must roll back. After boot recovery, create
        # a committed generation bump before releasing the workers that captured
        # generation 1; only then are their commands genuinely stale.
        rw=ctx.Process(target=reassign_worker,args=(start,done)); rw.start(); start.set(); rw.join(10)
        if rw.exitcode!=0: raise AssertionError(('post_crash_reassign_exit',rw.exitcode))
    # release stale workers only after the concurrent mutation/crash path
    try: barrier.wait(10)
    except Exception: pass
    for p in stale: p.join(10)
    vals=[]
    while not result.empty(): vals.append(result.get())
    rej=sum(1 for v in vals if v[0]=='rejected')
    mut=sum(1 for v in vals if v[0]=='mutated')
    if rej!=4 or mut!=0: raise AssertionError(('stale_results',vals))
    boot_check()
    os.environ['WUNOO_DB_PATH']=DB
    import app.main as m
    with m.core_db_connect() as c:
        row=dict(c.execute("SELECT dispatch_generation,courier_id,status FROM dispatch_jobs WHERE id='j326'").fetchone())
        audit=int(c.execute("SELECT COUNT(*) n FROM dispatch_fence_audit_v314 WHERE dispatch_job_id='j326'").fetchone()['n'])
    return {'iteration':i,'crash':do_crash,'stale_results':vals,'generation':row['dispatch_generation'],'courier_id':row['courier_id'],'status':row['status'],'audit_rows':audit}

def main():
    results=[]
    for i in range(6):
        results.append(one_iteration(i, do_crash=(i%2==1)))
    stale_attempts=sum(4 for r in results)
    stale_rejections=sum(sum(1 for v in r['stale_results'] if v[0]=='rejected') for r in results)
    stale_mutations=sum(sum(1 for v in r['stale_results'] if v[0]=='mutated') for r in results)
    print('V326_OK')
    print('ITERATIONS',len(results))
    print('PROCESS_RACES',len(results)*4)
    print('STALE_ATTEMPTS',stale_attempts)
    print('STALE_REJECTIONS',stale_rejections)
    print('STALE_MUTATIONS',stale_mutations)
    print('HARD_KILLS',sum(1 for r in results if r['crash']))
    print('BOOT_GATES',len(results))
    print('FENCE_INTEGRITY_OK',len(results))
    print('RESULTS',json.dumps(results,separators=(',',':')))

if __name__=='__main__': mp.freeze_support(); main()
