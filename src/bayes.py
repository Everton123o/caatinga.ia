"""
Cálculos de Bayes para o sensor de pragas do Caatinga.AI
P(D|+) = P(+|D) × P(D) / P(+)
onde D = infestado, + = sensor positivo
"""

from typing import Tuple

def calcular_ppv(prevalencia: float, sensibilidade: float, 
                 taxa_falso_positivo: float) -> Tuple[float, float]:
    """
    Calcula o Valor Preditivo Positivo (PPV)
    P(infestado | sensor positivo)
    
    Args:
        prevalencia: P(infestado) — proporção de talhões infectados
        sensibilidade: P(positivo | infestado) — taxa de detecção correta
        taxa_falso_positivo: P(positivo | não infestado) — taxa de alarmes falsos
    
    Returns:
        (ppv, p_positivo) — PPV e probabilidade total de positivo
    """
    # P(+) = P(+|D)×P(D) + P(+|¬D)×P(¬D)
    p_positivo = (sensibilidade * prevalencia) + (taxa_falso_positivo * (1 - prevalencia))
    
    if p_positivo == 0:
        return 0.0, 0.0
    
    # P(D|+) = P(+|D) × P(D) / P(+)
    ppv = (sensibilidade * prevalencia) / p_positivo
    
    return ppv, p_positivo

def analisar_sensor(parametros_sensor: dict) -> dict:
    """
    Análise completa do desempenho do sensor
    """
    prev = parametros_sensor["prevalencia"]
    sens = parametros_sensor["sensibilidade"]
    tfp = parametros_sensor["taxa_falso_positivo"]
    talhoes_semana = parametros_sensor["talhoes_por_semana"]
    
    ppv, p_pos = calcular_ppv(prev, sens, tfp)
    
    # 4.3b: A cada 100 alertas, quantos são falsos?
    falsos_por_100 = (1 - ppv) * 100
    
    # 4.3c: Falsos positivos por semana
    # Número de alertas por semana
    alertas_por_semana = talhoes_semana * p_pos
    falsos_por_semana = alertas_por_semana * (1 - ppv)
    horas_por_semana = (falsos_por_semana * 12) / 60  # 12 min por inspeção
    
    return {
        "prevalencia": prev,
        "sensibilidade": sens,
        "taxa_falso_positivo": tfp,
        "talhoes_por_semana": talhoes_semana,
        "ppv": ppv,
        "p_positivo": p_pos,
        "falsos_por_100": falsos_por_100,
        "alertas_por_semana": alertas_por_semana,
        "falsos_por_semana": falsos_por_semana,
        "horas_por_semana": horas_por_semana
    }

def aumentar_sensibilidade(parametros_atuais: dict, 
                          nova_sensibilidade: float) -> dict:
    """
    Simula aumento de sensibilidade mantendo taxa de falsos positivos
    """
    params_novos = parametros_atuais.copy()
    params_novos["sensibilidade"] = nova_sensibilidade
    return analisar_sensor(params_novos)

def relatorio_bayes(parametros: dict) -> str:
    """Gera relatório formatado dos cálculos de Bayes"""
    
    analise = analisar_sensor(parametros)
    
    prev = parametros["prevalencia"]
    sens = parametros["sensibilidade"]
    tfp = parametros["taxa_falso_positivo"]
    talhoes = parametros["talhoes_por_semana"]
    
    ppv = analise["ppv"]
    p_pos = analise["p_positivo"]
    falsos_100 = analise["falsos_por_100"]
    alertas_sem = analise["alertas_por_semana"]
    falsos_sem = analise["falsos_por_semana"]
    horas = analise["horas_por_semana"]
    
    texto = f"""
ANÁLISE BAYESIANA DO SENSOR DE PRAGAS
======================================

Parâmetros do sensor:
- Prevalência (P(infestado)): {prev:.4f} ({prev*100:.2f}%)
- Sensibilidade (P(+ | infestado)): {sens:.4f} ({sens*100:.2f}%)
- Taxa de falso positivo (P(+ | não-infestado)): {tfp:.4f} ({tfp*100:.2f}%)
- Talhões inspecionados/semana: {talhoes}

4.3(a) Cálculo de P(infestado | sensor positivo):
────────────────────────────────────────────────
P(+) = P(+|D)×P(D) + P(+|¬D)×P(¬D)
P(+) = {sens:.4f}×{prev:.4f} + {tfp:.4f}×{1-prev:.4f}
P(+) = {sens*prev:.6f} + {tfp*(1-prev):.6f}
P(+) = {p_pos:.6f}

P(D|+) = P(+|D)×P(D) / P(+)
P(D|+) = ({sens:.4f}×{prev:.4f}) / {p_pos:.6f}
P(D|+) = {sens*prev:.6f} / {p_pos:.6f}
P(D|+) = {ppv:.4f} ({ppv*100:.2f}%)

➜ RESULTADO: A cada alerta do sensor, a probabilidade de 
   haver realmente uma praga é {ppv*100:.1f}%.

4.3(b) Falsos positivos em 100 alertas:
──────────────────────────────────────
A cada 100 alertas do meu sistema, cerca de {falsos_100:.0f} serão falsos.

4.3(c) Carga de falsos positivos por semana:
─────────────────────────────────────────────
Alertas totais por semana: {alertas_sem:.1f}
Falsos positivos por semana: {falsos_sem:.1f}
Tempo gasto em falsos alertas: {horas:.2f} horas/semana

4.3(d) Simulação: aumentar sensibilidade para 99,9%:
──────────────────────────────────────────────────
"""
    
    analise_99_9 = aumentar_sensibilidade(parametros, 0.999)
    ppv_novo = analise_99_9["ppv"]
    falsos_100_novo = analise_99_9["falsos_por_100"]
    horas_novo = analise_99_9["horas_por_semana"]
    
    texto += f"""
Com sensibilidade 99,9% (mantendo taxa de falso positivo em {tfp:.4f}):
- Novo PPV: {ppv_novo:.4f} ({ppv_novo*100:.2f}%)
- Falsos por 100: {falsos_100_novo:.0f}
- Horas/semana em falsos: {horas_novo:.2f}

Melhoria: {((ppv_novo - ppv) / ppv * 100):.1f}% no PPV

ANÁLISE CRÍTICA:
O problema NÃO melhorou significativamente. O gargalo não é a 
sensibilidade, e sim a taxa de falso positivo. Quando prevalência é baixa
(rara), o denominador de Bayes é dominado por falsos positivos.

Solução prática: reduzir taxa_falso_positivo é mais impactante que 
aumentar sensibilidade em doenças raras.
"""
    
    return texto

if __name__ == "__main__":
    # Teste com parâmetros fictícios
    params_teste = {
        "prevalencia": 0.02,
        "sensibilidade": 0.95,
        "taxa_falso_positivo": 0.05,
        "talhoes_por_semana": 1200
    }
    
    print(relatorio_bayes(params_teste))
