import os,tempfile
os.environ['WUNOO_DB_PATH']=os.path.join(tempfile.gettempdir(),'wunoo_v368_test.db')
try: os.remove(os.environ['WUNOO_DB_PATH'])
except FileNotFoundError: pass
import app.main as m
from fastapi import HTTPException
m.init_db()
with m.core_db_connect() as c:
    m.migrate_v061(c); m.migrate_v314(c)
    c.execute("INSERT INTO dispatch_jobs(id,order_id,merchant_id,courier_id,status,offered_at,created_at,updated_at,dispatch_generation) VALUES(?,?,?,?,?,?,?,?,?)",('ownjob','o-own','m1','courier-A','accepted','t','t','t',3))
    c.execute("INSERT INTO dispatch_jobs(id,order_id,merchant_id,courier_id,status,offered_at,created_at,updated_at,dispatch_generation) VALUES(?,?,?,?,?,?,?,?,?)",('foreignjob','o-foreign','m1','courier-B','accepted','t','t','t',7))
    c.commit()
orig=m.current_user
try:
    m.current_user=lambda auth: {'id':'uA','role':'courier','courier_id':'courier-A'}
    own=m.v314_generation('ownjob','x')
    assert own['order_id']=='o-own' and own['courier_id']=='courier-A' and own['dispatch_generation']==3
    try:
        m.v314_generation('foreignjob','x')
        raise AssertionError('foreign courier job was exposed')
    except HTTPException as e:
        assert e.status_code==404
    m.current_user=lambda auth: {'id':'admin1','role':'admin'}
    admin=m.v314_generation('foreignjob','x')
    assert admin['order_id']=='o-foreign' and admin['courier_id']=='courier-B'
finally:
    m.current_user=orig
print('V368_V314_COURIER_SCOPE_PASS')
