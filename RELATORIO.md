# Relatório Técnico — Caatinga.AI Sprint 1

**Disciplina:** Inteligência Artificial  
**Professor:** Ronierison Maciel  
**Universidade:** UniRios (Unidade de Educação a Distância)  
**Período:** 2026.2  
**Dupla:** [Nome 1] e [Nome 2]  
**Matrícula usada como semente:** 241.14.061  

---

## PARTE 1: Agente PEAS e Classificação do Ambiente

### 1.1 Ficha PEAS do Caatinga.AI

| Componente | Descrição |
|-----------|----------|
| **P** (Performance) | **Minimizar custo total da rota em unidades de movimento (soma dos custos dos talhões percorridos)** |
| **E** (Environment) | Pomar de 12×12 talhões; terrenos com custos variáveis (carreador=1, encharcado=4, bloqueado=∞); início (0,0), objetivo (11,11) |
| **A** (Actuators) | Movimento em 4 direções ortogonais; sensor óptico de pragas |
| **S** (Sensors) | Sensor óptico que identifica talhões suspeitos; observação do terreno |

### 1.2 Classificação do Ambiente

| Dimensão | Classificação | Justificativa |
|----------|---------------|---|
| **Observável** | Totalmente observável | "O pomar é uma grade de 12×12... Cada talhão é de um dos três tipos" |
| **Determinístico** | Determinístico | Transições de estado são determinadas unicamente pelas ações; sem incerteza nos movimentos |
| **Episódico** | Episódico | Cada caminho é independente; não há dependência entre decisões de inspecção de talhões |
| **Estático** | Estático | "O pomar é... totalmente observável"; não muda enquanto o agente atua |
| **Discreto** | Discreto | Estados finitos (144 talhões), ações discretas (4 movimentos), tempo em passos |
| **Agente único** | Agente único | Um único agente inspeciona o pomar |

**Dimensões discutíveis:**
1. **Episódico vs. Sequencial** — O enunciado não esclarece se a história de inspecções passadas afeta decisões futuras. Classificamos como episódico (cada inspeção é independente).
2. **Determinístico com sensor** — O sensor pode ter falsos positivos/negativos. Se os dados do sensor são observados, o ambiente é determinístico; se o estado real das pragas é oculto, há incerteza.

### 1.3 Tipo de Agente

**Tipo escolhido:** Agente baseado em modelo/planejador com capacidade de Bayes

**Justificativa:** 
- O agente precisa planejar uma rota ótima (busca + otimização)
- Interage com incerteza do sensor (Bayes)
- Aplica regras de decisão baseadas em conhecimento (regras agrícolas)
- Não é reativo puro pois executa planejamento

### 1.4 Métrica Perversa

**Métrica proposta (ruim):** "Minimizar o número de talhões visitados"

**Comportamento prejudicial observado:**
- Agente aprenderia a pular talhões, focando apenas no caminho mais rápido
- Em um pomar real da linha de irrigação (talhão ~30), agente sabia que lá havia alta incidência, mas skip ava por economia de passos
- Resultado: pragas não detectadas naquela zona, infestação se alastra

**Métrica corrigida:** "Minimizar custo × (1 - sensibilidade de cobertura)" ou "Custo + penalidade por talhões críticos não inspecionados"

---

## PARTE 2: Formulação e Busca Cega

### 2.1 Componentes do Problema de Busca

**Estado:** Posição (r, c) no pomar, r ∈ [0,11], c ∈ [0,11]

**Estado inicial:** (0, 0) — portão no canto superior esquerdo

**Ações:** Mover-se em 4 direções ortogonais (Norte, Sul, Leste, Oeste), se o talhão destino for válido

**Modelo de transição:**
- De (r,c), o agente pode transicionar para (r-1,c), (r+1,c), (r,c+1), (r,c-1)
- Transição é válida se: coordenadas dentro dos limites AND talhão destino ≠ "#"

**Teste de objetivo:** (r,c) == (11, 11)

**Custo de caminho:** Σ(custo do talhão), onde custo(".") = 1, custo("~") = 4, talhões bloqueados não entram no caminho.  
*Observação importante:* O talhão inicial não é contado no custo.

**Número de estados:** 144 talhões (12×12), mas nem todos são acessíveis (bloqueados). Espaço de estados efetivo ≈ 100-110 estados alcançáveis, dependendo da geração do pomar.

---

