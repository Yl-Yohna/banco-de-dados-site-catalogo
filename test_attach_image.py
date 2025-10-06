from fastapi.testclient import TestClient
import api, io, base64, json

client = TestClient(api.app)
# tiny red PNG
red_png = base64.b64decode('iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR4nGNgYAAAAAMAASsJTYQAAAAASUVORK5CYII=')
files = {'file': ('red.png', io.BytesIO(red_png), 'image/png')}
r = client.post('/upload-image', files=files)
print('upload status', r.status_code, r.json())
url = r.json().get('url')
# update existing product id=1
payload = {'image_url': url}
r2 = client.patch('/products/1', json=payload)
print('patch status', r2.status_code)
print('product', json.dumps(r2.json(), ensure_ascii=False, indent=2))
