resource "google_bigquery_table" "k8s_lock" {  
  dataset_id = var.dataset_id
  table_id   = var.lock_table_id  
  deletion_protection = false

  labels = var.labels

  schema = file("${path.module}/bids_k8s_lock.json")
}

resource "google_bigquery_table" "config" {
  dataset_id = var.dataset_id
  table_id   = var.view_id
  deletion_protection = false

  view {
    query = templatefile("${path.module}/config.sql", {
      project_id      = var.project_id,
      dataset_id      = var.dataset_id,
      lock_table_id   = google_bigquery_table.k8s_lock.table_id,
    })
    use_legacy_sql = false
  }
}

resource "google_logging_project_sink" "sink" {
  name        = "bids_backload_to_bq"
  description = "Sink bids k8s backload logs to BQ"
  destination = "bigquery.googleapis.com/projects/${var.project_id}/datasets/${var.dataset_id}"
  filter      = "resource.type=k8s_container AND resource.labels.project_id=${var.project_id} AND resource.labels.location=${var.cluster_location} AND resource.labels.cluster_name=${var.cluster_name} AND resource.labels.namespace_name=default AND severity>=INFO"
  
  unique_writer_identity = true  
}