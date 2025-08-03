import pandas as pd
import lightgbm as lgb
from sklearn.metrics import mean_absolute_error, r2_score
import joblib 
import constants as c
import etl_functions as ef
import logging

logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

def montar_analise_dados(df):
    logging.info("[TRAINING MODEL] Iniciando a criação de features com médias móveis.")
    for column in c.SCOUT:
        nova_coluna = f'media_{column}_5_rodadas'
        series_media = df.groupby(c.ATLETAS_ID)[column].rolling(window=5, min_periods=1).mean().shift(1)
        df[nova_coluna] = series_media.reset_index(level=0, drop=True)
    logging.info("[TRAINING MODEL] Criação de features de média móvel concluída.")
    return df

if __name__ == '__main__':
    logging.info("--- Iniciando script de treinamento de modelo ---")
    
    logging.info("[TRAINING MODEL] Lendo dados de 'data/real/consolidado.csv'.")
    df = pd.read_csv('data/real/consolidado.csv')
    logging.info(f"[TRAINING MODEL] Dados carregados com sucesso.")
    
    df = montar_analise_dados(df)
    
    x = df[c.COLS_TRAIN]
    
    logging.info(f"[TRAINING MODEL] Dividindo os dados em treino e teste com base na rodada de corte: {c.TEST_CUTOUT}.")
    x_train = x[x[c.COLS_CUTOUT] < c.TEST_CUTOUT].copy()
    x_test = x[x[c.COLS_CUTOUT] > c.TEST_CUTOUT].copy()

    y_train = x_train[c.COLS_TARGET].copy()
    y_test = x_test[c.COLS_TARGET].copy()

    x_train.drop(columns=[c.COLS_TARGET, c.COLS_CUTOUT], inplace=True)
    x_test.drop(columns=[c.COLS_TARGET,c.COLS_CUTOUT], inplace=True)
    logging.info(f"[TRAINING MODEL] Divisão concluída. Tamanho do treino: {x_train.shape[0]} amostras. Tamanho do teste: {x_test.shape[0]} amostras.")

    forest = lgb.LGBMRegressor(
        n_estimators=1000,
        learning_rate=0.05,
        num_leaves=31,
        random_state=42,
        n_jobs=-1,
    )
    
    logging.info("[TRAINING MODEL] Iniciando treinamento do modelo LGBMRegressor...")
    forest.fit(x_train, y_train)
    logging.info("[TRAINING MODEL] Treinamento completo.")
    
    joblib.dump(forest, 'models/pontos_preview.joblib')
    logging.info("[TRAINING MODEL] Modelo salvo com sucesso em 'models/pontos_preview.joblib'.")

    logging.info("[TRAINING MODEL] Realizando previsões no conjunto de teste para avaliação.")
    previsoes = forest.predict(x_test)
    mae = mean_absolute_error(y_test, previsoes)
    r2 = r2_score(y_test, previsoes)

    importancias = pd.Series(forest.feature_importances_, index=x_train.columns)
    
    importancias_str = importancias.nlargest(15).to_string()
    
    logging.info(f"\n\n--- Features Mais Importantes ---\n{importancias_str}\n")
    logging.info(f"\n--- Avaliação do Modelo ---\n"
                 f"Erro Médio Absoluto (MAE): {mae:.4f}\n"
                 f"R-quadrado (R²): {r2:.4f}\n")
    
    logging.info("--- Script de treinamento de modelo finalizado ---")