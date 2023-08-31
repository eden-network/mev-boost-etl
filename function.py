import requests
import json
import os
import time
import glob
import pydata_google_auth
from google.cloud import bigquery

credentials = pydata_google_auth.get_user_credentials(["https://www.googleapis.com/auth/bigquery"])   # BigQuery authentication
client = bigquery.Client(project='avalanche-304119', credentials=credentials)

relays = [
{"id":"eden","url":"https://relay.edennetwork.io/relay/v1/data/bidtraces/proposer_payload_delivered?limit=100"},
{"id":"manifold","url":"https://mainnet-relay.securerpc.com/relay/v1/data/bidtraces/proposer_payload_delivered?limit=100"},
{"id":"flashbots","url":"https://boost-relay.flashbots.net/relay/v1/data/bidtraces/proposer_payload_delivered?limit=100"},
{"id":"blocknative","url":"https://builder-relay-mainnet.blocknative.com/relay/v1/data/bidtraces/proposer_payload_delivered?limit=100"},
{"id":"bloxrouteMaxProfit","url":"https://bloxroute.max-profit.blxrbdn.com/relay/v1/data/bidtraces/proposer_payload_delivered?limit=100"},
{"id":"bloxrouteRegulated","url":"https://bloxroute.regulated.blxrbdn.com/relay/v1/data/bidtraces/proposer_payload_delivered?limit=100"},
{"id":"agnostic","url":"https://agnostic-relay.net/relay/v1/data/bidtraces/proposer_payload_delivered?limit=100"},
{"id":"ultrasound","url":"https://relay.ultrasound.money/relay/v1/data/bidtraces/proposer_payload_delivered?limit=100"},
{"id":"aestus","url":"https://mainnet.aestus.live/relay/v1/data/bidtraces/proposer_payload_delivered?limit=100"}
]

query = ("SELECT MAX(slot) as latest_slot FROM `avalanche-304119.ethereum_mev_boost.mev_boost_staging`")   # Query to find the maximum value of the "slot" column
query_job = client.query(query)
results = query_job.result()

for row in results:   # Fetch the latest slot and increment by 1
    startSlot = row.latest_slot + 1

def getRelayData(id, url, cursor, current_file_size, current_file_index):
    global startSlot
    max_file_size = 15 * 1024 * 1024  # 15 MB in bytes

    if cursor == "latest":
        url = url
    else:
        url = url + "&cursor=" + str(cursor)

    try:
        x = requests.get(url)
        y = json.loads(x.text)

        outfile = open(f"relayData/{id}_{current_file_index}.ndjson", "a")

        for slot in y:
            slot["relay"] = id   # Add the 'relay' field to the slot dictionary

            if int(slot["slot"]) < startSlot:
                return "0", current_file_size, current_file_index
            
            json_object = json.dumps(slot)
            outfile.write(json_object + '\n')  # Writing the JSON object to file

            line_size = len(json_object.encode('utf-8'))
            current_file_size += line_size

            if current_file_size > max_file_size:   # Check if file size is exceeding 15 MB
                outfile.close()   # Close the current file
                current_file_index += 1   # Increment the file index
                outfile = open(f"relayData/{id}_{current_file_index}.ndjson", "a")   # Open a new file
                current_file_size = line_size   # Reset the file size
        
        outfile.close()

        returnCursor = y[-1]["slot"] if y else "0"
        return int(returnCursor) - 1, current_file_size, current_file_index
    
    except Exception as e:
      print(e)
      return "ERR"


def relayUpdater():
    global current_file_size, current_file_index
    success = True   # Initialize a flag to keep track of success

    files = glob.glob('relayData/*.ndjson')   # Delete previous files
    for f in files:
        os.remove(f)

    for relay in relays:
        id= relay["id"]
        url= relay["url"]
        cursor= "latest"

        current_file_index = 1  # Reset the file index for each relay
        current_file_size = 0  # Reset the file size for each relay
        
        while cursor != "0":   # If cursor is "0" it means you caught up to the latest block
            cursor, current_file_size, current_file_index = getRelayData(id, url, cursor, current_file_size, current_file_index)
            time.sleep(1)   # Relays have rate limits so we need to wait 1 second between requests 
            print(cursor)

            if cursor == "ERR":
                print ("error on relay: " + str(id))
                success = False   # Set the flag to False on failure
                break

        if not success:   # Break out of the outer loop if any error is encountered
            break

    return success # Return the final status


def pushToBigQuery():

    dataset_id = 'ethereum_mev_boost'   # Define BigQuery dataset and table
    table_id = 'mev_boost_staging'

    table_ref = client.dataset(dataset_id).table(table_id)   # Create a table reference

    job_config = bigquery.LoadJobConfig()   # Define job configuration
    job_config.source_format = bigquery.SourceFormat.NEWLINE_DELIMITED_JSON

    json_files = glob.glob("relayData/*.ndjson")   # Fetch all the NDJSON files

    for json_file in json_files:   # Iterate through files and load data
        with open(json_file, "rb") as source_file:
            job = client.load_table_from_file(
                source_file,
                table_ref,
                location="US",
                job_config=job_config,
            )
        job.result()

    print("Data successfully pushed to BQ")


if relayUpdater():   # Only call pushToBigQuery() if relayUpdater() returns True
    pushToBigQuery()