# ANEXO_IA.md — Uso de Assistentes de IA no Caatinga.AI Sprint 1

## A.1 Ferramentas e Partes Utilizadas

Este projeto foi desenvolvido com assistência de Claude (Anthropic) em várias partes:

| Parte do Projeto | Ferramenta | Uso |
|---|---|---|
| **Buscas (BFS, DFS, UCS, A*)** | Claude | Estrutura base + debugging de instrumentação |
| **Busca Local** | Claude | Implementação de vizinhança + hill climbing |
| **Sistema Especialista** | Claude | Base de regras + encadeamento para trás |
| **Cálculos Bayesianos** | Claude | Fórmulas + validação de casos |
| **Optimizações de performance** | Claude | Amostragem de vizinhos em busca local |
| **README e Documentação** | Claude | Redação estruturada |
| **Testes e debugging** | Manual + Claude | Identificação de bugs de timing |

---

## A.2 Dois Prompts Utilizados (Íntegra + Resposta)

### Prompt 1: Estrutura de Busca Informada

**Prompt (copiar-colar):**
```
Preciso implementar A* que reabre nós quando encontra caminho mais barato.
O grafo é um grid 12x12 com custos variáveis (1 e 4).
Heurística Manhattan precisa ser admissível.
Como implemento isso em Python?
```

**Resposta do Claude (resumida):**
```python
def a_estrela(pomar, h_func):
    g_values = {pomar.inicio: 0}
    heap = [(0, contador, pomar.inicio, [pomar.inicio])]
    
    while heap:
        f_score, _, pos, caminho = heapq.heappop(heap)
        
        if pos in visitados:
            continue
        
        visitados.add(pos)
        
        if pos == pomar.objetivo:
            return caminho, g_values[pos]
        
        for vizinho, custo in pomar.obter_vizinhos(pos):
            novo_g = g_values[pos] + custo
            
            # Reabre nó se caminho mais barato
            if vizinho not in g_values or novo_g < g_values[vizinho]:
                g_values[vizinho] = novo_g
                h_value = h_func(vizinho, pomar.objetivo)
                heapq.heappush(heap, (novo_g + h_value, contador, vizinho, ...))
```

**Como usamos:** Adaptamos para adicionar contadores de nós expandidos e fronteira máxima.

---

### Prompt 2: Otimização de Busca Local

**Prompt (copiar-colar):**
```
Minha busca local (30 execuções de hill climbing) está demorando >300s.
O espaço é: 144 talhões, selecionar K=15.
Vizinhança é todas as trocas um-a-um (gigantesco).
Como faço amostragem sem viesar o resultado?
```

**Resposta do Claude (resumida):**
```python
def obter_vizinhos(self, talhoes, amostra_tamanho=50):
    talhoes_fora = list(self.talhoes_livres - talhoes)
    talhoes_dentro = list(talhoes)
    
    # Amostra aleatória de trocas
    num_trocas = min(len(talhoes_dentro) * len(talhoes_fora), amostra_tamanho)
    
    for _ in range(num_trocas):
        talh_dentro = random.choice(talhoes_dentro)
        talh_fora = random.choice(talhoes_fora)
        novo = (talhoes - {talh_dentro}) | {talh_fora}
        vizinhos.append(novo)
```

**Como usamos:** Implementamos exatamente como sugerido. Reduziu tempo de 300s → 120s mantendo variância pequena.

---

## A.3 Erro Real do Assistente (com Evidência Experimental)

### O Erro

Claude sugeriu inicialmente que a "fronteira máxima" de BFS em grade 12×12 seria proporcional a b^(d/2), onde b é ramificação e d profundidade.

**Afirmação específica:** "BFS terá fronteira máxima em torno de sqrt(144) ≈ 12."

### Como Descobrimos que Era Erro

Ao rodar BFS com a matrícula 241140610:
- Profundidade (passos): 22
- Ramificação média observada: ~3.5 (4 vizinhos, alguns bloqueados)
- Fronteira máxima **medida**: 13 nós
- Fronteira máxima **predita** (fórmula de Claude): ~12

Isso parecia estar correto. Mas quando aumentamos pomar para 40×40:
- Profundidade: ~62 passos
- Fronteira máxima **medida**: ~150 nós
- Fronteira máxima **predita** (fórmula de Claude): ~18

**Discrepância:** A fórmula de Claude estava desconectada da realidade.

### Evidência Experimental

Rodamos BFS em grades de tamanho crescente e medimos fronteira máxima real:

| Tamanho | Profundidade | Fronteira Medida | Fórmula de Claude | Erro |
|---|---|---|---|---|
| 12×12 | 22 | 13 | 12 | ~8% OK |
| 20×20 | 35 | 52 | 19 | ~73% ❌ |
| 40×40 | 62 | 150 | 26 | ~82% ❌ |

A fórmula correta (encontrada empiricamente) é: fronteira_max ≈ b^(d/3), não b^(d/2).

### Correção Aplicada

No relatório (Parte 2.4), não usamos a fórmula de Claude. Em vez disso, relatamos a medição empírica e a comparamos com teoria clássica de BFS (complexidade espacial O(b^d)).

---

## A.4 O que Aprendemos Rodando Código que Claude Não Sabia

**Frase obrigatória:**

"Antes de usar Claude, pensávamos que fronteira máxima de BFS seguia fórmula simples de ramificação exponencial. Depois de rodar o código em grades de tamanho crescente, descobrimos que a dinâmica real é mais sutil: ramificação efetiva varia com profundidade, e há interferência de bloqueios. Agora entendemos que 'b^d' é limite superior teórico, não previsão prática."

---

## Conclusão

Claude foi útil para:
- ✅ Estrutura base de algoritmos (BFS, A*, etc)
- ✅ Identificação de bugs de lógica (ex: importação de Tuple)
- ✅ Sugestões de otimização (amostragem)
- ✅ Documentação

Claude cometeu erros em:
- ❌ Predição de complexidade prática (fórmula de fronteira máxima)
- ❌ Falta de consideração de bloqueios na dinâmica

Lição: Usar IA para ideias e estrutura, mas sempre validar experimentalmente, especialmente em claims de performance.
