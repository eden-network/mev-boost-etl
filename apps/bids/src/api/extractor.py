import asyncio, logging, time
from typing import List
from os import getenv
from google.cloud import storage, bigquery
from api.reader import async_download_bids
from transformer_json_bytes import async_transform_bytes, async_gzip_bytes
from cloud_storage.writer import async_push_bids_to_gcs
from bigquery.reader import async_get_latest_slot, async_relay_get_config, async_get_bau_config

project_id = getenv("PROJECT_ID")
batch_size_mb = int(getenv("BATCH_SIZE_MB", 1))

def should_upload(total_bytes: bytes, transformed_json_bytes: bytes) -> bool:
    return ((len(total_bytes) + len(transformed_json_bytes)) / (1024 * 1024)) > batch_size_mb

async def async_process_relay(relay: str, base_url: str, rate_limit: int, start_slot: int, end_slot: int) -> bool:
    logging.info(f"processing relay {relay} from {start_slot} to {end_slot} [total slots: {start_slot - end_slot}]")
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
        return await async_push_bids_to_gcs(client, gzipped_bytes, file_name)

    try:        
        slots_downloaded: List = []
        chunk_size = 50
        total_time = 0
        num_requests = 0
        for current_slot in range(start_slot, end_slot, -1):            
            url = f"{base_url}/builder_blocks_received?slot={current_slot}"            
            
            start_time = time.perf_counter()
            json_bytes = await async_download_bids(url)
            elapsed_time = time.perf_counter() - start_time
            
            total_time += elapsed_time
            num_requests += 1
            
            if num_requests % chunk_size == 0:
                average_time = total_time / chunk_size
                bytes_downloaded = len(total_bytes) / (1024 * 1024)
                logging.info(f"{relay} [current slot: {current_slot}, slots to go: {current_slot - end_slot}] average download time for last {chunk_size} slots: {average_time:.2f} seconds - mb since last upload: {bytes_downloaded:.2f} mb")
                total_time = 0  # Reset the total time for the next chunk

            if json_bytes is None:
                logging.error(f"failed bids extraction for {relay}, see previous message for more details", extra={
                    "payload": {
                        "url": url,
                        "relay": relay,
                        "slot": current_slot
                }})
                await asyncio.sleep(rate_limit)
                continue
            
            transformed_json_bytes = await async_transform_bytes(json_bytes, relay, current_slot)
            if transformed_json_bytes is None:
                await asyncio.sleep(rate_limit)
                continue

            if should_upload(total_bytes, transformed_json_bytes):
                if not await async_upload_data(private_client, relay, total_bytes, slots_downloaded):
                    logging.error(f"failed to upload bytes for {relay} to bigquery")
                    return False
                total_bytes = transformed_json_bytes
                slots_downloaded = [current_slot]
            else:
                total_bytes += transformed_json_bytes
                slots_downloaded.append(current_slot)

            await asyncio.sleep(rate_limit)

        if len(total_bytes) > 0 and not await async_upload_data(private_client, relay, total_bytes, slots_downloaded):
            logging.error(f"failed to upload last bytes for {relay} to bigquery")
            return False

    except Exception as e:
        logging.error(f"an error occurred while processing relay {relay}: {e}")
        return False

    return True


async def async_execute() -> bool:   
    logging.info("bids extraction running")
    client = bigquery.Client(project=project_id) 
    latest_slot = await async_get_latest_slot(client)
    if latest_slot is None:
        logging.error("failed to get latest slot")
        return False
    
    logging.info(f"latest slot: {latest_slot}")

    config = await async_relay_get_config(client)
    if config is None:
        logging.error("failed to get config")
        return False
    
    relays_from_config = {row['relay'] for row in config}

    bau_config = await async_get_bau_config(client)
    if bau_config is None:
        logging.error("failed to get bau config")
        return False
    
    bau_config_dict = {row['relay']: row for row in bau_config}
    
    if not relays_from_config.issubset(bau_config_dict.keys()):
        missing_relays = relays_from_config - set(bau_config_dict.keys())
        logging.error(f"missing relay(s) in bau_config: {missing_relays}")
        return False

    logging.info(f"starting bau config: {bau_config}")
    
    tasks = [async_process_relay(relay_config['relay'], relay_config['base_url'], relay_config['rate_limit'], latest_slot, bau_config_dict[relay_config['relay']]['end_slot']) for relay_config in config]

    results = await asyncio.gather(*tasks)

    for idx, success in enumerate(results):
        if success:
            logging.info(f"relay {config[idx]['relay']} extraction successful")
        else:            
            logging.error(f"relay {config[idx]['relay']} extraction failed")

    return True