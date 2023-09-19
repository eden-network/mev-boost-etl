import unittest
from unittest.mock import Mock
from reader_big_query import get_latest_slot
from google.api_core.exceptions import BadRequest, Forbidden

class TestGetLatestSlot(unittest.TestCase):

    def setUp(self):
        self.mock_client = Mock()
        self.mock_query_job = Mock()
        self.mock_client.query.return_value = self.mock_query_job

    def test_get_latest_slot_success(self):
        self.mock_query_job.errors = None
        self.mock_query_job.result.return_value = [Mock(latest_slot=10)]

        result = get_latest_slot(self.mock_client)
        self.assertEqual(result, 11)

    def test_get_latest_slot_query_error(self):
        self.mock_query_job.errors = ["some error"]

        result = get_latest_slot(self.mock_client)
        self.assertIsNone(result)

    def test_get_latest_slot_bad_request(self):
        self.mock_client.query.side_effect = BadRequest("Bad Request")
        
        result = get_latest_slot(self.mock_client)
        self.assertIsNone(result)

    def test_get_latest_slot_forbidden(self):
        self.mock_client.query.side_effect = Forbidden("Forbidden")

        result = get_latest_slot(self.mock_client)
        self.assertIsNone(result)

    def test_get_latest_slot_generic_exception(self):
        self.mock_client.query.side_effect = Exception("Some other exception")

        result = get_latest_slot(self.mock_client)
        self.assertIsNone(result)

    def test_get_latest_slot_multiple_rows(self):
        self.mock_query_job.errors = None
        self.mock_query_job.result.return_value = [Mock(latest_slot=10), Mock(latest_slot=11)]

        result = get_latest_slot(self.mock_client)
        self.assertIsNone(result)

    def test_get_latest_slot_no_rows(self):
        self.mock_query_job.errors = None
        self.mock_query_job.result.return_value = []

        result = get_latest_slot(self.mock_client)
        self.assertIsNone(result)

    def test_get_latest_slot_null_slot(self):
        self.mock_query_job.errors = None
        self.mock_query_job.result.return_value = [Mock(latest_slot=None)]

        result = get_latest_slot(self.mock_client)
        self.assertEqual(result, 0)

    def test_get_latest_slot_non_integer_slot(self):
        self.mock_query_job.errors = None
        self.mock_query_job.result.return_value = [Mock(latest_slot="string")]

        result = get_latest_slot(self.mock_client)
        self.assertIsNone(result)

if __name__ == '__main__':
    unittest.main()