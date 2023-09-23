import logging
import sys
from google.cloud import bigquery
from google.api_core.exceptions import BadRequest, Forbidden
from ndjson_file_operations import get_file_paths

def push_to_BQ(client):
    dataset_id = 'ethereum_mev_boost'
    table_id = 'mev_boost_staging'

    try:
        table_ref = client.dataset(dataset_id).table(table_id)
    except Exception as e:
        logging.error(f"An error occurred while creating a table reference: {e}")
        sys.exit(1)

    try:
        job_config = bigquery.LoadJobConfig()
        job_config.source_format = bigquery.SourceFormat.NEWLINE_DELIMITED_JSON
    except Exception as e:
        logging.error(f"An error occurred while setting up job configuration: {e}")
        sys.exit(1)

    json_files = get_file_paths('relayData/*_*-*.ndjson')
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
            logging.info(f"File {json_file} pushed to BQ.")

        except BadRequest as e:
            errors_occurred.append(f"Bad request error when pushing file {json_file} to BQ: {e}")
        except Forbidden as e:
            errors_occurred.append(f"Forbidden error when pushing file {json_file} to BQ: {e}")
        except Exception as e:
            errors_occurred.append(f"An unexpected error occurred when pushing file {json_file} to BQ: {e}")

    logging.info("Finished pushing data to BQ.")
    
    # Display all errors to see which data was not pushed to BQ
    if errors_occurred:
        logging.error("The following errors occurred during the process of pushing data to BQ:")
        for error in errors_occurred:
            logging.error(error)