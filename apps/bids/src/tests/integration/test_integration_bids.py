import unittest
from main import process_relay

class TestBids(unittest.TestCase):

    def test_download_bids_flashbots_with_no_limit(self):        
        relay = "flashbots"
        base_url = "https://boost-relay.flashbots.net/relay/v1/data/bidtraces/builder_blocks_received"        
        response = process_relay(relay, base_url, 2)
        self.assertEqual(response, True)

    def test_download_bids_agnostic_with_no_limit(self):        
        relay = "agnostic"
        base_url = "https://agnostic-relay.net/relay/v1/data/bidtraces/proposer_payload_delivered"        
        response = process_relay(relay, base_url, 2)
        self.assertEqual(response, True)

    def test_download_bids_bloxrouteMaxProfit_with_no_limit(self):        
        relay = "bloxrouteMaxProfit"
        base_url = "https://bloxroute.max-profit.blxrbdn.com/relay/v1/data/bidtraces/builder_blocks_received"
        response = process_relay(relay, base_url, 2)
        self.assertEqual(response, True)

if __name__ == '__main__':
    unittest.main()