import unittest
from blocks_received import process_relay

class TestBlocksReceived(unittest.TestCase):

    def test_download_builder_blocks_received_with_no_limit(self):        
        relay = "flashbots"
        base_url = "https://boost-relay.flashbots.net/relay/v1/data/bidtraces/builder_blocks_received"        
        response = process_relay(relay, base_url, 2)
        self.assertEqual(response, True)

if __name__ == '__main__':
    unittest.main()