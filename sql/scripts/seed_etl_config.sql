insert into `enduring-art-207419.mev_boost.etl_config`
select  'blocknative' as relay, false as active, 'https://builder-relay-mainnet.blocknative.com/relay/v1/data/bidtraces' as url, 450 as payloads_batch_size, 2 as bids_rate_limit
union all
select  'bloxrouteMaxProfit' as relay, true as active, 'https://bloxroute.max-profit.blxrbdn.com/relay/v1/data/bidtraces' as url, 100 as payloads_batch_size, 2 as bids_rate_limit
union all
select  'bloxrouteRegulated' as relay, true as active, 'https://bloxroute.regulated.blxrbdn.com/relay/v1/data/bidtraces' as url, 100 as payloads_batch_size, 2 as bids_rate_limit
union all
select  'manifold' as relay, true as active, 'https://mainnet-relay.securerpc.com/relay/v1/data/bidtraces' as url, 200 as payloads_batch_size, 2 as bids_rate_limit
union all
select  'aestus' as relay, true as active, 'https://mainnet.aestus.live/relay/v1/data/bidtraces' as url, 200 as payloads_batch_size, 2 as bids_rate_limit
union all
select  'agnostic' as relay, true as active, 'https://agnostic-relay.net/relay/v1/data/bidtraces' as url, 200 as payloads_batch_size, 2 as bids_rate_limit
union all
select  'eden' as relay, true as active, 'https://relay.edennetwork.io/relay/v1/data/bidtraces' as url, 200 as payloads_batch_size, 2 as bids_rate_limit
union all
select  'ultrasound' as relay, true as active, 'https://relay.ultrasound.money/relay/v1/data/bidtraces' as url, 200 as payloads_batch_size, 2 as bids_rate_limit
union all
select  'flashbots' as relay, true as active, 'https://boost-relay.flashbots.net/relay/v1/data/bidtraces' as url, 200 as payloads_batch_size, 2 as bids_rate_limit