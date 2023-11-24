-- get latest staged payloads and put them into temp table so we only access the data once
create temp table latest_payloads as
select distinct *
from `${project_id}.${dataset_id}.${staging_table_id}`;

-- archive staging rows as failsafe
insert into `${project_id}.${dataset_id}.${staging_archive_table_id}`
select *
from latest_payloads;

-- delete from staging table
delete `${project_id}.${dataset_id}.${staging_table_id}` ps
where exists (
select 1
from latest_payloads lp
where   ps.relay = lp.relay and
        ps.slot = lp.slot and
        ps.parent_hash = lp.parent_hash and
        ps.block_hash = lp.block_hash and
        ps.builder_pubkey = lp.builder_pubkey and
        ps.proposer_pubkey = lp.proposer_pubkey and
        ps.proposer_fee_recipient = lp.proposer_fee_recipient and
        ps.gas_limit = lp.gas_limit and
        ps.gas_used = lp.gas_used and
        ps.value = lp.value and
        ps.num_tx = lp.num_tx and
        ps.block_number = lp.block_number              
);

-- decorate payloads with block_timestamp for final partitioning; work out whether the block has been reorged or not
insert into `${project_id}.${dataset_id}.${table_id}`
with blocks as (
  select  b.`timestamp` as block_timestamp,
          b.`number` as block_number,
          b.`hash` as block_hash         
from `bigquery-public-data.crypto_ethereum.blocks` b
where b.`timestamp` > timestamp_sub(current_timestamp(), interval 1 day)
)
select  b1.block_timestamp,
        lp.*,
        case when b2.block_timestamp is null then true else false end as reorged
from latest_payloads lp
join blocks b1 on b1.block_number = lp.block_number
left join blocks b2 on b2.block_hash = lp.block_hash;