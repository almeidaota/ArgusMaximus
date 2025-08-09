import pandas as pd
import lightgbm as lgb
from sklearn.metrics import mean_absolute_error, r2_score
import joblib 
import settings
import etl_functions as ef
import logging
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

def montar_analise_dados(df):
    logging.info("[TRAINING MODEL] Iniciando a criação de features com médias móveis.")
    for column in settings.SCOUT:
        nova_coluna = f'media_{column}_5_rodadas'
        series_media = df.groupby(settings.ATLETAS_ID)[column].rolling(window=5, min_periods=1).mean().shift(1)
        df[nova_coluna] = series_media.reset_index(level=0, drop=True)
    logging.info("[TRAINING MODEL] Criação de features de média móvel concluída.")
    return df

def train_model():
    logging.info("--- Iniciando script de treinamento de modelo ---")

    logging.info("[TRAINING MODEL] Lendo dados de 'data/real/consolidado.csv'.")
    df = pd.read_csv(f'{settings.DATA_REAL_PATH}/consolidado.csv')
    logging.info(f"[TRAINING MODEL] Dados carregados com sucesso.")
    
    df = montar_analise_dados(df)
    
    x = df[settings.COLS_TRAIN]
    
    logging.info(f"[TRAINING MODEL] Dividindo os dados em treino e teste com base na rodada de corte: {settings.TEST_CUTOUT}.")
    x_train = x[x[settings.COLS_CUTOUT] < settings.TEST_CUTOUT].copy()
    x_test = x[x[settings.COLS_CUTOUT] > settings.TEST_CUTOUT].copy()

    y_train = x_train[settings.COLS_TARGET].copy()
    y_test = x_test[settings.COLS_TARGET].copy()

    x_train.drop(columns=[settings.COLS_TARGET, settings.COLS_CUTOUT], inplace=True)
    x_test.drop(columns=[settings.COLS_TARGET,settings.COLS_CUTOUT], inplace=True)
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
    
    joblib.dump(forest, f'{settings.MODELS_PATH}/pontos_preview.joblib')
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