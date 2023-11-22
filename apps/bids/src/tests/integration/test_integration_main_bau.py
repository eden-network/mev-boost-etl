import unittest
from main_bau import async_execute

class TestBau(unittest.IsolatedAsyncioTestCase):    

    async def test_async_execute_integration(self):
        await async_execute()                        

if __name__ == '__main__':
    unittest.main()
