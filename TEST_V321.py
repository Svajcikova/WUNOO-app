import os, tempfile, sqlite3, threading, json
DB=os.path.join(tempfile.gettempdir(),'wunoo_v321_chaos.db')
try: os.remove(DB)
except FileNotFoundError: pass
os.environ['WUNOO_DB_PATH']=DB

from app.main import init_db, core_db_connect, migrate_v061, migrate_v314, migrate_v315, migrate_v316, migrate_v318, migrate_v319, migrate_v321, _v314_bump_generation, _v319_fence_integrity

init_db()
with core_db_connect() as c:
    for fn in (migrate_v061,migrate_v314,migrate_v315,migrate_v316,migrate_v318,migrate_v319,migrate_v321): fn(c)
    ts='2026-01-01T00:00:00'
    c.execute("INSERT INTO merchants(id,name,created_at) VALUES(?,?,?)",('m321','Merchant 321',ts))
    c.execute("INSERT INTO customers(id,name,email,created_at) VALUES(?,?,?,?)",('cust321','Customer 321','c321@example.test',ts))
    c.execute("INSERT INTO couriers(id,name,created_at) VALUES(?,?,?)",('c321a','Courier A',ts))
    c.execute("INSERT INTO orders(id,customer_id,merchant_id,status,subtotal_czk,service_fee_czk,delivery_fee_czk,total_czk,address,created_at,updated_at,courier_id) VALUES(?,?,?,?,?,?,?,?,?,?,?,?)",('o321','cust321','m321','courier_assigned',100,0,0,100,'Test address',ts,ts,'c321a'))
    c.execute("INSERT INTO dispatch_jobs(id,order_id,merchant_id,courier_id,status,pickup_eta_minutes,delivery_eta_minutes,offered_at,accepted_at,created_at,updated_at,dispatch_generation) VALUES(?,?,?,?,?,?,?,?,?,?,?,?)",('j321','o321','m321','c321a','accepted',5,25,ts,ts,ts,ts,1))
    c.commit()

ITER=32
STALE=4
stale_rejections=0
stale_mutations=0
current_mutations=0
lock=threading.Lock()

for iteration in range(ITER):
    with core_db_connect() as c:
        row=c.execute('SELECT dispatch_generation FROM dispatch_jobs WHERE id=?',('j321',)).fetchone()
        observed=int(row['dispatch_generation'])
    # Invalidate the captured snapshot before any stale worker is allowed to write.
    with core_db_connect() as c:
        c.execute('BEGIN IMMEDIATE')
        _v314_bump_generation(c,'j321','o321',f'chaos_iteration_{iteration}','chaos')
        c.commit()

    barrier=threading.Barrier(STALE+1)
    results=[]
    def stale_worker(idx):
        barrier.wait()
        try:
            with core_db_connect() as c:
                cur=c.execute("UPDATE dispatch_jobs SET updated_at=? WHERE id=? AND dispatch_generation=? AND status='accepted'",(f'2026-01-01T00:{iteration:02d}:00','j321',observed))
                if cur.rowcount:
                    c.commit(); results.append(('STALE_MUTATION',idx))
                else:
                    c.rollback(); results.append(('STALE_REJECTED',idx))
        except Exception as exc:
            results.append(('STALE_ERROR',idx,type(exc).__name__))
    threads=[threading.Thread(target=stale_worker,args=(i,)) for i in range(STALE)]
    for t in threads: t.start()
    barrier.wait()
    for t in threads: t.join(timeout=10)
    assert len(results)==STALE, (iteration,results)
    stale_rejections += sum(1 for r in results if r[0]=='STALE_REJECTED')
    stale_mutations += sum(1 for r in results if r[0]=='STALE_MUTATION')
    assert stale_mutations==0, (iteration,results)

    # A worker using the fresh generation must still be able to mutate.
    with core_db_connect() as c:
        fresh=int(c.execute('SELECT dispatch_generation FROM dispatch_jobs WHERE id=?',('j321',)).fetchone()['dispatch_generation'])
        cur=c.execute("UPDATE dispatch_jobs SET updated_at=? WHERE id=? AND dispatch_generation=? AND status='accepted'",(f'2026-01-01T00:{iteration:02d}:01','j321',fresh))
        assert cur.rowcount==1, (iteration,fresh,cur.rowcount)
        c.commit(); current_mutations += 1

with core_db_connect() as c:
    row=c.execute('SELECT dispatch_generation,status,courier_id FROM dispatch_jobs WHERE id=?',('j321',)).fetchone()
    assert int(row['dispatch_generation'])==ITER+1, tuple(row)
    assert tuple(row[1:])==('accepted','c321a'), tuple(row)
    integrity=_v319_fence_integrity(c)
    assert integrity['passed'], integrity
    audits=c.execute('SELECT previous_generation,new_generation FROM dispatch_fence_audit_v314 WHERE dispatch_job_id=? ORDER BY created_at,id',('j321',)).fetchall()
    assert len(audits)==ITER and all(int(a[1])==int(a[0])+1 for a in audits), len(audits)

print('V321_OK')
print('ITERATIONS',ITER)
print('STALE_ATTEMPTS',ITER*STALE)
print('STALE_REJECTIONS',stale_rejections)
print('STALE_MUTATIONS',stale_mutations)
print('CURRENT_MUTATIONS',current_mutations)
# Boot gate regression: a valid fence must permit readiness.
from app.main import _v271_boot_reconcile_dispatch
boot=_v271_boot_reconcile_dispatch()
assert boot.get('ready') is True, boot
print('BOOT_FENCE_GATE_OK')
