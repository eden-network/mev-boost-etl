begin transaction;

  delete `eden-data-private.mev_boost.bids` 
  where block_timestamp > timestamp('2023-12-25 00:00:00')
    and slot > 8056880;

  delete `eden-data-private.mev_boost.bids_staging`
  where 1 = 1;

  delete `eden-data-private.mev_boost.bids_staging_archive` 
  where slot > 8056880;

  delete `eden-data-public.mev_boost.bids` 
  where block_timestamp > timestamp('2023-12-25 00:00:00') 
    and slot > 8056880;

  delete `eden-data-private.mev_boost.bids_ui`
  where block_number > 18859360
    and slot > 8056880;

rollback transaction;