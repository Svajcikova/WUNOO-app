# WUNOO v1.401 Candidate

## Změny
- Endpoint `POST /api/v062/settlement/run` už při opakovaném požadavku slepě nepřebírá existující settlement.
- Záznam `settlement_runs` musí být ve stavu `completed`, mít konečné nezáporné částky, odpovídat ceně objednávky a matematicky sedět na provizi, výplatu restaurace, kurýra a případnou úpravu.
- Starší záznam `settlements` se vrací jako úspěšný pouze ve stavu `reconciled`, s konečnými částkami, nulovou tolerovanou odchylkou a součtem odpovídajícím ceně objednávky.
- Poškozená, čekající, záporná, nekonečná nebo matematicky nekonzistentní evidence skončí HTTP 409 `SETTLEMENT_LEDGER_INCONSISTENT`.
- Vytváření nového settlementu z v1.400 zůstává beze změny.

## Ověření
- `TEST_V401.py`: platné aktuální i legacy záznamy přijaty; 11 poškozených scénářů odmítnuto HTTP 409.
- Regresní testy V400, V399, V398, V397, V396, V395, V394, V393, V392, V391, V390, V389, V381, V382 a V362 prošly.
- Kompilace Pythonu a kontrola integrity ZIP archivu.

## Omezení
- Lokální ověření používá SQLite. PostgreSQL souběh, reálný poskytovatel plateb a produkční nasazení nejsou tímto kandidátem certifikovány.
- Neproveden push do GitHubu ani produkční nasazení.
