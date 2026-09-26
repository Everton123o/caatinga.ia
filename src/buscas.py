from collections import deque, defaultdict
import heapq
import time
from typing import List, Tuple, Dict, Set

# Ordem de expansão dos vizinhos: Norte, Sul, Leste, Oeste (declarado)
DIRECOES = [(-1, 0), (1, 0), (0, 1), (0, -1)]  # N, S, L, O
NOMES_DIR = ["Norte", "Sul", "Leste", "Oeste"]

class Resultado:
    def __init__(self):
        self.custo_rota = 0
        self.num_passos = 0
        self.nos_expandidos = 0
        self.fronteira_max = 0
        self.rota = []
        self.tempo_ms = 0

class Pomar:
    def __init__(self, grade: List[List[str]]):
        self.grade = grade
        self.n = len(grade)
        self.inicio = (0, 0)
        self.objetivo = (self.n - 1, self.n - 1)
        self.custos = {".": 1, "~": 4}
        self.bloqueado = "#"
    
    def eh_valido(self, pos: Tuple[int, int]) -> bool:
        r, c = pos
        return 0 <= r < self.n and 0 <= c < self.n and self.grade[r][c] != self.bloqueado
    
    def obter_vizinhos(self, pos: Tuple[int, int]) -> List[Tuple[Tuple[int, int], int]]:
        """Retorna lista de (vizinho, custo) na ordem declarada"""
        vizinhos = []
        for dr, dc in DIRECOES:
            nr, nc = pos[0] + dr, pos[1] + dc
            if self.eh_valido((nr, nc)):
                custo = self.custos[self.grade[nr][nc]]
                vizinhos.append(((nr, nc), custo))
        return vizinhos
    
    def reconstroi_caminho(self, pai: Dict, atual: Tuple[int, int]) -> List[Tuple[int, int]]:
        caminho = []
        while atual is not None:
            caminho.append(atual)
            atual = pai.get(atual)
        return caminho[::-1]
    
    def calcula_custo_caminho(self, caminho: List[Tuple[int, int]]) -> int:
        """Calcula custo do caminho (não conta início)"""
        custo = 0
        for i in range(1, len(caminho)):
            r, c = caminho[i]
            custo += self.custos[self.grade[r][c]]
        return custo

def bfs(pomar: Pomar) -> Resultado:
    """Busca em largura — ótima em passos, não em custo"""
    res = Resultado()
    inicio = time.time()
    
    fila = deque([(pomar.inicio, [pomar.inicio])])
    visitados = {pomar.inicio}
    res.nos_expandidos = 0
    res.fronteira_max = 1
    
    while fila:
        res.fronteira_max = max(res.fronteira_max, len(fila))
        pos_atual, caminho = fila.popleft()
        res.nos_expandidos += 1
        
        if pos_atual == pomar.objetivo:
            res.custo_rota = pomar.calcula_custo_caminho(caminho)
            res.num_passos = len(caminho) - 1
            res.rota = caminho
            res.tempo_ms = (time.time() - inicio) * 1000
            return res
        
        for vizinho, _ in pomar.obter_vizinhos(pos_atual):
            if vizinho not in visitados:
                visitados.add(vizinho)
                fila.append((vizinho, caminho + [vizinho]))
    
    res.tempo_ms = (time.time() - inicio) * 1000
    return res

def dfs(pomar: Pomar) -> Resultado:
    """Busca em profundidade"""
    res = Resultado()
    inicio = time.time()
    
    pilha = [(pomar.inicio, [pomar.inicio])]
    visitados = {pomar.inicio}
    res.nos_expandidos = 0
    res.fronteira_max = 1
    
    while pilha:
        res.fronteira_max = max(res.fronteira_max, len(pilha))
        pos_atual, caminho = pilha.pop()
        res.nos_expandidos += 1
        
        if pos_atual == pomar.objetivo:
            res.custo_rota = pomar.calcula_custo_caminho(caminho)
            res.num_passos = len(caminho) - 1
            res.rota = caminho
            res.tempo_ms = (time.time() - inicio) * 1000
            return res
        
        # Expande em ordem reversa para manter ordem de vizinhos
        vizinhos = pomar.obter_vizinhos(pos_atual)
        for vizinho, _ in reversed(vizinhos):
            if vizinho not in visitados:
                visitados.add(vizinho)
                pilha.append((vizinho, caminho + [vizinho]))
    
    res.tempo_ms = (time.time() - inicio) * 1000
    return res

