resource "google_bigquery_table" "bids_staging" {
  dataset_id = var.dataset_id
  table_id   = var.staging_table_id

  time_partitioning {
    type  = "DAY"
    field = "timestamp"
  }

  labels = var.labels

  schema = file("${path.module}/bids_staging.json")
}

resource "google_bigquery_table" "bids_ui" {
  dataset_id = var.dataset_id
  table_id   = var.ui_table_id  

  range_partitioning {
    field = "block_number"
    range {
      start    = var.block_number_partitioning_start
      end      = var.block_number_partitioning_end
      interval = var.block_number_partitioning_interval
    }
  }

  labels = var.labels 

  schema = file("${path.module}/bids_staging.json")
}
