select  partition_id, 
      total_rows
from `eden-data-private.mev_boost.INFORMATION_SCHEMA.PARTITIONS`
where table_name = "bids"
  and partition_id != "__NULL__"
  and partition_id is not null
order by partition_id desc ;