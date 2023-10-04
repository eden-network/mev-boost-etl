import unittest
from unittest.mock import Mock, MagicMock, patch, call
from writer_big_query import push_to_big_query
from google.cloud import bigquery
from google.api_core.exceptions import BadRequest, Forbidden

class TestPushToBigQuery(unittest.TestCase):

    def setUp(self):
        self.mock_client = Mock()
        self.mock_table_ref = Mock()
        self.mock_client.dataset.return_value.table.return_value = self.mock_table_ref

        self.mock_job_config = Mock()
        self.mock_job_config.source_format = bigquery.SourceFormat.NEWLINE_DELIMITED_JSON
        self.mock_client.LoadJobConfig.return_value = self.mock_job_config

        self.open_mock = MagicMock(spec=open)

    def test_push_to_bigquery_success(self):        
        mock_job = Mock()
        mock_job.result.return_value = None
        self.mock_client.load_table_from_file.return_value = mock_job

        result = push_to_big_query(self.mock_client)
        self.assertIsNone(result)

    def test_push_to_bigquery_table_ref_exception(self):
        self.mock_client.dataset.side_effect = Exception("Table reference creation error")

        with self.assertRaises(SystemExit):
            push_to_big_query(self.mock_client)

    def test_push_to_bigquery_job_config_exception(self):
        self.mock_client.dataset.return_value.table.return_value = Mock()

        with patch('writer_big_query.bigquery.LoadJobConfig', side_effect=Exception("Job config error")):
            with self.assertRaises(SystemExit):
                push_to_big_query(self.mock_client)

    def test_push_to_bigquery_bad_request_exception(self):
        self.mock_client.load_table_from_file.side_effect = BadRequest("Bad request error")
        
        with patch('writer_big_query.glob.glob', return_value=["data/dummy1.ndjson"]) as mock_glob:
            with patch('builtins.open', self.open_mock):
                with patch('writer_big_query.logging.error') as mock_logging_error:
                    push_to_big_query(self.mock_client)
                    
                error_message1 = "Bad request error when pushing file data/dummy1.ndjson to BQ: 400 Bad request error"                
                error_messages = [call[0][0] for call in mock_logging_error.call_args_list]
                self.assertIn(error_message1, error_messages)                
                self.assertEqual(len(error_messages), 2)

    def test_push_to_bigquery_forbidden_exception(self):
        self.mock_client.load_table_from_file.side_effect = Forbidden("Forbidden error")

        with patch('writer_big_query.glob.glob', return_value=["data/dummy1.ndjson"]):
            with patch('builtins.open', self.open_mock):
                with patch('writer_big_query.logging.error') as mock_logging_error:
                    push_to_big_query(self.mock_client)
                    
                error_message = "Forbidden error when pushing file data/dummy1.ndjson to BQ: 403 Forbidden error"
                error_messages = [call[0][0] for call in mock_logging_error.call_args_list]
                self.assertIn(error_message, error_messages)
                self.assertEqual(len(error_messages), 2)

    def test_push_to_bigquery_generic_exception(self):
        self.mock_client.load_table_from_file.side_effect = Exception("Generic error")

        with patch('writer_big_query.glob.glob', return_value=["data/dummy1.ndjson"]):
            with patch('builtins.open', self.open_mock):
                with patch('writer_big_query.logging.error') as mock_logging_error:
                    push_to_big_query(self.mock_client)
                    
                error_message = "An unexpected error occurred when pushing file data/dummy1.ndjson to BQ: Generic error"
                error_messages = [call[0][0] for call in mock_logging_error.call_args_list]
                self.assertIn(error_message, error_messages)
                self.assertEqual(len(error_messages), 2)

    def test_push_to_bigquery_multiple_errors(self):
        logging_error_mock = MagicMock()

        self.mock_client.load_table_from_file.side_effect = [
            BadRequest("Bad request error"), 
            Forbidden("Forbidden error")
        ]

        with patch('builtins.open', self.open_mock):
            with patch('writer_big_query.logging.error', logging_error_mock):
                with patch('writer_big_query.glob.glob', return_value=["data/dummy1.ndjson", "data/dummy2.ndjson"]):
                    push_to_big_query(self.mock_client)

                    logging_error_mock.assert_has_calls([
                        call("The following errors occurred during the process of pushing data to BQ:"),
                        call('Bad request error when pushing file data/dummy1.ndjson to BQ: 400 Bad request error'),
                        call('Forbidden error when pushing file data/dummy2.ndjson to BQ: 403 Forbidden error'),
                    ], any_order=False)                         

    def test_push_to_bigquery_multiple_errors_plus_single_success(self):
        logging_info_mock = MagicMock()
        logging_error_mock = MagicMock()

        # Success result
        mock_job = Mock()
        mock_job.result.return_value = None        

        self.mock_client.load_table_from_file.side_effect = [
            BadRequest("Bad request error"), 
            Forbidden("Forbidden error"),
            mock_job
        ]

        with patch('builtins.open', self.open_mock):
            with patch('writer_big_query.logging.info', logging_info_mock):
                with patch('writer_big_query.logging.error', logging_error_mock):
                    with patch('writer_big_query.glob.glob', return_value=["data/dummy1.ndjson", "data/dummy2.ndjson", "data/dummy3.ndjson"]):
                        push_to_big_query(self.mock_client)

                        logging_info_mock.assert_has_calls([
                            call("File data/dummy3.ndjson pushed to BQ."),
                            call("Finished pushing data to BQ.")
                        ], any_order=False)

                        logging_error_mock.assert_has_calls([
                            call("The following errors occurred during the process of pushing data to BQ:"),
                            call('Bad request error when pushing file data/dummy1.ndjson to BQ: 400 Bad request error'),
                            call('Forbidden error when pushing file data/dummy2.ndjson to BQ: 403 Forbidden error'),
                        ], any_order=False)                    

if __name__ == '__main__':
    unittest.main()