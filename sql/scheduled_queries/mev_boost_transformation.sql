-- archive staging rows as failsafe
insert into `enduring-art-207419.flashbots.mev_boost_staging_archive`
select *
from `enduring-art-207419.flashbots.mev_boost_staging`;

-- insert new rows into blocks tables from staging
insert into `flashbots.mev_boost`
select  b1.`timestamp` as block_timestamp,
        mbs.*,
        case when b2.`timestamp` is null then 0 else 1 end as reorged
from `enduring-art-207419.flashbots.mev_boost_staging` mbs
join `bigquery-public-data.crypto_ethereum.blocks` b1 on b1.`number` = mbs.block_number
left join `bigquery-public-data.crypto_ethereum.blocks` b2 on b2.`hash` = mbs.block_hash
where b1.`timestamp` > timestamp_sub(current_timestamp(), interval 1 day)
    and b2.`timestamp` > timestamp_sub(current_timestamp(), interval 1 day);

-- truncate staging table for subsequent loads
truncate table `enduring-art-207419.flashbots.mev_boost_staging`;