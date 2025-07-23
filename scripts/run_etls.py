import joblib
import pandas as pd 
import etl_functions as ef
import constants as c

def generate_historical_data():
    df_atletas = ef.gerar_df_atletas()
    rodada = df_atletas[c.RODADA_ID][0]
    df_partidas = ef.gerar_df_partidas(rodada)
    df_final = ef.gerar_df_mergeado(df_partidas, df_atletas)
    df_final.to_csv(f'data/real/rodada-{rodada}.csv')
    df_consolidado = pd.read_csv(f'data/real/consolidado.csv')
    df_consolidado = pd.concat([df_consolidado, df_final]).sort_values(c.RODADA_ID)
    df_consolidado.to_csv(f'data/real/consolidado.csv', index=False)

def generate_preview_data():
    df_atletas = ef.gerar_df_atletas()
    rodada = df_atletas[c.RODADA_ID][0] + 1
    df_atletas[c.RODADA_ID] = rodada 
    df_partidas = ef.gerar_df_partidas(rodada)

    df_atletas_partidas_merged = ef.gerar_df_mergeado(df_partidas, df_atletas)
    df_full = pd.read_csv('data/real/consolidado.csv')
    df_full = pd.concat([df_full, df_atletas_partidas_merged])
    df_rodada = df_full[df_full[c.RODADA_ID]== rodada].copy()
    df_full = df_full[df_full[c.RODADA_ID] < rodada]
    
    media_historica_por_atleta = df_full.groupby(c.ATLETAS_ID)[c.PONTOS_NUM].mean()
    df_rodada[c.PONTOS_NUM] = media_historica_por_atleta
    df_rodada_predictions = df_rodada[c.COLS_TRAIN].copy()
    df_rodada_predictions.drop(columns = [c.COLS_CUTOUT, c.COLS_TARGET], inplace=True)

    forest = joblib.load('models/pontos_preview.joblib')
    predictions = forest.predict(df_rodada_predictions)

    df_rodada_predictions[c.PREVISAO_PONTOS] = predictions
    df_rodada_predictions = df_rodada_predictions[[c.ATLETAS_ID, c.PREVISAO_PONTOS]]
    df_rodada_predictions = df_rodada_predictions.merge(df_rodada, on=c.ATLETAS_ID)
    df_rodada_predictions.sort_values(by=c.PREVISAO_PONTOS, ascending=False, inplace=True)
    df_rodada_predictions.to_csv(f'data/previews/rodada_{rodada}.csv', index=False)


if __name__ == '__main__':
    status_mercado = ef.status_mercado()
    if status_mercado:
        generate_historical_data()
        generate_preview_data()