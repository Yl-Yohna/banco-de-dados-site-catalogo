import json
import os
from pathlib import Path
import catalog_db

p = catalog_db.DB_PATH
print('DB:', p)
print('exists', p.exists())
if p.exists():
    print('size', os.path.getsize(p))
    prods = catalog_db.list_products(10)
    print('count', len(prods))
    print(json.dumps(prods, ensure_ascii=False, indent=2))
else:
    print('DB missing. Run create_db.py and seed_db.py')
