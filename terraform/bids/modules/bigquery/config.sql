select relay, max(slot) as end_slot
from `${project_id}.${dataset_id}.${bids_table_id}`
group by relay