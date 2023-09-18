import logging
import glob
import sys
from google.cloud import bigquery
from google.api_core.exceptions import BadRequest, Forbidden

def push_to_BQ(client):

    # Define BQ dataset & table
    dataset_id = 'ethereum_mev_boost'
    table_id = 'mev_boost_staging'

    # Create a table reference
    try:
        table_ref = client.dataset(dataset_id).table(table_id)
    except Exception as e:
        logging.error(f"An error occurred while creating a table reference: {e}")
        sys.exit(1)

    # Define job configuration
    try:
        job_config = bigquery.LoadJobConfig()
        job_config.source_format = bigquery.SourceFormat.NEWLINE_DELIMITED_JSON
    except Exception as e:
        logging.error(f"An error occurred while setting up job configuration: {e}")
        sys.exit(1)

    # Fetch all .ndjson files
    try:
        json_files = glob.glob("relayData/*.ndjson")
    except Exception as e:
        logging.error(f"An error occurred while retrieving JSON files: {e}")
        sys.exit(1)
    
    # Create a list to store all the possible following errors for better visibility
    errors_occurred = []

    # Iterate through files and load data in batches, if an error occurs log the error and try to push the next file, at the end display the list of all files (which will contain relay name & starting/ending slot numbers) that failed
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
            logging.info(f"File {json_file} pushed to BQ")

        except BadRequest as e:
            errors_occurred.append(f"Bad request error when pushing file {json_file} to BQ: {e}")
        except Forbidden as e:
            errors_occurred.append(f"Forbidden error when pushing file {json_file} to BQ: {e}")
        except Exception as e:
            errors_occurred.append(f"An unexpected error occurred when pushing file {json_file} to BQ: {e}")

    logging.info("Data successfully pushed to BQ")
    
    # Display all errors to see which data was not pushed to BQ
    if errors_occurred:
        logging.error("The following errors occurred during the process:")
        for error in errors_occurred:
            logging.error(error)