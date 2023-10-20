import json
import logging
from datetime import datetime, date

def transform_bytes(bytes: bytes, relay: str, slot: date) -> bytes | None:
    """
    Transforms JSON bytes, adding additional properties to each JSON object
    and returning newline delimited json bytes.
    """
    try:        
        json_content = json.loads(bytes.decode('utf-8'))
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
        
        transformed_json_content = "\n".join(transformed_lines) + "\n"        
        return transformed_json_content.encode('utf-8')

    except Exception as e:
        logging.error(f"an error occurred while processing json bytes for {relay} {slot}: {str(e)}")
        return None

