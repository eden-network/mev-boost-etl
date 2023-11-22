import unittest
from reader_api import download_bids

class TestDownloadBuilderBlocksReceived(unittest.TestCase):

    def test_download_flashbots_bids_with_limit(self):
        url = "{base_url}?slot={slot}&limit={limit}"
        relay = "flashbots"
        base_url = "https://boost-relay.flashbots.net/relay/v1/data/bidtraces/builder_blocks_received"
        slot=7567001
        limit=100                
        response_bytes = download_bids(url.format(base_url=base_url, slot=slot, limit=limit))
        with open(f"./data/bids/{relay}-{slot}.json", 'wb') as output_file_stream:
            output_file_stream.write(response_bytes)

    def test_download_flashbots_bids_with_no_limit(self):
        url = "{base_url}?slot={slot}"
        relay = "flashbots"
        base_url = "https://boost-relay.flashbots.net/relay/v1/data/bidtraces/builder_blocks_received"
        slot=7567002
        response_bytes = download_bids(url.format(base_url=base_url, slot=slot))
        with open(f"./data/bids/{relay}-{slot}.json", 'wb') as output_file_stream:
            output_file_stream.write(response_bytes)

    def test_download_agnostic_bids_with_no_limit(self):
        url = "{base_url}?slot={slot}"
        relay = "agnostic"
        base_url = "https://agnostic-relay.net/relay/v1/data/bidtraces/builder_blocks_received"
        slot=7566613
        response_bytes = download_bids(url.format(base_url=base_url, slot=slot))
        with open(f"./data/bids/{relay}-{slot}.json", 'wb') as output_file_stream:
            output_file_stream.write(response_bytes)

    def test_download_bloxrouteMaxProfit_bids_with_no_limit(self):
        url = "{base_url}?slot={slot}"
        relay = "bloxrouteMaxProfit"
        base_url = "https://bloxroute.max-profit.blxrbdn.com/relay/v1/data/bidtraces/builder_blocks_received"
        slot=7613244
        response_bytes = download_bids(url.format(base_url=base_url, slot=slot))
        with open(f"./data/bids/{relay}-{slot}.json", 'wb') as output_file_stream:
            output_file_stream.write(response_bytes)            
            

if __name__ == '__main__':
    unittest.main()