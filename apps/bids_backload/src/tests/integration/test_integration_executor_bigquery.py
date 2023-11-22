import unittest
from executor_bigquery import async_execute
from google.cloud.bigquery import Client
from dotenv import load_dotenv
from os import getenv

load_dotenv()

project_id = getenv("PROJECT_ID_PRIVATE")

class TestExecutorBigQuery(unittest.IsolatedAsyncioTestCase):    

    async def test_async_execute(self):
                
        client = Client(project_id)
        result = await async_execute(client)
                
        self.assertTrue(result)

if __name__ == '__main__':
    unittest.main()
