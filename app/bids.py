import asyncio
from os import getenv
import logging
from google.cloud.bigquery import Client
from google.cloud import storage
from dotenv import load_dotenv
from api_reader import download_bids, async_download_bids
from json_bytes_transformer import transform_bytes, gzip_bytes, async_transform_bytes, async_gzip_bytes
from writer_big_query import push_bids_to_big_query
from writer_cloud_storage import async_push_bids_to_gcs
from time import sleep

load_dotenv()

logging_level = getenv("LOGGING_LEVEL", "INFO")
project_id_private = getenv("PROJECT_ID_PRIVATE")
batch_size_mb = int(getenv("BATCH_SIZE_MB", 1))

logging.basicConfig(level=logging.getLevelName(logging_level))
logging.getLogger("google.api_core").setLevel(logging.ERROR)
logging.getLogger("asyncio").setLevel(logging.ERROR)

def should_upload(total_bytes: bytes, transformed_json_bytes: bytes) -> bool:
    return ((len(total_bytes) + len(transformed_json_bytes)) / (1024 * 1024)) > batch_size_mb

async def async_process_relay(relay: str, base_url: str, rate_limit: int) -> bool:
    logging.info(f"processing relay {relay}")
    private_client = storage.Client(project=project_id_private)
    start_slot = 7565615
    number_of_slots = 100
    total_bytes = b''

    async def async_upload_data(client, relay, data: bytes, end_slot) -> bool:
        gzipped_bytes = await async_gzip_bytes(data)
        if gzipped_bytes is None:
            return False

        logging.debug(f"file size check:\nndjson Mb:\t{len(data) / (1024 * 1024)}\ngzip Mb:\t{len(gzipped_bytes) / (1024 * 1024)}")
        return await async_push_bids_to_gcs(client, gzipped_bytes, f"{relay}_{end_slot}.gz")

    try:
        last_slot: int = None
        for current_slot in range(start_slot, start_slot - number_of_slots, -1):
            last_slot = current_slot
            url = f"{base_url}?slot={current_slot}"
            json_bytes = await async_download_bids(url)
            
            if json_bytes is None:
                await asyncio.sleep(rate_limit)
                continue

            transformed_json_bytes = await async_transform_bytes(json_bytes, relay, current_slot)
            if transformed_json_bytes is None:
                await asyncio.sleep(rate_limit)
                continue

            if should_upload(total_bytes, transformed_json_bytes):
                if not await async_upload_data(private_client, relay, total_bytes, end_slot=last_slot):
                    logging.error(f"failed to upload bytes for {relay} to bigquery")
                    return False
                total_bytes = transformed_json_bytes
            else:
                total_bytes += transformed_json_bytes

            await asyncio.sleep(rate_limit)

        if len(total_bytes) > 0 and not await async_upload_data(private_client, relay, total_bytes, last_slot):
            logging.error(f"failed to upload last bytes for {relay} to bigquery")
            return False

    except Exception as e:
        logging.error(f"An error occurred while processing relay {relay}: {e}")
        return False

    return True

def process_relay(relay: str, base_url: str, rate_limit: int) -> bool:
    logging.info(f"processing relay {relay}")
    private_client = Client(project=project_id_private)
    start_slot = 7566611
    number_of_slots = 1000
    total_bytes = b''

    def upload_data(client, relay, data: bytes) -> bool:
        gzipped_bytes = gzip_bytes(data)
        if gzipped_bytes is None:
            return False

        logging.debug(f"file size check:\nndjson Mb:\t{len(data) / (1024 * 1024)}\ngzip Mb:\t{len(gzipped_bytes) / (1024 * 1024)}")
        return push_bids_to_big_query(client, gzipped_bytes, relay)

    try:
        for current_slot in range(start_slot, start_slot - number_of_slots, -1):
            url = f"{base_url}?slot={current_slot}"
            json_bytes = download_bids(url)
            
            if json_bytes is None:
                sleep(rate_limit)
                continue

            transformed_json_bytes = transform_bytes(json_bytes, relay, current_slot)
            if transformed_json_bytes is None:
                sleep(rate_limit)
                continue

            if should_upload(total_bytes, transformed_json_bytes):
                if not upload_data(private_client, relay, total_bytes):
                    logging.error(f"failed to upload bytes for {relay} to bigquery")
                    return False
                total_bytes = transformed_json_bytes
            else:
                total_bytes += transformed_json_bytes

            sleep(rate_limit)

        if len(total_bytes) > 0 and not upload_data(private_client, relay, total_bytes):
            logging.error(f"failed to upload last bytes for {relay} to bigquery")
            return False

    except Exception as e:
        logging.error(f"An error occurred while processing relay {relay}: {e}")
        return False

    return True


