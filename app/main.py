import sys
import requests
import json
import os
import time
import glob
import logging
from google.cloud import bigquery
from dotenv import load_dotenv
import os

load_dotenv()

project_id_public = os.getenv("PROJECT_ID_PUBLIC")
project_id_private = os.getenv("PROJECT_ID_PRIVATE")

# Setting up logging configuration
logging.basicConfig(level=logging.INFO)

# Import functions that get latest slot & push data to BQ
from reader_big_query import get_latest_slot
from writer_big_query import push_to_big_query

# Initializing the BigQuery client
public_client = bigquery.Client(project=project_id_public)
private_client = bigquery.Client(project=project_id_private)

# Batch size & rate limit
batch_size = int(os.getenv("BATCH_SIZE"))
rate_limit_seconds = int(os.getenv("RATE_LIMIT_SECONDS"))

# List of relay URLs and their respective IDs
relays = [
{"id":"eden","url":f"https://relay.edennetwork.io/relay/v1/data/bidtraces/proposer_payload_delivered?limit={batch_size}"},
{"id":"manifold","url":f"https://mainnet-relay.securerpc.com/relay/v1/data/bidtraces/proposer_payload_delivered?limit={batch_size}"},
{"id":"flashbots","url":f"https://boost-relay.flashbots.net/relay/v1/data/bidtraces/proposer_payload_delivered?limit={batch_size}"},
{"id":"blocknative","url":f"https://builder-relay-mainnet.blocknative.com/relay/v1/data/bidtraces/proposer_payload_delivered?limit={batch_size}"},
{"id":"bloxrouteMaxProfit","url":f"https://bloxroute.max-profit.blxrbdn.com/relay/v1/data/bidtraces/proposer_payload_delivered?limit={batch_size}"},
{"id":"bloxrouteRegulated","url":f"https://bloxroute.regulated.blxrbdn.com/relay/v1/data/bidtraces/proposer_payload_delivered?limit={batch_size}"},
{"id":"agnostic","url":f"https://agnostic-relay.net/relay/v1/data/bidtraces/proposer_payload_delivered?limit={batch_size}"},
{"id":"ultrasound","url":f"https://relay.ultrasound.money/relay/v1/data/bidtraces/proposer_payload_delivered?limit={batch_size}"},
{"id":"aestus","url":f"https://mainnet.aestus.live/relay/v1/data/bidtraces/proposer_payload_delivered?limit={batch_size}"}
]

# Logging the start of the data extraction process
logging.info("Starting relay data extraction")

# Getting the latest parsed slot from the BQ database
start_slot = get_latest_slot(public_client)
if start_slot is None:
    sys.exit(1)
logging.info(f"Parsing relay data from newest slot back to and including slot {start_slot}")

