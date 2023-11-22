import asyncio
import json
import logging
from datetime import datetime, date
from io import BytesIO
from gzip import GzipFile

async def async_transform_bytes(input_bytes: bytes, relay: str, slot: date) -> bytes | None:
    return await asyncio.get_running_loop().run_in_executor(
        None, 
        transform_bytes, 
        input_bytes, 
        relay, 
        slot
    )

async def async_gzip_bytes(input_bytes: bytes) -> bytes | None:
    return await asyncio.get_running_loop().run_in_executor(
        None, 
        gzip_bytes, 
        input_bytes
    )

def transform_bytes(input_bytes: bytes, relay: str, slot: date) -> bytes | None:
    try:        
        json_content = json.loads(input_bytes.decode('utf-8'))
        transformed_lines = []

        for obj in json_content:                        
            timestamp_secs = int(obj.get('timestamp'))
            timestamp_millis = int(obj.get('timestamp_ms'))            
            milliseconds = timestamp_millis % 1000
            timestamp_str = datetime.utcfromtimestamp(timestamp_secs).strftime('%Y-%m-%d %H:%M:%S') + f".{milliseconds:03}000"
                        
            obj['timestamp_s'] = obj.get('timestamp')
            obj['timestamp'] = timestamp_str 
            obj['relay'] = relay
            
            transformed_line = json.dumps(obj)
            transformed_lines.append(transformed_line)
        
        if len(transformed_lines) == 0:
            return b''
        
        transformed_json_content = "\n".join(transformed_lines) + "\n"        
        return transformed_json_content.encode('utf-8')

    except Exception as e:
        logging.error(f"an error occurred while processing json bytes for {relay} {slot}: {str(e)}")
        return None
    
def gzip_bytes(input_bytes: bytes) -> bytes | None:
    try:
        with BytesIO() as gzip_file_stream:
            with GzipFile(fileobj=gzip_file_stream, mode='wb') as gzip_file:
                gzip_file.write(input_bytes)
            return gzip_file_stream.getvalue()
    except Exception as e:
        logging.error(f"an error occurred while gzipping bytes: {str(e)}")
        return None

