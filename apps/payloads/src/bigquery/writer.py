import logging, asyncio
from google.cloud.bigquery import Client, LoadJobConfig, SourceFormat
from google.api_core.exceptions import BadRequest, Forbidden
from os import getenv

dataset_id = getenv("DATASET_ID")
table_id_staging = getenv("TABLE_ID_STAGING")

async def async_write(client, bucket_uri):
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(
        None,
        write,
        client,
        bucket_uri        
    )

def write(client: Client, bucket_uri: str) -> bool:
    logging.info(f"loading data from {bucket_uri} to BigQuery {table_id_staging}")
    try:
        table_ref = client.dataset(dataset_id).table(table_id_staging)
        job_config = LoadJobConfig()
        job_config.source_format = SourceFormat.NEWLINE_DELIMITED_JSON
                
        job = client.load_table_from_uri(
            bucket_uri,
            table_ref,
            location='US',
            job_config=job_config
        )
        job.result()
        logging.info(f"data from {bucket_uri} loaded into BigQuery")

    except BadRequest as e:
        logging.error(f"bad request error when loading from {bucket_uri} to BigQuery {table_id_staging}: {e}")
        return False
    except Forbidden as e:
        logging.error(f"forbidden error when loading from {bucket_uri} to BigQuery {table_id_staging}: {e}")
        return False
    except Exception as e:
        logging.error(f"unexpected error occurred when loading from {bucket_uri} to BigQuery {table_id_staging}: {e}")
        return False    

    return True