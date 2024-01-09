begin transaction;
        -- get latest staged bids and put them into temp table so we only access the data once
        create temp table latest_bids as
        select distinct *
        from `enduring-art-207419.mev_boost.bids_staging`;

        -- archive staging rows as failsafe
        insert into `eden-data-private.mev_boost.bids_staging_archive`
        select *
        from latest_bids;

        -- decorate bids with block_timestamp for final partitioning
        create temp table bids_decorated as
        with blocks as (
                select  b.`timestamp` as block_timestamp,
                        b.`number` as block_number          
                from `bigquery-public-data.crypto_ethereum.blocks` b
                where b.`timestamp` > timestamp("2024-01-07 16:00:46")
                        and b.`timestamp` <= timestamp("2024-01-08 13:29:59")
        )
        select  b1.block_timestamp,
                lhb.*        
        from latest_bids lhb
        join blocks b1 on b1.block_number = lhb.block_number;

        insert into `eden-data-private.mev_boost.bids`
        select *
        from bids_decorated;

        insert into `eden-data-public.mev_boost.bids`
        select *
        from bids_decorated;

        insert into `enduring-art-207419.mev_boost.bids_ui`
        select  *
        from latest_bids;

commit transaction;