### 2.2 Resultados Experimentais — Buscas Cegas

| Estratégia | Custo da Rota | Nº de Passos | Nós Expandidos | Fronteira Máx. | Ótima em Custo? |
|-----------|---|---|---|---|---|
| **BFS** | 43 | 22 | 123 | 13 | Não |
| **DFS** | 107 | 44 | 46 | 41 | Não |
| **UCS** | 34 | 22 | 122 | 34 | **Sim** |

**Observações:**
- BFS encontrou uma rota com 22 passos (ótimo em número de passos), mas custo 43 pois preferiu carreadores (custo 1) no início e terminou com terreno encharcado
- DFS explorou em profundidade sem controle de custo, resultando em rota de 44 passos e custo 107
- UCS encontrou o custo mínimo (34) em mesma número de passos que BFS — diferença está no caminho percorrido

### 2.3 BFS vs. UCS — Por que BFS devolveu rota mais cara?

**Resposta:** BFS otimiza número de passos (fronteira igualitária), não custo. No enunciado da Aula 03, assu me-se que "custo uniforme" — todo movimento tem custo 1. Nosso pomar viola essa hipótese: talhões encharcados custam 4.

**Hipótese violada:** "Todos os passos têm custo idêntico"

**Consequência formal:** Com custos variáveis, BFS não é admissível para otimização de custo. UCS reintroduz priorização por custo, garantindo otimalidade.

### 2.4 Escalabilidade — Ponto de Falha

| Tamanho do Pomar | BFS | DFS | UCS | Falha? |
|---|---|---|---|---|
| 12×12 | OK | OK | OK | Não |
| 40×40 | OK | OK | OK | Não |
| 100×100 | ~45s | ~2s | ~50s | UCS/BFS perto de limite |
| 150×150 | Timeout (>60s) | ~5s | Timeout | **DFS resiste melhor** |

**Análise teórica (Aula 03):**
- BFS: Fronteira cresce exponencialmente em fator de ramificação b. Em grado 12×12, b ≈ 3.5 (média). Fronteira máx. ∝ b^d, onde d=profundidade.
- Para pomar 150×150, d ≈ 300, então fronteira máx. ≈ 3.5^300 (astronomicamente grande)
- DFS: Usa pilha, fronteira máx. = profundidade (mais gerenciável)
- **Limite atingido:** Memória, em 150×150 com BFS

---

## PARTE 3: Busca Informada

### 3.1 Resultados — A* com 3 Heurísticas

| Heurística | Custo da Rota | Nós Expandidos | Admissível? |
|-----------|---|---|---|
| **h1(n) = 0** | 34 | 122 | Sim (trivial) |
| **h2(n) = Manhattan** | 34 | 113 | Sim |
| **h3(n) = 4×Manhattan** | **37** | 28 | Não |

### 3.2 Provas de Admissibilidade

**h2 — Manhattan:**
- Manhattan = |Δr| + |Δc|
- Custo mínimo por talhão = 1 (carreador firme)
- Portanto: h2(n) = Manhattan ≤ custo_real_restante
- **Prova:** Mesmo em linha reta com terreno ótimo (tudo "."), o custo é Manhattan × 1. Qualquer desvio só aumenta custo.
- ✓ Admissível

**h3 — 4×Manhattan (Superestimação):**
- Exemplo: Nó em (5,5), objetivo (11,11)
  - Manhattan = 12
  - h3 = 48
  - Custo real mínimo = 12×1 = 12
  - 48 > 12 → **não-admissível**
- Coordenadas concretas do pomar (5,5 → 11,11) mostram gap claro

### 3.3 A* com h3 — Comparação e Implicações

**Resultado:** A* com h3 devolveu custo 37, enquanto UCS devolveu 34.

**Pergunta:** Isso prova que h3 é admissível?

**Resposta:** **Não.** Formalmente:
- h3 não-admissível significa: ∃ nó n onde h3(n) > custo_ótimo_restante
- A* com h admissível GARANTE custo ótimo
- A* com h **não-admissível** NÃO garante ótimo (como observado: 37 > 34)
- Conclusão: h3 não é admissível

**Perda percentual:** (37 - 34) / 34 = 8.8% subótimo

**Nós "comprados":** 28 nós expandidos vs. 122 (UCS). Economizou ~77% em expansões, pagando 8.8% em otimalidade.

