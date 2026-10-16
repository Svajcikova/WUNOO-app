from pathlib import Path
s=Path('app/main.py').read_text()
assert 'elif u["role"] == "courier":' in s
assert 'SELECT id, name, status, verified FROM couriers WHERE id=?' in s
assert 'SELECT id, name, status, verified, earnings_czk FROM couriers ORDER BY name' in s
print('V371_COURIER_DIRECTORY_PRIVACY_PASS')
