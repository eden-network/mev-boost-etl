with numbers as (
  select x
  from unnest(generate_array(0, 19)) as x
), range_table as (
  select  x as `order`,
          format('mev-boost-bids-statefulset-%d', x) as pod_name,
          8158048 - (x * 323) as start_slot,
          case  when x = 19 
                then 8151600 
                else 8158048 - (x * 323) - 323 + 1 end as end_slot
  from numbers
)  
select *, start_slot - end_slot
from range_table 