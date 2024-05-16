import unittest, json
from os import getenv
from google.cloud import storage
from cloud_storage.writer import push_bids_to_gcs
from api.reader import download_bids
from transformer_json_bytes import transform_bytes, gzip_bytes

class TestAttemptFailedSlotDownload(unittest.TestCase):

    def test_pull_effected_relay_slots_in(self):
        project_id = getenv("PROJECT_ID")        
        client = storage.Client(project=project_id)
        data_key = "20240123"
        file_path = f"./data/bids/reload/{data_key}.json"
        with open(file_path, 'r', encoding='utf-8') as file:
            slots_to_load = json.load(file)
        
        for slot_row in slots_to_load:
            url = "{base_url}?slot={slot}"            
            base_url = slot_row.get("base_url")
            slot = slot_row.get("slot")
            relay = slot_row.get("relay")
            
            response_bytes = download_bids(url.format(base_url=base_url, slot=slot))
            # with open(f"./data/bids/{relay}-{slot}.json", 'wb') as output_file_stream:
            #     output_file_stream.write(response_bytes)
            transformed_json_bytes = transform_bytes(response_bytes, relay, slot)
            # content = transformed_json_bytes.decode('utf-8')
            # with open(f"./data/bids/{relay}_{slot}_T.json", 'w') as output_file:
            #     output_file.write(content)    
            gzipped_bytes = gzip_bytes(transformed_json_bytes)
            # with open(f"./data/bids/{relay}_{slot}_T.gz", 'wb') as output_file_stream:
            #     output_file_stream.write(gzipped_bytes)
            push_bids_to_gcs(client, gzipped_bytes, f"{relay}_{slot}_T.gz")

    def test_download_bloxrouteMaxProfit_bids_with_no_limit(self):
        project_id = getenv("PROJECT_ID")        
        client = storage.Client(project=project_id)
        url = "{base_url}?slot={slot}"
        relay = "bloxrouteMaxProfit"
        base_url = "https://relay.ultrasound.money/relay/v1/data/bidtraces/builder_blocks_received"
        slot=7718143
        response_bytes = download_bids(url.format(base_url=base_url, slot=slot))
        with open(f"./data/bids/{relay}-{slot}.json", 'wb') as output_file_stream:
            output_file_stream.write(response_bytes)
        transformed_json_bytes = transform_bytes(response_bytes, relay, slot)
        content = transformed_json_bytes.decode('utf-8')
        with open(f"./data/bids/{relay}_{slot}_T.json", 'w') as output_file:
            output_file.write(content)    
        gzipped_bytes = gzip_bytes(transformed_json_bytes)
        with open(f"./data/bids/{relay}_{slot}_T.gz", 'wb') as output_file_stream:
            output_file_stream.write(gzipped_bytes)
        push_bids_to_gcs(client, gzipped_bytes, f"{relay}_{slot}_T.gz")
            

if __name__ == '__main__':
    unittest.main()