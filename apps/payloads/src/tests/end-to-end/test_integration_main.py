import logging
import unittest
from main import execute
from unittest.mock import patch

logging.basicConfig(level=logging.DEBUG)

class TestIntegrationRelayDataFunctions(unittest.TestCase):

    @patch('main.get_relay_metadata')
    def test_main_with_mocked_metadata(self, mock_get_relay_metadata):
        mock_get_relay_metadata.return_value = iter([
                # {'relay': 'bloxrouteMaxProfit', 'url': 'https://bloxroute.max-profit.blxrbdn.com/relay/v1/data/bidtraces/proposer_payload_delivered', 'batch_size': 100, 'back_fill': True, 'head_slot': 7466804, 'tail_slot': 7396069},
                # {'relay': 'bloxrouteRegulated', 'url': 'https://bloxroute.regulated.blxrbdn.com/relay/v1/data/bidtraces/proposer_payload_delivered', 'batch_size': 100, 'back_fill': False, 'head_slot': 7365691, 'tail_slot': 4700737},
                # {'relay': 'blocknative', 'url': 'https://builder-relay-mainnet.blocknative.com/relay/v1/data/bidtraces/proposer_payload_delivered', 'batch_size': 450, 'back_fill': False, 'head_slot': 7365691, 'tail_slot': 4700737},
                # {'relay': 'eden', 'url': 'https://relay.edennetwork.io/relay/v1/data/bidtraces/proposer_payload_delivered', 'batch_size': 200, 'back_fill': False, 'head_slot': 7365691, 'tail_slot': 4700737},
                # {'relay': 'aestus', 'url': 'https://mainnet.aestus.live/relay/v1/data/bidtraces/proposer_payload_delivered', 'batch_size': 200, 'back_fill': False, 'head_slot': 7365691, 'tail_slot': 4700737},
                # {'relay': 'flashbots', 'url': 'https://boost-relay.flashbots.net/relay/v1/data/bidtraces/proposer_payload_delivered', 'batch_size': 200, 'back_fill': False, 'head_slot': 7365691, 'tail_slot': 4700737},
                # {'relay': 'agnostic', 'url': 'https://agnostic-relay.net/relay/v1/data/bidtraces/proposer_payload_delivered', 'batch_size': 200, 'back_fill': True, 'head_slot': 7467154, 'tail_slot': 7397382}#,
                # {'relay': 'ultrasound', 'url': 'https://relay.ultrasound.money/relay/v1/data/bidtraces/proposer_payload_delivered', 'batch_size': 200, 'back_fill': False, 'head_slot': 7365691, 'tail_slot': 4700737},
                # {'relay': 'manifold', 'url': 'https://mainnet-relay.securerpc.com/relay/v1/data/bidtraces/proposer_payload_delivered', 'batch_size': 200, 'back_fill': False, 'head_slot': 7365691, 'tail_slot': 4700737}
            ])
        execute()

    def test_main_full(self):
        execute()

if __name__ == '__main__':
    unittest.main()