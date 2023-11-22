import os
import unittest
from google.cloud import bigquery
from reader_big_query import get_relay_metadata

from dotenv import load_dotenv
load_dotenv()

class TestIntegrationGetRelayMetaData(unittest.TestCase):

    def test_get_relay_metadata_success(self):  
        project_id_private = os.getenv("PROJECT_ID_PRIVATE")
        client = bigquery.Client(project=project_id_private)
        results = get_relay_metadata(client)
        expected_result = {'relay': 'eden', 'url': 'https://relay.edennetwork.io/relay/v1/data/bidtraces/proposer_payload_delivered', 'batch_size': 200, 'back_fill': False, 'head_slot': 7365691, 'tail_slot': 4700737}
        self.assertIn(expected_result, results)

if __name__ == '__main__':
    unittest.main()