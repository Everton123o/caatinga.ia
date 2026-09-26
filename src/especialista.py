from typing import Set, List, Tuple, Optional

class SistemaEspecialista:
    """Sistema de regras para decisão de manejo de talhões"""
    
    def __init__(self):
        self.regras = self._definir_regras()
        self.fatos = {}
        self.tracos = []
    
    def _definir_regras(self) -> List[dict]:
        """Define base de regras do domínio agrícola"""
        return [
            {
                "id": "R1",
                "conclusao": "inspecionar_prioridade_alta",
                "condicoes": [
                    ("armadilha_positiva", True),
                    ("umidade_alta", True),
                    ("dias_desde_pulverizacao", lambda x: x > 14)
                ],
                "descricao": "Armadilha positiva + umidade alta + >14 dias desde pulverização"
            },
            {
                "id": "R2",
                "conclusao": "aplicar_inseticida",
                "condicoes": [
                    ("suspeita_praga", True),
                    ("fase_desenvolvimento", "vulneravel"),
                    ("condicoes_clima_favoravel", True)
                ],
                "descricao": "Suspeita confirmada + praga em fase vulnerável + clima favorável"
            },
            {
                "id": "R3",
                "conclusao": "monitoramento_intenso",
                "condicoes": [
                    ("historico_infestacao", True),
                    ("estacao_risco", True)
                ],
                "descricao": "Talhão com histórico + estação de risco"
            },
            {
                "id": "R4",
                "conclusao": "inspecao_urgente",
                "condicoes": [
                    ("multiplos_sinais", True),
                    ("proximidade_talhoes_afetados", True)
                ],
                "descricao": "Múltiplos sinais + próximo a talhões já afetados"
            },
            {
                "id": "R5",
                "conclusao": "manutencao_rotina",
                "condicoes": [
                    ("inspecao_urgente", False),
                    ("monitoramento_intenso", False),
                    ("inspecionar_prioridade_alta", False)
                ],
                "descricao": "Nenhuma ameaça identificada — manutenção de rotina"
            },
            {
                "id": "R6",
                "conclusao": "isolamento_preventivo",
                "condicoes": [
                    ("proximidade_talhoes_afetados", True),
                    ("aplicar_inseticida", False)
                ],
                "descricao": "Próximo a afetados mas ainda sem confirmação — isolamento preventivo"
            },
            {
                "id": "R7",
                "conclusao": "suspensao_pulverizacao",
                "condicoes": [
                    ("chuva_proxima", True),
                    ("aplicar_inseticida", True)
                ],
                "descricao": "Chuva prevista e aplicação programada — suspender até condições melhores"
            },
            {
                "id": "R8",
                "conclusao": "consultar_agronomista",
                "condicoes": [
                    ("suspeita_praga", True),
                    ("confianca_diagnostico", lambda x: x < 0.7)
                ],
                "descricao": "Suspeita mas baixa confiança — consultar especialista"
            }
        ]
    
    def definir_fatos(self, fatos: dict):
        """Define fatos conhecidos (observações)"""
        self.fatos = fatos
        self.tracos = []
    
    def _avalia_condicao(self, fato: str, operador) -> bool:
        """Avalia se uma condição é satisfeita"""
        if fato not in self.fatos:
            return False
        
        valor = self.fatos[fato]
        
        if isinstance(operador, bool):
            return valor == operador
        elif callable(operador):
            try:
                return operador(valor)
            except:
                return False
        else:
            return valor == operador
    
    def _encadeamento_para_tras(self, objetivo: str, 
                                visitados: Set[str] = None,
                                profundidade: int = 0) -> Tuple[bool, List[str]]:
        """
        Encadeamento para trás: tenta provar uma conclusão.
        Retorna (sucesso, cadeia_de_regras_aplicadas)
        """
        if visitados is None:
            visitados = set()
        
        if objetivo in visitados:
            return False, []  # Evita loops
        
        # Se o fato já é conhecido, retorna sucesso
        if objetivo in self.fatos and self.fatos[objetivo]:
            return True, [f"FATO: {objetivo}"]
        
        visitados.add(objetivo)
        indent = "  " * profundidade
        
        # Procura regra que conclui este objetivo
        for regra in self.regras:
            if regra["conclusao"] == objetivo:
                todas_condicoes_ok = True
                cadeia_local = [f"{indent}REGRA {regra['id']}: {regra['descricao']}"]
                subcadeias = []
                
                for condicao_fato, condicao_operador in regra["condicoes"]:
                    if not self._avalia_condicao(condicao_fato, condicao_operador):
                        # Tenta provar recursivamente
                        sucesso, subcadeia = self._encadeamento_para_tras(
                            condicao_fato, visitados.copy(), profundidade + 1
                        )
                        
                        if not sucesso:
                            todas_condicoes_ok = False
                            break
                        else:
                            subcadeias.extend(subcadeia)
                    else:
                        subcadeias.append(f"{indent}  ✓ {condicao_fato} = {self.fatos[condicao_fato]}")
                
                if todas_condicoes_ok:
                    cadeia_local.extend(subcadeias)
                    cadeia_local.append(f"{indent}➜ CONCLUSÃO: {objetivo}")
                    return True, cadeia_local
        
        return False, []
    
    def consultar(self, objetivo: str) -> Tuple[bool, str]:
        """
        Interface pública: consulta se um objetivo é satisfeito.
        Retorna (resultado, traço_explicativo)
        """
        self.tracos = []
        sucesso, cadeia = self._encadeamento_para_tras(objetivo)
        
        traço_formatado = "\n".join(cadeia)
        return sucesso, traço_formatado
    
    def diagnosticar_talho(self, observacoes: dict) -> dict:
        """Exemplo de uso: diagnostica ações para um talhão"""
        self.definir_fatos(observacoes)
        
        diagnostico = {}
        objetivos_principais = [
            "inspecionar_prioridade_alta",
            "aplicar_inseticida",
            "monitoramento_intenso",
            "inspecao_urgente",
            "manutencao_rotina",
            "isolamento_preventivo",
            "suspensao_pulverizacao",
            "consultar_agronomista"
        ]
        
        for objetivo in objetivos_principais:
            sucesso, traço = self.consultar(objetivo)
            diagnostico[objetivo] = {
                "concluido": sucesso,
                "cadeia": traço
            }
        
        return diagnostico

