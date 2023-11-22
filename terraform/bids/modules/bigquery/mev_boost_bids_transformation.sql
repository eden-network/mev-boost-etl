-- get latest staged bids and put them into temp table so we only access the data once
create temp table last_hour_bids as
select distinct *
from `enduring-art-207419.mev_boost.bids_staging`;

-- archive staging rows as failsafe
insert into `enduring-art-207419.mev_boost.bids_staging_archive`
select *
from last_hour_bids;

-- delete from staging table
delete `enduring-art-207419.mev_boost.bids_staging` bd
where exists (
  select 1
  from last_hour_bids lhb
  where bd.relay = lhb.relay and
        bd.slot = lhb.slot and
        bd.parent_hash = lhb.parent_hash and
        bd.block_hash = lhb.block_hash and
        bd.builder_pubkey = lhb.builder_pubkey and
        bd.proposer_pubkey = lhb.proposer_pubkey and
        bd.proposer_fee_recipient = lhb.proposer_fee_recipient and
        bd.gas_limit = lhb.gas_limit and
        bd.gas_used = lhb.gas_used and
        bd.value = lhb.value and
        bd.num_tx = lhb.num_tx and
        bd.block_number = lhb.block_number and
        bd.timestamp = lhb.timestamp and
        bd.timestamp_s = lhb.timestamp_s and
        bd.timestamp_ms = lhb.timestamp_ms and
        coalesce(bd.optimistic_submission, false) = coalesce(lhb.optimistic_submission, false)
);

-- -- insert new rows into bids tables from staging
insert into `enduring-art-207419.mev_boost.bids`
with blocks as (
  select  b.`timestamp` as block_timestamp,
          b.`number` as block_number          
  from `bigquery-public-data.crypto_ethereum.blocks` b
  where b.`timestamp` > timestamp_sub(current_timestamp(), interval 1 day)
)
select  b1.block_timestamp,
        lhb.*        
from last_hour_bids lhb
join blocks b1 on b1.block_number = lhb.block_number;