#!/usr/bin/env python3
"""
Caatinga.AI Sprint 1 - Agente de inspeção de pragas em pomar
Execução completa: buscas, busca local, regras, Bayes
Uso: python main.py <matricula>
"""

import sys
import csv
import os
from pathlib import Path

from gerador_pomar import gerar_pomar, parametros_sensor, CUSTO
from buscas import Pomar, bfs, dfs, ucs, a_estrela_h1, a_estrela_h2, a_estrela_h3
from busca_local import executar_buscas_locais
from bayes import analisar_sensor, relatorio_bayes

def salvar_pomar(grade, matricula, caminho_resultado):
    """Salva o pomar em arquivo txt"""
    with open(caminho_resultado, "w") as f:
        f.write(f"{matricula}\n")
        for linha in grade:
            f.write(" ".join(linha) + "\n")
    print(f"✓ Pomar salvo em {caminho_resultado}")

def salvar_resultados(resultados_buscas, caminho_csv):
    """Salva tabela de resultados em CSV"""
    with open(caminho_csv, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([
            "estrategia", "heuristica", "custo", "passos", 
            "nos_expandidos", "fronteira_max", "tempo_ms"
        ])
        
        for estrategia, heuristica, resultado in resultados_buscas:
            writer.writerow([
                estrategia,
                heuristica,
                resultado.custo_rota,
                resultado.num_passos,
                resultado.nos_expandidos,
                resultado.fronteira_max,
                f"{resultado.tempo_ms:.2f}"
            ])
    
    print(f"✓ Resultados salvos em {caminho_csv}")

def gerar_grafico(resultados_buscas, caminho_grafico):
    """Gera gráfico de nós expandidos vs estratégia"""
    try:
        import matplotlib.pyplot as plt
    except ImportError:
        print("⚠ matplotlib não instalado — pulando gráfico")
        return
    
    estrategias_nomes = []
    nos_expandidos = []
    
    for estrategia, heuristica, resultado in resultados_buscas:
        nome = estrategia
        if heuristica != "N/A":
            nome = f"{estrategia}\n({heuristica})"
        estrategias_nomes.append(nome)
        nos_expandidos.append(resultado.nos_expandidos)
    
    fig, ax = plt.subplots(figsize=(10, 6))
    cores = ["#FF6B6B", "#4ECDC4", "#45B7D1", "#FFA07A", "#98D8C8", "#F7DC6F", "#BB8FCE", "#85C1E2"]
    
    barras = ax.bar(range(len(estrategias_nomes)), nos_expandidos, color=cores[:len(estrategias_nomes)])
    
    ax.set_xlabel("Estratégia / Heurística", fontsize=12, fontweight="bold")
    ax.set_ylabel("Nós Expandidos", fontsize=12, fontweight="bold")
    ax.set_title("Comparação de Buscas: Nós Expandidos por Estratégia", fontsize=14, fontweight="bold")
    ax.set_xticks(range(len(estrategias_nomes)))
    ax.set_xticklabels(estrategias_nomes, fontsize=10)
    
    # Adiciona valores nas barras
    for barra, valor in zip(barras, nos_expandidos):
        altura = barra.get_height()
        ax.text(barra.get_x() + barra.get_width()/2., altura,
                f"{int(valor)}", ha='center', va='bottom', fontsize=9)
    
    ax.grid(axis="y", alpha=0.3, linestyle="--")
    plt.tight_layout()
    plt.savefig(caminho_grafico, dpi=150, bbox_inches="tight")
    print(f"✓ Gráfico salvo em {caminho_grafico}")

def main():
    if len(sys.argv) < 2:
        print("Uso: python main.py <matricula>")
        print("Exemplo: python main.py 241140610")
        sys.exit(1)
    
    try:
        matricula = int(sys.argv[1])
    except ValueError:
        print("Erro: matrícula deve ser um número inteiro")
        sys.exit(1)
    
    # Cria diretório de resultados
    Path("resultados").mkdir(exist_ok=True)
    
    print(f"\n{'='*60}")
    print(f"Caatinga.AI Sprint 1 - Agente de Inspeção de Pragas")
    print(f"Matrícula (semente): {matricula}")
    print(f"{'='*60}\n")
    
    # ========== PARTE 0: Geração do pomar ==========
    print("PARTE 0: Gerando pomar...")
    grade = gerar_pomar(matricula)
    params_sensor = parametros_sensor(matricula)
    
    print(f"Pomar: {len(grade)}x{len(grade[0])}")
    print(f"Sensor - Prevalência: {params_sensor['prevalencia']:.4f}, "
          f"Sensibilidade: {params_sensor['sensibilidade']:.2f}, "
          f"Taxa FP: {params_sensor['taxa_falso_positivo']:.2f}, "
          f"Talhões/semana: {params_sensor['talhoes_por_semana']}")
    
    # Salva pomar
    salvar_pomar(grade, matricula, "resultados/pomar.txt")
    
    # ========== PARTE 2: Busca Cega ==========
    print("\nPARTE 2: Executando Buscas Cegas...")
    pomar = Pomar(grade)
    
    print("  Executando BFS...")
    res_bfs = bfs(pomar)
    print(f"    Custo: {res_bfs.custo_rota}, Passos: {res_bfs.num_passos}, "
          f"Nós: {res_bfs.nos_expandidos}, Fronteira: {res_bfs.fronteira_max}")
    
    print("  Executando DFS...")
    res_dfs = dfs(pomar)
    print(f"    Custo: {res_dfs.custo_rota}, Passos: {res_dfs.num_passos}, "
          f"Nós: {res_dfs.nos_expandidos}, Fronteira: {res_dfs.fronteira_max}")
    
    print("  Executando UCS...")
    res_ucs = ucs(pomar)
    print(f"    Custo: {res_ucs.custo_rota}, Passos: {res_ucs.num_passos}, "
          f"Nós: {res_ucs.nos_expandidos}, Fronteira: {res_ucs.fronteira_max}")
    
    # ========== PARTE 3: Busca Informada ==========
    print("\nPARTE 3: Executando Buscas Informadas...")
    
    print("  Executando A* (h1 = 0)...")
    res_a_h1 = a_estrela_h1(pomar)
    print(f"    Custo: {res_a_h1.custo_rota}, Nós: {res_a_h1.nos_expandidos}")
    
    print("  Executando A* (h2 = Manhattan)...")
    res_a_h2 = a_estrela_h2(pomar)
    print(f"    Custo: {res_a_h2.custo_rota}, Nós: {res_a_h2.nos_expandidos}")
    
    print("  Executando A* (h3 = 4×Manhattan)...")
    res_a_h3 = a_estrela_h3(pomar)
    print(f"    Custo: {res_a_h3.custo_rota}, Nós: {res_a_h3.nos_expandidos}")
    
    # ========== Salva Resultados ==========
    resultados_buscas = [
        ("BFS", "N/A", res_bfs),
        ("DFS", "N/A", res_dfs),
        ("UCS", "N/A", res_ucs),
        ("A*", "h1 (0)", res_a_h1),
        ("A*", "h2 (Manhattan)", res_a_h2),
        ("A*", "h3 (4×Manhattan)", res_a_h3),
    ]
    
    salvar_resultados(resultados_buscas, "resultados/resultados.csv")
    gerar_grafico(resultados_buscas, "resultados/grafico.png")
    
    # ========== PARTE 4: Busca Local ==========
    print("\nPARTE 4: Executando Buscas Locais...")
    print("  Hill Climbing e Simulated Annealing (30 execuções)...")
    
    stats_locais = executar_buscas_locais(grade, K=15, num_execucoes=30)
    
    hc = stats_locais["hill_climbing"]
    sa = stats_locais["simulated_annealing"]
    
    print(f"  Hill Climbing:")
    print(f"    Média: {hc['media']:.2f}, Desvio: {hc['desvio']:.2f}, "
          f"Melhor: {hc['melhor']:.2f}")
    print(f"  Simulated Annealing:")
    print(f"    Média: {sa['media']:.2f}, Desvio: {sa['desvio']:.2f}, "
          f"Melhor: {sa['melhor']:.2f}")
    
    # ========== PARTE 4.3: Bayes ==========
    print("\nPARTE 4.3: Análise Bayesiana do Sensor...")
    print(relatorio_bayes(params_sensor))
    
    # ========== Resumo Final ==========
    print(f"\n{'='*60}")
    print("RESUMO DE RESULTADOS")
    print(f"{'='*60}")
    print(f"\nBuscas Cegas:")
    print(f"  BFS   — Custo: {res_bfs.custo_rota}, Passos: {res_bfs.num_passos}, Nós: {res_bfs.nos_expandidos}")
    print(f"  DFS   — Custo: {res_dfs.custo_rota}, Passos: {res_dfs.num_passos}, Nós: {res_dfs.nos_expandidos}")
    print(f"  UCS   — Custo: {res_ucs.custo_rota}, Passos: {res_ucs.num_passos}, Nós: {res_ucs.nos_expandidos}")
    
    print(f"\nBuscas Informadas:")
    print(f"  A*(h1) — Custo: {res_a_h1.custo_rota}, Nós: {res_a_h1.nos_expandidos}")
    print(f"  A*(h2) — Custo: {res_a_h2.custo_rota}, Nós: {res_a_h2.nos_expandidos}")
    print(f"  A*(h3) — Custo: {res_a_h3.custo_rota}, Nós: {res_a_h3.nos_expandidos}")
    
    print(f"\nBuscas Locais (K=15, 30 execuções):")
    print(f"  HC — Média: {hc['media']:.2f} ± {hc['desvio']:.2f}, Melhor: {hc['melhor']:.2f}")
    print(f"  SA — Média: {sa['media']:.2f} ± {sa['desvio']:.2f}, Melhor: {sa['melhor']:.2f}")
    
    print(f"\n{'='*60}\n")
    print("✓ Execução completa!")
    print(f"✓ Arquivos gerados em resultados/")

if __name__ == "__main__":
    main()
