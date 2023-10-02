# Description: This file is used to manually push data to big query
import os
import logging
from google.cloud import bigquery
from dotenv import load_dotenv
import os

load_dotenv()

project_id_private = os.getenv("PROJECT_ID_PRIVATE")
logging.basicConfig(level=logging.INFO)

from app.writer_big_query import push_to_big_query

private_client = bigquery.Client(project=project_id_private)
push_to_big_query(private_client)