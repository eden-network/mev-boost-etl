import unittest
from unittest.mock import patch, mock_open, call
from file_operations import *

class TestFileOperations(unittest.TestCase):

    def test_get_file_paths(self):
        with patch('ndjson_file_operations.glob.glob', return_value=["file1", "file2"]) as mock_glob:
            result = get_file_paths("some pattern")

            self.assertEqual(result, ["file1", "file2"])
            mock_glob.assert_called_with("some pattern")

    def test_read_lines_from_file(self):
        mock_file_content = "line1\nline2"
        m = mock_open(read_data=mock_file_content)

        with patch('ndjson_file_operations.open', m):
            result = read_lines_from_file("file_path")
            self.assertEqual(result, ["line1\n", "line2"])

    def test_delete_file(self):
        with patch('ndjson_file_operations.os.remove') as mock_remove, patch('ndjson_file_operations.logging.debug') as mock_log:
            delete_file("file_path")

            mock_remove.assert_called_with("file_path")
            mock_log.assert_called_with("removing file file_path")

    def test_parse_json_from_lines(self):
        lines = ['{"key": "value1"}', '{"key": "value2"}']
        first_line, last_line = parse_json_from_lines(lines)

        self.assertEqual(first_line, {"key": "value1"})
        self.assertEqual(last_line, {"key": "value2"})

    def test_rename_file(self):
        with patch('ndjson_file_operations.os.rename') as mock_rename, patch('ndjson_file_operations.logging.info') as mock_log:
            rename_file("old_file_path", "new_file_path")

            mock_rename.assert_called_with("old_file_path", "new_file_path")
            mock_log.assert_called_with("file old_file_path renamed to new_file_path")

    def test_correct_file_names(self):
        test_pattern = "some_pattern"
        with patch('ndjson_file_operations.get_file_paths', return_value=["file_path1", "file_path2"]) as mock_get_file_paths, \
            patch('ndjson_file_operations.read_lines_from_file', side_effect=[[], ["line1", "line2"]]) as mock_read_lines, \
            patch('ndjson_file_operations.parse_json_from_lines', return_value=({"relay": "id1", "slot": 1}, {"relay": "id2", "slot": 2})) as mock_parse_json, \
            patch('ndjson_file_operations.delete_file') as mock_delete_file, \
            patch('ndjson_file_operations.rename_file') as mock_rename_file:
     
            update_file_names(test_pattern)

            mock_get_file_paths.assert_called_with(test_pattern)
            mock_read_lines.assert_has_calls([call("file_path1"), call("file_path2")])
            mock_delete_file.assert_called_once_with("file_path1")
            mock_rename_file.assert_called_once_with("file_path2", "data/id1_1-2.ndjson")

if __name__ == '__main__':
    unittest.main()