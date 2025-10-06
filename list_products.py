"""Lista produtos do catálogo (exemplo de uso do módulo)."""
import catalog_db


def main():
    prods = catalog_db.list_products()
    if not prods:
        print("Sem produtos. Rode 'create_db.py' e 'seed_db.py' primeiro.")
        return
    for p in prods:
        price = p['price_cents'] / 100
        print(f"[{p['id']}] {p['name']} - R${price:.2f} - Estoque: {p['stock']} - Categoria: {p.get('category')}")


if __name__ == "__main__":
    main()
