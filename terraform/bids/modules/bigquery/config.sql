select relay, max(slot) as end_slot
from `eden-data-private.mev_boost.bids`
group by relay