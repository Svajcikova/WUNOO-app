import ast
from pathlib import Path
p=Path('app/main.py')
t=ast.parse(p.read_text(encoding='utf-8'))
funcs={n.name:n for n in t.body if isinstance(n,ast.FunctionDef)}
for name in ('v042_dispatch_queue','v042_dispatch_priority'):
    body=ast.unparse(funcs[name])
    assert "require_role(u, 'admin', 'ops_agent')" in body
    assert "'courier'" not in body.split('require_role',1)[1].split('\n',1)[0]
print('V366_V042_DISPATCH_IDOR_GUARD_PASS', {'queue_control_plane_only':True,'priority_control_plane_only':True,'courier_blocked':True})
