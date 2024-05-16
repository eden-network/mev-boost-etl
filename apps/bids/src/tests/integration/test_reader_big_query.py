import os, unittest
from google.cloud import bigquery
from dotenv import load_dotenv
load_dotenv()

from bigquery.reader import get_k8s_config, get_latest_slot, get_relay_config, get_bau_config

project_id = os.getenv("PROJECT_ID")

class TestIntegrationGetPodConfig(unittest.TestCase):

    def test_get_pod_config_sucess(self):        
        client = bigquery.Client(project=project_id)
        results = get_k8s_config(client)
        self.assertIsNotNone(results)
    
    def test_get_latest_slot(self):        
        client = bigquery.Client(project=project_id)
        results = get_latest_slot(client)
        self.assertIsNotNone(results)

    def test_get_config(self):        
        client = bigquery.Client(project=project_id)
        results = get_relay_config(client)
        self.assertIsNotNone(results)

    def test_get_bau_config(self):        
        client = bigquery.Client(project=project_id)
        results = get_bau_config(client)
        self.assertIsNotNone(results)

if __name__ == '__main__':
    unittest.main()