import time
import sys
import asyncio
from os import getenv, path
import logging
from google.cloud.bigquery import Client
from dotenv import load_dotenv
from reader_bigquery import async_get_k8s_config, async_relay_get_config
from processor_relay import async_process_relay

load_dotenv()

logging_level = getenv("LOGGING_LEVEL", "INFO")
project_id_private = getenv("PROJECT_ID_PRIVATE")

logging.basicConfig(level=logging.getLevelName(logging_level))
logging.getLogger("google.api_core").setLevel(logging.ERROR)
logging.getLogger("asyncio").setLevel(logging.ERROR)

async def async_execute() -> bool:        
    logging.info("initializing bids backfill")    

    try:
        bigquery_client = Client(project=project_id_private)

        config = await async_relay_get_config(bigquery_client)
        if config is None:
            logging.error("failed to config")
            sys.exit(1)       

        pod_config = await async_get_k8s_config(bigquery_client)

        if pod_config is None:
            logging.error("failed to get k8s config")
            sys.exit(1)
        else: 
            logging.info(f"starting k8s config: {pod_config}")

        tasks = [async_process_relay(row['relay'], row['base_url'], row['rate_limit'], pod_config['start_slot'], pod_config['end_slot']) for row in config]

        results = await asyncio.gather(*tasks)

        for idx, success in enumerate(results):
            if success:
                logging.info(f"relay {config[idx]['relay']} processed successfully")
            else:            
                logging.error(f"relay {config[idx]['relay']} processing failed")

        logging.info("bids backfill completed")
        return results
        
    except Exception as e:
        logging.error(f"an unexpected error occurred: {e}")
        sys.exit(1)

if __name__ == '__main__':    
    current_directory = path.dirname(path.abspath(__file__))
    file_path = path.join(current_directory, '.lock_file')
    logging.info(f"lock file path: {file_path}")
    
    if path.exists(file_path):
        logging.info("lock file exists, waiting for 1 hour")
        time.sleep(3600)
    else:
        logging.info("lock file does not exist, creating lock file")
        with open(file_path, 'w') as file:
            file.write(f'first run: {time.time()}')

    result = asyncio.run(async_execute())
    if not all(result):
        sys.exit(1)