import logging
import unittest
from google.cloud import bigquery
from relay_data_functions import process_relay

logging.basicConfig(level=logging.DEBUG)

class TestIntegrationRelayDataFunctions(unittest.TestCase):

    def test_get_relay_metadata_success(self):          
        result = process_relay('blocknative', 'https://builder-relay-mainnet.blocknative.com/relay/v1/data/bidtraces/proposer_payload_delivered', 450, 7365691, 4700737, False)
        self.assertEqual(result, True)

if __name__ == '__main__':
    unittest.main()