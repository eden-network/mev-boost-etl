import sys, asyncio, logging
from os import getenv
from dotenv import load_dotenv
load_dotenv()

from custom_logger import JsonFormatter
from bigquery.executor import async_execute as async_load

logging_level = getenv("LOGGING_LEVEL", "INFO")

logging.basicConfig(level=logging.getLevelName(logging_level))
logging.getLogger("google.api_core").setLevel(logging.ERROR)
logging.getLogger("asyncio").setLevel(logging.ERROR)

log_handler = logging.StreamHandler()
json_formatter = JsonFormatter()
log_handler.setFormatter(json_formatter)
logging.getLogger().handlers = [log_handler]

async def async_execute() -> bool:
    logging.info("bids load running")

    try:        
        if await async_load() is False:
            sys.exit(1)

        logging.info("bids load completed")

    except Exception as e:
        logging.error(f"an unexpected error occurred: {e}")        
        sys.exit(1)

if __name__ == '__main__':
    asyncio.run(async_execute())