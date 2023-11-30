with numbers as (
  select x
  from unnest(generate_array(0, 9)) as x
), range_table as (
  select  format('mev-boost-bids-statefulset-%d', x) as pod_name,
          7770000 - (x * 1000) as start_slot,
          case  when x = 9 
                then 7760001 
                else 7770000 - (x * 1000) - 1000 + 1 end as end_slot
  from numbers n
)
select  rt.pod_name,
        rt.start_slot,
        rt.end_slot,
        lt.process_attempted              
from range_table rt
left join `${project_id}.${dataset_id}.${lock_table_id}` lt on rt.pod_name = lt.pod_name
order by rt.pod_name