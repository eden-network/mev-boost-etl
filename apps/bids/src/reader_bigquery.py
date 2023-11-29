import logging
from google.api_core.exceptions import BadRequest, Forbidden
from dotenv import load_dotenv
import os
import asyncio

load_dotenv()

dataset_id = os.getenv("DATASET_ID")
pod_name = os.getenv("POD_NAME")
pod_config_table_id = os.getenv("POD_CONFIG_TABLE_ID")
config_table_id = os.getenv("CONFIG_TABLE_ID")
bau_config_table_id = os.getenv("BAU_CONFIG_TABLE_ID")

async def async_get_latest_slot(client):
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(
        None,
        get_latest_slot,
        client
    )

def get_latest_slot(client) -> int:
    query = (f"select max(block_slot) as slot from `public-data-finance.crypto_ethereum2.beacon_blocks` where date(block_timestamp) = current_date('UTC')")
    try:
        logging.info("getting latest slot from bigquery")
        query_job = client.query(query)
        if query_job.errors:
            logging.error(f"sql query returned an error: {query_job.error_result}")
            return None

        results = query_job.result()

        rows = [dict(zip(row.keys(), row.values())) for row in results]
        if len(rows) == 0:
            logging.error(f"expected 1 or more rows but got: {len(rows)}")
            return None    
        
        if len(rows) > 1:
            logging.error(f"expected 1 row but got: {len(rows)}")
            return None    
            
        slot = rows[0]['slot']

        if slot is None:
            logging.error(f"invalid slot returned: None")
            return None

        slot = int(slot) - 50 # (take 50 slots off to give some buffer [50 * 12s = 10min])

        if slot < 4700567:
            logging.error(f"invalid slot returned: before first mev-boost slot (4700567)")
            return None

        return slot

    except BadRequest as e:
        logging.error(f"bad request error: {e}")
        return None
    except Forbidden as e:
        logging.error(f"forbidden error: {e}")
        return None
    except Exception as e:
        logging.error(f"an unexpected error occurred: {e}")
        return None

async def async_get_k8s_config(client):
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(
        None,
        get_k8s_config,
        client
    )

def get_k8s_config(client):    
    try:
        logging.info(f"getting k8s config for pod: {pod_name} from {dataset_id}.{pod_config_table_id}")

        query = (f"select pod_name, start_slot, end_slot from `{dataset_id}.{pod_config_table_id}` where pod_name = '{pod_name}'")
        query_job = client.query(query)
        if query_job.errors:
            logging.error(f"sql query returned an error: {query_job.error_result}")
            return None

        results = query_job.result()

        rows = [dict(zip(row.keys(), row.values())) for row in results]
        if len(rows) == 0:
            logging.error(f"expected 1 or more rows but got: {len(rows)}")
            return None    
        
        if len(rows) > 1:
            logging.error(f"expected 1 row but got: {len(rows)}")
            return None    
            
        return rows[0]

    except BadRequest as e:
        logging.error(f"bad request error: {e}")
        return None
    except Forbidden as e:
        logging.error(f"forbidden error: {e}")
        return None
    except Exception as e:
        logging.error(f"an unexpected error occurred: {e}")
        return None

async def async_relay_get_config(client):
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(
        None,
        get_relay_config,
        client
    )

def get_relay_config(client) -> int:
    query = (f"select relay, url as base_url, bids_rate_limit as rate_limit from `{dataset_id}.{config_table_id}` where active = true")
    try:
        logging.info("getting relay config from bigquery")
        query_job = client.query(query)
        if query_job.errors:
            logging.error(f"sql query returned an error: {query_job.error_result}")
            return None

        results = query_job.result()

        rows = [dict(zip(row.keys(), row.values())) for row in results]
        if len(rows) == 0:
            logging.error(f"expected 1 or more rows but got: {len(rows)}")
            return None                         

        return rows

    except BadRequest as e:
        logging.error(f"bad request error: {e}")
        return None
    except Forbidden as e:
        logging.error(f"forbidden error: {e}")
        return None
    except Exception as e:
        logging.error(f"an unexpected error occurred: {e}")
        return None
    
async def async_get_bau_config(client):
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(
        None,
        get_bau_config,
        client
    )

def get_bau_config(client) -> int:
    query = (f"select relay, end_slot from `{dataset_id}.{bau_config_table_id}`")
    try:
        logging.info("getting bau config from bigquery")
        query_job = client.query(query)
        if query_job.errors:
            logging.error(f"sql query returned an error: {query_job.error_result}")
            return None

        results = query_job.result()

        rows = [dict(zip(row.keys(), row.values())) for row in results]
        if len(rows) == 0:
            logging.error(f"expected 1 or more rows but got: {len(rows)}")
            return None                         

        return rows

    except BadRequest as e:
        logging.error(f"bad request error: {e}")
        return None
    except Forbidden as e:
        logging.error(f"forbidden error: {e}")
        return None
    except Exception as e:
        logging.error(f"an unexpected error occurred: {e}")
        return None    