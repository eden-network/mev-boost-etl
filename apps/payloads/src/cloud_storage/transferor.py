import asyncio, logging
from google.cloud import storage, bigquery
from bigquery.writer import async_write
from os import getenv

project_id = getenv("PROJECT_ID")
bucket_name = getenv("BUCKET_NAME")
processed_bucket_name = bucket_name + "-processed"
failed_bucket_name = bucket_name + "-failed"

async def async_execute() -> bool:
    try:
        storage_client = storage.Client(project_id)
        bigquery_client = bigquery.Client(project_id)
        bucket = storage_client.bucket(bucket_name)
        processed_bucket = storage_client.bucket(processed_bucket_name)
        failed_bucket = storage_client.bucket(failed_bucket_name)
        blobs = list(bucket.list_blobs())
        batch_size = 5
        blob_batches = [blobs[i:i + batch_size] for i in range(0, len(blobs), batch_size)]
        full_results = []
        
        for blob_batch in blob_batches:
            upload_tasks = [async_write(bigquery_client, f"gs://{bucket_name}/{blob.name}") for blob in blob_batch]
            
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
        logging.error(f"an unexpected error occurred: {e}")
        return False