import unittest
from unittest.mock import Mock
from app.reader_big_query import get_latest_slot
from google.api_core.exceptions import BadRequest, Forbidden

class TestGetLatestSlot(unittest.TestCase):

    def test_get_latest_slot_success(self):
        mock_client = Mock()
        mock_query_job = Mock()
        mock_query_job.errors = None
        mock_query_job.result.return_value = [Mock(latest_slot=10)]
        
        mock_client.query.return_value = mock_query_job

        result = get_latest_slot(mock_client)
        self.assertEqual(result, 11)

    def test_get_latest_slot_query_error(self):
        mock_client = Mock()
        mock_query_job = Mock()
        mock_query_job.errors = ['some error']
        
        mock_client.query.return_value = mock_query_job

        result = get_latest_slot(mock_client)
        self.assertIsNone(result)

    def test_get_latest_slot_bad_request(self):
        mock_client = Mock()
        mock_client.query.side_effect = BadRequest("Bad Request")
        
        result = get_latest_slot(mock_client)
        self.assertIsNone(result)

    def test_get_latest_slot_forbidden(self):
        mock_client = Mock()
        mock_client.query.side_effect = Forbidden("Forbidden")

        result = get_latest_slot(mock_client)
        self.assertIsNone(result)

    def test_get_latest_slot_generic_exception(self):
        mock_client = Mock()
        mock_client.query.side_effect = Exception("Some other exception")

        result = get_latest_slot(mock_client)
        self.assertIsNone(result)

    def test_get_latest_slot_multiple_rows(self):
        mock_client = Mock()
        mock_query_job = Mock()
        mock_query_job.errors = None
        mock_query_job.result.return_value = [Mock(latest_slot=10), Mock(latest_slot=11)]

        mock_client.query.return_value = mock_query_job

        result = get_latest_slot(mock_client)
        self.assertIsNone(result)

    def test_get_latest_slot_no_rows(self):
        mock_client = Mock()
        mock_query_job = Mock()
        mock_query_job.errors = None
        mock_query_job.result.return_value = []

        mock_client.query.return_value = mock_query_job

        result = get_latest_slot(mock_client)
        self.assertIsNone(result)

    def test_get_latest_slot_null_slot(self):
        mock_client = Mock()
        mock_query_job = Mock()
        mock_query_job.errors = None
        mock_query_job.result.return_value = [Mock(latest_slot=None)]

        mock_client.query.return_value = mock_query_job

        result = get_latest_slot(mock_client)
        self.assertEqual(result, 0)

    def test_get_latest_slot_non_integer_slot(self):
        mock_client = Mock()
        mock_query_job = Mock()
        mock_query_job.errors = None
        mock_query_job.result.return_value = [Mock(latest_slot="string")]

        mock_client.query.return_value = mock_query_job

        result = get_latest_slot(mock_client)
        self.assertIsNone(result)

if __name__ == '__main__':
    unittest.main()
