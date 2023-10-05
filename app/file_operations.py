import logging
import glob
import json
import os
import sys

def get_file_paths(pattern):
    """
    Fetch all file paths that match the given pattern.
    """
    try:
        logging.debug(f"fetching files with pattern {pattern}")
        files = glob.glob(pattern)
        return files
    except Exception as e:
        logging.error(f"unexpected error when fetching files with pattern {pattern}. Error: {e}")
        sys.exit(1)

def read_lines_from_file(file_path):
    """
    Read all lines from a file using it's file path.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.readlines()    
    except FileNotFoundError as e:
        logging.error(f"file not found: {file_path}. Error: {e}")
        sys.exit(1)
    except IOError as e:
        logging.error(f"io error when reading from file: {file_path}. Error: {e}")
        sys.exit(1)
    except Exception as e:
        logging.error(f"unexpected error when reading from file: {file_path}. Error: {e}")
        sys.exit(1)

def delete_file(file_path):
    """
    Delete a file using it's file path.
    """
    try:
        logging.debug(f"deleting file {file_path}")
        os.remove(file_path)        
    except FileNotFoundError as e:
        logging.error(f"file not found: {file_path}. Error: {e}")
        sys.exit(1)
    except PermissionError as e:
        logging.error(f"permission error when deleting file: {file_path}. Error: {e}")
        sys.exit(1)
    except Exception as e:
        logging.error(f"unexpected error when deleting file: {file_path}. Error: {e}")
        sys.exit(1)

def parse_json_from_lines(lines):
    """
    Parse the first and last line of a list of lines as JSON objects.
    """
    try:
        first_line = json.loads(lines[0])
        last_line = json.loads(lines[-1])
        return first_line, last_line
    except json.JSONDecodeError as e:
        logging.error(f"json decoding error when parsing lines. Error: {e}")
        sys.exit(1)
    except Exception as e:
        logging.error(f"unexpected error when parsing lines. Error: {e}")
        sys.exit(1)

def rename_file(file_path, new_file_name):
    """
    Rename a file using it's file path and a new file name.
    """
    try:
        os.rename(file_path, new_file_name)
        logging.info(f"file {file_path} renamed to {new_file_name}")
    except FileNotFoundError as e:
        logging.error(f"file not found when renaming: {file_path} to {new_file_name}. Error: {e}")
        sys.exit(1)
    except PermissionError as e:
        logging.error(f"permission error when renaming file: {file_path} to {new_file_name}. Error: {e}")
        sys.exit(1)
    except FileExistsError as e:
        logging.error(f"target file already exists when renaming: {file_path} to {new_file_name}. Error: {e}")
        sys.exit(1)
    except Exception as e:
        logging.error(f"unexpected error when renaming {file_path} to {new_file_name}. Error: {e}")
        sys.exit(1)
 
def update_file_names(pattern):
    """
    Rename .ndjson files to include start & end slot numbers using the above functions
    """
    file_paths = get_file_paths(pattern)

    for file_path in file_paths:
        lines = read_lines_from_file(file_path)

        if not lines:
            delete_file(file_path)
        else:
            first_line, last_line = parse_json_from_lines(lines)
            id = first_line["relay"]
            start_slot = first_line["slot"]
            end_slot = last_line["slot"]
            new_file_name = f"data/{id}_{start_slot}-{end_slot}.ndjson"
            rename_file(file_path, new_file_name)

def reset_local_storage():
    """
    Remove all .ndjson files from the data directory.    
    """
    logging.info("resetting local storage")
    files = get_file_paths('data/*.ndjson')
    logging.debug(f"found {len(files)} files to remove")
    for file in files:
        delete_file(file)