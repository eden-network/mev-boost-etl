import unittest
from main_transfer import async_execute

class TestBidsMainTransfer(unittest.IsolatedAsyncioTestCase):    

    async def test_async_execute(self):
        await async_execute()                        

if __name__ == '__main__':
    unittest.main()
