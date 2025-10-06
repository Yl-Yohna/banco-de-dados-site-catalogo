from fastapi.testclient import TestClient
import api, io, base64, json

client = TestClient(api.app)
# tiny red PNG
red_png = base64.b64decode('iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR4nGNgYAAAAAMAASsJTYQAAAAASUVORK5CYII=')
files = {'file': ('red.png', io.BytesIO(red_png), 'image/png')}
r = client.post('/upload-image', files=files)
print('upload status', r.status_code, r.json())
url = r.json().get('url')

payload = {'name':'Produto com imagem','description':'Teste','price_cents':1000,'sku':'IMG-1','stock':1,'category':'Test','image_url':url}
r2 = client.post('/products', json=payload)
print('create status', r2.status_code)
print('product', json.dumps(r2.json(), ensure_ascii=False, indent=2))
