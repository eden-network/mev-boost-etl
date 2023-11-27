import unittest
from unittest.mock import Mock, patch
from reader_big_query import get_config
from google.api_core.exceptions import BadRequest, Forbidden

class TestGetRelayMetaData(unittest.TestCase):

    def setUp(self):
        self.mock_client = Mock()
        self.mock_query_job = Mock()
        self.mock_client.query.return_value = self.mock_query_job

    def test_get_relay_metadata_success(self):
        self.mock_query_job.errors = None
        self.mock_query_job.result.return_value = iter([{'relay': 'relay_1', 'url': 'url_1', 'batch_size': 10, 'back_fill': True, 'head_slot': 5}])

        result = get_config(self.mock_client)
        expected_result = [{'relay': 'relay_1', 'url': 'url_1', 'batch_size': 10, 'back_fill': True, 'head_slot': 5}]
        self.assertEqual(result, expected_result)

    def test_get_relay_metadata_query_error(self):
        self.mock_query_job.errors = ["some error"]

        result = get_config(self.mock_client)
        self.assertIsNone(result)

    def test_get_relay_metadata_bad_request(self):
        self.mock_client.query.side_effect = BadRequest("Bad Request")
        
        result = get_config(self.mock_client)
        self.assertIsNone(result)

    def test_get_relay_metadata_forbidden(self):
        self.mock_client.query.side_effect = Forbidden("Forbidden")

        result = get_config(self.mock_client)
        self.assertIsNone(result)

    def test_get_relay_metadata_generic_exception(self):
        self.mock_client.query.side_effect = Exception("Some other exception")

        result = get_config(self.mock_client)
        self.assertIsNone(result)

    def test_get_relay_metadata_no_rows(self):
        self.mock_query_job.errors = None
        self.mock_query_job.result.return_value = []

        with patch('writer_big_query.logging.error') as mock_logging_error:
            result = get_config(self.mock_client)            
            error_messages = [call[0][0] for call in mock_logging_error.call_args_list]
            self.assertIn("expected 1 or more rows but got: 0", error_messages)
            self.assertEqual(result, None)
            
if __name__ == '__main__':
    unittest.main()