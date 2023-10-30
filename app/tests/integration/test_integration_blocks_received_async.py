import unittest
from app.bids import async_process_relay, async_execute

class TestBlocksReceived(unittest.IsolatedAsyncioTestCase):

    async def test_download_bids_with_no_limit(self):        
        relay = "flashbots"
        base_url = "https://boost-relay.flashbots.net/relay/v1/data/bidtraces/builder_blocks_received"
        response = await async_process_relay(relay, base_url, 2)
        self.assertEqual(response, True)

    async def test_async_execute_integration(self):
        results = await async_execute()
                
        self.assertTrue(all(results), "Not all relays processed successfully.")        

if __name__ == '__main__':
    unittest.main()
