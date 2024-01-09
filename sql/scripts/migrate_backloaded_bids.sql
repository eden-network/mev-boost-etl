declare start_slot int64; 
declare end_slot int64; 
declare existing_count int64;
set start_slot = 6930000;
set end_slot = 7180000;
begin transaction;
  
  set existing_count = (
      select count(*)
      from `eden-data-private.mev_boost.bids`
      where slot > start_slot and slot <= end_slot
  );
  if existing_count > 0 then
      rollback transaction;      
      raise using message = 'records already exist in the destination table for the specified slot range.';
  end if;
  
  create temp table new_bids as  
  select *
  from `enduring-art-207419.mev_boost.bids`
  where slot > start_slot and slot <= end_slot;

  insert into `eden-data-private.mev_boost.bids`
  select *
  from new_bids;

  insert into `eden-data-private.mev_boost.bids_ui`
  select * except(block_timestamp)
  from new_bids;
  
  insert into `eden-data-public.mev_boost.bids`
  select *
  from new_bids;

rollback transaction;