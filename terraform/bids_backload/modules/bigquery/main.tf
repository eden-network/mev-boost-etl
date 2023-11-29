resource "google_bigquery_table" "config" {
  dataset_id = var.dataset_id
  table_id   = var.view_id
  deletion_protection = false

  view {
    query = file("${path.module}/config.sql")
    use_legacy_sql = false
  }
}

resource "google_logging_project_sink" "sink" {
  name        = "bids_backload_to_bq"
  description = "Sink bids k8s backload logs to BQ"
  destination = "bigquery.googleapis.com/projects/${var.project_id}/datasets/${var.dataset_id}}"
  filter      = "resource.type=k8s_container and resource.labels.project_id=${var.project_id} AND resource.labels.location=${var.cluster_location} AND resource.labels.cluster_name=${var.cluster_name} AND resource.labels.namespace_name=default AND severity>=INFO"
  
  unique_writer_identity = true  
}