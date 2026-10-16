import os, tempfile, sqlite3, threading, time
DB=os.path.join(tempfile.gettempdir(),'wunoo_v320_chaos.db')
try: os.remove(DB)
except FileNotFoundError: pass
os.environ['WUNOO_DB_PATH']=DB

from app.main import init_db, core_db_connect, migrate_v061, migrate_v314, migrate_v315, migrate_v316, migrate_v318, migrate_v319, _v314_bump_generation, _v319_fence_integrity

init_db()
with core_db_connect() as c:
    for fn in (migrate_v061,migrate_v314,migrate_v315,migrate_v316,migrate_v318,migrate_v319): fn(c)
    ts='2026-01-01T00:00:00'
    c.execute("INSERT INTO merchants(id,name,created_at) VALUES(?,?,?)",('m320','Merchant 320',ts))
    c.execute("INSERT INTO customers(id,name,email,created_at) VALUES(?,?,?,?)",('cust320','Customer 320','c320@example.test',ts))
    c.execute("INSERT INTO couriers(id,name,created_at) VALUES(?,?,?)",('c320','Courier 320',ts))
    c.execute("INSERT INTO couriers(id,name,created_at) VALUES(?,?,?)",('c321','Courier 321',ts))
    c.execute("INSERT INTO orders(id,customer_id,merchant_id,status,subtotal_czk,service_fee_czk,delivery_fee_czk,total_czk,address,created_at,updated_at) VALUES(?,?,?,?,?,?,?,?,?,?,?)",('o320','cust320','m320','courier_assigned',100,0,0,100,'Test address',ts,ts))
    c.execute("UPDATE orders SET courier_id=? WHERE id=?",('c320','o320'))
    c.execute("INSERT INTO dispatch_jobs(id,order_id,merchant_id,courier_id,status,pickup_eta_minutes,delivery_eta_minutes,offered_at,accepted_at,created_at,updated_at,dispatch_generation) VALUES(?,?,?,?,?,?,?,?,?,?,?,?)",
              ('j320','o320','m320','c320','accepted',5,25,ts,ts,ts,ts,1))
    c.commit()

reassignment_done=threading.Event()
observed_generation_holder=[]
results=[]

def stale_worker():
    try:
        with core_db_connect() as c:
            row=c.execute('SELECT dispatch_generation FROM dispatch_jobs WHERE id=?',('j320',)).fetchone()
            observed_generation_holder.append(int(row['dispatch_generation']))
        reassignment_done.wait(timeout=5)
        with core_db_connect() as c:
            observed=observed_generation_holder[0]
            cur=c.execute("UPDATE dispatch_jobs SET status='picked_up',updated_at=? WHERE id=? AND dispatch_generation=? AND status='accepted'",('2026-01-01T00:01:00','j320',observed))
            if cur.rowcount:
                c.commit(); results.append(('STALE_MUTATION',cur.rowcount))
            else:
                c.rollback(); results.append(('STALE_REJECTED',0))
    except Exception as e:
        results.append(('STALE_ERROR',type(e).__name__))

def reassignment_worker():
    try:
        with core_db_connect() as c:
            c.execute('BEGIN IMMEDIATE')
            row=c.execute('SELECT dispatch_generation FROM dispatch_jobs WHERE id=?',('j320',)).fetchone()
            old=int(row['dispatch_generation'])
            _v314_bump_generation(c,'j320','o320','operator_reassignment','ops320')
            c.execute("UPDATE dispatch_jobs SET courier_id=?,status='accepted',updated_at=? WHERE id=?",('c321','2026-01-01T00:02:00','j320'))
            c.execute("UPDATE orders SET courier_id=?,status='courier_assigned',updated_at=? WHERE id=?",('c321','2026-01-01T00:02:00','o320'))
            c.commit(); results.append(('REASSIGNED',old+1))
        reassignment_done.set()
    except Exception as e:
        try: c.rollback()
        except Exception: pass
        reassignment_done.set()
        results.append(('REASSIGN_ERROR',type(e).__name__))

threads=[threading.Thread(target=stale_worker),threading.Thread(target=reassignment_worker)]
for t in threads: t.start()
for t in threads: t.join(timeout=10)

assert len(results)==2, results
assert any(x[0]=='REASSIGNED' for x in results), results
assert any(x[0]=='STALE_REJECTED' for x in results), results
assert not any(x[0]=='STALE_MUTATION' for x in results), results

with core_db_connect() as c:
    job=c.execute('SELECT status,courier_id,dispatch_generation FROM dispatch_jobs WHERE id=?',('j320',)).fetchone()
    order=c.execute('SELECT status,courier_id FROM orders WHERE id=?',('o320',)).fetchone()
    assert tuple(job)==('accepted','c321',2), tuple(job)
    assert tuple(order)==('courier_assigned','c321'), tuple(order)
    integrity=_v319_fence_integrity(c)
    assert integrity['passed'], integrity
    audit=c.execute('SELECT previous_generation,new_generation,reason FROM dispatch_fence_audit_v314 WHERE dispatch_job_id=? ORDER BY created_at,id',('j320',)).fetchall()
    assert len(audit)==1 and tuple(audit[0])==(1,2,'operator_reassignment'), [tuple(x) for x in audit]

print('V320_OK')
print('CHAOS_RESULTS',sorted(results))
