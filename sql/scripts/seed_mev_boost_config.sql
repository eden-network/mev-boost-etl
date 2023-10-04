insert into `eden-data-private.flashbots.mev_boost_config`
select "eden" as relay, "https://relay.edennetwork.io/relay/v1/data/bidtraces/proposer_payload_delivered" as `url`, 200 as batch_size, true as active, false as back_fill
union all
select "manifold" as relay, "https://mainnet-relay.securerpc.com/relay/v1/data/bidtraces/proposer_payload_delivered" as `url`, 200 as batch_size, true as active, false as back_fill
union all
select "flashbots" as relay, "https://boost-relay.flashbots.net/relay/v1/data/bidtraces/proposer_payload_delivered" as `url`, 200 as batch_size, true as active, false as back_fill
union all
select "blocknative" as relay, "https://builder-relay-mainnet.blocknative.com/relay/v1/data/bidtraces/proposer_payload_delivered" as `url`, 450 as batch_size, true as active, false as back_fill
union all
select "bloxrouteMaxProfit" as relay, "https://bloxroute.max-profit.blxrbdn.com/relay/v1/data/bidtraces/proposer_payload_delivered" as `url`, 100 as batch_size, true as active, false as back_fill
union all
select "bloxrouteRegulated" as relay, "https://bloxroute.regulated.blxrbdn.com/relay/v1/data/bidtraces/proposer_payload_delivered" as `url`, 100 as batch_size, true as active, false as back_fill
union all
select "agnostic" as relay, "https://agnostic-relay.net/relay/v1/data/bidtraces/proposer_payload_delivered" as `url`, 200 as batch_size, true as active, false as back_fill
union all
select "ultrasound" as relay, "https://relay.ultrasound.money/relay/v1/data/bidtraces/proposer_payload_delivered" as `url`, 200 as batch_size, true as active, false as back_fill
union all
select "aestus" as relay, "https://mainnet.aestus.live/relay/v1/data/bidtraces/proposer_payload_delivered" as `url`, 200 as batch_size, true as active, false as back_fill;

