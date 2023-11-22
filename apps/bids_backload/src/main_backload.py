import asyncio
from os import getenv
import logging
from google.cloud.bigquery import Client
from dotenv import load_dotenv
from reader_bigquery import async_get_pod_config, async_relay_get_config
from processor_relay import async_process_relay

load_dotenv()

logging_level = getenv("LOGGING_LEVEL", "INFO")
project_id_private = getenv("PROJECT_ID_PRIVATE")

logging.basicConfig(level=logging.getLevelName(logging_level))
logging.getLogger("google.api_core").setLevel(logging.ERROR)
logging.getLogger("asyncio").setLevel(logging.ERROR)

async def async_execute():        
    logging.info("initializing bids backfill")    

    try:
        bigquery_client = Client(project=project_id_private)

        config = await async_relay_get_config(bigquery_client)
        if config is None:
            logging.error("failed to config")
            return        

        pod_config = await async_get_pod_config(bigquery_client)

        if pod_config is None:
            logging.error("failed to get pod config")
            return
        else: 
            logging.info(f"starting pod config: {pod_config}")

        tasks = [async_process_relay(row['relay'], row['base_url'], row['rate_limit'], pod_config['start_slot'], pod_config['end_slot']) for row in config]

        results = await asyncio.gather(*tasks)

        for idx, success in enumerate(results):
            if success:
                logging.info(f"relay {config[idx]['relay']} processed successfully")
            else:            
                logging.error(f"relay {config[idx]['relay']} processing failed")

        return results
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")        

if __name__ == '__main__':
    asyncio.run(async_execute())