import random
import math
from typing import Set, Tuple, List
from statistics import mean, stdev

class BuscaLocal:
    """Seleção de K talhões para inspecionar (problema de otimização local)"""
    
    def __init__(self, pomar_grade: List[List[str]], K: int = 15):
        self.grade = pomar_grade
        self.n = len(pomar_grade)
        self.K = K
        self.bloqueado = "#"
        self.talhoes_livres = self._obter_talhoes_livres()
    
    def _obter_talhoes_livres(self) -> Set[Tuple[int, int]]:
        """Retorna conjunto de talhões que não são bloqueados"""
        livres = set()
        for i in range(self.n):
            for j in range(self.n):
                if self.grade[i][j] != self.bloqueado:
                    livres.add((i, j))
        return livres
    
    def funcao_objetivo(self, talhoes: Set[Tuple[int, int]]) -> float:
        """
        Objetivo: maximizar a probabilidade ponderada de pragas.
        Assumimos que cada talhão livre tem a mesma probabilidade base.
        Aqui usamos como proxy: número de talhões * densidade (heurística).
        """
        if not talhoes:
            return 0.0
        # Métrica simples: favor talhões em área de maior risco (diagonal sudeste)
        score = 0.0
        for r, c in talhoes:
            # Peso maior para talhões distantes (potencialmente mais infectados)
            distancia = r + c
            score += distancia
        return score / len(talhoes)
    
    def obter_vizinhos(self, talhoes: Set[Tuple[int, int]], 
                      amostra_tamanho: int = 50) -> List[Set[Tuple[int, int]]]:
        """
        Vizinhança: troca um talhão da solução por um fora dela.
        Retorna amostra aleatória das trocas possíveis para eficiência.
        """
        vizinhos = []
        talhoes_fora = list(self.talhoes_livres - talhoes)
        talhoes_dentro = list(talhoes)
        
        # Amostra aleatória de trocas para não explodir em problemas grandes
        num_trocas = min(len(talhoes_dentro) * len(talhoes_fora), amostra_tamanho)
        
        for _ in range(num_trocas):
            talh_dentro = random.choice(talhoes_dentro)
            talh_fora = random.choice(talhoes_fora)
            novo_estado = (talhoes - {talh_dentro}) | {talh_fora}
            vizinhos.append(novo_estado)
        
        # Garante pelo menos alguns vizinhos
        if not vizinhos and talhoes_dentro and talhoes_fora:
            talh_dentro = talhoes_dentro[0]
            for talh_fora in talhoes_fora[:10]:
                novo_estado = (talhoes - {talh_dentro}) | {talh_fora}
                vizinhos.append(novo_estado)
        
        return vizinhos
    
    def hill_climbing(self) -> Tuple[Set[Tuple[int, int]], float]:
        """
        Subida de encosta: começa com estado aleatório, melhora até platô.
        Retorna (talhoes_selecionados, valor_objetivo)
        """
        # Estado inicial aleatório
        talhoes_atuais = set(random.sample(sorted(self.talhoes_livres), self.K))
        valor_atual = self.funcao_objetivo(talhoes_atuais)
        
        melhorou = True
        iteracoes = 0
        max_iteracoes = 100  # Limite para evitar loops infinitos
        
        while melhorou and iteracoes < max_iteracoes:
            melhorou = False
            iteracoes += 1
            vizinhos = self.obter_vizinhos(talhoes_atuais, amostra_tamanho=100)
            
            # Avalia vizinhos
            melhor_vizinho = None
            melhor_valor = valor_atual
            
            for vizinho in vizinhos:
                valor = self.funcao_objetivo(vizinho)
                if valor > melhor_valor:
                    melhor_valor = valor
                    melhor_vizinho = vizinho
                    melhorou = True
            
            if melhorou:
                talhoes_atuais = melhor_vizinho
                valor_atual = melhor_valor
        
        return talhoes_atuais, valor_atual
    
    def simulated_annealing(self, temp_inicial: float = 100.0, 
                           taxa_resfriamento: float = 0.95, 
                           iteracoes_por_temp: int = 20) -> Tuple[Set[Tuple[int, int]], float]:
        """
        Têmpera simulada: aceita pioras com probabilidade que diminui.
        Retorna (talhoes_selecionados, valor_objetivo)
        """
        # Estado inicial aleatório
        talhoes_atuais = set(random.sample(sorted(self.talhoes_livres), self.K))
        valor_atual = self.funcao_objetivo(talhoes_atuais)
        
        melhor_talhoes = talhoes_atuais.copy()
        melhor_valor = valor_atual
        
        temperatura = temp_inicial
        
        while temperatura > 1e-3:
            for _ in range(iteracoes_por_temp):
                # Gera vizinho aleatório
                vizinhos = self.obter_vizinhos(talhoes_atuais)
                vizinho = random.choice(vizinhos)
                valor_vizinho = self.funcao_objetivo(vizinho)
                
                # Critério de Metropolis
                delta = valor_vizinho - valor_atual
                
                if delta > 0 or random.random() < math.exp(delta / max(temperatura, 1e-8)):
                    talhoes_atuais = vizinho
                    valor_atual = valor_vizinho
                
                # Atualiza melhor solução global
                if valor_atual > melhor_valor:
                    melhor_talhoes = talhoes_atuais.copy()
                    melhor_valor = valor_atual
            
            temperatura *= taxa_resfriamento
        
        return melhor_talhoes, melhor_valor

def executar_buscas_locais(pomar_grade: List[List[str]], K: int = 15, 
                           num_execucoes: int = 30) -> dict:
    """
    Executa hill climbing e SA múltiplas vezes, retorna estatísticas.
    """
    bl = BuscaLocal(pomar_grade, K)
    
    resultados_hc = []
    resultados_sa = []
    
    for _ in range(num_execucoes):
        _, valor_hc = bl.hill_climbing()
        _, valor_sa = bl.simulated_annealing()
        
        resultados_hc.append(valor_hc)
        resultados_sa.append(valor_sa)
    
    return {
        "hill_climbing": {
            "media": mean(resultados_hc),
            "desvio": stdev(resultados_hc) if len(resultados_hc) > 1 else 0.0,
            "melhor": max(resultados_hc),
            "pior": min(resultados_hc),
            "valores": resultados_hc
        },
        "simulated_annealing": {
            "media": mean(resultados_sa),
            "desvio": stdev(resultados_sa) if len(resultados_sa) > 1 else 0.0,
            "melhor": max(resultados_sa),
            "pior": min(resultados_sa),
            "valores": resultados_sa
        }
    }
