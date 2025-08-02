import joblib
import pandas as pd 
import etl_functions as ef
import constants as c
import os 
import logging

logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

def generate_historical_data():
    logging.info("[HISTORICAL DATA] Iniciando geração de dados históricos.")
    df_atletas = ef.gerar_df_atletas()
    rodada = df_atletas[c.RODADA_ID][0]
    logging.info(f"[HISTORICAL DATA] Dados de atletas para a rodada {rodada} obtidos.")
    
    caminho_arquivo_rodada = f'data/real/rodada-{rodada}.csv'
    if not os.path.exists(caminho_arquivo_rodada):
        df_partidas = ef.gerar_df_partidas(rodada)
        logging.info(f"[HISTORICAL DATA] Dados de partidas para a rodada {rodada} obtidos.")
        
        df_final = ef.gerar_df_mergeado(df_partidas, df_atletas)
        logging.info("[HISTORICAL DATA] Merge de dados de partidas e atletas concluído.")
        
        df_final.to_csv(caminho_arquivo_rodada, index=False)
        logging.info(f"[HISTORICAL DATA] Dados salvos em '{caminho_arquivo_rodada}'.")
        
        df_consolidado = pd.read_csv('data/real/consolidado.csv')
        df_consolidado = pd.concat([df_consolidado, df_final]).sort_values(c.RODADA_ID)
        df_consolidado.to_csv('data/real/consolidado.csv', index=False)
        logging.info("[HISTORICAL DATA] Arquivo 'consolidado.csv' atualizado com a nova rodada.")
    else:
        logging.warning(f"[HISTORICAL DATA] Rodada {rodada} já inclusa em data/real. Encerrando execução.") 

def generate_preview_data():
    logging.info("[PREVIEW DATA] Iniciando geração de dados para previsão.")
    df_atletas = ef.gerar_df_atletas()
    rodada = df_atletas[c.RODADA_ID][0] + 1
    logging.info(f"[PREVIEW DATA] Rodada para previsão: {rodada}.")

    caminho_arquivo_previsao = f'data/previews/rodada-{rodada}.csv'
    if not os.path.exists(caminho_arquivo_previsao):
        logging.info(f"[PREVIEW DATA] Arquivo de previsão '{caminho_arquivo_previsao}' não encontrado. Gerando nova previsão.")
        df_atletas[c.RODADA_ID] = rodada 
        df_partidas = ef.gerar_df_partidas(rodada)
        logging.info("[PREVIEW DATA] Dados de partidas e atletas para a previsão obtidos.")

        df_atletas_partidas_merged = ef.gerar_df_mergeado(df_partidas, df_atletas)
        df_full = pd.read_csv('data/real/consolidado.csv')
        df_atletas_partidas_merged = ef.media_scout(df_atletas_partidas_merged, df_full)
        logging.info("[PREVIEW DATA] Cálculo de médias de scouts para atletas concluído.")
        
        df_full = pd.concat([df_full, df_atletas_partidas_merged])

        df_rodada = df_full[df_full[c.RODADA_ID] == rodada].copy()
        df_full = df_full[df_full[c.RODADA_ID] < rodada]

        media_historica_por_atleta = df_full.groupby(c.ATLETAS_ID)[c.PONTOS_NUM].mean()
        df_rodada[c.PONTOS_NUM] = media_historica_por_atleta
        df_rodada_predictions = df_rodada[c.COLS_TRAIN].copy()
        df_rodada_predictions.drop(columns=[c.COLS_CUTOUT, c.COLS_TARGET], inplace=True)

        logging.info("[PREVIEW DATA] Carregando modelo 'models/pontos_preview.joblib'.")
        forest = joblib.load('models/pontos_preview.joblib')
        
        logging.info(f"[PREVIEW DATA] Realizando previsões para a rodada {rodada}.")
        predictions = forest.predict(df_rodada_predictions)

        df_rodada_predictions[c.PREVISAO_PONTOS] = predictions
        df_rodada_predictions = df_rodada_predictions[[c.ATLETAS_ID, c.PREVISAO_PONTOS]]
        df_rodada_predictions = df_rodada_predictions.merge(df_rodada, on=c.ATLETAS_ID)
        df_rodada_predictions.sort_values(by=c.PREVISAO_PONTOS, ascending=False, inplace=True)
        
        df_rodada_predictions.to_csv(caminho_arquivo_previsao, index=False)
        logging.info(f"[PREVIEW DATA] Previsões salvas em '{caminho_arquivo_previsao}'.")
    else:
        logging.warning(f"[PREVIEW DATA] Previsão para a rodada {rodada} já inclusa em data/previews. Nenhuma ação tomada.")

if __name__ == '__main__':
    logging.info("--- Iniciando processo de ETL ---")
    status_mercado = ef.status_mercado()
    if status_mercado:
        logging.info("Mercado aberto. Executando ETLs.")
        generate_historical_data()
        generate_preview_data()
    else:
        logging.warning("Mercado fechado. Processo não executado.")
    logging.info("--- Processo de ETL finalizado ---")