import os
import logging
import unittest
from google.cloud.bigquery import Client
from writer_big_query import push_to_big_query, push_bids_to_big_query, load_from_gcs_to_bigquery

logging.basicConfig(level=logging.DEBUG)

class TestIntegrationWriterBigQuery(unittest.TestCase):
    
    def test_push_to_big_query_success(self):
        project_id_private = os.getenv("PROJECT_ID_PRIVATE")
        private_client = Client(project=project_id_private)
        push_to_big_query(private_client)

    def test_push_bids_to_big_query_success(self):
        relay = "flashbots"
        slot = "7567002"
        project_id_private = os.getenv("PROJECT_ID_PRIVATE")
        private_client = Client(project=project_id_private)
        with open(f"./data/bids/{relay}_{slot}_T.gz", 'rb') as file_stream:
            gzip_file_bytes = file_stream.read()        
        
        result = push_bids_to_big_query(private_client, gzip_file_bytes, relay)
        self.assertEqual(result, True)

    def test_push_bids_from_gcs_to_big_query_success(self):        
        project_id_private = os.getenv("PROJECT_ID_PRIVATE")
        private_client = Client(project=project_id_private)
        result = load_from_gcs_to_bigquery(private_client, "gs://mev-boost-bids/agnostic_>_7565516")
        self.assertEqual(result, True)        

if __name__ == '__main__':
    unittest.main()