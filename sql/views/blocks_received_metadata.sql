create or replace view flashbots.mev_boost_metadata as
with head_slot_per_relay as (
  select  relay,
          max(slot) as head_slot,
          min(slot) as tail_slot
  from `eden-data-public.flashbots.blocks_received` mb
  group by relay
)
select  mbm.relay,
        mbm.url,
        mbm.batch_size,
        mbm.active, 
        mbm.back_fill,       
        coalesce(hspr.head_slot, 0) as head_slot,
        coalesce(hspr.tail_slot, 0) as tail_slot
from `eden-data-private.flashbots.mev_boost_config` mbm
left join head_slot_per_relay hspr on hspr.relay = mbm.relay