import os,tempfile
os.environ['WUNOO_DB_PATH']=os.path.join(tempfile.gettempdir(),'wunoo_v314_test.db')
try: os.remove(os.environ['WUNOO_DB_PATH'])
except FileNotFoundError: pass
from app.main import init_db,core_db_connect,migrate_v061,migrate_v314,_V314_POLICY
assert _V314_POLICY['schema_version']=='1.314'
init_db()
with core_db_connect() as c:
    migrate_v061(c)
    migrate_v314(c)
    cols=[r[1] for r in c.execute('PRAGMA table_info(dispatch_jobs)').fetchall()]
    assert 'dispatch_generation' in cols
    c.execute("INSERT INTO dispatch_jobs(id,order_id,merchant_id,status,offered_at,created_at,updated_at,dispatch_generation) VALUES(?,?,?,?,?,?,?,?)",('j1','o1','m1','offered','t','t','t',1))
    g=c.execute('SELECT dispatch_generation FROM dispatch_jobs WHERE id=?',('j1',)).fetchone()[0]
    assert g==1
    from app.main import _v314_bump_generation
    ng=_v314_bump_generation(c,'j1','o1','test','a1')
    assert ng==2
    assert c.execute('SELECT dispatch_generation FROM dispatch_jobs WHERE id=?',('j1',)).fetchone()[0]==2
    assert c.execute('SELECT COUNT(*) FROM dispatch_fence_audit_v314').fetchone()[0]==1
print('V314_OK')