def execute():        
    logging.info("initializing block received backfill")    

    relay_metadata = [
        {'base_url': "https://agnostic-relay.net/relay/v1/data/bidtraces/builder_blocks_received", 'relay': "agnostic", 'rate_limit': 2},
        {'base_url': "https://bloxroute.max-profit.blxrbdn.com/relay/v1/data/bidtraces/builder_blocks_received", 'relay': "bloxrouteMaxProfit", 'rate_limit': 2},
        {'base_url': "https://relay.edennetwork.io/relay/v1/data/bidtraces/builder_blocks_received", 'relay': "eden", 'rate_limit': 2},
        {'base_url': "https://relay.ultrasound.money/relay/v1/data/bidtraces/builder_blocks_received", 'relay': "ultrasound", 'rate_limit': 2},
        {'base_url': "https://boost-relay.flashbots.net/relay/v1/data/bidtraces/builder_blocks_received", 'relay': "flashbots", 'rate_limit': 2}
    ]

    for row in relay_metadata:
        success = True
        success = process_relay(row['relay'], row['base_url'], row['rate_limit'])
        if success:
            logging.info(f"relay {row['relay']} processed successfully")
        else:            
            logging.error(f"relay {row['relay']} processing failed")    

async def async_execute():        
    logging.info("initializing block received backfill")    

    relay_metadata = [
        {'base_url': "https://agnostic-relay.net/relay/v1/data/bidtraces/builder_blocks_received", 'relay': "agnostic", 'rate_limit': 2},
        {'base_url': "https://bloxroute.regulated.blxrbdn.com/relay/v1/data/bidtraces/builder_blocks_received", 'relay': "bloxrouteRegulated", 'rate_limit': 2},
        {'base_url': "https://mainnet.aestus.live/relay/v1/data/bidtraces/builder_blocks_received", 'relay': "aestus", 'rate_limit': 2},
        {'base_url': "https://mainnet-relay.securerpc.com/relay/v1/data/bidtraces/builder_blocks_received", 'relay': "manifold", 'rate_limit': 2},
        {'base_url': "https://bloxroute.max-profit.blxrbdn.com/relay/v1/data/bidtraces/builder_blocks_received", 'relay': "bloxrouteMaxProfit", 'rate_limit': 2},
        {'base_url': "https://relay.edennetwork.io/relay/v1/data/bidtraces/builder_blocks_received", 'relay': "eden", 'rate_limit': 2},
        {'base_url': "https://relay.ultrasound.money/relay/v1/data/bidtraces/builder_blocks_received", 'relay': "ultrasound", 'rate_limit': 2},
        {'base_url': "https://boost-relay.flashbots.net/relay/v1/data/bidtraces/builder_blocks_received", 'relay': "flashbots", 'rate_limit': 2}
    ]

    tasks = [async_process_relay(row['relay'], row['base_url'], row['rate_limit']) for row in relay_metadata]

    results = await asyncio.gather(*tasks)

    for idx, success in enumerate(results):
        if success:
            logging.info(f"relay {relay_metadata[idx]['relay']} processed successfully")
        else:            
            logging.error(f"relay {relay_metadata[idx]['relay']} processing failed")

    return results            

if __name__ == '__main__':
    asyncio.run(async_execute())                    

# if __name__ == '__main__':
#     execute()