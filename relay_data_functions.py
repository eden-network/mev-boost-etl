import logging
import json
import requests
import time
from ndjson_file_operations import get_file_paths, delete_file

def fetch_data_from_url(url, cursor="latest"):
    """
    Fetch data from the given URL. If cursor is not "latest", append it to the URL to fetch a specific batch.
    """
    if cursor != "latest":
        url = f"{url}&cursor={cursor}"

    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
    except requests.exceptions.RequestException as e:
        logging.error(f"An error occurred while fetching data: {e}")
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

def process_individual_slot(id, outfile, slot, max_file_size, current_file_size):
    """
    Process an individual slot: extract necessary details and write it to the file.
    """
    slot["relay"] = id
    error, current_file_size = write_data_to_file(outfile, [slot], max_file_size, current_file_size)

    if error:
        return error, current_file_size
    
    return None, current_file_size

def determine_next_cursor(data, startSlot):
    """
    Determine the next cursor based on the slots received in the current batch.
    If all data up to startSlot has been processed, return "0" to indicate completion.
    """
    if data:
        last_slot = int(data[-1]["slot"])
        if last_slot < startSlot:
            return "0"
        else:
            return str(last_slot - 1)
    else:
        return "0"

# FUNCTIONS BELOW NOT YET TESTED 
def get_relay_data(id, url, cursor, current_file_size, file_count, startSlot):
    """
    Fetch, process, and write relay data to files.
    
    Parameters:
        id (str): Relay ID.
        url (str): URL to fetch data from.
        cursor (str): Position to start fetching data from.
        current_file_size (int): Current size of the output file.
        file_count (int): Counter for the number of files created.
        startSlot (int): The slot to start processing from.
        
    Returns:
        next_cursor (str): The next cursor to use for fetching data.
        current_file_size (int): Updated current file size.
        file_count (int): Updated file count.
    """
    max_file_size = 15 * 1024 * 1024  # Max file size is 15 MB

    error, data = fetch_data_from_url(url, cursor)
    if error == "ERR":
        logging.error("An error occurred while fetching data.")
        return "ERR"
    
    with open(f"relayData/{id}_{file_count}.ndjson", "a") as outfile:
        logging.info(f"Opening file for id: {id}")

        for slot in data:

            if int(slot["slot"]) < startSlot:
                logging.info(f"All new data for relay {id} has been parsed, moving on to the next relay.")
                outfile.close()
                return "0", current_file_size, file_count

            error, current_file_size = process_individual_slot(id, outfile, slot, max_file_size, current_file_size)

            if error == "NEW_FILE":
                logging.info(f"Data for relay {id} has reached the file cap, creating a new file for the relay.")

                outfile.close()
                current_file_size = 0
                file_count += 1

                outfile = open(f"relayData/{id}_{file_count}.ndjson", "a")
                
                _, current_file_size = process_individual_slot(id, outfile, slot, max_file_size, current_file_size)

    next_cursor = determine_next_cursor(data, startSlot)

    return next_cursor, current_file_size, file_count
        
def process_single_relay(relay, startSlot, rateLimitSeconds):
    """
    Process a single relay by fetching its data, processing it, and saving it to files.
    
    Parameters:
        relay (dict): Dictionary containing relay information.
        startSlot (int): The slot to start processing from.
        rateLimitSeconds (int): Rate limit to avoid overloading the APIs.
        
    Returns:
        bool: True if successful, False otherwise.
    """
    id, url = relay["id"], relay["url"]
    cursor = "latest"
    current_file_size = 0
    file_count = 1

    while cursor != "0":
        cursor, current_file_size, file_count = get_relay_data(id, url, cursor, current_file_size, file_count, startSlot)
        logging.info(f"Current cursor value: {cursor}")
        time.sleep(rateLimitSeconds)

        if cursor == "ERR":
            logging.error(f"Error on relay {id}")
            return False

    return True

def relay_updater(startSlot, rateLimitSeconds, relays):
    """
    Main function to start the relay data extraction process.
    
    Parameters:
        startSlot (int): The slot to start processing from.
        rateLimitSeconds (int): Rate limit to avoid overloading the APIs.
        relays (list): List of dictionaries containing relay information.
        
    Returns:
        bool: True if all relays processed successfully, False otherwise.
    """
    logging.info("Starting relay data extraction")
    success = True   

    files = get_file_paths('relayData/*.ndjson')   
    for file in files:
        delete_file(file)
    
    logging.info("Previous files have been removed")

    for relay in relays:
        success = process_single_relay(relay, startSlot, rateLimitSeconds)
        if not success:
            break

    return success