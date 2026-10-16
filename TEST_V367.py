import ast
from pathlib import Path

src=Path('app/main.py').read_text(encoding='utf-8')
tree=ast.parse(src)
func=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='v116_courier_queue')
body=ast.unparse(func)
assert "WHERE o.courier_id=?" in body
assert "o.status IN ('assigned','picked_up','out_for_delivery')" in body
assert "WHERE o.courier_id=? AND o.status IN ('dispatch_pending','assigned','picked_up','out_for_delivery')" not in body
print('V367_LEGACY_COURIER_QUEUE_IDOR_GUARD_PASS')
print({'dispatch_pending_enumeration_blocked':True,'assigned_orders_only':True})
