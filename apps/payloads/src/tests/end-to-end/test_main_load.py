import unittest
from main_load import async_execute

class TestIntegrationMainLoad(unittest.IsolatedAsyncioTestCase):

    async def test_main_transfer_load(self):
        await async_execute()

if __name__ == '__main__':
    unittest.main()