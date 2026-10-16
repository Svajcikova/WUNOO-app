import os,tempfile,sqlite3
DB=os.path.join(tempfile.gettempdir(),'wunoo_v319_test.db')
try: os.remove(DB)
except FileNotFoundError: pass
os.environ['WUNOO_DB_PATH']=DB
from app.main import init_db, migrate_v061, migrate_v314, migrate_v318, migrate_v319, core_db_connect, _v319_fence_integrity, _v319_boot_fence_gate
init_db()
with core_db_connect() as c:
    migrate_v061(c); migrate_v314(c); migrate_v318(c); migrate_v319(c)
    c.execute("INSERT INTO dispatch_jobs(id,order_id,merchant_id,status,offered_at,created_at,updated_at,dispatch_generation) VALUES(?,?,?,?,datetime('now'),datetime('now'),datetime('now'),?)",('j1','o1','m1','offered',1))
    c.commit()
    assert _v319_fence_integrity(c)['passed']
    c.execute("UPDATE dispatch_jobs SET dispatch_generation=2 WHERE id='j1'")
    c.commit()
    assert not _v319_fence_integrity(c)['passed']
    c.execute("UPDATE dispatch_jobs SET dispatch_generation=1 WHERE id='j1'")
    c.execute("INSERT INTO dispatch_fence_audit_v314(id,dispatch_job_id,order_id,previous_generation,new_generation,reason,created_at) VALUES(?,?,?,?,?,?,datetime('now'))",('a1','j1','o1',1,2,'test'))
    c.commit()
    assert not _v319_fence_integrity(c)['passed']
    c.execute("UPDATE dispatch_jobs SET dispatch_generation=2 WHERE id='j1'")
    c.commit()
    assert _v319_fence_integrity(c)['passed']
print('V319_OK')
