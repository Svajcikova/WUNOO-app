import os, tempfile
os.environ['WUNOO_DB_PATH']=os.path.join(tempfile.gettempdir(),'wunoo_v318_test.db')
try: os.remove(os.environ['WUNOO_DB_PATH'])
except FileNotFoundError: pass
import app.main as m
m.init_db()
with m.core_db_connect() as c:
    m.migrate_v061(c); m.migrate_v314(c); m.migrate_v318(c)
    merchant=c.execute('SELECT id FROM merchants LIMIT 1').fetchone()['id']
    ts=m.now()
    c.execute("INSERT INTO dispatch_jobs (id,order_id,merchant_id,status,pickup_eta_minutes,delivery_eta_minutes,offered_at,created_at,updated_at) VALUES (?,?,?,?,?,?,?,?,?)",('j318','o318',merchant,'offered',5,25,ts,ts,ts))
    c.commit()
with m.core_db_connect() as c:
    assert m._v318_integrity(c)['passed']
    m._v314_bump_generation(c,'j318','o318','redispatch','ops318')
    m._v314_bump_generation(c,'j318','o318','recovery_reopen','ops318')
    c.commit()
with m.core_db_connect() as c:
    ok=m._v318_integrity(c); assert ok['passed'],ok
    row=c.execute("SELECT dispatch_generation FROM dispatch_jobs WHERE id='j318'").fetchone(); assert int(row['dispatch_generation'])==3
    c.execute("UPDATE dispatch_fence_audit_v314 SET previous_generation=99 WHERE dispatch_job_id='j318' AND new_generation=3"); c.commit()
with m.core_db_connect() as c:
    bad=m._v318_integrity(c); assert not bad['passed'],bad
    assert any(x['reason']=='audit_not_contiguous' for x in bad['failures'])
print('V318_OK')
