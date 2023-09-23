import sys
import os
import time
import logging
from google.cloud import bigquery
from reader_big_query import get_latest_slot
from writer_big_query import push_to_BQ
from ndjson_file_operations import get_file_paths, correct_file_names
from relay_data_functions import *

# Setting up logging configuration & initializing BQ client
logging.basicConfig(filename='progress.log', filemode='w', level=logging.INFO)
client = bigquery.Client(project='avalanche-304119')

# Setting up batch size & rate limit
batchSize = 100
rateLimitSeconds = 2

# List of relay URLs and their respective IDs
relays = [
{"id":"eden","url":f"https://relay.edennetwork.io/relay/v1/data/bidtraces/proposer_payload_delivered?limit={batchSize}"},
{"id":"manifold","url":f"https://mainnet-relay.securerpc.com/relay/v1/data/bidtraces/proposer_payload_delivered?limit={batchSize}"},
{"id":"flashbots","url":f"https://boost-relay.flashbots.net/relay/v1/data/bidtraces/proposer_payload_delivered?limit={batchSize}"},
{"id":"blocknative","url":f"https://builder-relay-mainnet.blocknative.com/relay/v1/data/bidtraces/proposer_payload_delivered?limit={batchSize}"},
{"id":"bloxrouteMaxProfit","url":f"https://bloxroute.max-profit.blxrbdn.com/relay/v1/data/bidtraces/proposer_payload_delivered?limit={batchSize}"},
{"id":"bloxrouteRegulated","url":f"https://bloxroute.regulated.blxrbdn.com/relay/v1/data/bidtraces/proposer_payload_delivered?limit={batchSize}"},
{"id":"agnostic","url":f"https://agnostic-relay.net/relay/v1/data/bidtraces/proposer_payload_delivered?limit={batchSize}"},
{"id":"ultrasound","url":f"https://relay.ultrasound.money/relay/v1/data/bidtraces/proposer_payload_delivered?limit={batchSize}"},
{"id":"aestus","url":f"https://mainnet.aestus.live/relay/v1/data/bidtraces/proposer_payload_delivered?limit={batchSize}"}
]

logging.info("Starting relay data extraction")

# Getting the latest parsed slot from the BQ database
startSlot = get_latest_slot(client)
if startSlot is None:
    sys.exit(1)
logging.info(f"Parsing relay data from newest slot back to and including slot {startSlot}")

startSlot = 7388270 # REMOVE LATER, FOR TESTING PURPOSES

# Parse relay data
def get_relay_data(id, url, cursor, current_file_size, file_count):
    global startSlot

    max_file_size = 15 * 1024 * 1024  # Max file size is 15 MB

    # Fetch data from the URL
    error, data = fetch_data_from_url(url, cursor)
    if error == "ERR":
        logging.error("An error occurred while fetching data.")
        return "ERR"
    
    # Open a file to store relay data
    with open(f"relayData/{id}_{file_count}.ndjson", "a") as outfile:
        logging.info(f"Opening file for id: {id}")

        # Loop through the data & write it to .ndjson file
        for slot in data:

            # If slot number less than starting slot, stop parsing for this relay
            if int(slot["slot"]) < startSlot:
                logging.info(f"All new data for relay {id} has been parsed, moving on to the next relay")
                outfile.close()
                return "0", current_file_size, file_count

            error, current_file_size = process_individual_slot(id, outfile, slot, max_file_size, current_file_size)

            if error == "NEW_FILE":
                logging.info(f"Data for relay {id} has reached the file cap, creating a new file for the relay")

                # Close the current file and reset counters
                outfile.close()
                current_file_size = 0
                file_count += 1

                # Open a new file
                outfile = open(f"relayData/{id}_{file_count}.ndjson", "a")
                
                # Write the current slot to the new file
                _, current_file_size = process_individual_slot(id, outfile, slot, max_file_size, current_file_size)

    # Determine the next cursor based on the last slot in the data batch
    next_cursor = determine_next_cursor(data, startSlot)

    logging.info(f"Next cursor value: {next_cursor}")
    return next_cursor, current_file_size, file_count
        
# Update relay data
def relay_updater():
    global current_file_size

    # Variable to indicate if all data has successfully been parsed, if it was, modify file names and push into BigQuery
    success = True   

    # Remove all previous .ndjson files
    files = get_file_paths('relayData/*.ndjson')   
    for f in files:
        os.remove(f)
    
    logging.info("Previous files have been removed")

    # Get the id and url of each relay and start parsing with the cursor set to "latest" to get the first batch, for all the following batches cursor will be modified. The 'while' loop parses each batch of 100 slots at a time until it gets all data for a relay
    for relay in relays:
        id = relay["id"]
        url = relay["url"]
        cursor = "latest"

        # Initialize counters for the file number and size
        current_file_size = 0
        file_count = 1
        
        # Loop that gets data for each relay by calling the "getRelayData" function, cursor will be "0" when all data has been parsed up to the latest saved slot in BigQuery, stop parsing when that happens. Sleep the code for the API rate limits
        while cursor != "0":   
            cursor, current_file_size, file_count = get_relay_data(id, url, cursor, current_file_size, file_count)
            time.sleep(rateLimitSeconds)   
            logging.info(f"Current cursor value: {cursor}")

            # If cursor is 'ERR' an error occured when parsing data for the relay, set 'success' to false to prevent pushing to BigQuery and exit both loops, otherwise both loops will finish and move on to modifying file names and pushing to BigQuery
            if cursor == "ERR":
                logging.error(f"Error on relay {str(id)}")
                success = False   
                break

        if not success:   
            break

    return success 

# If parsing relay data was successful, modify file names and push data to BQ
if relay_updater():
    correct_file_names('relayData/*_*.ndjson')
    push_to_BQ(client)