import os, tempfile, multiprocessing as mp

DB=os.path.join(tempfile.gettempdir(),'wunoo_v322_process.db')

def stale_worker(db, expected, q):
    os.environ['WUNOO_DB_PATH']=db
    from app.main import core_db_connect
    try:
        with core_db_connect() as c:
            cur=c.execute("UPDATE dispatch_jobs SET updated_at=? WHERE id=? AND dispatch_generation=? AND status='accepted'",('stale','j322',expected))
            if cur.rowcount:
                c.commit(); q.put('MUTATION')
            else:
                c.rollback(); q.put('REJECTED')
    except Exception as e:
        q.put('ERROR:'+type(e).__name__)

def current_worker(db, q):
    os.environ['WUNOO_DB_PATH']=db
    from app.main import core_db_connect
    try:
        with core_db_connect() as c:
            fresh=int(c.execute('SELECT dispatch_generation FROM dispatch_jobs WHERE id=?',('j322',)).fetchone()['dispatch_generation'])
            cur=c.execute("UPDATE dispatch_jobs SET updated_at=? WHERE id=? AND dispatch_generation=? AND status='accepted'",('fresh','j322',fresh))
            if cur.rowcount: c.commit(); q.put('CURRENT_OK')
            else: c.rollback(); q.put('CURRENT_FAIL')
    except Exception as e: q.put('CURRENT_ERROR:'+type(e).__name__)

def main():
    try: os.remove(DB)
    except FileNotFoundError: pass
    os.environ['WUNOO_DB_PATH']=DB
    from app.main import init_db, core_db_connect, migrate_v061, migrate_v314, migrate_v315, migrate_v316, migrate_v318, migrate_v319, migrate_v321, migrate_v322, _v314_bump_generation, _v319_fence_integrity
    init_db()
    with core_db_connect() as c:
        for fn in (migrate_v061,migrate_v314,migrate_v315,migrate_v316,migrate_v318,migrate_v319,migrate_v321,migrate_v322): fn(c)
        ts='2026-01-01T00:00:00'
        c.execute("INSERT INTO merchants(id,name,created_at) VALUES(?,?,?)",('m322','M322',ts))
        c.execute("INSERT INTO customers(id,name,email,created_at) VALUES(?,?,?,?)",('cust322','C322','c322@example.test',ts))
        c.execute("INSERT INTO couriers(id,name,created_at) VALUES(?,?,?)",('c322','Courier 322',ts))
        c.execute("INSERT INTO orders(id,customer_id,merchant_id,status,subtotal_czk,service_fee_czk,delivery_fee_czk,total_czk,address,created_at,updated_at,courier_id) VALUES(?,?,?,?,?,?,?,?,?,?,?,?)",('o322','cust322','m322','courier_assigned',100,0,0,100,'A',ts,ts,'c322'))
        c.execute("INSERT INTO dispatch_jobs(id,order_id,merchant_id,courier_id,status,pickup_eta_minutes,delivery_eta_minutes,offered_at,accepted_at,created_at,updated_at,dispatch_generation) VALUES(?,?,?,?,?,?,?,?,?,?,?,?)",('j322','o322','m322','c322','accepted',5,25,ts,ts,ts,ts,1))
        c.commit()
    ctx=mp.get_context('fork'); ITER=8; N=6
    rejected=mutations=errors=current_ok=0
    for i in range(ITER):
        with core_db_connect() as c:
            old=int(c.execute('SELECT dispatch_generation FROM dispatch_jobs WHERE id=?',('j322',)).fetchone()['dispatch_generation'])
            c.execute('BEGIN IMMEDIATE'); _v314_bump_generation(c,'j322','o322',f'process_chaos_{i}','chaos'); c.commit()
        q=ctx.Queue(); ps=[ctx.Process(target=stale_worker,args=(DB,old,q)) for _ in range(N)]
        for p in ps: p.start()
        for p in ps: p.join(10)
        for p in ps: assert p.exitcode==0, ('worker_exit',i,p.exitcode)
        vals=[q.get(timeout=3) for _ in ps]
        iter_rejected=vals.count('REJECTED'); iter_mutations=vals.count('MUTATION'); iter_errors=sum(v.startswith('ERROR:') for v in vals)
        rejected += iter_rejected; mutations += iter_mutations; errors += iter_errors
        assert iter_mutations==0 and iter_errors==0 and iter_rejected==N, (i,vals)
        q2=ctx.Queue(); p=ctx.Process(target=current_worker,args=(DB,q2)); p.start(); p.join(10); assert p.exitcode==0
        v=q2.get(timeout=3); assert v=='CURRENT_OK', (i,v); current_ok+=1
    with core_db_connect() as c:
        row=c.execute('SELECT dispatch_generation,status,courier_id FROM dispatch_jobs WHERE id=?',('j322',)).fetchone()
        assert int(row['dispatch_generation'])==ITER+1
        assert tuple(row[1:])==('accepted','c322')
        integrity=_v319_fence_integrity(c); assert integrity['passed'], integrity
        audits=c.execute('SELECT previous_generation,new_generation FROM dispatch_fence_audit_v314 WHERE dispatch_job_id=? ORDER BY created_at,id',('j322',)).fetchall()
        assert len(audits)==ITER and all(int(a[1])==int(a[0])+1 for a in audits)
    print('V322_OK'); print('ITERATIONS',ITER); print('PROCESSES_PER_ITERATION',N); print('STALE_ATTEMPTS',ITER*N); print('STALE_REJECTIONS',rejected); print('STALE_MUTATIONS',mutations); print('PROCESS_ERRORS',errors); print('CURRENT_MUTATIONS',current_ok); print('FENCE_INTEGRITY_OK')

if __name__ == '__main__':
    mp.freeze_support(); main()
