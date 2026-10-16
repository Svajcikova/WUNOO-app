import os,tempfile,threading,time,sqlite3
os.environ['WUNOO_DB_PATH']=os.path.join(tempfile.gettempdir(),'wunoo_v316_test.db')
try: os.remove(os.environ['WUNOO_DB_PATH'])
except FileNotFoundError: pass
from app.main import init_db, core_db_connect, migrate_v061, migrate_v314, migrate_v315, migrate_v316, _v314_bump_generation, _v314_require_generation
init_db()
with core_db_connect() as c:
    migrate_v061(c); migrate_v314(c); migrate_v315(c); migrate_v316(c)
    c.execute("INSERT INTO dispatch_jobs (id,order_id,merchant_id,status,pickup_eta_minutes,delivery_eta_minutes,offered_at,created_at,updated_at) VALUES (?,?,?,?,?,?,?,?,?)",('dj316','o316','m316','accepted',5,25,'2026-01-01T00:00:00','2026-01-01T00:00:00','2026-01-01T00:00:00'))
    c.commit()

# Worker A fences the job; worker B holds a stale snapshot and must not mutate it.
barrier=threading.Barrier(2)
results=[]
def worker_a():
    with core_db_connect() as c:
        barrier.wait(); _v314_bump_generation(c,'dj316','o316','operator_reassignment','ops316'); c.commit(); results.append(('fence',2))
def worker_b():
    with core_db_connect() as c:
        snap=int(c.execute("SELECT dispatch_generation FROM dispatch_jobs WHERE id='dj316'").fetchone()[0])
        barrier.wait(); time.sleep(0.05)
        row=c.execute("SELECT dispatch_generation FROM dispatch_jobs WHERE id='dj316'").fetchone()
        actual=int(row[0])
        assert actual != snap, (snap,actual)
        try: _v314_require_generation(c,'dj316',str(snap)); raise AssertionError('stale generation accepted')
        except Exception as e: assert getattr(e,'status_code',None)==409
        # stale conditional mutation must affect zero rows
        cur=c.execute("UPDATE dispatch_jobs SET status='delivered' WHERE id=? AND dispatch_generation=?",('dj316',snap))
        assert cur.rowcount==0
        results.append(('stale_rejected',snap,actual))
threads=[threading.Thread(target=worker_a),threading.Thread(target=worker_b)]
[t.start() for t in threads]; [t.join() for t in threads]
with core_db_connect() as c:
    row=c.execute("SELECT status,dispatch_generation FROM dispatch_jobs WHERE id='dj316'").fetchone()
    assert tuple(row)==('accepted',2), tuple(row)
    audits=c.execute("SELECT reason,previous_generation,new_generation FROM dispatch_fence_audit_v314 WHERE dispatch_job_id='dj316'").fetchall()
    assert any(tuple(a)==('operator_reassignment',1,2) for a in audits)
print('V316_OK')
