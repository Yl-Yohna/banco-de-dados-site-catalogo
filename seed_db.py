"""Insere alguns produtos e categorias de exemplo no DB."""
from pathlib import Path
import catalog_db


def main():
    # categorias
    cat_elec = catalog_db.add_category("Eletrônicos")
    cat_roupa = catalog_db.add_category("Roupas")

    # produtos
    catalog_db.add_product(
        name="Smartphone Exemplo",
        description="Um smartphone com recursos básicos",
        price_cents=99900,
        sku="SMPL-001",
        stock=10,
        category_id=cat_elec,
    )

    catalog_db.add_product(
        name="Camiseta Básica",
        description="Camiseta 100% algodão",
        price_cents=2999,
        sku="TSH-001",
        stock=50,
        category_id=cat_roupa,
    )

    print("Semente inserida com sucesso.")


if __name__ == "__main__":
    main()