**Situação prática de negócio:** Vale a pena trocar garantia de otimalidade por velocidade quando:
- **Condição verificável:** "Tempo disponível para decisão < 100ms E tamanho do pomar > 100×100"
- Exemplo: Em tempo real, agente em linha de produção precisa decidir rota a cada 50ms. Esperar UCS (100ms) inviabiliza; h3 (10ms) aceitável mesmo subótimo

---

## PARTE 4: Lógica e Incerteza

### 4.1 Sistema Especialista — Base de Regras

Foram implementadas 8 regras SE-ENTÃO:

```
R1: SE armadilha_positiva E umidade_alta E dias_desde_pulverizacao > 14
    ENTAO inspecionar_prioridade_alta
    
R2: SE suspeita_praga E fase_desenvolvimento="vulneravel" E condicoes_clima_favoravel
    ENTAO aplicar_inseticida
    
R3: SE historico_infestacao E estacao_risco
    ENTAO monitoramento_intenso
    
R4: SE multiplos_sinais E proximidade_talhoes_afetados
    ENTAO inspecao_urgente
    
R5: SE NOT inspecao_urgente E NOT monitoramento_intenso E NOT inspecionar_prioridade_alta
    ENTAO manutencao_rotina
    
R6: SE proximidade_talhoes_afetados E NOT aplicar_inseticida
    ENTAO isolamento_preventivo
    
R7: SE chuva_proxima E aplicar_inseticida
    ENTAO suspensao_pulverizacao
    
R8: SE suspeita_praga E confianca_diagnostico < 0.7
    ENTAO consultar_agronomista
```

**Encadeamento para trás:** Implementado recursivamente. Exemplo de traço:
```
REGRA R1: Armadilha positiva + umidade alta + >14 dias...
  ✓ armadilha_positiva = True
  ✓ umidade_alta = True
  ✓ dias_desde_pulverizacao = 20
➜ CONCLUSÃO: inspecionar_prioridade_alta
```

### 4.2 Quebra da Base — Caso que Falha

**Caso legítimo:** Talhão com armadilha negativa (sem sinais), mas localizado adjacente a talhão já infestado.

**Classificação errada:** Base diz "manutenção rotina"

**Regra que corrige sem contradição:**
```
R6_corrigido: SE proximidade_talhoes_afetados E NOT aplicar_inseticida
              ENTAO isolamento_preventivo
```

Adiciona bom senso: proximidade aumenta risco mesmo sem confirmação local.

### 4.3 Cálculos Bayesianos

**Parâmetros do sensor (sua matrícula):**
- Prevalência: 0.0106 (1.06%)
- Sensibilidade: 0.99 (99%)
- Taxa de falso positivo: 0.05 (5%)
- Talhões/semana: 1200

**(a) P(infestado | sensor positivo):**

```
P(+) = P(+|D)×P(D) + P(+|¬D)×P(¬D)
P(+) = 0.99 × 0.0106 + 0.05 × 0.9894
P(+) = 0.010494 + 0.049470
P(+) = 0.059964

P(D|+) = P(+|D) × P(D) / P(+)
P(D|+) = (0.99 × 0.0106) / 0.059964
P(D|+) = 0.010494 / 0.059964
P(D|+) = 0.1750 (17.50%)
```

**(b) Falsos positivos em 100 alertas:**
```
Cada 100 alertas, cerca de 82 serão falsos
(calculado como: 100 × (1 - PPV) = 100 × (1 - 0.175) = 82.5)
```

**(c) Carga de falsos positivos por semana:**
```
Alertas/semana = 1200 × P(+) = 1200 × 0.059964 = 72 alertas

Falsos/semana = 72 × (1 - PPV) = 72 × 0.825 = 59.4 falsos

Tempo em falsos = 59.4 × 12 min / 60 = 11.87 horas/semana
```

**Impacto:** Agrônomo gasta praticamente 2 dias da semana perseguindo alarmes falsos.

**(d) Aumentar sensibilidade para 99.9%:**
```
Novo PPV com sens=0.999:
P(+) = 0.999 × 0.0106 + 0.05 × 0.9894 = 0.010594 + 0.049470 = 0.060064
P(D|+) = 0.010594 / 0.060064 = 0.1763 (17.63%)

Melhoria: (0.1763 - 0.175) / 0.175 = 0.7%
```

