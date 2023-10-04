import logging
import unittest
from file_operations import update_file_names

logging.basicConfig(level=logging.DEBUG)

class TestIntegrationFileOperations(unittest.TestCase):
    
    def test_update_file_names_success(self):
        update_file_names('data/*_*.ndjson')

if __name__ == '__main__':
    unittest.main()