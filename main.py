import sys
import logging
from google.cloud import bigquery
from reader_big_query import get_latest_slot
from relay_data_functions import relay_updater
from ndjson_file_operations import correct_file_names
from writer_big_query import push_to_BQ

logging.basicConfig(filename='progress.log', filemode='w', level=logging.INFO)
client = bigquery.Client(project='avalanche-304119')

batchSize = 100
rateLimitSeconds = 2

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

logging.info("Starting relay data extraction.")

startSlot = get_latest_slot(client)
if startSlot is None:
    sys.exit(1)
logging.info(f"Parsing relay data from newest slot back to and including slot {startSlot}")

if relay_updater(startSlot, rateLimitSeconds, relays):
    correct_file_names('relayData/*_*.ndjson')
    push_to_BQ(client)