<<<<<<< HEAD
=======
# Caatinga.AI Sprint 1 — Agente de Inspeção de Pragas

**Disciplina:** Inteligência Artificial  
**Professor:** Ronierison Maciel  
**Instituição:** UniRios — 2026.2  
**Formato:** Dupla  
**Matrícula usada como semente:** 241.14.061  
>>>>>>> f786f988a42afcdcc67a2a6be4c3974df50db349

## O que este projeto faz

Caatinga.AI é um agente inteligente que inspeciona um pomar de 12×12 talhões para detecção de pragas. O projeto implementa:

1. **Buscas cegas** (BFS, DFS, UCS) para encontrar rota ótima entre portão e coleta
2. **Buscas informadas** (A* com múltiplas heurísticas)
3. **Busca local** (hill climbing e simulated annealing) para seleção de K talhões
4. **Sistema especialista** com regras SE-ENTÃO e encadeamento para trás
5. **Análise bayesiana** do sensor de pragas (PPV, falsos positivos)

O código é totalmente instrumentado com contadores de nós expandidos, fronteira máxima e tempo de execução.

## Como rodar

### Pré-requisitos
- Python 3.8+

### Instalação

```bash
pip install -r requirements.txt
```

### Execução

```bash
python src/main.py 241140610
```

Substitua `241140610` pela sua matrícula (ou use 20231045 para testar contra a caixa de aferição).

**Saída gerada:**
- `resultados/pomar.txt` — Grade 12×12 do pomar
- `resultados/resultados.csv` — Tabela com custo, passos, nós expandidos, fronteira, tempo
- `resultados/grafico.png` — Gráfico de nós expandidos por estratégia

## Resumo dos Resultados

| Estratégia | Custo | Passos | Nós Expandidos | Fronteira Máx. | Ótimo em Custo? |
|-----------|-------|--------|---|---|---|
| BFS | - | - | - | - | Não |
| DFS | - | - | - | - | Não |
| UCS | - | - | - | - | **Sim** |
| A* (h1=0) | - | - | - | - | Sim |
| A* (h2 Manhattan) | - | - | - | - | Sim |
| A* (h3 4×Manhattan) | - | - | - | - | **Não** |

*Preencher com números da sua execução*

## Configurações Técnicas

**Ordem de expansão dos vizinhos:** Norte, Sul, Leste, Oeste  
**A* implementado com:** Reabertura de nós (versão consistente)

## Estrutura do Repositório

| Arquivo | Responsável |
|---------|-----------|
| `src/gerador_pomar.py` | Gerador de pomar (intacto do enunciado) |
| `src/buscas.py` | BFS, DFS, UCS, A* com instrumentação |
| `src/busca_local.py` | Hill climbing e simulated annealing |
| `src/especialista.py` | Sistema de regras com encadeamento para trás |
| `src/bayes.py` | Cálculos bayesianos do sensor |
| `src/main.py` | Orquestrador principal |
| `RELATORIO.md` | Relatório completo com todas as partes |
| `ANEXO_IA.md` | Anexo descrevendo uso de assistentes de IA |

## Limitações Conhecidas

1. **Matplotlib opcional** — o código roda sem ela, mas o gráfico não é gerado
2. **Busca local não usa topologia do pomar** — otimiza seleção sem considerar caminho entre talhões (escopo reduzido para Sprint 1)
3. **Sistema especialista usa métricas simplificadas** — em produção precisaria de dados agrícolas reais
4. **A* com h3 é não-admissível** — isto é propositalmente testado na Parte 3
<<<<<<< HEAD
=======

## Checklist de Entrega

- [ ] Repositório público no GitHub
- [ ] README com identificação, comando e tabela-resumo
- [ ] RELATORIO.md preenchido com todas as tabelas
- [ ] ANEXO_IA.md descrevendo uso de IA
- [ ] Código roda com `python src/main.py <matricula>`
- [ ] Mínimo 8 commits com os dois integrantes
- [ ] gerador_pomar.py intacto
- [ ] resultados.csv, grafico.png e pomar.txt gerados
>>>>>>> f786f988a42afcdcc67a2a6be4c3974df50db349
