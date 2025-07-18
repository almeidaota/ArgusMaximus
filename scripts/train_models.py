import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, r2_score
import joblib 
import constants as c



if __name__ == '__main__':
    df = pd.read_csv('data/real/consolidado.csv')

    x = df[c.COLS_TRAIN]
    x_train = x[x[c.COLS_CUTOUT] < c.TEST_CUTOUT].copy()
    x_test = x[x[c.COLS_CUTOUT] > c.TEST_CUTOUT].copy()

    y_train = x_train[c.COLS_TARGET].copy()
    y_test = x_test[c.COLS_TARGET].copy()

    x_train.drop(columns=[c.COLS_TARGET, c.COLS_CUTOUT], inplace=True)
    x_test.drop(columns=[c.COLS_TARGET,c.COLS_CUTOUT], inplace=True)

    forest = RandomForestRegressor(n_estimators=1000, random_state=42, n_jobs=-1, oob_score=True)
    forest.fit(x_train, y_train)
    joblib.dump(forest, 'models/pontos_preview.joblib')
    print('treinamento completo')

    previsoes = forest.predict(x_test)
    mae = mean_absolute_error(y_test, previsoes)
    r2 = r2_score(y_test, previsoes)

    importancias = pd.Series(forest.feature_importances_, index=x_train.columns)
    print("\n--- Features Mais Importantes ---")
    print(importancias.nlargest(15))

    print(f"\n--- Avaliação do Modelo ---")
    print(f"Erro Médio Absoluto (MAE): {mae:.4f}")
    print(f"R-quadrado (R²): {r2:.4f}")