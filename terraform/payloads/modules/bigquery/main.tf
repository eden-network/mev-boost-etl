resource "google_bigquery_table" "payloads" {
  dataset_id = var.dataset_id
  table_id   = var.table_id
  time_partitioning {
    type  = "DAY"
    field = "block_timestamp"
  }
  clustering = ["relay", "builder_pubkey", "slot"]
  labels     = var.labels
  schema     = file("${path.module}/payloads.json")
}

resource "google_bigquery_table" "payloads_staging" {
  dataset_id = var.dataset_id
  table_id   = var.staging_table_id
  labels     = var.labels
  schema     = file("${path.module}/payloads_staging.json")
}

resource "google_bigquery_table" "payloads_staging_archive" {
  dataset_id  = var.dataset_id
  table_id    = "${var.staging_table_id}_archive"
  description = "archive table for ${var.staging_table_id} table"
  labels      = var.labels
  schema      = file("${path.module}/payloads_staging.json")
}

resource "google_bigquery_table" "config" {
  dataset_id          = var.dataset_id
  table_id            = var.config_view_id
  deletion_protection = false
  view {
    query = templatefile("${path.module}/config.sql", {
      project_id         = var.project_id,
      dataset_id         = var.dataset_id,
      table_id           = var.table_id,
      etl_config_view_id = var.etl_config_view_id
    })
    use_legacy_sql = false
  }
}

resource "google_bigquery_routine" "sproc" {
  dataset_id   = var.dataset_id
  routine_id   = var.load_stored_procedure_id
  routine_type = "PROCEDURE"
  language     = "SQL"
  definition_body = templatefile("${path.module}/load_payloads.sql", {
    sp_id                    = var.load_stored_procedure_id,
    project_id               = var.project_id,
    dataset_id               = var.dataset_id,
    table_id                 = var.table_id,
    staging_table_id         = var.staging_table_id,
    staging_archive_table_id = "${var.staging_table_id}_archive",
    public_project_id        = var.public_project_id
  })
}

resource "google_bigquery_table" "payloads_public" {
  project    = var.public_project_id
  dataset_id = var.dataset_id
  table_id   = var.table_id
  time_partitioning {
    type  = "DAY"
    field = "block_timestamp"
  }
  labels = var.labels
  schema = file("${path.module}/payloads.json")
}