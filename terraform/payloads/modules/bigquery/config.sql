with head_slot_per_relay as (
  select  relay,
          max(slot) as head_slot,
          min(slot) as tail_slot
  from `${project_id}.${dataset_id}.${table_id}` mb
  group by relay
)
select  mbm.relay,
        mbm.url,
        mbm.payloads_batch_size as batch_size,
        mbm.active,         
        hspr.head_slot as head_slot,
        hspr.tail_slot as tail_slot
from `${project_id}.${dataset_id}.${etl_config_view_id}` mbm
left join head_slot_per_relay hspr on hspr.relay = mbm.relay