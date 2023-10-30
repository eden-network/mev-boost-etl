import unittest
from bids_received_transfer import async_execute

class TestBidsReceivedTransfer(unittest.IsolatedAsyncioTestCase):    

    async def test_async_execute_integration(self):
        results = await async_execute()
                
        self.assertTrue(all(results), "Not all relays processed successfully.")        

if __name__ == '__main__':
    unittest.main()
