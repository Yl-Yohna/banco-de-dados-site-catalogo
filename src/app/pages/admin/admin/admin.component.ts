import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatCardModule } from '@angular/material/card';
import { MatButtonModule } from '@angular/material/button';
import { MatButtonToggleModule } from '@angular/material/button-toggle';
import { HttpClientModule, HttpClient } from '@angular/common/http';
import { MatIconModule } from '@angular/material/icon';
import { FormsModule } from '@angular/forms';
import { MatInputModule } from '@angular/material/input';

@Component({
  selector: 'app-admin',
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    HttpClientModule,
    MatInputModule,
    MatCardModule,
    MatButtonModule,
    MatButtonToggleModule,
    MatIconModule,
  ],
  templateUrl: './admin.component.html',
  styleUrls: ['./admin.component.scss']
})
export class AdminComponent {
 categoriaSelecionada = 'todas';

  // form model
  name = '';
  description = '';
  price = 0;
  sku = '';
  stock = 0;
  category = '';
  file: File | null = null;
  imagePreview: string | null = null;

  API_BASE = 'http://127.0.0.1:8000';

  constructor(private http: HttpClient) {}

  ngOnInit(): void {
    this.loadProducts();
  }

  private mapBackendProduct(p: any) {
    return {
      id: p.id,
      nome: p.name,
      descricao: p.description,
      preco: (p.price_cents || 0) / 100,
      imagemUrl: p.image_url || p.imageUrl || p.image || null,
      categoria: p.category || null,
      raw: p,
    };
  }

  loadProducts() {
    this.http.get<any[]>(`${this.API_BASE}/products`).subscribe({
      next: (rows) => {
        this.produtos = rows.map(r => this.mapBackendProduct(r));
        this.produtosFiltrados = [...this.produtos];
      },
      error: (err) => console.error('Erro ao carregar produtos', err),
    });
  }

  produtos = [
    {
      id: 1,
      nome: 'Shampoo Brilho Intenso',
      descricao: 'Limpa suavemente e dá brilho ao cabelo',
      preco: 19.90,
      imagemUrl: 'https://via.placeholder.com/300x200',
      categoria: 'cabelo'
    },
    {
      id: 2,
      nome: 'Esmalte Vermelho Clássico',
      descricao: 'Cor vibrante e longa duração',
      preco: 9.99,
      imagemUrl: 'https://via.placeholder.com/300x200',
      categoria: 'unhas'
    },
    {
      id: 3,
      nome: 'Bolo de Cenoura com Cobertura',
      descricao: 'Fofinho e com muito chocolate',
      preco: 12.00,
      imagemUrl: 'https://via.placeholder.com/300x200',
      categoria: 'comida'
    }
  ];

  produtosFiltrados = [...this.produtos];

  onCategoriaChange(categoria: string) {
    this.categoriaSelecionada = categoria;

    if (categoria === 'todas') {
      this.produtosFiltrados = [...this.produtos];
    } else {
      this.produtosFiltrados = this.produtos.filter(p => p.categoria === categoria);
    }
  }

  editarProduto(produto: any) {
    console.log('Editar (simulado):', produto);
  }

  excluirProduto(id: number) {
    console.log('Excluir (simulado):', id);
  }

  onFileSelected(event: Event) {
    const input = event.target as HTMLInputElement;
    if (!input.files || input.files.length === 0) {
      this.file = null;
      this.imagePreview = null;
      return;
    }
    this.file = input.files[0];
    const reader = new FileReader();
    reader.onload = () => (this.imagePreview = reader.result as string);
    reader.readAsDataURL(this.file);
  }

  createProduct() {
    const payload: any = {
      name: this.name,
      description: this.description,
      price_cents: Math.round((this.price || 0) * 100),
      sku: this.sku,
      stock: this.stock,
      category: this.category,
    };

    const doCreate = (imageUrl?: string) => {
      if (imageUrl) payload.image_url = imageUrl;
      this.http.post(`${this.API_BASE}/products`, payload).subscribe({
        next: (res) => {
          console.log('Produto criado', res);
          // reset form
          this.name = '';
          this.description = '';
          this.price = 0;
          this.sku = '';
          this.stock = 0;
          this.category = '';
          this.file = null;
          this.imagePreview = null;
          alert('Produto criado com sucesso');
          this.loadProducts();
        },
        error: (err) => {
          console.error('Erro ao criar produto', err);
          alert('Erro ao criar produto');
        },
      });
    };

    if (this.file) {
      const fd = new FormData();
      fd.append('file', this.file, this.file.name);
      this.http.post<{ url: string }>(`${this.API_BASE}/upload-image`, fd).subscribe({
        next: (r) => {
          const url = r.url;
          doCreate(url);
        },
        error: (err) => {
          console.error('Erro upload', err);
          alert('Erro ao enviar imagem');
        },
      });
    } else {
      doCreate();
    }
  }
}
