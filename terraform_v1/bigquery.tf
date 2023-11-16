resource "google_bigquery_dataset" "mev_boost" {
  dataset_id                  = "mev_boost"
  description                 = "Dataset for housing mev-boost staging data"
  location                    = "US"

  access {
    role          = "OWNER"
    user_by_email = data.google_service_account.mev_boost_sync_sa.email
  }
}

resource "google_bigquery_table" "bids_staging" {
  dataset_id = google_bigquery_dataset.mev_boost.dataset_id
  table_id   = "bids_staging"
  deletion_protection = false

  time_partitioning {
    type = "DAY"
    field = "timestamp"
  }

  labels = {
    env = "test"
  }  

  schema = <<EOF
[
  {
    "description": "the relay that receveived the block",
    "mode": "REQUIRED",
    "name": "relay",
    "type": "STRING"
  },
  {
    "description": "slot number",
    "mode": "REQUIRED",
    "name": "slot",
    "type": "INTEGER"
  },
  {
    "description": "hash of the parent block",
    "mode": "REQUIRED",
    "name": "parent_hash",
    "type": "STRING"
  },
  {
    "description": "hash of the block",
    "mode": "REQUIRED",
    "name": "block_hash",
    "type": "STRING"
  },
  {
    "description": "public key of builder",
    "mode": "REQUIRED",
    "name": "builder_pubkey",
    "type": "STRING"
  },
  {
    "description": "public key of proposer",
    "mode": "REQUIRED",
    "name": "proposer_pubkey",
    "type": "STRING"
  },
  {
    "description": "fee recipient of proposer",
    "mode": "REQUIRED",
    "name": "proposer_fee_recipient",
    "type": "STRING"
  },
  {
    "description": "the maximum gas allowed in this block",
    "mode": "REQUIRED",
    "name": "gas_limit",
    "type": "INTEGER"
  },
  {
    "description": "the total used gas by all transactions in this block",
    "mode": "REQUIRED",
    "name": "gas_used",
    "type": "INTEGER"
  },
  {
    "description": "mev block reward",
    "mode": "REQUIRED",
    "name": "value",
    "type": "NUMERIC"
  },
  {
    "description": "the number of transactions in the block",
    "mode": "REQUIRED",
    "name": "num_tx",
    "type": "INTEGER"
  },
  {
    "description": "the block number",
    "mode": "REQUIRED",
    "name": "block_number",
    "type": "INTEGER"
  },
  {
    "description": "timestamp block received",
    "mode": "REQUIRED",
    "name": "timestamp",
    "type": "TIMESTAMP"
  },
  {
    "description": "timestamp in seconds when block received",
    "mode": "REQUIRED",
    "name": "timestamp_s",
    "type": "INTEGER"
  },
  {
    "description": "timestamp in ms when block received",
    "mode": "REQUIRED",
    "name": "timestamp_ms",
    "type": "INTEGER"
  },
  {
    "description": "whether block submitted was configured as optimistic",
    "name": "optimistic_submission",
    "type": "BOOLEAN"
  }
]
EOF

}

resource "google_bigquery_table" "config" {
  dataset_id = google_bigquery_dataset.mev_boost.dataset_id
  table_id   = "bids_pod_config"
  project    = google_bigquery_dataset.mev_boost.project
  deletion_protection = false

  view {
    query = <<EOF
with numbers as (
  select x
  from unnest(generate_array(0, 7)) as x
)
select  format('mev-boost-bids-statefulset-%d', x) as pod_name,
        7710300 - (x * 37500) as start_slot,
        case  when x = 7 
              then 7410300 
              else 7710300 - (x * 37500) - 37500 + 1 end as end_slot
from numbers
order by x        
EOF    
    use_legacy_sql = false
  }
}


