import requests
import pandas as pd 


def cartola_api(endpoint):
    url = "https://api.cartola.globo.com/" + endpoint 
    response = requests.get(f'{url}')
    response.raise_for_status()
    data = response.json()
    return data 


def status_mercado():
    status_mercado = cartola_api('mercado/status')
    status_mercado = status_mercado['status_mercado']
    return True if status_mercado == 1 else False


def rename_columns_df_atletas(df):
    df.rename(columns={
    'apelido': 'atletas.apelido',
    'apelido_abreviado': 'atletas.apelido_abreviado',
    'atleta_id': 'atletas.atleta_id',
    'clube_id': 'atletas.clube_id',
    'entrou_em_campo': 'atletas.entrou_em_campo',
    'foto': 'atletas.foto',
    'jogos_num': 'atletas.jogos_num',
    'media_num': 'atletas.media_num',
    'nome': 'atletas.nome',
    'pontos_num': 'atletas.pontos_num',
    'posicao_id': 'atletas.posicao_id',
    'preco_num': 'atletas.preco_num',
    'rodada_id': 'atletas.rodada_id',
    'slug': 'atletas.slug',
    'status_id': 'atletas.status_id',
    'variacao_num': 'atletas.variacao_num'
    }, inplace=True)
    return df


def gerar_df_atletas():
    dados_atletas = cartola_api('atletas/mercado')
    df_atletas = pd.DataFrame(dados_atletas['atletas'])
    df_scouts = pd.json_normalize(df_atletas['scout'])
    df_scouts = df_scouts.fillna(0).astype(int)
    df_atletas = pd.concat([df_atletas, df_scouts], axis=1)
    df_atletas.drop(columns='scout', inplace=True)
    df_atletas = rename_columns_df_atletas(df_atletas)
    df_atletas.drop(columns=['atletas.foto'], inplace=True)

    return df_atletas


def gerar_df_partidas(rodada):
    df_partidas = pd.DataFrame(cartola_api(f'partidas/{rodada}')['partidas'])
    df_partidas = df_partidas.drop(columns=['transmissao', 'status_transmissao_tr', 'periodo_tr',
                                            'status_cronometro_tr', 'inicio_cronometro_tr']) #drop useless columns
    df_partidas['aproveitamento_mandante'] = df_partidas['aproveitamento_mandante'].apply(calculo_aproveitamento)
    df_partidas['aproveitamento_visitante'] = df_partidas['aproveitamento_visitante'].apply(calculo_aproveitamento)

    return df_partidas

def gerar_df_mergeado(df_partidas, df_atletas):
    df_mandante = pd.merge(df_atletas, df_partidas, left_on='atletas.clube_id', right_on='clube_casa_id', how='inner')
    df_visitante = pd.merge(df_atletas, df_partidas, left_on='atletas.clube_id', right_on='clube_visitante_id', how='inner')
    df_mergeado = pd.concat([df_mandante, df_visitante])
    df_mergeado['mandante'] = df_mergeado.apply(lambda x: False if x['clube_visitante_id'] != x['atletas.clube_id'] else True, axis=1)

    return df_mergeado


def calculo_aproveitamento(aproveitamento: list) -> int:
    vitorias = aproveitamento.count('v')
    empates = aproveitamento.count('e')
    aproveitamento = (vitorias*3 + empates*1) / (5 * 3) * 100
    return round(aproveitamento, 2)
