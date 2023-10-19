import unittest
from api_reader import download_builder_blocks_received

class TestDownloadBuilderBlocksReceived(unittest.TestCase):

    def test_download_builder_blocks_received_with_limit(self):
        url = "{base_url}?slot={slot}&limit={limit}"
        relay = "flashbots"
        base_url = "https://boost-relay.flashbots.net/relay/v1/data/bidtraces/builder_blocks_received"
        slot=7567001
        limit=100                
        response_bytes = download_builder_blocks_received(url.format(base_url=base_url, slot=slot, limit=limit))
        with open(f"./data/builder_block_received/{relay}-{slot}.json", 'wb') as output_file_stream:
            output_file_stream.write(response_bytes)

    def test_download_builder_blocks_received_with_no_limit(self):
        url = "{base_url}?slot={slot}"
        relay = "flashbots"
        base_url = "https://boost-relay.flashbots.net/relay/v1/data/bidtraces/builder_blocks_received"
        slot=7567002
        response_bytes = download_builder_blocks_received(url.format(base_url=base_url, slot=slot))
        with open(f"./data/builder_block_received/{relay}-{slot}.json", 'wb') as output_file_stream:
            output_file_stream.write(response_bytes)

if __name__ == '__main__':
    unittest.main()