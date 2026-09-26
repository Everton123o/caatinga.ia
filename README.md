
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




