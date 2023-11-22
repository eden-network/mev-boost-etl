from io import BytesIO
import unittest
from transformer_json_bytes import transform_bytes
from gzip import GzipFile

class TestJsonByteTransformer(unittest.TestCase):    

    def test_transform_and_check_csv_on_disk(self):
        relay = "flashbots"
        slot = "7567001"
        with open(f"./data/bids/{relay}-{slot}.json", "rb") as file_stream:
            json_bytes = file_stream.read()
            transformed_json_bytes = transform_bytes(json_bytes, "flashbots", "7567001")
            content = transformed_json_bytes.decode('utf-8')
            with open(f"./data/bids/{relay}_{slot}_T.json", 'w') as output_file:
                output_file.write(content)

    def test_transform_and_gzip_json_file(self):
        relay = "flashbots"
        slot = "7567002"
        with open(f"./data/bids/{relay}-{slot}.json", "rb") as file_stream:
            json_bytes = file_stream.read()
            transformed_json_bytes = transform_bytes(json_bytes, "flashbots", "7567001")
            
            gzip_buffer = BytesIO()                    
            with GzipFile(None, 'wb', fileobj=gzip_buffer) as gzip_out:
                gzip_out.write(transformed_json_bytes)

            with open(f"./data/bids/{relay}_{slot}_T.gz", 'wb') as output_file:
                output_file.write(gzip_buffer.getvalue())

if __name__ == '__main__':  
    unittest.main()