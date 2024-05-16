import unittest
from main_transfer import async_execute

class TestIntegrationMainTransfer(unittest.IsolatedAsyncioTestCase):

    async def test_main_transfer_full(self):
        await async_execute()

if __name__ == '__main__':
    unittest.main()