import os
import logging
import unittest
from google.cloud import bigquery
from writer_big_query import push_to_big_query

logging.basicConfig(level=logging.DEBUG)

class TestIntegrationWriterBigQuery(unittest.TestCase):
    
    def test_push_to_big_query_success(self):
        project_id_private = os.getenv("PROJECT_ID_PRIVATE")
        private_client = bigquery.Client(project=project_id_private)
        push_to_big_query(private_client)

if __name__ == '__main__':
    unittest.main()