import run_etls
import train_models
import logging
import etl_functions as ef
if __name__ == '__main__':
    logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S')

    logging.info("--- Iniciando processo de ETL ---")

    try:
        status_mercado = ef.status_mercado()
        if status_mercado:
            logging.info("Mercado aberto. Executando ETLs.")
            run_etls.generate_historical_data()
            train_models.train_model()
            run_etls.generate_preview_data()
        else:
            logging.warning("Mercado fechado. Processo não executado.")
            logging.info("--- Processo de ETL finalizado ---")
    except Exception as e:
        logging.error('ERRO: ', e)