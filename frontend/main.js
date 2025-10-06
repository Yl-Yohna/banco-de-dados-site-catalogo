const API_BASE = 'http://127.0.0.1:8000';

async function fetchProducts() {
  const res = await fetch(`${API_BASE}/products`);
  const data = await res.json();
  const container = document.getElementById('products');
  if (!data || data.length === 0) {
    container.innerHTML = '<div>Nenhum produto encontrado.</div>';
    return;
  }
  container.innerHTML = '';
  data.forEach(p => {
    const el = document.createElement('div');
    el.className = 'product';
    el.innerHTML = `<strong>${p.name}</strong> — R$${(p.price_cents/100).toFixed(2)}<br>${p.description || ''}<br><em>Estoque: ${p.stock} | Categoria: ${p.category || '-'}</em>`;
    container.appendChild(el);
  });
}

async function createProduct() {
  const name = document.getElementById('name').value;
  const description = document.getElementById('description').value;
  const price = parseFloat(document.getElementById('price').value || '0');
  const sku = document.getElementById('sku').value || undefined;
  const stock = parseInt(document.getElementById('stock').value || '0', 10);
  const category = document.getElementById('category').value || undefined;

  const payload = {
    name,
    description,
    price_cents: Math.round(price * 100),
    sku,
    stock,
    category
  };

  const status = document.getElementById('status');
  status.textContent = 'Enviando...';

  try {
    const res = await fetch(`${API_BASE}/products`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload) });
    if (!res.ok) {
      const err = await res.text();
      status.textContent = 'Erro: ' + err;
      return;
    }
    const data = await res.json();
    status.textContent = `Criado: ${data.name} (id=${data.id})`;
    fetchProducts();
  } catch (e) {
    status.textContent = 'Erro: ' + e.message;
  }
}

document.getElementById('createBtn').addEventListener('click', createProduct);
fetchProducts();
