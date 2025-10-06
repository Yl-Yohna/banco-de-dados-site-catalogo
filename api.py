from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pathlib import Path
from pydantic import BaseModel
import jwt
import os
from datetime import datetime, timedelta
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional, List
import catalog_db
from fastapi import UploadFile, File
import os, uuid

app = FastAPI(title="Catálogo de Produtos")

# Authentication setup
JWT_SECRET = os.environ.get('JWT_SECRET', 'devsecret')
JWT_ALGORITHM = 'HS256'
JWT_EXP_MINUTES = int(os.environ.get('JWT_EXP_MINUTES', '60'))
security = HTTPBearer()

def create_token(subject: str) -> str:
    now = datetime.utcnow()
    payload = {
        'sub': subject,
        'iat': now,
        'exp': now + timedelta(minutes=JWT_EXP_MINUTES)
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

def verify_token(creds: HTTPAuthorizationCredentials = Depends(security)):
    token = creds.credentials
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
    except Exception as e:
        raise HTTPException(status_code=401, detail='Token inválido')
    return payload.get('sub')

# Habilita CORS para permitir que seu front-end local consuma a API durante desenvolvimento.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # em produção restrinja para os domínios do seu front-end
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve arquivos estáticos do front-build se a pasta existir.
# Ajuste FRONT_DIR se necessário (pasta informada pelo usuário).
FRONT_DIR = Path(r"C:\Users\ylcay\OneDrive\Documentos\site-catalogo-main\build")
LOCAL_FRONT = Path(__file__).parent / "frontend"

# opcionalmente monta /static se existir em qualquer uma das pastas
if (FRONT_DIR / "static").exists():
    app.mount("/static", StaticFiles(directory=str(FRONT_DIR / "static")), name="static")
elif (LOCAL_FRONT / "static").exists():
    app.mount("/static", StaticFiles(directory=str(LOCAL_FRONT / "static")), name="static")

# uploads directory for images (served statically at /uploads)
UPLOAD_DIR = Path(__file__).parent / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)
app.mount("/uploads", StaticFiles(directory=str(UPLOAD_DIR)), name="uploads")


def _find_file_in_frontends(path: str) -> Optional[Path]:
    # procura pelo arquivo solicitado nas duas pastas (build primeiro)
    candidates = [FRONT_DIR, LOCAL_FRONT]
    for base in candidates:
        if not base.exists():
            continue
        p = base / path
        if p.exists() and p.is_file():
            return p
        # também tenta dentro de 'static' (CRA)
        p2 = base / "static" / path
        if p2.exists() and p2.is_file():
            return p2
    return None





class ProductIn(BaseModel):
    name: str
    description: Optional[str] = None
    price_cents: int
    sku: Optional[str] = None
    stock: int = 0
    category: Optional[str] = None
    image_url: Optional[str] = None


class ProductOut(ProductIn):
    id: int
    created_at: str
    updated_at: str
    category: Optional[str] = None
    image_url: Optional[str] = None


class ProductUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price_cents: Optional[int] = None
    sku: Optional[str] = None
    stock: Optional[int] = None
    category: Optional[str] = None
    image_url: Optional[str] = None


@app.on_event("startup")
def startup():
    # garante que o DB e schema existam
    catalog_db.get_connection().close()


@app.get("/products", response_model=List[ProductOut])
def api_list_products(limit: int = 100):
    prods = catalog_db.list_products(limit=limit)
    return prods


@app.get("/products/{product_id}", response_model=ProductOut)
def api_get_product(product_id: int):
    p = catalog_db.get_product(product_id)
    if not p:
        raise HTTPException(status_code=404, detail="Produto não encontrado")
    return p


@app.post("/products", response_model=ProductOut, status_code=201)
def api_create_product(item: ProductIn, user=Depends(verify_token)):
    cat_id = None
    if item.category:
        cat_id = catalog_db.add_category(item.category)
    pid = catalog_db.add_product(
        name=item.name,
        description=item.description,
        price_cents=item.price_cents,
        sku=item.sku,
        stock=item.stock,
        category_id=cat_id,
        image_url=item.image_url,
    )
    p = catalog_db.get_product(pid)
    return p


@app.post('/upload-image')
def upload_image(file: UploadFile = File(...), user=Depends(verify_token)):
    # Basic validation
    if not file.content_type.startswith('image/'):
        raise HTTPException(status_code=400, detail='Tipo de arquivo inválido')
    ext = os.path.splitext(file.filename)[1] or '.jpg'
    filename = f"{uuid.uuid4().hex}{ext}"
    dest = UPLOAD_DIR / filename
    with open(dest, 'wb') as f:
        f.write(file.file.read())
    # Return the URL path relative to API host
    return {"url": f"/uploads/{filename}"}


@app.patch('/products/{product_id}', response_model=ProductOut)
def api_update_product(product_id: int, item: ProductUpdate, user=Depends(verify_token)):
    # allow partial updates; item may contain image_url
    data = item.dict(exclude_unset=True)
    # handle category -> category_id
    cat_id = None
    if 'category' in data and data.get('category'):
        cat_id = catalog_db.add_category(data['category'])
        data['category_id'] = cat_id
    # remove category key to avoid inserting raw name
    data.pop('category', None)
    success = catalog_db.update_product(product_id, **data)
    if not success:
        raise HTTPException(status_code=404, detail='Produto não encontrado ou nada para atualizar')
    p = catalog_db.get_product(product_id)
    return p


class LoginIn(BaseModel):
    username: str
    password: str


@app.post('/auth/login')
def auth_login(payload: LoginIn):
    admin_user = os.environ.get('ADMIN_USER', 'admin')
    admin_pass = os.environ.get('ADMIN_PASS', 'password')
    if payload.username == admin_user and payload.password == admin_pass:
        token = create_token(payload.username)
        return {'access_token': token}
    raise HTTPException(status_code=401, detail='Credenciais inválidas')


@app.get("/", include_in_schema=False)
def serve_index():
    # retorna index.html do primeiro frontend disponível
    for base in (FRONT_DIR, LOCAL_FRONT):
        idx = base / "index.html"
        if idx.exists():
            return FileResponse(idx)
    raise HTTPException(status_code=404, detail="Not Found")


@app.get("/{full_path:path}", include_in_schema=False)
def spa_fallback(full_path: str):
    # procura arquivo estático solicitado, senão retorna index.html para SPA
    f = _find_file_in_frontends(full_path)
    if f:
        return FileResponse(f)
    # fallback para index
    for base in (FRONT_DIR, LOCAL_FRONT):
        idx = base / "index.html"
        if idx.exists():
            return FileResponse(idx)
    raise HTTPException(status_code=404, detail="Not Found")
