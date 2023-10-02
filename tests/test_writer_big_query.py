import glob
import unittest
from unittest.mock import Mock, MagicMock, patch
from app.writer_big_query import push_to_big_query
from google.cloud import bigquery
from google.api_core.exceptions import BadRequest, Forbidden

class TestPushToBigQuery(unittest.TestCase):

    def test_push_to_bigquery_success(self):

        # Setup mock objects
        mock_client = Mock()
        mock_table_ref = Mock()
        mock_client.dataset.return_value.table.return_value = mock_table_ref

        # Mocking job_config instance
        mock_job_config = Mock()
        mock_job_config.source_format = bigquery.SourceFormat.NEWLINE_DELIMITED_JSON
        mock_client.LoadJobConfig.return_value = mock_job_config

        # Mocking glob.glob to return a list of dummy files
        glob.glob.return_value = ["data/dummy1.ndjson", "data/dummy2.ndjson"]

        # Mocking open function to not actually open files
        open_mock = MagicMock(spec=open)

        # Mocking logging.info to capture log messages
        logging_info_mock = MagicMock()

        with unittest.mock.patch('builtins.open', open_mock):
            with unittest.mock.patch('app.writer_big_query.logging.info', logging_info_mock):
                with unittest.mock.patch('app.writer_big_query.glob.glob', return_value=["data/dummy1.ndjson", "data/dummy2.ndjson"]):

                    # Mocking the job instance to not actually perform any operations
                    mock_job = Mock()
                    mock_job.result.return_value = None
                    mock_client.load_table_from_file.return_value = mock_job

                    # Call the function and verify the result
                    result = push_to_big_query(mock_client)
                    self.assertIsNone(result)

                    # Verify that the logging calls were made
                    logging_info_mock.assert_has_calls([
                        unittest.mock.call("File data/dummy1.ndjson pushed to BQ"),
                        unittest.mock.call("File data/dummy2.ndjson pushed to BQ"),
                        unittest.mock.call("Data successfully pushed to BQ")
                    ])

    def test_push_to_bigquery_table_ref_exception(self):
        mock_client = Mock()
        mock_client.dataset.side_effect = Exception("Table reference creation error")

        with self.assertRaises(SystemExit):
            push_to_big_query(mock_client)

    def test_push_to_bigquery_job_config_exception(self):
        mock_client = Mock()
        mock_client.dataset.return_value.table.return_value = Mock()

        with patch('app.writer_big_query.bigquery.LoadJobConfig', side_effect=Exception("Job config error")):
            with self.assertRaises(SystemExit):
                push_to_big_query(mock_client)

    def test_push_to_bigquery_glob_exception(self):
        mock_client = Mock()
        mock_client.dataset.return_value.table.return_value = Mock()

        with patch('app.writer_big_query.glob.glob', side_effect=Exception("Glob error")):
            with self.assertRaises(SystemExit):
                push_to_big_query(mock_client)

    def test_push_to_bigquery_bad_request_exception(self):
        mock_client = Mock()
        mock_client.dataset.return_value.table.return_value = Mock()
        
        # Setting up a mock for logging.error
        logging_error_mock = MagicMock()
        
        with patch('app.writer_big_query.logging.error', logging_error_mock):
            mock_client.load_table_from_file.side_effect = BadRequest("Bad request error")
        
            with patch('app.writer_big_query.glob.glob', return_value=["data/dummy1.ndjson"]):
                with patch('builtins.open', MagicMock(spec=open)):
                    push_to_big_query(mock_client)
                    
                    # Verify that the logging.error was called with the correct error message
                    logging_error_mock.assert_called_with('Bad request error when pushing file data/dummy1.ndjson to BQ: 400 Bad request error')

    def test_push_to_bigquery_forbidden_exception(self):
        mock_client = Mock()
        mock_client.dataset.return_value.table.return_value = Mock()
        mock_client.load_table_from_file.side_effect = Forbidden("Forbidden error")
        
        logging_error_mock = MagicMock()

        with patch('app.writer_big_query.logging.error', logging_error_mock):
            with patch('app.writer_big_query.glob.glob', return_value=["data/dummy1.ndjson"]):
                with patch('builtins.open', MagicMock(spec=open)):
                    push_to_big_query(mock_client)

                    logging_error_mock.assert_called_with('Forbidden error when pushing file data/dummy1.ndjson to BQ: 403 Forbidden error')

    def test_push_to_bigquery_generic_exception(self):
        mock_client = Mock()
        mock_client.dataset.return_value.table.return_value = Mock()
        mock_client.load_table_from_file.side_effect = Exception("Generic error")

        logging_error_mock = MagicMock()

        with patch('app.writer_big_query.logging.error', logging_error_mock):
            with patch('app.writer_big_query.glob.glob', return_value=["data/dummy1.ndjson"]):
                with patch('builtins.open', MagicMock(spec=open)):
                    push_to_big_query(mock_client)

                    logging_error_mock.assert_called_with('An unexpected error occurred when pushing file data/dummy1.ndjson to BQ: Generic error')

    def test_push_to_bigquery_multiple_errors(self):

        mock_client = Mock()
        mock_table_ref = Mock()
        mock_client.dataset.return_value.table.return_value = mock_table_ref

        mock_job_config = Mock()
        mock_job_config.source_format = bigquery.SourceFormat.NEWLINE_DELIMITED_JSON
        mock_client.LoadJobConfig.return_value = mock_job_config

        glob.glob.return_value = ["data/dummy1.ndjson", "data/dummy2.ndjson"]
        open_mock = MagicMock(spec=open)
        logging_error_mock = MagicMock()

        # Setting up an exception side effect for the load_table_from_file method
        # This will simulate errors occurring during the file pushing process
        mock_client.load_table_from_file.side_effect = [
            BadRequest("Bad request error"), 
            Forbidden("Forbidden error")
        ]

        with unittest.mock.patch('builtins.open', open_mock):
            with unittest.mock.patch('app.writer_big_query.logging.error', logging_error_mock):
                with unittest.mock.patch('app.writer_big_query.glob.glob', return_value=["data/dummy1.ndjson", "data/dummy2.ndjson"]):

                    # Call the function
                    push_to_big_query(mock_client)

                    # Verify that the logging.error calls were made
                    logging_error_mock.assert_has_calls([
                        unittest.mock.call("The following errors occurred during the process:"),
                        unittest.mock.call('Bad request error when pushing file data/dummy1.ndjson to BQ: 400 Bad request error'),
                        unittest.mock.call('Forbidden error when pushing file data/dummy2.ndjson to BQ: 403 Forbidden error'),
                    ], any_order=True)


if __name__ == '__main__':
    unittest.main()