import sys, logging, asyncio
from os import getenv
from custom_logger import JsonFormatter
from dotenv import load_dotenv
from api.extractor import async_execute as async_extract
from cloud_storage.transferor import async_execute as async_transfer
from bigquery.executor import async_execute as async_load

load_dotenv()

logging_level = getenv("LOGGING_LEVEL", "INFO")

logging.basicConfig(level=logging.getLevelName(logging_level))
logging.getLogger("asyncio").setLevel(logging.ERROR)
logging.getLogger("google.api_core").setLevel(logging.ERROR)

log_handler = logging.StreamHandler()
json_formatter = JsonFormatter()
log_handler.setFormatter(json_formatter)
logging.getLogger().handlers = [log_handler]

async def async_execute():  
    logging.info("payloads etl running")

    try:        
        if await async_extract() is False:
            sys.exit(1)

        if await async_transfer() is False:
            sys.exit(1)

        if await async_load() is False:
            sys.exit(1)

        logging.info("payloads etl completed successfully")

    except Exception as e:
        logging.error(f"an unexpected error occurred: {e}")        
        sys.exit(1)

if __name__ == '__main__':
    asyncio.run(async_execute())