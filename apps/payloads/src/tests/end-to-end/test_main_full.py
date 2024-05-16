import unittest
from main_full import async_execute

class TestIntegrationMainFull(unittest.IsolatedAsyncioTestCase):

    async def test_main_full(self):
        await async_execute()

if __name__ == '__main__':
    unittest.main()