from pathlib import Path
import catalog_db

conn = catalog_db.get_connection()
cur = conn.cursor()
cur.execute("PRAGMA table_info(products)")
cols = [r[1] for r in cur.fetchall()]
if 'image_url' not in cols:
    cur.execute("ALTER TABLE products ADD COLUMN image_url TEXT")
    conn.commit()
    print('image_url column added')
else:
    print('image_url column already exists')
conn.close()
