import logging
from google.api_core.exceptions import BadRequest, Forbidden
from dotenv import load_dotenv
import os
import asyncio

load_dotenv()

dataset_id = os.getenv("DATASET_ID")
pod_name = os.getenv("POD_NAME")
bids_pod_config_table_id = os.getenv("BIDS_POD_CONFIG_TABLE_ID")

def get_latest_slot(client) -> int:
    """
    Get latest from the BigQuery.
    """
    query = (f"select max(block_slot) as slot from from `public-data-finance.crypto_ethereum2.beacon_blocks` where date(block_timestamp) = current_date('UTC')")
    try:
        logging.info("getting latest slot from bigquery")
        query_job = client.query(query)
        if query_job.errors:
            logging.error(f"sql query returned an error: {query_job.error_result}")
            return None

        results = query_job.result()

    except BadRequest as e:
        logging.error(f"bad request error: {e}")
        return None
    except Forbidden as e:
        logging.error(f"forbidden error: {e}")
        return None
    except Exception as e:
        logging.error(f"an unexpected error occurred: {e}")
        return None

    rows = [dict(zip(row.keys(), row.values())) for row in results]
    if len(rows) == 0:
        logging.error(f"expected 1 or more rows but got: {len(rows)}")
        return None    
    
    if len(rows) > 1:
        logging.error(f"expected 1 row but got: {len(rows)}")
        return None    
        
    return rows[0].slot

async def async_get_pod_config(client):
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(
        None,
        get_pod_config,
        client
    )

def get_pod_config(client):
    """
    Get pod config from the BigQuery.
    """
    query = (f"select pod_name, start_slot, end_slot from `{dataset_id}.{bids_pod_config_table_id}` where pod_name = '{pod_name}'")
    try:
        logging.info("getting pod config from bigquery")
        query_job = client.query(query)
        if query_job.errors:
            logging.error(f"sql query returned an error: {query_job.error_result}")
            return None

        results = query_job.result()

    except BadRequest as e:
        logging.error(f"bad request error: {e}")
        return None
    except Forbidden as e:
        logging.error(f"forbidden error: {e}")
        return None
    except Exception as e:
        logging.error(f"an unexpected error occurred: {e}")
        return None

    rows = [dict(zip(row.keys(), row.values())) for row in results]
    if len(rows) == 0:
        logging.error(f"expected 1 or more rows but got: {len(rows)}")
        return None    
    
    if len(rows) > 1:
        logging.error(f"expected 1 row but got: {len(rows)}")
        return None    
        
    return rows[0]