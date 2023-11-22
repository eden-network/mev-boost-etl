import asyncio
from google.cloud.storage import Client
from google.cloud import bigquery
from writer_bigquery import async_load_from_gcs_to_bigquery
import logging
from os import getenv
from dotenv import load_dotenv

load_dotenv()

logging_level = getenv("LOGGING_LEVEL", "INFO")
project_id = getenv("PROJECT_ID_PRIVATE")
bucket_name = getenv("BUCKET_NAME")
processed_bucket_name = bucket_name + "-processed"
failed_bucket_name = bucket_name + "-failed"

logging.basicConfig(level=logging.getLevelName(logging_level))
logging.getLogger("google.api_core").setLevel(logging.ERROR)
logging.getLogger("asyncio").setLevel(logging.ERROR)

async def async_execute() -> bool:
    logging.info("initializing bids blob transfer")

    try:
        storage_client = Client(project_id)
        bigquery_client = bigquery.Client(project_id)
        bucket = storage_client.bucket(bucket_name)
        processed_bucket = storage_client.bucket(processed_bucket_name)
        failed_bucket = storage_client.bucket(failed_bucket_name)
        blobs = list(bucket.list_blobs())        
        batch_size = 5
        blob_batches = [blobs[i:i + batch_size] for i in range(0, len(blobs), batch_size)]
        full_results = []
        
        for blob_batch in blob_batches:        
            upload_tasks = [async_load_from_gcs_to_bigquery(bigquery_client, f"gs://{bucket_name}/{blob.name}") for blob in blob_batch]
            
            results = await asyncio.gather(*upload_tasks, return_exceptions=True)

            for idx, success in enumerate(results):
                blob = blob_batch[idx]            
                if success:
                    logging.info(f"blob {blob.name} processed successfully, copying to processed bucket")
                    bucket.copy_blob(blob, processed_bucket, blob.name)
                    bucket.delete_blob(blob.name)                
                else: 
                    logging.error(f"blob {blob.name} processing failed, copying to failed bucket")
                    bucket.copy_blob(blob, failed_bucket, blob.name)
                    bucket.delete_blob(blob.name)

            full_results.extend(results)
            await asyncio.sleep(10)        

        return True
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")
        return False

if __name__ == '__main__':
    asyncio.run(async_execute())