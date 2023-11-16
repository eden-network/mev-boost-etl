with numbers as (
  select x
  from unnest(generate_array(0, 7)) as x
)
select  format('mev-boost-bids-statefulset-%d', x) as pod_name,
        7710300 - (x * 37500) as start_slot,
        case  when x = 7 
              then 7410300 
              else 7710300 - (x * 37500) - 37500 + 1 end as end_slot
from numbers
order by x