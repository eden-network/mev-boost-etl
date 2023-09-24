import requests
import unittest
from unittest.mock import patch, Mock
from io import StringIO
from relay_data_functions import *

class TestFetchDataFromUrl(unittest.TestCase):

    @patch('requests.get')
    def test_successful_fetch_with_latest_cursor(self, mock_get):
        mock_get.return_value = Mock(status_code=200)
        mock_get.return_value.json.return_value = {"some": "data"}

        error, data = fetch_data_from_url("http://example.com/api")

        self.assertIsNone(error)
        self.assertEqual(data, {"some": "data"})

    @patch('requests.get')
    def test_successful_fetch_with_specific_cursor(self, mock_get):
        mock_get.return_value = Mock(status_code=200)
        mock_get.return_value.json.return_value = {"some": "data"}

        error, data = fetch_data_from_url("http://example.com/api", cursor="12345")

        self.assertIsNone(error)
        self.assertEqual(data, {"some": "data"})

    @patch('requests.get')
    def test_request_exception(self, mock_get):
        mock_get.side_effect = requests.exceptions.RequestException("An error occurred")

        error, data = fetch_data_from_url("http://example.com/api")
        
        self.assertEqual(error, "ERR")
        self.assertEqual(data, [])

    @patch('requests.get')
    def test_http_error_status(self, mock_get):
        mock_get.return_value = Mock(status_code=404)
        mock_get.return_value.raise_for_status.side_effect = requests.exceptions.HTTPError("Not found")

        error, data = fetch_data_from_url("http://example.com/api")

        self.assertEqual(error, "ERR")
        self.assertEqual(data, [])


class TestWriteDataToFile(unittest.TestCase):

    def test_write_data_within_size_limit(self):
        mock_file = StringIO()
        data = [{"key": "value"}, {"another_key": "another_value"}]
        max_file_size = 1000
        current_file_size = 0

        error, new_file_size = write_data_to_file(mock_file, data, max_file_size, current_file_size)

        self.assertIsNone(error)
        self.assertTrue(new_file_size > 0)

    def test_write_data_exceeds_size_limit(self):
        mock_file = StringIO()
        data = [{"key": "value"}, {"another_key": "another_value"}]
        max_file_size = 10
        current_file_size = 0

        error, new_file_size = write_data_to_file(mock_file, data, max_file_size, current_file_size)

        self.assertEqual(error, "NEW_FILE")
        self.assertEqual(new_file_size, current_file_size)

    def test_write_data_exact_size_limit(self):
        mock_file = StringIO()
        data = [{"key": "value"}]
        current_file_size = 0

        json_object = json.dumps(data[0])
        line_size = len(json_object.encode('utf-8'))
        max_file_size = line_size

        error, new_file_size = write_data_to_file(mock_file, data, max_file_size, current_file_size)

        self.assertIsNone(error)
        self.assertEqual(new_file_size, line_size)


class TestProcessIndividualSlot(unittest.TestCase):

    def test_successful_processing(self):
        mock_file = StringIO()
        id = "some_id"
        slot = {"key": "value"}
        max_file_size = 1000
        current_file_size = 0

        error, new_file_size = process_individual_slot(id, mock_file, slot, max_file_size, current_file_size)

        self.assertIsNone(error)
        self.assertTrue(new_file_size > 0)

    def test_max_file_size_reached(self):
        mock_file = StringIO()
        id = "some_id"
        slot = {"key": "value"}
        max_file_size = 10
        current_file_size = 0

        error, new_file_size = process_individual_slot(id, mock_file, slot, max_file_size, current_file_size)

        self.assertEqual(error, "NEW_FILE")
        self.assertEqual(new_file_size, 0)


class TestDetermineNextCursor(unittest.TestCase):

    def test_data_not_empty_last_slot_less_than_startSlot(self):
        data = [{"slot": 3}, {"slot": 4}]
        startSlot = 5
        self.assertEqual(determine_next_cursor(data, startSlot), "0")

    def test_data_not_empty_last_slot_greater_than_startSlot(self):
        data = [{"slot": 3}, {"slot": 4}, {"slot": 5}]
        startSlot = 4
        self.assertEqual(determine_next_cursor(data, startSlot), "4")

    def test_data_empty(self):
        data = []
        startSlot = 5
        self.assertEqual(determine_next_cursor(data, startSlot), "0")
        

