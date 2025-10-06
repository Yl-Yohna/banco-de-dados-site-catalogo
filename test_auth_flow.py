from fastapi.testclient import TestClient
import api, json

client = TestClient(api.app)

# Attempt to create product without auth -> should be 401
payload = {"name":"X","description":"d","price_cents":100,"sku":"TST-1","stock":1}
r = client.post('/products', json=payload)
print('create without token status', r.status_code)

# Login with default creds (admin/password)
r2 = client.post('/auth/login', json={'username':'admin','password':'password'})
print('login status', r2.status_code, r2.json())
if r2.status_code==200:
    token = r2.json()['access_token']
    headers = {'Authorization': f'Bearer {token}'}
    r3 = client.post('/products', json=payload, headers=headers)
    print('create with token status', r3.status_code)
    print('body', r3.json())