# Exemplo de uso
if __name__ == "__main__":
    se = SistemaEspecialista()
    
    # Cenário 1: talhão suspeito
    observacoes_1 = {
        "armadilha_positiva": True,
        "umidade_alta": True,
        "dias_desde_pulverizacao": 20,
        "suspeita_praga": True,
        "fase_desenvolvimento": "vulneravel",
        "condicoes_clima_favoravel": True,
        "historico_infestacao": False,
        "estacao_risco": False,
        "multiplos_sinais": False,
        "proximidade_talhoes_afetados": False,
        "chuva_proxima": False,
        "confianca_diagnostico": 0.85
    }
    
    print("=" * 60)
    print("DIAGNÓSTICO - Talhão com sinais de alerta")
    print("=" * 60)
    
    diagnostico = se.diagnosticar_talho(observacoes_1)
    for acao, resultado in diagnostico.items():
        if resultado["concluido"]:
            print(f"\n✓ {acao.upper()}")
            print(resultado["cadeia"])
    
    # Cenário 2: talhão seguro
    observacoes_2 = {
        "armadilha_positiva": False,
        "umidade_alta": False,
        "dias_desde_pulverizacao": 7,
        "suspeita_praga": False,
        "fase_desenvolvimento": "robusta",
        "condicoes_clima_favoravel": False,
        "historico_infestacao": False,
        "estacao_risco": False,
        "multiplos_sinais": False,
        "proximidade_talhoes_afetados": False,
        "chuva_proxima": False,
        "confianca_diagnostico": 1.0
    }
    
    print("\n" + "=" * 60)
    print("DIAGNÓSTICO - Talhão sem ameaças")
    print("=" * 60)
    
    diagnostico = se.diagnosticar_talho(observacoes_2)
    for acao, resultado in diagnostico.items():
        if resultado["concluido"]:
            print(f"\n✓ {acao.upper()}")
            print(resultado["cadeia"])
