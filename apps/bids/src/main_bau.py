import sys
import asyncio
from os import getenv
import logging
from google.cloud.bigquery import Client
from dotenv import load_dotenv
from reader_bigquery import async_get_bau_config, async_relay_get_config, async_get_latest_slot
from processor_relay import async_process_relay
from main_transfer import async_execute as async_transfer
from executor_bigquery import async_execute as async_load

load_dotenv()

logging_level = getenv("LOGGING_LEVEL", "INFO")
project_id_private = getenv("PROJECT_ID_PRIVATE")

logging.basicConfig(level=logging.getLevelName(logging_level))
logging.getLogger("asyncio").setLevel(logging.ERROR)

async def async_extract(client: Client) -> bool:    
    latest_slot = await async_get_latest_slot(client)
    logging.info(f"latest slot: {latest_slot}")

    config = await async_relay_get_config(client)
    if config is None:
        logging.error("failed to get config")
        return False
    
    relays_from_config = {row['relay'] for row in config}

    bau_config = await async_get_bau_config(client)
    if bau_config is None:
        logging.error("failed to get bau config")
        return False
    
    bau_config_dict = {row['relay']: row for row in bau_config}
    
    if not relays_from_config.issubset(bau_config_dict.keys()):
        missing_relays = relays_from_config - set(bau_config_dict.keys())
        logging.error(f"missing relay(s) in bau_config: {missing_relays}")
        return False

    logging.info(f"starting bau config: {bau_config}")
    
    tasks = [async_process_relay(relay_config['relay'], relay_config['base_url'], relay_config['rate_limit'], latest_slot, bau_config_dict[relay_config['relay']]['end_slot']) for relay_config in config]

    results = await asyncio.gather(*tasks)

    for idx, success in enumerate(results):
        if success:
            logging.info(f"relay {config[idx]['relay']} extraction successful")
        else:            
            logging.error(f"relay {config[idx]['relay']} extraction failed")

    return True

async def async_execute():        
    logging.info("initializing bids bau")    

    try:
        bigquery_client = Client(project=project_id_private)        

        if await async_extract(bigquery_client) is False:
            sys.exit(1)        

        if await async_transfer() is False:
            sys.exit(1)

        if await async_load(bigquery_client) is False:
            sys.exit(1)

    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")        
        sys.exit(1)

if __name__ == '__main__':
    asyncio.run(async_execute())