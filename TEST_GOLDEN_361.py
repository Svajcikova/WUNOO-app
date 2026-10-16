import os,tempfile,sqlite3
DB=os.path.join(tempfile.gettempdir(),'wunoo_golden_361.db')
try: os.remove(DB)
except FileNotFoundError: pass
os.environ['WUNOO_DB_PATH']=DB
import app.main as m
m.init_db()
with m.core_db_connect() as c:
    m.migrate_v061(c); m.migrate_v120(c); m.migrate_v122(c); m.migrate_v314(c)
    c.commit()
now=m.now()
# seed canonical entities
with m.core_db_connect() as c:
    c.execute("INSERT INTO customers VALUES (?,?,?,?)",('cuG','Golden Customer','g@test',now))
    c.execute("INSERT INTO merchants VALUES (?,?,?,?,?,?,?)",('mG','Golden Merchant',15,1,49.834,18.292,now))
    c.execute("INSERT INTO couriers VALUES (?,?,?,?,?,?,?,?)",('cG','Golden Courier','online',49.834,18.292,1,0,now))
    c.execute("INSERT INTO orders(id,customer_id,merchant_id,status,subtotal_czk,service_fee_czk,delivery_fee_czk,total_czk,courier_id,address,delivery_distance_km,created_at,updated_at) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)",('oG','cuG','mG','payment_pending',80,10,10,100,None,'Golden St 1',1.0,now,now))
    c.execute("INSERT INTO payments VALUES (?,?,?,?,?,?)",('pG','oG','piG',100,'captured',now))
    c.commit()
# payment -> merchant pending
with m.core_db_connect() as c:
    m.transition(c,'oG','payment_pending','merchant_pending',{'id':'custG'},'payment_captured',{'amount_czk':100})
    c.commit()
# merchant accept -> ready -> dispatch assignment
with m.core_db_connect() as c:
    m.transition(c,'oG','merchant_pending','preparing',{'id':'merchG'},'merchant_accepted',{})
    m.transition(c,'oG','preparing','dispatch_pending',{'id':'merchG'},'merchant_ready',{})
    cur=c.execute("UPDATE orders SET courier_id='cG',status='courier_assigned',assigned_at=?,updated_at=? WHERE id='oG' AND status='dispatch_pending'",(m.now(),m.now()))
    assert cur.rowcount==1
    c.execute("INSERT INTO dispatch_jobs(id,order_id,merchant_id,courier_id,status,pickup_eta_minutes,delivery_eta_minutes,offered_at,accepted_at,created_at,updated_at,dispatch_generation) VALUES(?,?,?,?,?,?,?,?,?,?,?,?)",('djG','oG','mG','cG','accepted',5,25,now,now,now,now,1))
    c.commit()
# pickup/start/deliver using actual functions with controlled auth
old_user=m.current_user
m.current_user=lambda auth:{'id':'courierG','role':'courier','courier_id':'cG'}
assert m.pickup('oG',None)['status']=='picked_up'
assert m.start_delivery('oG',None)['status']=='out_for_delivery'
r=m.deliver('oG',None)
assert r['status']=='delivered'
# settlement idempotency is protected at deliver endpoint
with m.core_db_connect() as c:
    assert c.execute("SELECT COUNT(*) n FROM settlements WHERE order_id='oG'").fetchone()['n']==1
    assert c.execute("SELECT earnings_czk FROM couriers WHERE id='cG'").fetchone()['earnings_czk']==47.0
# refund as admin, should be net of courier payout
m.current_user=lambda auth:{'id':'adminG','role':'admin'}
rr=m.refund('oG',None)
assert rr['status']=='succeeded'
assert abs(float(rr['amount_czk'])-53.0)<1e-9, rr
# second refund must be blocked
try:
    m.refund('oG',None)
    raise AssertionError('double refund accepted')
except Exception as e:
    assert getattr(e,'status_code',None)==409 or 'nezbývá' in str(e)
# final accounting invariants
with m.core_db_connect() as c:
    o=c.execute("SELECT status FROM orders WHERE id='oG'").fetchone()['status']
    p=c.execute("SELECT status FROM payments WHERE order_id='oG'").fetchone()['status']
    s=c.execute("SELECT COUNT(*) n FROM settlements WHERE order_id='oG'").fetchone()['n']
    refs=c.execute("SELECT COUNT(*) n, COALESCE(SUM(amount_czk),0) a FROM refunds WHERE order_id='oG' AND status='succeeded'").fetchone()
    ev=c.execute("SELECT type,COUNT(*) n FROM events WHERE order_id='oG' GROUP BY type ORDER BY type").fetchall()
    assert o=='delivered' and p=='refunded' and s==1 and refs['n']==1 and abs(refs['a']-53.0)<1e-9
print('GOLDEN_ORDER_PASS')
print('STATUS',o)
print('SETTLEMENTS',s)
print('COURIER_EARNINGS',47.0)
print('REFUND',refs['a'])
print('EVENTS',[(x['type'],x['n']) for x in ev])
