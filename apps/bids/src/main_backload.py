import time
import sys
import asyncio
import json
from os import getenv, path

import logging
from google.cloud.bigquery import Client
from dotenv import load_dotenv
from reader_bigquery import async_get_k8s_config, async_relay_get_config
from writer_bigquery import async_update_k8s_config
from processor_relay import async_process_relay

load_dotenv()

logging_level = getenv("LOGGING_LEVEL", "INFO")
project_id_private = getenv("PROJECT_ID_PRIVATE")

class JsonFormatter(logging.Formatter):
    def format(self, record):
        payload = getattr(record, 'payload', None)
        log_record = {
            'severity': record.levelname,
            'message': record.getMessage(),
            'name': record.name,
            'timestamp': self.formatTime(record, self.datefmt),            
            'additional_info': {
                'file_name': record.filename,
                'function_name': record.funcName,
                'line_no': record.lineno,
                'payload': payload or {}
            }
        }
        return json.dumps(log_record)

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
        bigquery_client = Client(project=project_id_private)

        config = await async_relay_get_config(bigquery_client)
        if config is None:
            logging.error("failed to get config")
            sys.exit(1)
        else:
            logging.info("got relay config from bigquery", extra={
                "payload": config
            })   

        pod_config = await async_get_k8s_config(bigquery_client)

        if pod_config is None:
            logging.error("failed to get k8s config")
            sys.exit(1)
        elif pod_config['process_attempted']:
            logging.info("k8s config already processed, waiting for 1 hour", extra={
                "payload": pod_config             
            })
            await asyncio.sleep(3600)
            return True
        else:
            result = await async_update_k8s_config(bigquery_client)
            if not result:
                logging.error("failed to update k8s config")
                sys.exit(1)
            else:
                logging.info("starting k8s config", extra={
                    "payload": pod_config             
                })

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
        logging.error(f"an unexpected error occurred: ${e}")
        sys.exit(1)

if __name__ == '__main__':    
    result = asyncio.run(async_execute())
    if not all(result):
        sys.exit(1)