import asyncio
from google.cloud.storage import Client
from google.cloud import bigquery
from writer_big_query import async_load_from_gcs_to_bigquery
import logging
from os import getenv

project_id = getenv("PROJECT_ID_PRIVATE")
bucket_name = getenv("BUCKET_NAME")
processed_bucket_name = getenv("PROCESSED_BUCKET_NAME")
failed_bucket_name = getenv("FAILED_BUCKET_NAME")

async def async_execute():
    logging.info("initializing bids blob transfer")

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
            else:  # If there was an exception
                logging.error(f"blob {blob.name} processing failed, copying to failed bucket")
                bucket.copy_blob(blob, failed_bucket, blob.name)
                bucket.delete_blob(blob.name)

        full_results.extend(results)
        # wait 10 seconds between batches
        await asyncio.sleep(10)

    return full_results

if __name__ == '__main__':
    asyncio.run(async_execute())