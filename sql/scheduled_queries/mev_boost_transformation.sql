-- archive staging rows as failsafe
insert into `eden-data-private.flashbots.mev_boost_staging_archive`
select *
from `eden-data-private.flashbots.mev_boost_staging`;

-- insert new rows into blocks tables from staging
insert into `eden-data-public.flashbots.mev_boost`
with blocks as (
  select  b.`timestamp` as block_timestamp,
          b.`number` as block_number,
          b.`hash` as block_hash
  from `bigquery-public-data.crypto_ethereum.blocks` b
  where b.`timestamp` > timestamp_sub(current_timestamp(), interval 1 day)
)
select  b1.block_timestamp,
        mbs.*,
        case when b2.block_timestamp is null then true else false end as reorged
from `eden-data-private.flashbots.mev_boost_staging_archive` mbs
join blocks b1 on b1.block_number = mbs.block_number
left join blocks b2 on b2.block_hash = mbs.block_hash;

-- truncate staging table for subsequent loads
truncate table `eden-data-private.flashbots.mev_boost_staging`;