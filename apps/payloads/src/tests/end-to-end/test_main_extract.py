import unittest
from unittest.mock import patch, AsyncMock
from main_extract import async_execute

class TestIntegrationMainExtract(unittest.IsolatedAsyncioTestCase):

    @patch('api.extractor.async_get_config', new_callable=AsyncMock)
    @patch('api.extractor.async_get_latest_slot', new_callable=AsyncMock)
    async def test_main_extract_with_mocked_metadata(self, mock_get_latest_slot, mock_get_config):
        mock_get_config.return_value = [                
                {'relay': 'titan', 'url': 'https://titanrelay.xyz/relay/v1/data/bidtraces', 'batch_size': 200, 'active': True, 'head_slot': 8597233}
            ]
        mock_get_latest_slot.return_value = 8927153
        await async_execute()

    async def test_main_extract(self):
        await async_execute()

if __name__ == '__main__':
    unittest.main()