# Function that gets relay data
def get_relay_data(id, url, cursor, current_file_size, file_count):
    global start_slot

    # Max file size is 15 MB (it is set to 14.9 but the latest entry before stopping should be a few bytes over 14.9, that's fine but it must not exceed 15)
    max_file_size = 14.9 * 1024 * 1024  

    # Modifying URL based on the cursor position, for the first 100 rows cursor is set to 'latest', afterwards we specify a position to fetch the next 100 sized batches
    if cursor == "latest":
        url = url
    else:
        url = url + "&cursor=" + str(cursor)

    logging.info(f"Current URL is {url}")

    try:
        # Making a request to the relay URL and parsing the JSON response
        x = requests.get(url)
        y = json.loads(x.text)

        # If the response is empty, return "0" as the cursor to stop parsing data for this relay
        if y == []:
            logging.info(f"Relay {id} returned an empty array, moving on to the next relay")            
            return "0",  current_file_size, file_count

        # Opening a file to store relay data (will be renamed at the end when slot numbers are known)
        outfile = open(f"data/{id}_{file_count}.ndjson", "a")
        logging.info(f"Opening file for id: {id}")

        # Looping through the data and writing it to the file
        for slot in y:
            slot["relay"] = id
            
            # If the current slot number is less than the latest parsed slot saved in BigQuery OR slot == 0 (only occurs at the end of backload of agnostic data), stop parsing data for this relay
            if int(slot["slot"]) < start_slot or int(slot["slot"]) == 0:
                logging.info(f"All new data for relay {id} has been parsed, moving on to the next relay")
                outfile.close()
                return "0", current_file_size, file_count

            # Write the current slot data to the file
            json_object = json.dumps(slot)
            outfile.write(json_object + '\n')  

            # Encode the data into bytes and add it to the file size tracker (to make sure it doesn't go over 15 MB)
            line_size = len(json_object.encode('utf-8'))
            current_file_size += line_size

            # If the current file size exceeds the size limit, reset the size, increment the file counter and create a new file for the same relay
            if current_file_size > max_file_size:
                logging.info(f"Data for relay {id} has reached the file cap, creating new file for the relay")
                outfile.close()
                current_file_size = 0  
                file_count += 1
                outfile = open(f"data/{id}_{file_count}.ndjson", "a")

        # If the current batch does not exceed the file size or slot number tresholds, close the file in preparation for the next batch of 100 entries
        else:
            outfile.close()
            
        # After processing all the slots in the current batch, we get the slot number of the last slot in the batch to use as the cursor for the next batch. If the batch is empty (y is an empty list), we set the returnCursor to '0'
        return_cursor = y[-1]["slot"] if y else "0"
        logging.info(f"Latest slot in the batch is {return_cursor}")

        # We return the cursor for the next batch (decremented by 1 to avoid missing any slots), along with the current file size and file count, to continue from where we left in the next iteration. If we set the cursor to '0' and decrement by 1, we would perform an API call with -1, resulting in an error, which will return 'ERR' in the following code, thus ending the parsing
        return int(return_cursor) - 1, current_file_size, file_count

    # If an error occurs, terminate the script and do not push data to BigQuery
    except Exception as e:
        logging.error(f"An error occurred: {e}")
        return "ERR", None, None

# Function to update the relay data
def relay_updater():
    global current_file_size

    # Variable to indicate if all data has successfully been parsed, if it was, modify file names and push into BigQuery
    success = True   

    # Remove all previous .ndjson files
    files = glob.glob('data/*.ndjson')   
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
            time.sleep(rate_limit_seconds)   
            logging.info(f"Current cursor value: {cursor}")

            # If cursor is 'ERR' an error occured when parsing data for the relay, set 'success' to false to prevent pushing to BigQuery and exit both loops, otherwise both loops will finish and move on to modifying file names and pushing to BigQuery
            if cursor == "ERR":
                logging.error(f"Error on relay {str(id)}")
                success = False   
                break

        if not success:   
            break

    return success 

# Function to modify file names, if renaming files fails, terminate the script and do not push to BQ
def correct_file_names():
    try:
        # Loop over the files, read each file
        files = glob.glob('data/*_*.ndjson')
        for file in files:
            with open(file, 'r') as f:
                lines = f.readlines()
            
            # Modify the file name to include the first and last slot numbers of each file
            if lines:
                id = json.loads(lines[0])["relay"]
                start_slot = json.loads(lines[0])["slot"]
                end_slot = json.loads(lines[-1])["slot"]
                new_file_name = f"data/{id}_{start_slot}-{end_slot}.ndjson"
                os.rename(file, new_file_name)
                logging.info(f"File {file} renamed to {new_file_name}")
            else:
                # If a file is empty it means there was no new data for the relay, delete the file
                logging.info(f"Removing file {file}")
                os.remove(file)

    except Exception as e:
        logging.error(f"Error occured when modifying file names: {e}")
        sys.exit(1)

# Modify file names and push to BQ if data parsing was successful
if relay_updater():
    correct_file_names()
    push_to_big_query(private_client)