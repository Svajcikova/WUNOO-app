import os,sys,time,json,tempfile,subprocess,urllib.request,urllib.error
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
env=os.environ.copy()
env["WUNOO_ENV"]="development"
db=tempfile.NamedTemporaryFile(prefix="wunoo_rc41_",suffix=".db",delete=False);db.close()
env["WUNOO_DB_PATH"]=db.name
env["PYTHONPATH"]=str(ROOT.parent)+os.pathsep+env.get("PYTHONPATH","")
p=subprocess.Popen([sys.executable,"-m","uvicorn","app.main:app","--host","127.0.0.1","--port","8931"],
                   cwd=ROOT.parent,env=env,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
def get(path):
    try:
        with urllib.request.urlopen("http://127.0.0.1:8931"+path,timeout=2) as r:
            return r.status,r.read(200).decode(errors="replace")
    except urllib.error.HTTPError as e:return e.code,""
    except Exception:return None,""
result={"version":"1.00.0-rc41","production_target":False,"checks":[]}
try:
    ready=False
    for _ in range(24):
        time.sleep(.25)
        code,_=get("/api/health")
        if code is not None: ready=True; break
    result["checks"].append({"name":"health","status":code,"passed":code==200})
    if ready:
        oc,_=get("/openapi.json")
        result["checks"].append({"name":"openapi","status":oc,"passed":oc==200})
        hc,_=get("/api/health")
        result["checks"].append({"name":"repeat_health","status":hc,"passed":hc==200})
    else:
        result["checks"].append({"name":"runtime_ready","passed":False})
finally:
    p.terminate()
    try:p.wait(timeout=3)
    except:p.kill()
    try:os.unlink(db.name)
    except:pass
    result["production_db_touched"]=False
    result["overall"]="PASS" if result["checks"] and all(x.get("passed") for x in result["checks"]) else "BLOCKED"
    Path("RC41_BOOTSTRAP_SMOKE_RESULTS.json").write_text(json.dumps(result,indent=2))
