with numbers as (
  select x
  from unnest(generate_array(0, 9)) as x
)
select  format('mev-boost-bids-statefulset-%d', x) as pod_name,
        7805560 - (x * 1555) as start_slot,
        case  when x = 9 
              then 7790001 
              else 7805560 - (x * 1555) - 1555 + 1 end as end_slot
from numbers
order by x