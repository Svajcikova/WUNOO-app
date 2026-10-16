import ast
from pathlib import Path
p=Path('app/main.py')
t=ast.parse(p.read_text(encoding='utf-8'))
funcs={n.name:n for n in t.body if isinstance(n,ast.FunctionDef)}
body=ast.unparse(funcs['v041_order_promise'])
assert "o['courier_id'] == u.get('courier_id')" in body
assert 'isinstance(o, dict)' not in body
assert "o.get('courier_id') == u['id']" not in body
assert "o['customer_id'] == u['customer_id']" in body
assert "o['merchant_id'] == u['merchant_id']" in body
print('V369_V041_COURIER_PROMISE_SCOPE_PASS', {'courier_uses_courier_id':True,'sqlite_row_safe':True,'customer_scope_preserved':True,'merchant_scope_preserved':True})
