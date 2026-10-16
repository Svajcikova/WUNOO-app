"""v1.401 regression: settlement replay fails closed on corrupted current/legacy rows."""
import os, sys, tempfile, uuid
from pathlib import Path
from fastapi import HTTPException
ROOT = Path(__file__).resolve().parent
os.environ['WUNOO_DB_PATH'] = os.path.join(tempfile.gettempdir(), 'wunoo_v401_' + uuid.uuid4().hex + '.db')
sys.path.insert(0, str(ROOT))
from app import main

current = {'id':'set-1','status':'completed','gross_czk':100.0,'platform_fee_czk':18.0,
           'merchant_payout_czk':43.0,'courier_payout_czk':39.0,'delivery_fee_czk':39.0,
           'adjustment_czk':0.0,'net_czk':82.0}
assert main._v401_validate_settlement_replay(100, current, 'settlement_runs')['settlement_id'] == 'set-1'
legacy = {'id':'legacy-1','status':'reconciled','merchant_czk':43.0,'courier_czk':39.0,
          'platform_czk':18.0,'variance_czk':0.0}
assert main._v401_validate_settlement_replay(100, legacy, 'legacy_settlements')['source'] == 'legacy_settlements'

def reject(row, total=100, source='settlement_runs'):
    try:
        main._v401_validate_settlement_replay(total, row, source)
    except HTTPException as exc:
        assert exc.status_code == 409 and exc.detail['code'] == 'SETTLEMENT_LEDGER_INCONSISTENT', (exc.status_code, exc.detail)
    else:
        raise AssertionError(f'accepted inconsistent {source} replay: {row!r}')

for key, value in [('gross_czk', 99), ('platform_fee_czk', float('inf')),
                   ('merchant_payout_czk', -1), ('net_czk', 100), ('status', 'pending')]:
    row = dict(current); row[key] = value; reject(row)
row = dict(current); row['platform_fee_czk'] = True; reject(row)
for key, value in [('status','exception'), ('variance_czk',1.0), ('merchant_czk',float('nan')),
                   ('courier_czk',-1)]:
    row = dict(legacy); row[key] = value; reject(row, source='legacy_settlements')
row = dict(legacy); row['variance_czk'] = True; reject(row, source='legacy_settlements')
print('V401_SETTLEMENT_REPLAY_INTEGRITY_PASS current_valid=PASS legacy_valid=PASS corrupt_cases=11 rejected=409')
