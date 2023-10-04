import os
import sys
import logging
from google.cloud import bigquery
from reader_big_query import get_relay_metadata
from relay_data_functions import process_relay
from file_operations import update_file_names, reset_local_storage
from writer_big_query import push_to_big_query
from dotenv import load_dotenv

load_dotenv()

logging_level = os.getenv("LOGGING_LEVEL", "INFO")
project_id_public = os.getenv("PROJECT_ID_PUBLIC")
project_id_private = os.getenv("PROJECT_ID_PRIVATE")

# Setting up logging configuration
logging.basicConfig(level=logging.getLevelName(logging_level))

def execute():
    """
    Main function that executes the ETL process.
    """
    # Initializing the BigQuery client
    public_client = bigquery.Client(project=project_id_public)
    private_client = bigquery.Client(project=project_id_private)    

    logging.info("initializing relay data etl")    

    relay_metadata = get_relay_metadata(private_client)
    if relay_metadata is None:
        sys.exit(1)

    reset_local_storage()
    
    successful_relays = []
    for row in relay_metadata:
        success = True
        success = process_relay(row['relay'], row['url'], row['batch_size'], row['head_slot'], row['tail_slot'], row['back_fill'])
        if success:
            successful_relays.append(row['relay'])
            logging.info(f"relay {row['relay']} processed successfully")
        else:
            logging.error(f"relay {row['relay']} processing failed")        

    if len(successful_relays) > 0:
        logging.info(f"{len(successful_relays)} relays processed successfully, pushing data to bigquery")
        update_file_names('data/*_*.ndjson')
        push_to_big_query(private_client)
    else:
        logging.error("no relays were processed successfully, exiting")


if __name__ == '__main__':
    execute()