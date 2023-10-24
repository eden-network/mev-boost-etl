from os import getenv
import logging
from google.cloud.bigquery import Client
from dotenv import load_dotenv
from api_reader import download_builder_blocks_received
from json_bytes_transformer import transform_bytes
from writer_big_query import push_builder_blocks_received_to_big_query
from time import sleep

load_dotenv()

logging_level = getenv("LOGGING_LEVEL", "INFO")
project_id_private = getenv("PROJECT_ID_PRIVATE")
batch_size_mb = int(getenv("BATCH_SIZE_MB", 16))

logging.basicConfig(level=logging.getLevelName(logging_level))

def process_relay(relay: str, base_url: str, rate_limit: int) -> bool:
    logging.info(f"processing relay {relay}")
    private_client = Client(project=project_id_private)
    start_slot = 7566959
    number_of_slots = 1000
    current_slot = start_slot
    total_bytes = b''
    try:        
        while current_slot > start_slot - number_of_slots:
            url = f"{base_url}?slot={current_slot}"
            json_bytes = download_builder_blocks_received(url)
            transformed_json_bytes = transform_bytes(json_bytes, relay, current_slot)            
            if ((len(total_bytes) + len(transformed_json_bytes)) / (1024 * 1024)) > batch_size_mb:
                result = push_builder_blocks_received_to_big_query(private_client, total_bytes, relay)
                if result:
                    total_bytes = b''
                else:
                    logging.error(f"failed to upload bytes for {relay} to bigquery")
                    return False
            else:
                total_bytes += transformed_json_bytes
            current_slot -= 1
            sleep(rate_limit)
        
        if len(total_bytes) > 0:
            result = push_builder_blocks_received_to_big_query(private_client, total_bytes, relay)
            if not result:
                logging.error(f"failed to upload last bytes for {relay} to bigquery")
                return False

    except Exception as e:
        logging.error(f"An error occurred while processing relay {relay}: {e}")
        return False

    return True

def execute():        
    logging.info("initializing block received backfill")    

    relay_metadata = [
        {'base_url': "https://agnostic-relay.net/relay/v1/data/bidtraces/proposer_payload_delivered/proposer_payload_delivered", 'relay': "agnostic", 'rate_limit': 2},
        {'base_url': "https://bloxroute.max-profit.blxrbdn.com/relay/v1/data/bidtraces/proposer_payload_delivered", 'relay': "bloxrouteMaxProfit", 'rate_limit': 2},
        {'base_url': "https://relay.edennetwork.io/relay/v1/data/bidtraces/proposer_payload_delivered", 'relay': "eden", 'rate_limit': 2},
        {'base_url': "https://relay.ultrasound.money/relay/v1/data/bidtraces/proposer_payload_delivered", 'relay': "ultrasound", 'rate_limit': 2},
        {'base_url': "https://boost-relay.flashbots.net/relay/v1/data/bidtraces/proposer_payload_delivered", 'relay': "flashbots", 'rate_limit': 2}
    ]

    for row in relay_metadata:
        success = True
        success = process_relay(row['relay'], row['base_url'], row['rate_limit'])
        if success:
            logging.info(f"relay {row['relay']} processed successfully")
        else:            
            logging.error(f"relay {row['relay']} processing failed")            

if __name__ == '__main__':
    execute()