resource "google_bigquery_table" "bids_staging_deduped" {
  dataset_id = google_bigquery_dataset.mev_boost.dataset_id
  table_id   = "bids_staging_deduped"
  deletion_protection = false

  time_partitioning {
    type = "DAY"
    field = "timestamp"
  }

  labels = {
    env = "test"
  }  

  schema = <<EOF
[
  {
    "description": "the relay that receveived the block",
    "mode": "REQUIRED",
    "name": "relay",
    "type": "STRING"
  },
  {
    "description": "slot number",
    "mode": "REQUIRED",
    "name": "slot",
    "type": "INTEGER"
  },
  {
    "description": "hash of the parent block",
    "mode": "REQUIRED",
    "name": "parent_hash",
    "type": "STRING"
  },
  {
    "description": "hash of the block",
    "mode": "REQUIRED",
    "name": "block_hash",
    "type": "STRING"
  },
  {
    "description": "public key of builder",
    "mode": "REQUIRED",
    "name": "builder_pubkey",
    "type": "STRING"
  },
  {
    "description": "public key of proposer",
    "mode": "REQUIRED",
    "name": "proposer_pubkey",
    "type": "STRING"
  },
  {
    "description": "fee recipient of proposer",
    "mode": "REQUIRED",
    "name": "proposer_fee_recipient",
    "type": "STRING"
  },
  {
    "description": "the maximum gas allowed in this block",
    "mode": "REQUIRED",
    "name": "gas_limit",
    "type": "INTEGER"
  },
  {
    "description": "the total used gas by all transactions in this block",
    "mode": "REQUIRED",
    "name": "gas_used",
    "type": "INTEGER"
  },
  {
    "description": "mev block reward",
    "mode": "REQUIRED",
    "name": "value",
    "type": "NUMERIC"
  },
  {
    "description": "the number of transactions in the block",
    "mode": "REQUIRED",
    "name": "num_tx",
    "type": "INTEGER"
  },
  {
    "description": "the block number",
    "mode": "REQUIRED",
    "name": "block_number",
    "type": "INTEGER"
  },
  {
    "description": "timestamp block received",
    "mode": "REQUIRED",
    "name": "timestamp",
    "type": "TIMESTAMP"
  },
  {
    "description": "timestamp in seconds when block received",
    "mode": "REQUIRED",
    "name": "timestamp_s",
    "type": "INTEGER"
  },
  {
    "description": "timestamp in ms when block received",
    "mode": "REQUIRED",
    "name": "timestamp_ms",
    "type": "INTEGER"
  },
  {
    "description": "whether block submitted was configured as optimistic",
    "name": "optimistic_submission",
    "type": "BOOLEAN"
  }
]
EOF
}

resource "google_bigquery_table" "bids_ui" {
  dataset_id = google_bigquery_dataset.mev_boost.dataset_id
  table_id   = "bids_ui"
  deletion_protection = false

  range_partitioning {
    field = "block_number"
    range {
      start    = "18237000"
      end      = "18519100"
      interval = "100"
    }
  }

  labels = {
    env = "test"
  }  

  schema = <<EOF
[ {
    "description": "the relay that receveived the block",
    "mode": "REQUIRED",
    "name": "relay",
    "type": "STRING"
  },
  {
    "description": "slot number",
    "mode": "REQUIRED",
    "name": "slot",
    "type": "INTEGER"
  },
  {
    "description": "hash of the parent block",
    "mode": "REQUIRED",
    "name": "parent_hash",
    "type": "STRING"
  },
  {
    "description": "hash of the block",
    "mode": "REQUIRED",
    "name": "block_hash",
    "type": "STRING"
  },
  {
    "description": "public key of builder",
    "mode": "REQUIRED",
    "name": "builder_pubkey",
    "type": "STRING"
  },
  {
    "description": "public key of proposer",
    "mode": "REQUIRED",
    "name": "proposer_pubkey",
    "type": "STRING"
  },
  {
    "description": "fee recipient of proposer",
    "mode": "REQUIRED",
    "name": "proposer_fee_recipient",
    "type": "STRING"
  },
  {
    "description": "the maximum gas allowed in this block",
    "mode": "REQUIRED",
    "name": "gas_limit",
    "type": "INTEGER"
  },
  {
    "description": "the total used gas by all transactions in this block",
    "mode": "REQUIRED",
    "name": "gas_used",
    "type": "INTEGER"
  },
  {
    "description": "mev block reward",
    "mode": "REQUIRED",
    "name": "value",
    "type": "NUMERIC"
  },
  {
    "description": "the number of transactions in the block",
    "mode": "REQUIRED",
    "name": "num_tx",
    "type": "INTEGER"
  },
  {
    "description": "the block number",
    "mode": "REQUIRED",
    "name": "block_number",
    "type": "INTEGER"
  },
  {
    "description": "timestamp block received",
    "mode": "REQUIRED",
    "name": "timestamp",
    "type": "TIMESTAMP"
  },
  {
    "description": "timestamp in seconds when block received",
    "mode": "REQUIRED",
    "name": "timestamp_s",
    "type": "INTEGER"
  },
  {
    "description": "timestamp in ms when block received",
    "mode": "REQUIRED",
    "name": "timestamp_ms",
    "type": "INTEGER"
  },
  {
    "description": "whether block submitted was configured as optimistic",
    "name": "optimistic_submission",
    "type": "BOOLEAN"
  }
]
EOF
}