def ucs(pomar: Pomar) -> Resultado:
    """Busca de custo uniforme — ótima em custo"""
    res = Resultado()
    inicio = time.time()
    
    # heap: (custo_acumulado, contador_desempate, pos, caminho)
    contador = 0
    heap = [(0, contador, pomar.inicio, [pomar.inicio])]
    visitados = set()
    res.nos_expandidos = 0
    res.fronteira_max = 1
    
    while heap:
        res.fronteira_max = max(res.fronteira_max, len(heap))
        custo_atual, _, pos_atual, caminho = heapq.heappop(heap)
        
        if pos_atual in visitados:
            continue
        
        visitados.add(pos_atual)
        res.nos_expandidos += 1
        
        if pos_atual == pomar.objetivo:
            res.custo_rota = custo_atual
            res.num_passos = len(caminho) - 1
            res.rota = caminho
            res.tempo_ms = (time.time() - inicio) * 1000
            return res
        
        for vizinho, custo_vizinho in pomar.obter_vizinhos(pos_atual):
            if vizinho not in visitados:
                novo_custo = custo_atual + custo_vizinho
                contador += 1
                heapq.heappush(heap, (novo_custo, contador, vizinho, caminho + [vizinho]))
    
    res.tempo_ms = (time.time() - inicio) * 1000
    return res

def manhattan(pos: Tuple[int, int], objetivo: Tuple[int, int]) -> int:
    """Heurística Manhattan"""
    return abs(pos[0] - objetivo[0]) + abs(pos[1] - objetivo[1])

def a_estrela(pomar: Pomar, h_func, h_nome: str = "h1") -> Resultado:
    """A* com reabertura de nós (versão consistente)"""
    res = Resultado()
    inicio = time.time()
    
    contador = 0
    g_values = {pomar.inicio: 0}  # custo real até cada nó
    heap = [(0, contador, pomar.inicio, [pomar.inicio])]
    visitados = set()
    res.nos_expandidos = 0
    res.fronteira_max = 1
    
    while heap:
        res.fronteira_max = max(res.fronteira_max, len(heap))
        f_score, _, pos_atual, caminho = heapq.heappop(heap)
        
        if pos_atual in visitados:
            continue
        
        visitados.add(pos_atual)
        res.nos_expandidos += 1
        
        if pos_atual == pomar.objetivo:
            res.custo_rota = g_values[pos_atual]
            res.num_passos = len(caminho) - 1
            res.rota = caminho
            res.tempo_ms = (time.time() - inicio) * 1000
            return res
        
        for vizinho, custo_vizinho in pomar.obter_vizinhos(pos_atual):
            if vizinho not in visitados:
                novo_g = g_values[pos_atual] + custo_vizinho
                
                # Reabre nó se encontrou caminho mais barato
                if vizinho not in g_values or novo_g < g_values[vizinho]:
                    g_values[vizinho] = novo_g
                    h_value = h_func(vizinho, pomar.objetivo)
                    f_score_novo = novo_g + h_value
                    contador += 1
                    heapq.heappush(heap, (f_score_novo, contador, vizinho, caminho + [vizinho]))
    
    res.tempo_ms = (time.time() - inicio) * 1000
    return res

def a_estrela_h1(pomar: Pomar) -> Resultado:
    """A* com h(n) = 0"""
    return a_estrela(pomar, lambda pos, obj: 0, "h1")

def a_estrela_h2(pomar: Pomar) -> Resultado:
    """A* com h(n) = Manhattan"""
    return a_estrela(pomar, manhattan, "h2")

def a_estrela_h3(pomar: Pomar) -> Resultado:
    """A* com h(n) = 4 * Manhattan"""
    return a_estrela(pomar, lambda pos, obj: 4 * manhattan(pos, obj), "h3")
