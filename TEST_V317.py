import os,tempfile
os.environ['WUNOO_DB_PATH']=os.path.join(tempfile.gettempdir(),'wunoo_v317_test.db')
try: os.remove(os.environ['WUNOO_DB_PATH'])
except FileNotFoundError: pass
from app.main import init_db, core_db_connect, migrate_v061, migrate_v314, migrate_v315, migrate_v316, _v314_bump_generation, _v314_require_generation, _V317_POLICY
init_db()
with core_db_connect() as c:
    migrate_v061(c); migrate_v314(c); migrate_v315(c); migrate_v316(c)
    c.execute("INSERT INTO dispatch_jobs (id,order_id,merchant_id,status,pickup_eta_minutes,delivery_eta_minutes,offered_at,created_at,updated_at) VALUES (?,?,?,?,?,?,?,?,?)",('dj317','o317','m317','accepted',5,25,'2026-01-01T00:00:00','2026-01-01T00:00:00','2026-01-01T00:00:00'))
    c.commit()
with core_db_connect() as c:
    expected=_v314_require_generation(c,'dj317','1')
    # Simulate the exact race window: generation changes after the pre-lock check
    # but before the lifecycle mutation reaches its post-lock validation.
    _v314_bump_generation(c,'dj317','o317','redispatch','ops317')
    c.commit()
with core_db_connect() as c:
    try:
        _v314_require_generation(c,'dj317',str(expected))
        raise AssertionError('stale generation survived post-lock-equivalent recheck')
    except Exception as e:
        assert getattr(e,'status_code',None)==409
    cur=c.execute("UPDATE dispatch_jobs SET status='delivered' WHERE id=? AND dispatch_generation=?",('dj317',str(expected)))
    assert cur.rowcount==0
    row=c.execute("SELECT status,dispatch_generation FROM dispatch_jobs WHERE id='dj317'").fetchone()
    assert tuple(row)==('accepted',2),tuple(row)
print('V317_OK')
