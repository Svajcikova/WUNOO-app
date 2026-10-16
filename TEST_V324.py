import os, tempfile, multiprocessing as mp, time, signal
DB=os.path.join(tempfile.gettempdir(),'wunoo_v324_hardkill.db')

def seed():
    try: os.remove(DB)
    except FileNotFoundError: pass
    os.environ['WUNOO_DB_PATH']=DB
    from app.main import init_db, core_db_connect, migrate_v046,migrate_v052,migrate_v053,migrate_v061,migrate_v119,migrate_v120,migrate_v121,migrate_v122,migrate_v310,migrate_v311,migrate_v312,migrate_v313,migrate_v314,migrate_v315,migrate_v316,migrate_v318,migrate_v319,migrate_v321,migrate_v322,migrate_v323
    init_db()
    with core_db_connect() as c:
        for fn in (migrate_v046,migrate_v052,migrate_v053,migrate_v061,migrate_v119,migrate_v120,migrate_v121,migrate_v122,migrate_v310,migrate_v311,migrate_v312,migrate_v313,migrate_v314,migrate_v315,migrate_v316,migrate_v318,migrate_v319,migrate_v321,migrate_v322,migrate_v323): fn(c)
        ts='2026-01-01T00:00:00'
        c.execute("INSERT INTO merchants(id,name,created_at) VALUES(?,?,?)",('m324','M324',ts))
        c.execute("INSERT INTO customers(id,name,email,created_at) VALUES(?,?,?,?)",('cust324','C324','c324@example.test',ts))
        for cid in ('cA','cB'): c.execute("INSERT INTO couriers(id,name,status,created_at) VALUES(?,?,?,?)",(cid,cid,'online',ts))
        c.execute("INSERT INTO orders(id,customer_id,merchant_id,status,subtotal_czk,service_fee_czk,delivery_fee_czk,total_czk,address,created_at,updated_at,courier_id,assigned_at) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)",('o324','cust324','m324','courier_assigned',100,0,0,100,'A',ts,ts,'cA',ts))
        c.execute("INSERT INTO dispatch_jobs(id,order_id,merchant_id,courier_id,status,pickup_eta_minutes,delivery_eta_minutes,offered_at,accepted_at,created_at,updated_at,dispatch_generation) VALUES(?,?,?,?,?,?,?,?,?,?,?,?)",('j324','o324','m324','cA','accepted',5,25,ts,ts,ts,ts,1))
        c.commit()

def crash_worker(db, mode, ready):
    os.environ['WUNOO_DB_PATH']=db
    from app.main import core_db_connect, _v314_bump_generation
    try:
        with core_db_connect() as c:
            c.execute('BEGIN IMMEDIATE')
            ready.set()
            if mode=='reassign':
                _v314_bump_generation(c,'j324','o324','hardkill_reassignment','ops324')
                c.execute("UPDATE dispatch_jobs SET courier_id='cB',status='accepted',updated_at='hk' WHERE id='j324'")
                c.execute("UPDATE orders SET courier_id='cB',status='courier_assigned',updated_at='hk' WHERE id='o324'")
            elif mode=='redispatch':
                _v314_bump_generation(c,'j324','o324','hardkill_redispatch','ops324')
                c.execute("UPDATE dispatch_jobs SET courier_id=NULL,status='redispatched',updated_at='hk' WHERE id='j324'")
                c.execute("UPDATE orders SET courier_id=NULL,status='dispatch_pending',updated_at='hk' WHERE id='o324'")
            else:
                raise ValueError(mode)
            time.sleep(30)
            c.commit()
    except Exception:
        pass

def run_crash(mode):
    os.environ['WUNOO_DB_PATH']=DB
    from app.main import core_db_connect
    with core_db_connect() as c:
        before=c.execute("SELECT dispatch_generation,courier_id,status FROM dispatch_jobs WHERE id='j324'").fetchone()
    ctx=mp.get_context('fork'); ready=ctx.Event(); p=ctx.Process(target=crash_worker,args=(DB,mode,ready)); p.start()
    assert ready.wait(10), (mode,'worker not ready')
    time.sleep(0.2)
    os.kill(p.pid, signal.SIGKILL); p.join(10)
    assert p.exitcode == -signal.SIGKILL, (mode,p.exitcode)
    # New connection must be able to acquire the DB and observe rollback.
    with core_db_connect() as c:
        after=c.execute("SELECT dispatch_generation,courier_id,status FROM dispatch_jobs WHERE id='j324'").fetchone()
        integ=__import__('app.main',fromlist=['_v319_fence_integrity'])._v319_fence_integrity(c)
    assert tuple(before)==tuple(after), (mode,dict(before),dict(after))
    assert integ['passed'], (mode,integ)
    return dict(before),dict(after)

def main():
    seed()
    r1=run_crash('reassign')
    r2=run_crash('redispatch')
    print('V324_OK')
    print('HARD_KILL_POINTS 2')
    print('ROLLBACK_VERIFIED 2')
    print('POST_RESTART_DB_UNLOCKED 2')
    print('GENERATION_ROLLBACK_OK 2')
    print('FENCE_INTEGRITY_OK')
    print('FINAL_STATE',r2[1])

if __name__=='__main__': mp.freeze_support(); main()
