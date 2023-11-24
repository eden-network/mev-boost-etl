import os
import sys
import logging
from google.cloud.bigquery import Client
from reader_big_query import get_config
from relay_data_functions import process_relay
from file_operations import update_file_names, reset_local_storage
from writer_big_query import push_to_big_query
from dotenv import load_dotenv
from executor_bigquery import execute as load

load_dotenv()

logging_level = os.getenv("LOGGING_LEVEL", "INFO")
project_id = os.getenv("PROJECT_ID")

logging.basicConfig(level=logging.getLevelName(logging_level))

def extract(client: Client) -> bool:
    """
    Main function that executes the ETL process.
    """            
    relay_metadata = get_config(client)
    if relay_metadata is None:
        return False

    reset_local_storage()
    
    successful_relays = []
    unsuccessful_relays = []
    for row in relay_metadata:
        success = True
        success = process_relay(row['relay'], row['url'], row['batch_size'], row['head_slot'], row['tail_slot'])
        if success:
            successful_relays.append(row['relay'])
            logging.info(f"relay {row['relay']} processed successfully")
        else:
            unsuccessful_relays.append(row['relay'])
            logging.error(f"relay {row['relay']} processing failed")        

    if len(successful_relays) > 0:
        logging.info(f"{len(successful_relays)} relays processed successfully, pushing data to bigquery")
        update_file_names('data/*_*.ndjson')
        push_to_big_query(client)
    else:
        logging.error("no relays were processed successfully, exiting")
        return False

    if len(unsuccessful_relays) > 0:
        logging.error(f"{len(unsuccessful_relays)} relays failed to process, see error logs for details")
    
    return True

def execute():
    logging.info("initializing payloads etl")    

    try:
        client = Client(project=project_id)    

        if extract(client) is False:
            sys.exit(1)

        if load(client) is False:
            sys.exit(1)

    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")        
        sys.exit(1)

if __name__ == '__main__':
    execute()