class TestGetRelayData(unittest.TestCase):

    @patch('relay_data_functions.fetch_data_from_url')
    @patch('builtins.open', new_callable=unittest.mock.mock_open)
    def test_successful_get_relay_data(self, mock_open, mock_fetch):
        mock_fetch.return_value = (None, [{"slot": 10}, {"slot": 11}])
        
        cursor, current_file_size, file_count = get_relay_data(
            id="eden",
            url="http://example.com/api",
            cursor="latest",
            current_file_size=0,
            file_count=1,
            startSlot=5
        )

        self.assertEqual(cursor, "10")
        self.assertTrue(current_file_size > 0)
        self.assertEqual(file_count, 1)
        mock_open.assert_called_with('relayData/eden_1.ndjson', 'a')

    @patch('relay_data_functions.fetch_data_from_url')
    @patch('builtins.open', new_callable=unittest.mock.mock_open)
    def test_err_fetch_data(self, mock_open, mock_fetch):
        mock_fetch.return_value = ("ERR", [])
        
        cursor = get_relay_data(
            id="eden",
            url="http://example.com/api",
            cursor="latest",
            current_file_size=0,
            file_count=1,
            startSlot=5
        )
        
        self.assertEqual(cursor, "ERR")
        
    @patch('relay_data_functions.fetch_data_from_url')
    @patch('builtins.open', new_callable=unittest.mock.mock_open)
    def test_reach_startSlot(self, mock_open, mock_fetch):
        mock_fetch.return_value = (None, [{"slot": 2}, {"slot": 3}])
        
        cursor, current_file_size, file_count = get_relay_data(
            id="eden",
            url="http://example.com/api",
            cursor="latest",
            current_file_size=0,
            file_count=1,
            startSlot=3
        )
        
        self.assertEqual(cursor, "0")
        self.assertEqual(current_file_size, 0)
        self.assertEqual(file_count, 1)


class TestProcessSingleRelay(unittest.TestCase):
    
    @patch('relay_data_functions.get_relay_data')
    @patch('time.sleep')
    def test_successful_execution(self, mock_sleep, mock_get_relay_data):
        mock_get_relay_data.side_effect = [
            ("cursor_1", 1000, 1),
            ("cursor_2", 2000, 1),
            ("0", 3000, 1)
        ]
        
        relay = {"id": "eden", "url": "http://example.com/api"}
        result = process_single_relay(relay, startSlot=5, rateLimitSeconds=1)
        
        self.assertTrue(result)
        mock_sleep.assert_called_with(1)
    
    @patch('relay_data_functions.get_relay_data')
    @patch('time.sleep')
    def test_error_in_relay_processing(self, mock_sleep, mock_get_relay_data):
        mock_get_relay_data.return_value = ("ERR", 0, 1)
        
        relay = {"id": "eden", "url": "http://example.com/api"}
        result = process_single_relay(relay, startSlot=5, rateLimitSeconds=1)
        
        self.assertFalse(result)
        mock_sleep.assert_called_with(1)


class TestRelayUpdater(unittest.TestCase):

    @patch('relay_data_functions.process_single_relay')
    @patch('relay_data_functions.get_file_paths')
    @patch('relay_data_functions.delete_file')
    def test_all_relays_successful(self, mock_delete_file, mock_get_file_paths, mock_process_single_relay):
        mock_get_file_paths.return_value = ["file1", "file2"]
        mock_process_single_relay.return_value = True

        result = relay_updater(startSlot=5, rateLimitSeconds=1, relays=[{"id": "Eden"}, {"id": "Manifold"}])
        
        self.assertTrue(result)
        mock_delete_file.assert_called()
        mock_process_single_relay.assert_called()

    @patch('relay_data_functions.process_single_relay')
    @patch('relay_data_functions.get_file_paths')
    @patch('relay_data_functions.delete_file')
    def test_error_in_one_relay(self, mock_delete_file, mock_get_file_paths, mock_process_single_relay):
        mock_get_file_paths.return_value = ["file1", "file2"]
        mock_process_single_relay.side_effect = [True, False]

        result = relay_updater(startSlot=5, rateLimitSeconds=1, relays=[{"id": "Eden"}, {"id": "Manifold"}])
        
        self.assertFalse(result)
        mock_delete_file.assert_called()
        mock_process_single_relay.assert_called()


if __name__ == '__main__':
    unittest.main()