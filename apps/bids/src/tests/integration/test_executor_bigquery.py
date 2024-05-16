import unittest
from dotenv import load_dotenv
load_dotenv()

from bigquery.executor import async_execute

class TestExecutorBigQuery(unittest.IsolatedAsyncioTestCase):    

    async def test_async_execute(self):                        
        result = await async_execute()                
        self.assertTrue(result)

if __name__ == '__main__':
    unittest.main()
