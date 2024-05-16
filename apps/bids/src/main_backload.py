import sys, asyncio, logging
from os import getenv
from dotenv import load_dotenv
load_dotenv()

from custom_logger import JsonFormatter
from google.cloud.bigquery import Client
from bigquery.reader import async_get_k8s_config, async_relay_get_config
from bigquery.writer import async_update_k8s_config
from api.extractor import async_process_relay

logging_level = getenv("LOGGING_LEVEL", "INFO")
project_id = getenv("PROJECT_ID")

logging.basicConfig(level=logging.getLevelName(logging_level))
logging.getLogger("google.api_core").setLevel(logging.ERROR)
logging.getLogger("asyncio").setLevel(logging.ERROR)

log_handler = logging.StreamHandler()
json_formatter = JsonFormatter()
log_handler.setFormatter(json_formatter)
logging.getLogger().handlers = [log_handler]

async def async_execute() -> bool:
    logging.info("initializing bids backfill")

    try:
        bigquery_client = Client(project=project_id)

        config = await async_relay_get_config(bigquery_client)
        if config is None:
            logging.error("failed to get config")
            return False
        else:
            logging.info("got relay config from bigquery", extra={
                "config": config
            })

        pod_config = await async_get_k8s_config(bigquery_client)

        if pod_config is None:
            logging.error("failed to get k8s config")
            return False
        elif pod_config['process_attempted']:
            logging.info("k8s config already processed, waiting for 1 hour")
            await asyncio.sleep(3600)
            return True
        else:
            await asyncio.sleep(pod_config['order'] * 2) # stagger the start of each pod as to not result in lock contention for updating the k8s lock table
            result = await async_update_k8s_config(bigquery_client)
            if not result:
                logging.error("failed to update k8s config")
                return False
            else:
                logging.info("starting k8s config", extra={
                    "pod_config": pod_config
                })

        tasks = [async_process_relay(row['relay'], row['base_url'], row['rate_limit'], pod_config['start_slot'], pod_config['end_slot']) for row in config]

        results = await asyncio.gather(*tasks)

        for idx, success in enumerate(results):
            if success:
                logging.info(f"relay {config[idx]['relay']} processed successfully")
            else:
                logging.error(f"relay {config[idx]['relay']} processing failed")

        logging.info("bids backfill completed")        
        return True
        
    except Exception as e:
        logging.error(f"an unexpected error occurred: ${e}")
        return False

if __name__ == '__main__':    
    result = asyncio.run(async_execute())
    if not result:
        sys.exit(1)