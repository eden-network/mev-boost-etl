import os, logging, unittest
from google.cloud import storage
from dotenv import load_dotenv
load_dotenv()

from cloud_storage.writer import push_bids_to_gcs

logging.basicConfig(level=logging.DEBUG)

project_id = os.getenv("PROJECT_ID")      

class TestWriterCloudStorage(unittest.TestCase):

    def test_push_bids_to_gcs_success(self):                  
        private_client = storage.Client(project=project_id)
        with open(f"./data/bids/flashbots_7567002_T.gz", 'rb') as file_stream:
            gzip_file_bytes = file_stream.read()        
        
        result = push_bids_to_gcs(private_client, gzip_file_bytes, "flashbots_7567002_T.gz")
        self.assertEqual(result, True)

if __name__ == '__main__':
    unittest.main()