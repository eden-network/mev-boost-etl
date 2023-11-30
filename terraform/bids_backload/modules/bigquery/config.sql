with numbers as (
  select x
  from unnest(generate_array(0, 19)) as x
), range_table as (
  select  x as `order`,
          format('mev-boost-bids-statefulset-%d', x) as pod_name,
          7740000 - (x * 1000) as start_slot,
          case  when x = 19 
                then 7720001 
                else 7740000 - (x * 1000) - 1000 + 1 end as end_slot
  from numbers
)
select  rt.pod_name,
        rt.start_slot,
        rt.end_slot,
        rt.`order`,
        lt.process_attempted,        
from range_table rt
left join `${project_id}.${dataset_id}.${lock_table_id}` lt on rt.pod_name = lt.pod_name
order by rt.pod_name