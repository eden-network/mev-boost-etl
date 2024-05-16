import sys, asyncio, logging
from custom_logger import JsonFormatter
from os import getenv
from dotenv import load_dotenv
from bigquery.executor import async_execute as async_load

load_dotenv()

logging_level = getenv("LOGGING_LEVEL", "INFO")
logging.basicConfig(level=logging.getLevelName(logging_level))
logging.getLogger("google.api_core").setLevel(logging.ERROR)
logging.getLogger("asyncio").setLevel(logging.ERROR)

log_handler = logging.StreamHandler()
json_formatter = JsonFormatter()
log_handler.setFormatter(json_formatter)
logging.getLogger().handlers = [log_handler]

async def async_execute() -> bool:
    logging.info("payloads load running")

    try:        
        if await async_load() is False:
            sys.exit(1)

        logging.info("payloads load completed")

    except Exception as e:
        logging.error(f"an unexpected error occurred: {e}")        
        sys.exit(1)

if __name__ == '__main__':
    asyncio.run(async_execute())    