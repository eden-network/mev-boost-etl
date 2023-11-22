import os
import logging
import unittest
from google.cloud.storage import Client
from writer_cloud_storage import push_bids_to_gcs

logging.basicConfig(level=logging.DEBUG)

class TestIntegrationWriterCloudStorage(unittest.TestCase):

    def test_push_bids_to_gcs_success(self):        
        project_id_private = os.getenv("PROJECT_ID_PRIVATE")        
        private_client = Client(project=project_id_private)
        with open(f"./data/bids/flashbots_7567002_T.gz", 'rb') as file_stream:
            gzip_file_bytes = file_stream.read()        
        
        result = push_bids_to_gcs(private_client, gzip_file_bytes, "flashbots_7567002_T.gz")
        self.assertEqual(result, True)

if __name__ == '__main__':
    unittest.main()