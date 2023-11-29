import logging
import sys
import glob
from google.cloud.bigquery import Client, LoadJobConfig, SourceFormat
from google.api_core.exceptions import BadRequest, Forbidden
from dotenv import load_dotenv
from os import getenv

load_dotenv()

dataset_id = getenv("DATASET_ID")
table_id_staging = getenv("TABLE_ID_STAGING")

def push_to_big_query(client: Client):
    try:
        table_ref = client.dataset(dataset_id).table(table_id_staging)
    except Exception as e:
        logging.error(f"an error occurred while creating a table reference: {e}")
        sys.exit(1)

    try:
        job_config = LoadJobConfig()
        job_config.source_format = SourceFormat.NEWLINE_DELIMITED_JSON
    except Exception as e:
        logging.error(f"an error occurred while setting up job configuration: {e}")
        sys.exit(1)

    # Fetch all .ndjson files
    try:
        json_files = glob.glob("data/*.ndjson")
    except Exception as e:
        logging.error(f"an error occurred while retrieving JSON files: {e}")
        sys.exit(1)
    
    # Create a list to store all the possible following errors for better visibility
    errors_occurred = []

    # Iterate through files and load data in batches, if an error occurs, log the error and try to push the next file
    for json_file in json_files: 
        try:
            with open(json_file, 'rb') as source_file:
                job = client.load_table_from_file(
                    source_file,
                    table_ref,
                    location='US',
                    job_config=job_config,
                )
            job.result()
            logging.info(f"file {json_file} pushed to BQ.")

        except BadRequest as e:
            errors_occurred.append(f"bad request error when pushing file {json_file} to BQ: {e}")
        except Forbidden as e:
            errors_occurred.append(f"forbidden error when pushing file {json_file} to BQ: {e}")
        except Exception as e:
            errors_occurred.append(f"an unexpected error occurred when pushing file {json_file} to BQ: {e}")

    logging.info("finished pushing data to BQ.")
    
    # Display all errors to see which data was not pushed to BQ
    if errors_occurred:
        logging.error("the following errors occurred during the process of pushing data to BQ:")
        for error in errors_occurred:
            logging.error(error)