import os
import unittest
from google.cloud import bigquery
from reader_bigquery import get_pod_config, get_latest_slot, get_relay_config, get_bau_config

from dotenv import load_dotenv
load_dotenv()

class TestIntegrationGetPodConfig(unittest.TestCase):

    def test_get_pod_config_sucess(self):
        project_id_private = os.getenv("PROJECT_ID_PRIVATE")
        client = bigquery.Client(project=project_id_private)
        results = get_pod_config(client)
        self.assertIsNotNone(results)
    
    def test_get_latest_slot(self):
        project_id_private = os.getenv("PROJECT_ID_PRIVATE")
        client = bigquery.Client(project=project_id_private)
        results = get_latest_slot(client)
        self.assertIsNotNone(results)

    def test_get_config(self):
        project_id_private = os.getenv("PROJECT_ID_PRIVATE")
        client = bigquery.Client(project=project_id_private)
        results = get_relay_config(client)
        self.assertIsNotNone(results)

    def test_get_bau_config(self):
        project_id_private = os.getenv("PROJECT_ID_PRIVATE")
        client = bigquery.Client(project=project_id_private)
        results = get_bau_config(client)
        self.assertIsNotNone(results)

if __name__ == '__main__':
    unittest.main()