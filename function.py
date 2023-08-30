import requests
import json
import os
import time
import glob
import pydata_google_auth
from google.cloud import bigquery

print(os.getcwd())

# BigQuery authentication
credentials = pydata_google_auth.get_user_credentials(["https://www.googleapis.com/auth/bigquery"])
client = bigquery.Client(project='avalanche-304119', credentials=credentials)

relays = [
{"id":"eden","url":"https://relay.edennetwork.io/relay/v1/data/bidtraces/proposer_payload_delivered?limit=100"},
{"id":"relayoor","url":"https://relayooor.wtf/relay/v1/data/bidtraces/proposer_payload_delivered?limit=100"},
{"id":"manifold","url":"https://mainnet-relay.securerpc.com/relay/v1/data/bidtraces/proposer_payload_delivered?limit=100"},
{"id":"flashbots","url":"https://boost-relay.flashbots.net/relay/v1/data/bidtraces/proposer_payload_delivered?limit=100"},
{"id":"blocknative","url":"https://builder-relay-mainnet.blocknative.com/relay/v1/data/bidtraces/proposer_payload_delivered?limit=100"},
{"id":"bloxrouteMaxProfit","url":"https://bloxroute.max-profit.blxrbdn.com/relay/v1/data/bidtraces/proposer_payload_delivered?limit=100"},
{"id":"bloxrouteEthical","url":"https://bloxroute.ethical.blxrbdn.com/relay/v1/data/bidtraces/proposer_payload_delivered?limit=100"},
{"id":"bloxrouteRegulated","url":"https://bloxroute.regulated.blxrbdn.com/relay/v1/data/bidtraces/proposer_payload_delivered?limit=100"},
{"id":"agnostic","url":"https://agnostic-relay.net/relay/v1/data/bidtraces/proposer_payload_delivered?limit=100"},
{"id":"ultrasound","url":"https://relay.ultrasound.money/relay/v1/data/bidtraces/proposer_payload_delivered?limit=100"},
{"id":"aestus","url":"https://mainnet.aestus.live/relay/v1/data/bidtraces/proposer_payload_delivered?limit=100"}
]

latestSlotStored = 7213000 # TO-DO should be parsed from bigquery table, initially 0 as we parse from the start
startSlot = latestSlotStored

def getRelayData(id,url,cursor):
    global startSlot

    if cursor == "latest":
        url=url
    else:
        url=url+"&cursor="+str(cursor)

    try:
      x = requests.get(url)
      y = json.loads(x.text)

      with open(f"relayData/{id}.ndjson", "a") as outfile:
        for slot in y:

             # Add the 'relay' field to the slot dictionary
            slot["relay"] = id

            if int(slot["slot"]) < startSlot:
                return "0"
            
            # Write each slot as a new line in NDJSON file
            json_object = json.dumps(slot)
            outfile.write(json_object + '\n')
        
        returnCursor = y[-1]["slot"] if y else "0"
        return int(returnCursor) - 1
    
    except Exception as e:
      print(e)
      return "ERR"
    
def relayUpdater():

    # Delete previous files
    files = glob.glob('relayData/*.ndjson')
    for f in files:
        os.remove(f)

    for relay in relays:
        id= relay["id"]
        url= relay["url"]
        cursor= "latest"
        
        while cursor != "0":
            cursor = getRelayData(id,url,cursor)
            time.sleep(1) # Relays have rate limits so we need to wait 1 second between requests 
            print(cursor)
            if cursor == "ERR":
                print ("error on relay: "+str(id))
                break

def pushToBigQuery():
    
    # Define BigQuery dataset and table
    dataset_id = 'ethereum_mev_boost'
    table_id = 'mev_boost_staging'

    # Create a table reference
    table_ref = client.dataset(dataset_id).table(table_id)

    # Define job configuration
    job_config = bigquery.LoadJobConfig()
    job_config.source_format = bigquery.SourceFormat.NEWLINE_DELIMITED_JSON

    # Fetch all the NDJSON files
    json_files = glob.glob("relayData/*.ndjson")

    # Iterate through files and load data
    for json_file in json_files:
        with open(json_file, "rb") as source_file:
            job = client.load_table_from_file(
                source_file,
                table_ref,
                location="US",
                job_config=job_config,
            )
        job.result()

relayUpdater()
pushToBigQuery()