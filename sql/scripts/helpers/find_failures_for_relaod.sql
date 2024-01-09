select  regexp_extract(jsonpayload.message, r'https://([^/]+)') as domain,
        regexp_extract(jsonpayload.message, r'(https://[^\s?]+)') as base_url, 
        ec.relay,               
        regexp_extract(jsonpayload.message, r'slot=(\d+)') as slot
from `enduring-art-207419.mev_boost.stderr_20231205` mb
join `enduring-art-207419.mev_boost.etl_config` ec on concat(ec.url,"/builder_blocks_received") = regexp_extract(jsonpayload.message, r'(https://[^\s?]+)')
where severity = "ERROR"  
  	and jsonpayload.message like "failed to download data for%"  
  and `timestamp` > timestamp("2023-12-05 17:00:00")
  and `timestamp` < timestamp("2023-12-06 09:00:00")   
order by `timestamp` desc