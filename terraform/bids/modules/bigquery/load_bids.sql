-- get latest staged bids and put them into temp table so we only access the data once
create temp table latest_bids as
select distinct *
from `${project_id}.${dataset_id}.${bids_staging_table_id}`;

-- archive staging rows as failsafe
insert into `${project_id}.${dataset_id}.${bids_staging_archive_table_id}`
select *
from latest_bids;

-- delete from staging table
delete `${project_id}.${dataset_id}.${bids_staging_table_id}` bd
where exists (
select 1
from latest_bids lhb
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

-- decorate bids with block_timestamp for final partitioning
create temp table bids_decorated as
with blocks as (
select  b.`timestamp` as block_timestamp,
        b.`number` as block_number          
from `bigquery-public-data.crypto_ethereum.blocks` b
where b.`timestamp` > timestamp_sub(current_timestamp(), interval 1 day)
)
select  b1.block_timestamp,
        lhb.*        
from latest_bids lhb
join blocks b1 on b1.block_number = lhb.block_number;

insert into `${project_id}.${dataset_id}.${bids_table_id}`
select *
from bids_decorated;

insert into `${public_project_id}.${dataset_id}.${bids_table_id}`
select *
from bids_decorated;

insert into `${project_id}.${dataset_id}.${ui_table_id}`
select  *
from latest_bids;