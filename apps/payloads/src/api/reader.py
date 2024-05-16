import asyncio, requests
from requests.exceptions import RequestException
import logging

async def async_download(url: str) -> bytes | None:
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(
        None,
        download,
        url
    )

def download(url: str) -> bytes | None:
    try:
        response = requests.get(url, stream=True)
        if response.status_code == 200:
            logging.debug(f"successfully downloaded data for {url}.")
            return response.content
        else:
            logging.error(f"failed to download data for {url}. response code: {response.status_code}")
            return None
    except RequestException as e:
        logging.error(f"failed to download data for {url}: {e}")
        return None
    except Exception as e:
        logging.error(f"an error occurred for {url}: {e}")
        return None