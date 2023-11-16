resource "google_bigquery_table" "config" {
  dataset_id = var.dataset_id,
  table_id   = var.view_id 

  view {
    query = file("${path.module}/config.sql")
    use_legacy_sql = false
  }
}