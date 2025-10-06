"""Cria o arquivo SQLite para o catálogo aplicando o esquema em schema.sql"""
from pathlib import Path
import catalog_db

HERE = Path(__file__).parent
DB_FILE = HERE / "data" / "catalog.db"


def main():
    DB_FILE.parent.mkdir(parents=True, exist_ok=True)
    conn = catalog_db.get_connection()
    catalog_db.execute_sql_file(conn, str(HERE / "schema.sql"))
    conn.close()
    print(f"Banco criado/atualizado em: {DB_FILE}")


if __name__ == "__main__":
    main()
