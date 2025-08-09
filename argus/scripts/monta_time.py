import pandas as pd
import pulp
import time
from pathlib import Path

# --- FUNÇÃO DE OTIMIZAÇÃO PARA O TIME TITULAR (sem alterações) ---
def otimizar_time(df_jogadores, custo_maximo, formacao, nome_problema="Otimizacao"):
    prob = pulp.LpProblem(nome_problema, pulp.LpMaximize)
    jogadores_vars = pulp.LpVariable.dicts("Jogador", df_jogadores.index, cat='Binary')
    prob += pulp.lpSum([df_jogadores.loc[i, 'previsao_pontos'] * jogadores_vars[i] for i in df_jogadores.index])
    prob += pulp.lpSum([df_jogadores.loc[i, 'atletas.preco_num'] * jogadores_vars[i] for i in df_jogadores.index]) <= custo_maximo, "Custo_Total"
    for pos_id, qtd in formacao.items():
        if qtd > 0:
            prob += pulp.lpSum([jogadores_vars[i] for i in df_jogadores.index if df_jogadores.loc[i, 'atletas.posicao_id'] == pos_id]) == qtd, f"Posicao_{pos_id}"
    total_de_vagas = sum(formacao.values())
    prob += pulp.lpSum(jogadores_vars.values()) == total_de_vagas, "Restricao_Total_Jogadores"
    prob.solve(pulp.PULP_CBC_CMD(msg=0))
    if prob.status == pulp.LpStatusOptimal:
        return [i for i in df_jogadores.index if jogadores_vars[i].varValue == 1]
    return []

# --- NOVA FUNÇÃO PARA ENCONTRAR O BANCO COM BASE NA SUA REGRA ---
def encontrar_banco_pela_regra(df_titulares, df_nao_selecionados):
    """
    Encontra o banco de reservas seguindo a regra:
    Para cada posição, o reserva deve ser mais barato que o titular mais barato da mesma posição.
    Dentre os candidatos, seleciona o de maior pontuação prevista.
    """
    reservas_encontrados = []
    posicoes_para_banco = {1: 'Goleiro', 2: 'Lateral', 3: 'Zagueiro', 4: 'Meia', 5: 'Atacante'}

    for pos_id, pos_nome in posicoes_para_banco.items():
        # 1. Achar o titular mais barato da posição
        titulares_da_posicao = df_titulares[df_titulares['atletas.posicao_id'] == pos_id]
        if titulares_da_posicao.empty:
            continue
        preco_min_titular = titulares_da_posicao['atletas.preco_num'].min()

        # 2. Achar candidatos a reserva (mesma posição E mais baratos que o titular)
        candidatos_reserva = df_nao_selecionados[
            (df_nao_selecionados['atletas.posicao_id'] == pos_id) &
            (df_nao_selecionados['atletas.preco_num'] < preco_min_titular)
        ]

        # 3. Dentre os candidatos, escolher o de maior pontuação prevista
        if not candidatos_reserva.empty:
            melhor_reserva = candidatos_reserva.loc[candidatos_reserva['previsao_pontos'].idxmax()]
            reservas_encontrados.append(melhor_reserva)

    if not reservas_encontrados:
        return pd.DataFrame()
        
    return pd.concat(reservas_encontrados, axis=1).T


def exibir_time(df_time, titulo):
    """Formata e exibe um time."""
    print("=" * 60)
    print(titulo.upper())
    print("=" * 60)
    if df_time.empty:
        print("Nenhum jogador encontrado com os critérios definidos.")
        return
    colunas_exibir = ['atletas.apelido', 'posicao', 'atletas.clube.id.full.name', 'atletas.preco_num', 'previsao_pontos']
    df_ordenado = df_time.sort_values(by='atletas.posicao_id')
    df_para_exibir = df_ordenado[colunas_exibir]
    print(df_para_exibir.to_string(index=False))


# --- Bloco Principal ---
try:
    script_path = Path(__file__).resolve()
    project_root = script_path.parent.parent
    data_previews_path = f'{project_root}/data/previews'

    df = pd.read_csv(f'{data_previews_path}/rodada-19.csv')
except FileNotFoundError:
    print("Arquivo 'data/previews/rodada-17.csv' não encontrado.")
    exit()

posicoes_map = {1: 'Goleiro', 2: 'Lateral', 3: 'Zagueiro', 4: 'Meia', 5: 'Atacante', 6: 'Técnico'}
custo_total_disponivel = 107.56

formacoes_validas = {
    "4-3-3": {1: 1, 2: 2, 3: 2, 4: 3, 5: 3, 6: 1}, "4-4-2": {1: 1, 2: 2, 3: 2, 4: 4, 5: 2, 6: 1},
    "4-5-1": {1: 1, 2: 2, 3: 2, 4: 5, 5: 1, 6: 1}, "5-3-2": {1: 1, 2: 2, 3: 3, 4: 3, 5: 2, 6: 1},
    "5-4-1": {1: 1, 2: 2, 3: 3, 4: 4, 5: 1, 6: 1}, "3-4-3": {1: 1, 2: 0, 3: 3, 4: 4, 5: 3, 6: 1},
    "3-5-2": {1: 1, 2: 0, 3: 3, 4: 5, 5: 2, 6: 1},
}

df_provaveis = df[df['atletas.status_id'] == 7].copy()
df_provaveis['posicao'] = df_provaveis['atletas.posicao_id'].map(posicoes_map)

print("Otimizando... Encontrando a melhor formação e time titular.")
start_time = time.time()
melhor_pontuacao, melhor_time_indices, melhor_formacao_nome = -1, [], ""

for nome, formacao in formacoes_validas.items():
    indices_time_atual = otimizar_time(df_provaveis, custo_total_disponivel, formacao, nome_problema=f"Otimizacao_{nome}")
    if not indices_time_atual: continue
    df_time_atual = df_provaveis.loc[indices_time_atual]
    pontuacao_atual = df_time_atual['previsao_pontos'].sum()
    if pontuacao_atual > melhor_pontuacao:
        melhor_pontuacao, melhor_time_indices, melhor_formacao_nome = pontuacao_atual, indices_time_atual, nome

print(f"Otimização de titulares completa em {time.time() - start_time:.2f} segundos.\n")

df_titulares = df_provaveis.loc[melhor_time_indices]
custo_time_titular = df_titulares['atletas.preco_num'].sum()

# --- CHAMANDO A NOVA FUNÇÃO DO BANCO BASEADA NA SUA REGRA ---
print("Encontrando banco de reservas pela regra de custo por posição...")
df_nao_selecionados = df_provaveis.drop(melhor_time_indices)
df_reservas = encontrar_banco_pela_regra(df_titulares, df_nao_selecionados)


# --- EXIBIÇÃO DOS RESULTADOS ---
titulo_time_principal = f"TIME IDEAL (Formação: {melhor_formacao_nome})"
exibir_time(df_titulares, titulo_time_principal)
print("\n--- Sumário do Time Titular ---")
print(f"Custo Total: C$ {custo_time_titular:.2f}")
print(f"Pontuação Prevista: {df_titulares['previsao_pontos'].sum():.2f}")

exibir_time(df_reservas, "\nBanco de Reservas (Mais Barato que os Titulares)")
print("\n--- Sumário do Banco de Reservas ---")
print(f"Custo do Banco: C$ {df_reservas['atletas.preco_num'].sum():.2f}")
print(f"Pontuação Prevista do Banco: {df_reservas['previsao_pontos'].sum():.2f}")