import logging
from google.api_core.exceptions import BadRequest, Forbidden

def get_latest_slot(client):
    query = ("SELECT MAX(slot) AS latest_slot FROM `avalanche-304119.ethereum_mev_boost.mev_boost_staging`")
    try:
        logging.info("Getting latest slot from BQ")
        query_job = client.query(query)
        if query_job.errors:
            logging.error(f"SQL query returned an error: {query_job.error_result}")
            return None

        results = query_job.result()

    except BadRequest as e:
        logging.error(f"Bad request error: {e}")
        return None
    except Forbidden as e:
        logging.error(f"Forbidden error: {e}")
        return None
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")
        return None

    rows = list(results)
    if len(rows) != 1:
        logging.error(f"Expected a single row, got: {len(rows)}")
        return None

    row = rows[0]
    if row.latest_slot is None:
        logging.error("The table is empty, initiated parsing from beginning.")
        return 0

    if not isinstance(row.latest_slot, int):
        logging.error(f"Expected an integer value for latest_slot, got: {type(row.latest_slot)}")
        return None

    startSlot = row.latest_slot + 1
    return startSlot