import unittest
from main_extract import async_execute

class TestBidsMainExtract(unittest.IsolatedAsyncioTestCase):    

    async def test_async_execute(self):
        await async_execute()                        

if __name__ == '__main__':
    unittest.main()
