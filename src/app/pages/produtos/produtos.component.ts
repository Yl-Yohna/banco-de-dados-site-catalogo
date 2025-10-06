import { CommonModule } from '@angular/common';
import { Component, OnInit } from '@angular/core';
import { MatCardModule } from '@angular/material/card'; // importe aqui
import { MatButtonModule } from '@angular/material/button'; // se for usar botões
import { MatButtonToggleModule } from '@angular/material/button-toggle';
import { HttpClientModule, HttpClient } from '@angular/common/http';
// RouterLink/RouterLinkActive removed because templates do not use router links here

@Component({
  selector: 'app-produtos',
  standalone: true,
  imports: [CommonModule, MatCardModule, MatButtonModule, MatButtonToggleModule, HttpClientModule],
  templateUrl: './produtos.component.html',
  styleUrls: ['./produtos.component.scss']
})
export class ProdutosComponent implements OnInit {
  categoriaSelecionada = 'todas';
  produtos: any[] = [];
  produtosFiltrados: any[] = [];
  API_BASE = 'http://127.0.0.1:8000';

  constructor(private http: HttpClient) {}

  ngOnInit(): void {
    this.loadProducts();
  }

  loadProducts() {
    this.http.get<any[]>(`${this.API_BASE}/products`).subscribe({
      next: (rows) => {
        this.produtos = rows.map(p => ({
          nome: p.name,
          descricao: p.description,
          preco: (p.price_cents || 0) / 100,
          categoria: p.category,
          imagemUrl: p.image_url || null,
        }));
        this.produtosFiltrados = [...this.produtos];
      },
      error: (err) => console.error('Erro ao buscar produtos', err),
    });
  }

  onCategoriaChange(categoria: string) {
    this.categoriaSelecionada = categoria;
    if (categoria === 'todas') {
      this.produtosFiltrados = this.produtos;
    } else {
      this.produtosFiltrados = this.produtos.filter(p => p.categoria === categoria);
    }
  }

  gerarLinkWhatsapp(nomeProduto: string): string {
    const telefone = '11983511295';
    const mensagem = `Olá! Tenho interesse no produto: ${nomeProduto}`;
    return `https://wa.me/${telefone}?text=${encodeURIComponent(mensagem)}`;
  }
}
