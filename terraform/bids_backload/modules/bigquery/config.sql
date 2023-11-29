with numbers as (
  select x
  from unnest(generate_array(0, 9)) as x
)
select  format('mev-boost-bids-statefulset-%d', x) as pod_name,
        7780000 - (x * 1000) as start_slot,
        case  when x = 9 
              then 7770001 
              else 7780000 - (x * 1000) - 1000 + 1 end as end_slot
from numbers
order by x