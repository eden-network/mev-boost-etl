select min(slot), max(slot)
from `enduring-art-207419.mev_boost.bids_staging` 

select block_slot, block_timestamp
from `public-data-finance.crypto_ethereum2.beacon_blocks`
where block_timestamp > timestamp("2023-12-25")
  and block_slot in (8151602, 8158048)