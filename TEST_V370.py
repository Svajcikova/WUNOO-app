from pathlib import Path
import importlib.util, os, tempfile
os.environ['WUNOO_DB_PATH']=str(Path(tempfile.mkdtemp())/'test.db')
spec=importlib.util.spec_from_file_location('wunoo','app/main.py')
m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
m.init_db()
with m.core_db_connect() as c:
    u=c.execute('SELECT * FROM users WHERE role=? LIMIT 1',('customer',)).fetchone()
    repo=m.V134AuthRepository(c)
    token,_=repo.create_session(u['id']); c.commit()
    out=m.v134_auth_me('Bearer '+token)
    assert out['user']['id']==u['id']
    assert 'password_hash' not in out['user']
    assert 'session_expires_at' not in out['user']
    assert out['user']['role']==u['role']
print('V370_AUTH_ME_SECRET_FIELDS_GUARD_PASS', {'password_hash_exposed':False,'session_metadata_exposed':False})
