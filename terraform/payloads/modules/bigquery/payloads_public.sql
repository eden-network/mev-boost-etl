select *
from `${project_id}.${dataset_id}.${table_id}`
where block_timestamp > timestamp_sub(current_timestamp(), interval 28 day)
