import asyncio
from os import getenv
import logging
from google.cloud import storage
from dotenv import load_dotenv
from reader_api import async_download_bids
from transformer_json_bytes import async_transform_bytes, async_gzip_bytes
from writer_cloud_storage import async_push_bids_to_gcs

load_dotenv()

project_id_private = getenv("PROJECT_ID_PRIVATE")
batch_size_mb = int(getenv("BATCH_SIZE_MB", 1))

def should_upload(total_bytes: bytes, transformed_json_bytes: bytes) -> bool:
    return ((len(total_bytes) + len(transformed_json_bytes)) / (1024 * 1024)) > batch_size_mb

async def async_process_relay(relay: str, base_url: str, rate_limit: int, start_slot: int, end_slot: int) -> bool:
    logging.info(f"processing relay {relay}")
    private_client = storage.Client(project=project_id_private)
    total_bytes = b''

    async def async_upload_data(client, relay, data: bytes, slots_downloaded) -> bool:
        gzipped_bytes = await async_gzip_bytes(data)
        if gzipped_bytes is None:
            return False

        start_slot = slots_downloaded[-1]
        end_slot = slots_downloaded[0]
        file_name = f"{relay}_{start_slot}_{end_slot}_{len(slots_downloaded)}.gz"
        logging.info(f"checkpoint: {file_name}", extra={
            "payload": {
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
        slots_downloaded: [] = []
        for current_slot in range(start_slot, end_slot, -1):            
            url = f"{base_url}/builder_blocks_received?slot={current_slot}"
            json_bytes = await async_download_bids(url)
            
            if json_bytes is None:
                logging.error(f"failed to slot bids extraction, see previous message for more details", extra={
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