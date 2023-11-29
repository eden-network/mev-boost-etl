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

resource "google_bigquery_table" "bids_staging_archive" {
  dataset_id = var.dataset_id
  table_id   = "${var.staging_table_id}_archive"
  description = "archive table for ${var.staging_table_id} table"
  
  time_partitioning {
    type              = "DAY"
    field             = "timestamp"
    expiration_ms     = 2592000000  # 30 days in milliseconds    
  }

  labels = var.labels

  schema = file("${path.module}/bids_staging.json")
}

resource "google_bigquery_table" "bids" {
  dataset_id = var.dataset_id
  table_id   = var.table_id

  time_partitioning {
    type  = "DAY"
    field = "block_timestamp"
  }

  clustering = ["relay", "builder_pubkey", "slot"]  

  labels = var.labels

  schema = file("${path.module}/bids.json")
}

resource "google_bigquery_table" "bids_ui" {
  dataset_id = var.dataset_id
  table_id   = var.ui_table_id  
  deletion_protection = false

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



resource "google_bigquery_table" "config" {
  dataset_id = var.dataset_id
  table_id   = var.config_view_id

  view {
    query = templatefile("${path.module}/config.sql", {
      project_id = var.project_id,
      dataset_id = var.dataset_id,
      bids_table_id   = var.table_id
    })
    use_legacy_sql = false
  }
}

resource "google_bigquery_routine" "sproc" {
  dataset_id = var.dataset_id

  routine_id = var.load_storedproc_name
  routine_type = "PROCEDURE"
  language = "SQL"
  definition_body = templatefile("${path.module}/load_bids.sql", {
    sp_id = var.load_storedproc_name,
    project_id = var.project_id,
    dataset_id = var.dataset_id,
    bids_table_id   = var.table_id,
    bids_staging_table_id = var.staging_table_id,
    bids_staging_archive_table_id = "${var.staging_table_id}_archive",
    ui_table_id = var.ui_table_id,
    public_project_id = var.public_project_id
  })
}

# resource "google_bigquery_table" "bids_public" {
#   project = var.public_project_id
#   dataset_id = var.dataset_id
#   table_id   = var.table_id
#   deletion_protection = false
#   view {
#     query = templatefile("${path.module}/bids_public.sql", {    
#     project_id = var.project_id,
#     dataset_id = var.dataset_id,
#     table_id   = var.table_id 
#   })
#     use_legacy_sql = false
#   }
# }

# resource "google_bigquery_dataset_access" "permissioned_view" {
#   dataset_id = var.dataset_id

#   view {
#     project_id = var.public_project_id
#     dataset_id = var.dataset_id
#     table_id   = var.table_id
#   }
# }

resource "google_bigquery_table" "bids_public" {
  project = var.public_project_id
  dataset_id = var.dataset_id
  table_id   = var.table_id

  time_partitioning {
    type              = "DAY"
    field             = "block_timestamp"
    expiration_ms     = 2419200000  # 28 days in milliseconds    
  }

  labels = var.labels

  schema = file("${path.module}/bids.json")
}
