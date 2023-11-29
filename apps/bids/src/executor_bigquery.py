import asyncio
import logging
from google.cloud.bigquery import Client
from google.api_core.exceptions import BadRequest, Forbidden
from dotenv import load_dotenv
from os import getenv

load_dotenv()

dataset_id = getenv("DATASET_ID")
load_sp = getenv("LOAD_SP_ID")

async def async_execute(client) -> bool:
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(
        None,
        execute,
        client             
    )

def execute(client: Client) -> bool:
    logging.info(f"executing stored procedure {dataset_id}.{load_sp}")
    try:        
        sql = f"CALL `{dataset_id}.{load_sp}`();"        
        query_job = client.query(sql)                
        if query_job.errors:
            logging.error(f"execution of stored procedure returned an error: {query_job.error_result}")
            return False                                
        
        result = query_job.result()

        return True  
    
    except BadRequest as e:
        logging.error(f"bad request error: {e}")
        return False
    except Forbidden as e:
        logging.error(f"forbidden error: {e}")
        return False     
    except Exception as e:
        logging.error(f"unexpected error occurred when executing stored procedure: {e}")
        return False        