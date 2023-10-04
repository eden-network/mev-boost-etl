import logging
from google.api_core.exceptions import BadRequest, Forbidden
from dotenv import load_dotenv
import os

load_dotenv()

dataset_id = os.getenv("DATASET_ID")
metadata_view_id = os.getenv("METADATA_VIEW_ID")

def get_relay_metadata(client):
    """
    Get relay metadata from the BigQuery.
    """
    query = (f"select relay, url, batch_size, head_slot, tail_slot, back_fill from `{dataset_id}.{metadata_view_id}` where active = true")
    try:
        logging.info("getting relay metadata from bigquery")
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
    
    for row in rows:
        if row.get('head_slot') is None or row.get('tail_slot') is None:
            logging.error(f"expected all head_slot and tail_slot columns to be non-null")
            return None
        
    return rows