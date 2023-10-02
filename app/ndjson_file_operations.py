import logging
import glob
import json
import os
import sys

def get_file_paths(pattern):
    try:
        files = glob.glob(pattern)
        return files
    except Exception as e:
        logging.error(f"Unexpected error when fetching files with pattern {pattern}. Error: {e}")
        sys.exit(1)

def read_lines_from_file(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.readlines()    
    except FileNotFoundError as e:
        logging.error(f"File not found: {file_path}. Error: {e}")
        sys.exit(1)
    except IOError as e:
        logging.error(f"IO error when reading from file: {file_path}. Error: {e}")
        sys.exit(1)
    except Exception as e:
        logging.error(f"Unexpected error when reading from file: {file_path}. Error: {e}")
        sys.exit(1)

def delete_file(file_path):
    try:
        os.remove(file_path)
        logging.info(f"Removing file {file_path}")
    except FileNotFoundError as e:
        logging.error(f"File not found: {file_path}. Error: {e}")
        sys.exit(1)
    except PermissionError as e:
        logging.error(f"Permission error when deleting file: {file_path}. Error: {e}")
        sys.exit(1)
    except Exception as e:
        logging.error(f"Unexpected error when deleting file: {file_path}. Error: {e}")
        sys.exit(1)

def parse_json_from_lines(lines):
    try:
        first_line = json.loads(lines[0])
        last_line = json.loads(lines[-1])
        return first_line, last_line
    except json.JSONDecodeError as e:
        logging.error(f"JSON decoding error when parsing lines. Error: {e}")
        sys.exit(1)
    except Exception as e:
        logging.error(f"Unexpected error when parsing lines. Error: {e}")
        sys.exit(1)

def rename_file(file_path, new_file_name):
    try:
        os.rename(file_path, new_file_name)
        logging.info(f"File {file_path} renamed to {new_file_name}")
    except FileNotFoundError as e:
        logging.error(f"File not found when renaming: {file_path} to {new_file_name}. Error: {e}")
        sys.exit(1)
    except PermissionError as e:
        logging.error(f"Permission error when renaming file: {file_path} to {new_file_name}. Error: {e}")
        sys.exit(1)
    except FileExistsError as e:
        logging.error(f"Target file already exists when renaming: {file_path} to {new_file_name}. Error: {e}")
        sys.exit(1)
    except Exception as e:
        logging.error(f"Unexpected error when renaming {file_path} to {new_file_name}. Error: {e}")
        sys.exit(1)

# Rename .ndjson files to include start & end slot numbers using the above functions
def correct_file_names():
    file_paths = get_file_paths('data/*_*.ndjson')

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