import os
import logging
import json
import requests
import time

rate_limit_seconds = int(os.getenv("RATE_LIMIT_SECONDS", 2))

def fetch_data_from_url(url, batch_size, cursor="latest"):
    """
    Fetch data from the given URL. If cursor is not "latest", append it to the URL to fetch a specific batch.
    """
    url = f"{url}/proposer_payload_delivered?limit={batch_size}"
    if cursor != "latest":
        url = f"{url}&cursor={cursor}"

    try:
        logging.debug(f"fetching data from url: {url} with cursor: {cursor}")
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
    except requests.exceptions.RequestException as e:
        logging.error(f"an error occurred while fetching data: {e}")
        return "ERR", []
    
    return None, data

def write_data_to_file(outfile, data, max_file_size, current_file_size):
    """
    Write data to the file while keeping track of the file size.
    If the file size exceeds max_file_size, return a signal to create a new file.
    """
    for slot in data:
        json_object = json.dumps(slot)
        line_size = len(json_object.encode('utf-8'))

        if current_file_size + line_size > max_file_size:
            return "NEW_FILE", current_file_size
        
        outfile.write(json_object + '\n')
        current_file_size += line_size

    return None, current_file_size

def process_slot(id, outfile, slot, max_file_size, current_file_size):
    """
    Process an individual slot: extract necessary details and write it to the file.
    """
    slot["relay"] = id
    error, current_file_size = write_data_to_file(outfile, [slot], max_file_size, current_file_size)

    if error:
        return error, current_file_size
    
    return None, current_file_size

def determine_next_cursor(data, start_slot):
    """
    Determine the next cursor based on the slots received in the current batch.
    If all data up to startSlot has been processed, return "0" to indicate completion.
    """
    if data:
        logging.debug(f"determining next cursor with parameters: start_slot: {start_slot}")
        last_slot = int(data[-1]["slot"])
        if last_slot < start_slot:
            logging.debug(f"last slot {last_slot} is less than start slot {start_slot}, returning 0")
            return "0"
        else:
            next_cursor = str(last_slot - 1)
            logging.debug(f"returning last slot {last_slot} - 1 as the next cursor")
            return next_cursor
    else:
        logging.debug(f"no data received, returning 0")
        return "0"

def get_relay_data(relay, url, batch_size, cursor, current_file_size, file_count, head_slot):
    max_file_size = 15 * 1024 * 1024  # Max file size is 15 MB
    error, data = fetch_data_from_url(url, batch_size, cursor)

    if error == "ERR":
        return "ERR", None, None
    logging.info(f"relay {relay} fetched {len(data)} slots")
    
    with open(f"data/{relay}_{file_count}.ndjson", "a") as outfile:
        logging.debug(f"opening file for relay {relay} with parameters: file_count: {file_count}, current_file_size: {current_file_size}")

        for slot in data:
            if int(slot["slot"]) <= head_slot:
                logging.info(f"all new data for relay {relay} has been parsed")
                outfile.close()
                return "0", current_file_size, file_count

            error, current_file_size = process_slot(relay, outfile, slot, max_file_size, current_file_size)

            if error == "NEW_FILE":
                logging.info(f"data for relay {relay} has reached the file cap, creating a new file for the relay.")
                outfile.close()
                current_file_size = 0
                file_count += 1
                outfile = open(f"data/{relay}_{file_count}.ndjson", "a")
                _, current_file_size = process_slot(relay, outfile, slot, max_file_size, current_file_size)

    next_cursor = determine_next_cursor(data, head_slot)
    return next_cursor, current_file_size, file_count
        
def process_relay(relay, url, batch_size, head_slot, latest_slot): 
    cursor = latest_slot #"latest"    
    current_file_size = 0
    file_count = 1
    logging.info(f"processing relay {relay} with the following parameters: head_slot: {head_slot}, cursor: {cursor}")

    while cursor != "0":
        logging.debug(f"relay {relay}, cursor value: {cursor}")
        cursor, current_file_size, file_count = get_relay_data(relay, url, batch_size, cursor, current_file_size, file_count, head_slot)        
        time.sleep(rate_limit_seconds)

        if cursor == "ERR":
            logging.error(f"error on relay {relay}, exiting")
            return False

    return True