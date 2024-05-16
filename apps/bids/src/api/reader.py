import asyncio, requests, logging
from requests.exceptions import RequestException

async def async_download_bids(url: str) -> bytes | None:
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(
        None,
        download_bids,
        url
    )

def download_bids(url: str) -> bytes | None:
    try:
        response = requests.get(url, stream=True, timeout=60)
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