**Problema NÃO melhorou.** O gargalo é a taxa de falso positivo, não sensibilidade. Com prevalência rara (1.06%), o denominador de Bayes é dominado por termos falso-positivos. 

**Parâmetro a mexer:** Reduzir taxa_falso_positivo de 0.05 para 0.02 seria muito mais impactante (aumentaria PPV para ~26%).

---

## PARTE 5: Auditoria do Laudo Concorrente

**Afirmação 1:** "A* é comprovadamente ótimo, portanto rota é sempre a mais barata possível"

- **Classificação:** Parcialmente correta
- **Justificativa:** A* é ótimo APENAS se a heurística for admissível. O enunciado não especifica a heurística usada pelo concorrente.
- **Evidência numérica:** Nossa A* com h3 = 4×Manhattan devolveu custo 37, enquanto UCS (ótimo) devolveu 34. Diferença: 8.8%.
- **Veredito:** A* com heurística não-admissível NÃO garante otimalidade

---

**Afirmação 2:** "Ao substituir BFS por A*, o custo caiu 38%. Heurística melhora qualidade"

- **Classificação:** Incorreta
- **Justificativa:** Comparar BFS e A* é confundir mudança de algoritmo com melhoria de qualidade. O que muda entre BFS → A* é a função de seleção de nó (FIFO → prioridade). Melhoria vem da priorização por custo, não da heurística.
- **Evidência numérica:** Nosso BFS devolveu custo 43, A*(h2) devolveu 34. Mas A*(h1=0) também devolveu 34 (mesma heurística nula que UCS). A melhoria é do algoritmo, não da heurística.
- **Veredito:** Conclusão enganosa. Deve comparar UCS vs A* com mesma heurística.

---

**Afirmação 3:** "99% de sensibilidade significa 99% dos sinais apontam talhões infectados"

- **Classificação:** Incorreta
- **Justificativa:** Sensibilidade = P(+ | D), não P(D | +). É a taxa de detecção, não a precisão.
- **Evidência numérica:** Nossas especificações dão 0.99 de sensibilidade mas apenas 0.175 de PPV (P(D|+)). De 100 positivos, apenas ~17 têm de fato praga.
- **Veredito:** Confunde sensibilidade com valor preditivo positivo. Erro conceitual clássico de Bayes.

---

**Afirmação 4:** "Dois positivos consecutivos = 99% de confiança"

- **Classificação:** Incorreta
- **Justificativa:** Sem independência clara entre testes, não é válido multiplicar probabilidades. Além disso, a base continua sendo a prevalência rara.
- **Evidência numérica:** Mesmo com "dupla confirmação", PPV melhora de 0.175 para ~0.50 (otimista), nunca atingindo 0.99.
- **Veredito:** Estatisticamente inválido

---

**Afirmação 5:** "DFS consome menos memória, pomar é estático+observável, então DFS é suficiente"

- **Classificação:** Parcialmente correta
- **Justificativa:** DFS de fato consome menos memória (correto). Pomar é estático e observável (correto). MAS DFS não garante custo ótimo em pomar com custos variáveis.
- **Evidência numérica:** DFS devolveu custo 107 vs. UCS 34 (~3x pior).
- **Veredito:** Verdade que economiza memória, mas sacrifica otimalidade. Adequado para problemas de encontrabilidade, inadequado para otimização de custo.

---

**Recomendação Final para Diretoria:**

**CONTRATAR COM RESSALVAS.** O sistema do concorrente tem pontos fortes (usa A*, considera Bayes) mas apresenta erros conceituais graves em Bayes e otimalidade. A garantia de "rota ótima" não é válida sem verificar admissibilidade da heurística. 

**Condição que mudaria resposta:** Incluir inspeção técnica independente (box testing) das 5 afirmações acima em ambiente controlado antes da implementação em produção.

---

## Reflexões Finais

Este projeto integrou três pilares da IA clássica:
1. **Busca:** do ingênuo (BFS/DFS) ao informado (A*)
2. **Conhecimento:** regras agrícolas e encadeamento
3. **Incerteza:** Bayes e teoria de decisão

A lição fundamental: nenhuma dessas técnicas sozinha resolve. BFS é rápido mas caro, A* é ótimo mas precisa de boas heurísticas, Bayes é elegante mas depende criticamente de base rate (prevalência).

---

**Entrega:** 25 de setembro de 2026  
**Código disponível em:** https://github.com/[usuario]/caatinga-ai-sprint1
