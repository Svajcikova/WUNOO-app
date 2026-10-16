import os,tempfile
os.environ['WUNOO_DB_PATH']=os.path.join(tempfile.gettempdir(),'wunoo_v315_test.db')
try: os.remove(os.environ['WUNOO_DB_PATH'])
except FileNotFoundError: pass
from app.main import init_db, core_db_connect, migrate_v061, migrate_v314, migrate_v315, _v314_bump_generation, _v314_require_generation
init_db()
with core_db_connect() as c:
    migrate_v061(c); migrate_v314(c); migrate_v315(c)
    c.execute("INSERT INTO dispatch_jobs (id,order_id,merchant_id,status,pickup_eta_minutes,delivery_eta_minutes,offered_at,created_at,updated_at) VALUES (?,?,?,?,?,?,?,?,?)",('dj_test','o_test','m_test','offered',5,25,'2026-01-01T00:00:00','2026-01-01T00:00:00','2026-01-01T00:00:00'))
    c.commit()
    assert _v314_require_generation(c,'dj_test','1') == 1
    assert _v314_bump_generation(c,'dj_test','o_test','redispatch','ops') == 2
    try: _v314_require_generation(c,'dj_test','1'); raise AssertionError('stale generation accepted')
    except Exception as e: assert getattr(e,'status_code',None)==409
    assert _v314_require_generation(c,'dj_test','2') == 2
    row=c.execute("SELECT dispatch_generation FROM dispatch_jobs WHERE id='dj_test'").fetchone(); assert row[0]==2
    audit=c.execute("SELECT reason,previous_generation,new_generation FROM dispatch_fence_audit_v314 WHERE dispatch_job_id='dj_test'").fetchone(); assert tuple(audit)==('redispatch',1,2)
print('V315_OK')
