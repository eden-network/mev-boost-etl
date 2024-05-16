import unittest
from unittest.mock import patch
from main_extract import async_execute

class TestIntegrationMainTransfer(unittest.IsolatedAsyncioTestCase):

    @patch('main.async_get_config')
    async def test_main_extract_with_mocked_metadata(self, mock_get_config):
        mock_get_config.return_value = [                
                {'relay': 'titan', 'url': 'https://titanrelay.xyz/relay/v1/data/bidtraces', 'batch_size': 200, 'active': True, 'head_slot': 8597232}
            ]
        await async_execute()

    async def test_main_extract(self):
        await async_execute()

if __name__ == '__main__':
    unittest.main()