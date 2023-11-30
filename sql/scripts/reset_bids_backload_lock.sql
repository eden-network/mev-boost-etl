begin transaction;

  truncate table `enduring-art-207419.mev_boost.bids_k8s_lock`;

  insert into `enduring-art-207419.mev_boost.bids_k8s_lock`
  with numbers as (
    select x
    from unnest(generate_array(0, 9)) as x
  )
  select  format('mev-boost-bids-statefulset-%d', x) as pod_name,
          false as process_attempted
  from numbers
  order by x;

commit transaction;