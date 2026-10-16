import os, tempfile, sqlite3, threading
os.environ['WUNOO_DB_PATH']=os.path.join(tempfile.gettempdir(),'wunoo_v313_test.db')
try: os.remove(os.environ['WUNOO_DB_PATH'])
except FileNotFoundError: pass
from app.main import migrate_v312, migrate_v313, core_db_connect, _V313_POLICY, init_db
assert _V313_POLICY['schema_version']=='1.313'
init_db()
with core_db_connect() as c:
    migrate_v312(c)
    migrate_v313(c)
    cols=[r[1] for r in c.execute("PRAGMA table_info(ai_dispatch_command_journal_v312)").fetchall()]
    assert 'request_key' in cols and 'status' in cols
print('V313_OK')
