# Catálogo de Produtos (SQLite)

Pequeno conjunto de utilitários para criar e usar um banco de dados SQLite para um site de catálogo de produtos.

Arquivos principais:

- `data/catalog.db` - arquivo do banco (gerado pelo script)
- `schema.sql` - esquema do banco
- `create_db.py` - cria o DB e aplica o esquema
- `seed_db.py` - insere alguns produtos de exemplo
- `catalog_db.py` - módulo com funções para acessar o DB
- `list_products.py` - script de exemplo que lista produtos

Requisitos:

- Python 3.8+

Dependências para a API (opcional):

- `fastapi` - framework web
- `uvicorn` - ASGI server para rodar a aplicação
- `httpx` - cliente HTTP para testes
Como usar (PowerShell):

```powershell
python create_db.py
python seed_db.py
python list_products.py

# Para executar a API (instale as dependências primeiro):
python -m pip install -r requirements.txt
python -m uvicorn api:app --reload
```
Conectar seu front-end local
---------------------------

Se o seu front está rodando em `http://localhost:3000` (por exemplo), a API estará disponível em `http://127.0.0.1:8000` por padrão. Exemplo simples em JavaScript (fetch):

```javascript
// listar produtos
fetch('http://127.0.0.1:8000/products')
	.then(r => r.json())
	.then(data => console.log(data));

// criar produto
fetch('http://127.0.0.1:8000/products', {
	method: 'POST',
	headers: { 'Content-Type': 'application/json' },
	body: JSON.stringify({ name: 'Caneca', price_cents: 1999, stock: 10, category: 'Casa' })
}).then(r => r.json()).then(console.log);
```

Observação: CORS está habilitado com origins="*" para desenvolvimento; em produção, restrinja os domínios permitidos.

Rodando o front-end estático (exemplo)
------------------------------------

No diretório do projeto, rode um servidor HTTP simples para servir a pasta `frontend` (PowerShell):

```powershell
cd frontend
python -m http.server 3000
```

Então abra `http://127.0.0.1:3000` no navegador. O front apontará por padrão para `http://127.0.0.1:8000` — se seu backend estiver em outro host/porta, atualize `frontend/main.js` e a constante `API_BASE`.

Integrando seu front existente
-----------------------------

- Se seu front já está configurado, apenas aponte as chamadas para a API para `http://127.0.0.1:8000` durante desenvolvimento.
- Se o front usa um proxy (por exemplo `vite` ou `create-react-app`), configure o proxy para encaminhar `/api` para `http://127.0.0.1:8000` ou configure CORS no backend (já habilitado para dev).

