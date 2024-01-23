create temp table distinct_bids as
select  distinct block_timestamp,
        relay,
        slot,
        parent_hash,
        block_hash,
        builder_pubkey,
        proposer_pubkey,
        proposer_fee_recipient,
        gas_limit,
        gas_used,
        value,
        num_tx,
        block_number,
        timestamp,
        timestamp_s,
        timestamp_ms,
        optimistic_submission
from `eden-data-private.mev_boost.bids`;

truncate table `eden-data-private.mev_boost.bids`;

insert into `eden-data-private.mev_boost.bids`
select *
from distinct_bids;

truncate table `eden-data-private.mev_boost.bids_ui`;

insert into `eden-data-private.mev_boost.bids_ui`
select * except(block_timestamp)
from `eden-data-private.mev_boost.bids`;

truncate table `eden-data-public.mev_boost.bids`;

insert into `eden-data-public.mev_boost.bids`
select *
from `eden-data-private.mev_boost.bids`
where block_timestamp > timestamp_sub(current_timestamp(), INTERVAL -29 day);