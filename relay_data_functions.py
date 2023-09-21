import logging
import json
import requests

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
        last_slot = data[-1]["slot"]
        if last_slot < startSlot:
            return "0"
        else:
            return str(last_slot - 1)
    else:
        return "0"