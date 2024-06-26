import asyncio, logging
from google.cloud.storage import Client
from io import BytesIO
from os import getenv

bucket_name = getenv("BUCKET_NAME")

async def async_push_bids_to_gcs(client: Client, gzip_file_bytes: bytes, object_name: str):
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(
        None,
        push_bids_to_gcs,
        client,        
        gzip_file_bytes,
        object_name
    )

def push_bids_to_gcs(client: Client, gzip_file_bytes: bytes, object_name: str) -> bool:
    logging.debug(f"uploading gzip bytes for {object_name} to GCS bucket {bucket_name}")
    try:        
        bucket = client.bucket(bucket_name)
        blob = bucket.blob(object_name)
        
        with BytesIO(gzip_file_bytes) as gzip_file_stream:
            blob.upload_from_file(
                gzip_file_stream,
                content_type='application/gzip'
            )
        logging.debug(f"gzip for {object_name} uploaded to GCS bucket {bucket_name}")

    except Exception as e:
        logging.error(f"error occurred when uploading {object_name} to GCS: {e}")
        return False

    return True
