import logging, asyncio, time
from typing import List
from google.cloud import storage, bigquery
from os import getenv
from api.reader import async_download
from transformer_json_bytes import async_transform_bytes, async_gzip_bytes
from cloud_storage.writer import async_push_to_gcs
from bigquery.reader import async_get_config, async_get_latest_slot

project_id = getenv("PROJECT_ID")
rate_limit = int(getenv("RATE_LIMIT_SECONDS", 2))
batch_size_mb = int(getenv("BATCH_SIZE_MB", 3))

def should_upload(total_bytes: bytes, transformed_json_bytes: bytes) -> bool:
    return ((len(total_bytes) + len(transformed_json_bytes)) / (1024 * 1024)) > batch_size_mb

async def async_process(relay: str, base_url: str, start_slot: int, end_slot: int, batch_size: int) -> bool:    
    logging.info(f"processing relay {relay} from {start_slot} to {end_slot}")
    if start_slot <= end_slot:
        logging.error(f"invalid slot range for {relay}: {start_slot} - {end_slot}")
        return False
    
    private_client = storage.Client(project=project_id)
    total_bytes = b''

    async def async_upload_data(client, relay, data: bytes, slots_downloaded) -> bool:
        gzipped_bytes = await async_gzip_bytes(data)
        if gzipped_bytes is None:
            return False

        start_slot = slots_downloaded[-1]
        end_slot = slots_downloaded[0]
        file_name = f"{relay}_{start_slot}_{end_slot}_{len(slots_downloaded)}.gz"
        logging.info(f"checkpoint: {relay}: {start_slot}-{end_slot} -> {len(slots_downloaded)} slots", extra={
            "payload": {
                "filter": "metrics",
                "relay": relay,
                "file_name": file_name,                
                "start_slot": start_slot,
                "end_slot": end_slot,
                "slots_downloaded": len(slots_downloaded),
                "ndjson_mb" : len(data) / (1024 * 1024), 
                "gzip_mb" : len(gzipped_bytes) / (1024 * 1024)
                }
            }
        )
        return await async_push_to_gcs(client, gzipped_bytes, file_name)

    try:      
        slots_downloaded: List = []
        chunk_size = 100
        total_time = 0
        num_requests = 0
        current_slot = start_slot
        while current_slot > end_slot:
            url = f"{base_url}/proposer_payload_delivered?limit={batch_size}&cursor={current_slot}"

            start_time = time.perf_counter()
            json_bytes = await async_download(url)
            elapsed_time = time.perf_counter() - start_time

            total_time += elapsed_time
            num_requests += 1

            if num_requests % chunk_size == 0:
                average_time = total_time / chunk_size
                logging.info(f"average download time for last {chunk_size} slots: {average_time:.2f} seconds")
                total_time = 0  # Reset the total time for the next chunk
            
            if json_bytes is None:
                logging.error(f"failed payloads extraction for {relay}, see previous message for more details", extra={
                    "payload": {
                        "url": url,
                        "relay": relay,
                        "slot": current_slot
                }})
                break
                        
            transformed_json_bytes, new_slots_downloaded = await async_transform_bytes(json_bytes, relay, end_slot)            

            if transformed_json_bytes is None and new_slots_downloaded is None:
                return False
            elif transformed_json_bytes is None and len(new_slots_downloaded) == 0:
                break

            current_slot = new_slots_downloaded[-1] - 1

            if should_upload(total_bytes, transformed_json_bytes):
                if not await async_upload_data(private_client, relay, total_bytes, slots_downloaded):
                    logging.error(f"failed to upload bytes for {relay} to bigquery")
                    return False
                total_bytes = transformed_json_bytes
                slots_downloaded = new_slots_downloaded
            else:
                total_bytes += transformed_json_bytes
                slots_downloaded.extend(new_slots_downloaded)

            await asyncio.sleep(rate_limit)

        if len(total_bytes) > 0 and not await async_upload_data(private_client, relay, total_bytes, slots_downloaded):
            logging.error(f"failed to upload last bytes for {relay} to bigquery")
            return False

    except Exception as e:
        logging.error(f"an error occurred while processing relay {relay}: {e}")
        return False

    return True

async def async_execute() -> bool:
    logging.info("payloads extraction running")
    client = bigquery.Client(project=project_id)
    latest_slot = await async_get_latest_slot(client)
    logging.info(f"latest slot: {latest_slot}")
    if latest_slot is None:
        return False

    config_list = await async_get_config(client)
    logging.info(f"payloads config: {config_list}")
    if config_list is None:
        return False

    tasks = [async_process(config['relay'], config['url'], latest_slot, config['head_slot'], config['batch_size']) for config in config_list]

    results = await asyncio.gather(*tasks)

    for idx, success in enumerate(results):
        if success:
            logging.info(f"relay {config_list[idx]['relay']} extraction successful")
        else:            
            logging.error(f"relay {config_list[idx]['relay']} extraction failed")

    return True