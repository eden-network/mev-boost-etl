import asyncio, logging, json
from typing import Tuple, List
from io import BytesIO
from gzip import GzipFile

async def async_gzip_bytes(input_bytes: bytes) -> bytes | None:
    return await asyncio.get_running_loop().run_in_executor(
        None, 
        gzip_bytes, 
        input_bytes
    )
    
def gzip_bytes(input_bytes: bytes) -> bytes | None:
    try:
        with BytesIO() as gzip_file_stream:
            with GzipFile(fileobj=gzip_file_stream, mode='wb') as gzip_file:
                gzip_file.write(input_bytes)
            return gzip_file_stream.getvalue()
    except Exception as e:
        logging.error(f"an error occurred while gzipping bytes: {str(e)}")
        return None
    
async def async_transform_bytes(input_bytes: bytes, relay: str, end_slot: int) -> Tuple[bytes, List | None] | Tuple[None, None]:
    return await asyncio.get_running_loop().run_in_executor(
        None, 
        transform_bytes, 
        input_bytes, 
        relay,
        end_slot
    )
    
def transform_bytes(input_bytes: bytes, relay: str, end_slot: int) -> Tuple[bytes, List] | Tuple[None, None]:
    try:
        json_content = json.loads(input_bytes.decode('utf-8'))
        transformed_lines = []
        slots = set()

        for obj in json_content:
            obj['relay'] = relay
            if int(obj['slot']) > end_slot:
                slots.add(int(obj['slot']))
                transformed_line = json.dumps(obj)
                transformed_lines.append(transformed_line)
            else:                
                break

        if not transformed_lines:
            return None, [] # this means we're done with the extraction

        transformed_json_content = "\n".join(transformed_lines) + "\n"

        sorted_slots = sorted(slots, reverse=True)

        return transformed_json_content.encode('utf-8'), sorted_slots

    except Exception as e:
        logging.error(f"An error occurred while processing JSON bytes for {relay}: {str(e)}")
        return None, None