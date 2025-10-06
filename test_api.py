from fastapi.testclient import TestClient
import api
import catalog_db


client = TestClient(api.app)


def setup_module(module):
    # garante DB limpo para testes
    catalog_db.get_connection().close()


def test_list_products_empty_or_not_raises():
    # apenas chama o endpoint para garantir que responde
    r = client.get("/products")
    assert r.status_code == 200


def test_create_and_get_product():
    import uuid
    unique_sku = f"MUG-TEST-{uuid.uuid4().hex[:8]}"
    payload = {
        "name": "Teste Caneca",
        "description": "Caneca de cerâmica",
        "price_cents": 1999,
        "sku": unique_sku,
        "stock": 5,
        "category": "Casa"
    }
    r = client.post("/products", json=payload)
    assert r.status_code == 201
    data = r.json()
    assert data["name"] == payload["name"]
    pid = data["id"]

    r2 = client.get(f"/products/{pid}")
    assert r2.status_code == 200
    data2 = r2.json()
    assert data2["sku"] == payload["sku"]
